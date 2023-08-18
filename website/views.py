import os
import sys
import sqlalchemy
import random
import time

from flask import Response, Blueprint, render_template, request, jsonify, redirect, url_for, send_from_directory  #, flash
from flask_login import login_required, current_user
from .models import DBScript, Settings, User, SimulationTask
from . import db
from .demo_scripts import demo_scripts
from .global_variables import gvar

from exceptions import InterruptedSimulation


# Import stuff (e.g. util) from parent directory learningsimulator/
# (why so complicated to import from parent dir in Python?)
currentdir = os.path.dirname(os.path.realpath(__file__))  # Path to learningsimulator/website/
parentdir = os.path.dirname(currentdir)  # Path to learningsimulator/
sys.path.append(parentdir)
import util
from util import ParseUtil
from parsing import Script, ExportCmd
import keywords as kw

views = Blueprint('views', __name__)


# @views.route('/favicon.ico')
# def fav():
#     return send_from_directory(os.path.join(views.root_path, 'static'), 'favicon.ico')


# @views.route('/update_predef')
# def update_predef():
#     try:
#         add_predefined()
#         flash('Public datasets updated!', category='success')
#     except Exception as e:
#         flash(f'There was an error updating the database: {e}', category='error')
#     return redirect(url_for('views.home'))


# @views.before_request
# def before_request_func():
#     print("before_request executing!")


@views.route('/', methods=['GET'])
def landing():
    return render_template("landing.html", user=current_user)


# @views.route('/admini', methods=['GET'])
# def admin_page():
#     return redirect('/ewlr0249ler')


def run_simulation(script):
    progress = None
    try:
        script_obj = Script(script)
        script_obj.parse(is_webapp=True)  # Use is_webapp=True to discriminate Tkinter from browser frontend

        deprecated_warn = script_obj.check_deprecated_syntax()

        progress = ProgressWeb(script_obj)
        progress.set_done(False)
        progress.set_stop_clicked(False)

        amend_export_filenames(script_obj.script_parser.postcmds.cmds)

        simulation_data = script_obj.run(progress)
        script_obj.postproc(simulation_data, progress)
        progress.set_done(True)
        return False, script_obj.script_parser.postcmds, deprecated_warn
    except Exception as ex:
        stop_clicked = isinstance(ex, InterruptedSimulation)
        err_msg, lineno, stack_trace = util.get_errormsg(ex)
        if progress is not None:  # If parsing fails, ProgressWeb object is not created
            progress.set_done(True)
        return True, (err_msg, lineno, stack_trace, stop_clicked), None


def amend_export_filenames(cmds):
    '''
    Change all ExportCmd's filename to the same filename but including the absolute path to the current
    user's export directory. Filename is only a name (without path), enforced in the parsing.
    '''
    for cmd in cmds:
        if isinstance(cmd, ExportCmd):
            filename = cmd.parameters.get(kw.FILENAME)
            cmd.filename_no_path = filename
            export_dir = get_user_export_dir()
            os.makedirs(export_dir, exist_ok=True)
            abspath_filename = os.path.join(export_dir, filename)
            cmd.parameters.set_filename(abspath_filename)


def validate_script(name, code, id=None):
    err = None
    if len(name) == 0:
        err = "Script name must not be empty."
    elif len(name) > gvar['SCRIPTNAME_MAXLENGTH']:
        err = f"Script name must not be longer than {gvar['SCRIPTNAME_MAXLENGTH']} characters."
    elif len(code) > gvar['CODE_MAXLENGTH']:
        err = f"Script must not be longer than {gvar['CODE_MAXLENGTH']} characters."
    else:
        if id is not None:
            id = int(id)
            users_scripts = DBScript.query.filter(DBScript.user_id == current_user.id).all()
            for script in users_scripts:
                if script.name == name and script.id != id:
                    err = f"There is already a script with the name '{name}'."
                    break
    return err


@views.route('/my_scripts')
@login_required
def my_scripts():
    return render_template("my_scripts.html", user=current_user)


@views.route('/get/<int:id>')
@login_required
def get_script(id):
    script = DBScript.query.get_or_404(id)
    return {'name': script.name, 'code': script.code}


@views.route('/get_settings/<int:settings_id>')
@login_required
def get_settings(settings_id):
    settings = Settings.query.get_or_404(settings_id)
    return settings.to_dict()


def validate_settings(s):
    def is_hex_color(c):
        if len(c) != 4 and len(c) != 7:
            return False
        elif c[0] != '#':
            return False
        else:
            for ch in c[1:]:
                if ch.lower() not in ('0123456789abcdef'):
                    return False
        return True

    PREFIX = "Invalid value for "

    val = s['plot_type']
    if val not in ('plot', 'image'):
        return PREFIX + f"plot type: {str(val)}."

    val = s['file_type_mpl']
    if val not in ('png', 'jpg', 'svg', 'pdf'):
        return PREFIX + f"file type: {str(val)}."

    val = s['file_type_plotly']
    if val not in ('png', 'jpeg', 'svg', 'webp'):
        return PREFIX + f"file type: {str(val)}."

    val = s['plot_orientation']
    if val not in ('horizontal', 'vertical'):
        return PREFIX + f"plot orientation: {str(val)}."

    val, _ = ParseUtil.is_int(s['plot_width'])
    if val is None:
        return "Chart width not specified."
    elif (val < gvar['PLOTWIDTH_MINLENGTH'] or val > gvar['PLOTWIDTH_MAXLENGTH']):
        return PREFIX + f"chart width: {str(s['plot_width'])}. Width must be >= {gvar['PLOTWIDTH_MINLENGTH']} and <= {gvar['PLOTWIDTH_MAXLENGTH']}."

    val, _ = ParseUtil.is_int(s['plot_height'])
    if val is None:
        return "Chart height not specified."
    elif (val < gvar['PLOTHEIGHT_MINLENGTH'] or val > gvar['PLOTHEIGHT_MAXLENGTH']):
        return PREFIX + f"chart height: {str(s['plot_height'])}. Height must be >= {gvar['PLOTHEIGHT_MINLENGTH']} and <= {gvar['PLOTHEIGHT_MAXLENGTH']}."

    # val, _ = ParseUtil.is_float(s['legend_x'])
    # if val is None:
    #     return PREFIX + "legend relative x-coordinate: " + str(s['legend_x'])

    # val, _ = ParseUtil.is_float(s['legend_y'])
    # if val is None:
    #     return PREFIX + "legend relative y-coordinate: " + str(s['legend_y'])

    # val = s['legend_x_anchor']
    # if val not in ('left', 'center', 'right'):
    #     return PREFIX + "legend x-anchor: " + str(val)

    # val = s['legend_y_anchor']
    # if val not in ('bottom', 'middle', 'top'):
    #     return PREFIX + "legend y-anchor: " + str(val)

    val = s['legend_orientation']
    if val not in ('h', 'v'):
        return PREFIX + f"legend orientation: {str(val)}."

    val = s['paper_color']
    if not is_hex_color(val):
        return PREFIX + f"paper color: {str(val)}."

    val = s['plot_bgcolor']
    if not is_hex_color(val):
        return PREFIX + f"plot background color: {str(val)}."

    return None


@views.route('/save_settings', methods=['POST'])
@login_required
def save_settings():
    id = request.json['id']
    settings = request.json['settings']

    err = validate_settings(settings)
    if err:
        return {'error': err}
    settings_to_update = Settings.query.get_or_404(id)
    settings_to_update.save(settings)

    err = None
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.session.rollback()
        err = f"Error when saving the settings:\n{e}"
    return {'error': err}


@views.route('/get_demo/<int:index>', methods=['GET'])
def get_demo(index):
    script = demo_scripts[index - 1]
    return {'name': script['name'], 'code': script['code']}


@views.route('/save', methods=['POST'])
@login_required
def save_script():
    id = request.json['id']
    name = request.json['name']
    code = request.json['code']
    script_to_update = DBScript.query.get_or_404(id)
    err = validate_script(name, code, id)
    if err:
        return {'error': err}
    else:
        script_to_update.name = name
        script_to_update.code = code
        err = None
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            db.session.rollback()
            err = f"Error when saving script:\n{e}"
        return {'error': err}


@views.route('/add', methods=['POST'])
@login_required
def add():
    name = request.json['name']
    code = request.json['code']
    err = validate_script(name, code)
    new_script = DBScript(name=name,
                          code=code,
                          user_id=current_user.id)
    db.session.add(new_script)
    err = None
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        # If database server is down, this method add() cannot even be called
        # because of @login_required (which calls current_user)
        db.session.rollback()
        err = f"Error when adding script:\n{e}"
    return {'id': new_script.id, 'error': err}


@views.route('/delete', methods=['POST'])
def delete():
    ids_to_delete = request.json['ids']
    for id in ids_to_delete:
        script_to_delete = DBScript.query.get_or_404(id)
        script_to_delete_name = script_to_delete.name
        try:
            db.session.delete(script_to_delete)
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            db.session.rollback()
            err = f"Error when deleting script:\n{e}"
            return {'name': script_to_delete_name, 'error': err}
    return {'name': script_to_delete_name, 'error': None}


class ProgressWeb():
    def __init__(self, script_obj):
        self.script_obj = script_obj

        id = current_user.simulation_task_id
        self.db_task = SimulationTask.query.get_or_404(id)

        # self.DB_COMMIT_AT = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
        self.DB_COMMIT_AT = [0, 5, 20, 40, 60, 80, 95, 100]
        self.next_commit = self.DB_COMMIT_AT.pop(0)

        self.nsteps1 = sum(script_obj.script_parser.runs.get_n_subjects())
        self.nsteps1_percent = 100 / self.nsteps1 if self.nsteps1 > 0 else 1

        self.nsteps2 = script_obj.script_parser.runs.get_n_phases()
        self.nsteps2_percent = dict()
        for key in self.nsteps2:
            self.nsteps2_percent[key] = 100 / self.nsteps2[key] if self.nsteps2[key] > 0 else 1

        self.set_progress1(0)
        self.message1 = ""  # tk.StringVar()

        # Set to True when the Stop button has been clicked
        self.stop_clicked = False

        self.done = False

    def get_stop_clicked(self):
        return self.db_task.stop_clicked

    def set_stop_clicked(self, stop_clicked):
        self.db_task.stop_clicked = stop_clicked
        db.session.commit()

    def set_done(self, is_done):
        self.db_task.is_done = is_done
        if is_done:
            self.set_progress1(0)
            self.report1("")
        db.session.commit()

    def get_n_runs(self):
        return len(self.nsteps2)

    def set_progress1(self, val):
        self.progress1 = val
        self.db_task.progress1 = val
        if val >= self.next_commit:
            db.session.commit()
            if len(self.DB_COMMIT_AT) > 0:
                self.next_commit = self.DB_COMMIT_AT.pop(0)

    def increment1(self):
        new_value = self.progress1 + self.nsteps1_percent
        self.set_progress1(new_value)

    def increment2(self, run_label):
        pass

    def reset1(self):
        self.set_progress1(0)

    def reset2(self):
        pass

    def report1(self, message):
        self.message1 = message
        self.db_task.message1 = message

    def report2(self, message):
        pass

    def set_dlg_visibility2(self, visibility):
        pass
    
    def set_dlg_title(self, title):
        pass


@views.route('/run', methods=['POST'])
@login_required
def run():
    code = request.json['code']
    is_err, simulation_output, deprecated_warn = run_simulation(code)
    if is_err:
        err_msg, lineno, stack_trace, stop_clicked = simulation_output
        print(err_msg)
        print(stack_trace)
        return jsonify({'err_msg': err_msg, 'lineno': lineno, 'stack_trace': stack_trace,
                        'stop_clicked': stop_clicked})
    else:
        postcmds = simulation_output
        postcmds_out = []
        for cmd in postcmds.cmds:
            postcmds_out.append(cmd.to_dict())

        return jsonify({'postcmds': postcmds_out,
                        'deprecated_warn': deprecated_warn})


@views.route('/get_sim_status')
@login_required
def get_sim_status():
    try:
        db.session.commit()
        id = current_user.simulation_task_id
        task_to_read = SimulationTask.query.get_or_404(id)
        message1 = task_to_read.message1
        progress1 = task_to_read.progress1
        is_done = task_to_read.is_done
        err = None
    except sqlalchemy.exc.SQLAlchemyError as e:
        err = "Could not get simulation status."
        message1 = err
        progress1 = None
        is_done = True
    return {'message1': message1, 'progress1': progress1,
            'is_done': is_done, 'err': err}


@views.route('/stop_simulation')
@login_required
def stop_simulation():
    id = current_user.simulation_task_id
    db_task = SimulationTask.query.get_or_404(id)
    db_task.stop_clicked = True
    db_task.is_done = True  # Needed when called from simulate(id)
    err = None
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.session.rollback()
        err = f"Error when stopping simulation:\n{e}"
    return {'err': err}


@views.route('/run_mpl_fig', methods=['POST'])
@login_required
def run_mpl_fig():
    code = request.json['code']
    settings = request.json['settings']
    file_type = settings['file_type_mpl']
    is_err, simulation_output, deprecated_warn = run_simulation(code)
    if is_err:
        err_msg, lineno, stack_trace, stop_clicked = simulation_output
        return jsonify({'err_msg': err_msg, 'lineno': lineno, 'stack_trace': stack_trace,
                        'stop_clicked': stop_clicked})
    else:
        postcmds = simulation_output
        figs = postcmds.plot_no_pyplot(settings)
        user_dirname, img_dir = get_user_img_dir()
        os.makedirs(img_dir, exist_ok=True)
        out = list()
        for fig in figs:
            randstr = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            filename = f'figfile{randstr}.{file_type}'
            abspath = os.path.join(img_dir, filename)
            relpath = url_for('static', filename=f'mplfigimg/{user_dirname}/{filename}')
            fig.savefig(abspath, format=file_type)
            out.append(relpath)

        export_cmds = postcmds.get_export_cmds()
        export_cmds_json = []
        for exportcmd in export_cmds:
            export_cmds_json.append(exportcmd.to_dict())

        return jsonify({'imgfiles': out, 'exportcmds': export_cmds_json,
                        'deprecated_warn': deprecated_warn})


@views.route('/download_export_file/<path:filename>')
@login_required
def download_export_file(filename):
    export_dir = get_user_export_dir()
    return send_from_directory(export_dir, filename, as_attachment=True)


def get_user_img_dir():
    user_dirname = f'user{current_user.id}'
    img_dir = os.path.join(views.root_path, 'static', 'mplfigimg', user_dirname)
    return user_dirname, img_dir


def get_user_export_dir():
    user_dirname = f'user{current_user.id}'
    img_dir = os.path.join(views.root_path, 'static', 'export', user_dirname)
    return img_dir


def delete_all_files_in(dir):
    if os.path.isdir(dir):
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))


@views.route('/simulate/<int:id>', methods=['GET'])
@login_required
def simulate(id):

    # If ongoing simulation at reload, stop it
    sim_status = get_sim_status()
    if not sim_status['is_done']:
        stop_simulation()

    # Delete image files in users img dir
    _, img_dir = get_user_img_dir()
    delete_all_files_in(img_dir)

    # Delete exported files in users export dir
    export_dir = get_user_export_dir()
    delete_all_files_in(export_dir)

    script = DBScript.query.get_or_404(id)
    demo_script_names = [ds['name'] for ds in demo_scripts]
    settings = Settings.query.get(current_user.settings_id)

    return render_template("simulate.html", user=current_user, settings=settings,
                           script=script, demo_script_names=demo_script_names,
                           gvar=gvar)

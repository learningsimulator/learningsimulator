import os

from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import Script
from . import db
from .util import to_bool, list_to_csv, csv_to_list
from .webrunner import run_simulation
from .example_scripts import example_scripts

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


# @views.route('/', methods=['GET'])
# def landing():
#     return render_template("landing.html")


@views.route('/', methods=['GET'])
def home():
    example_script_names = [script['name'] for script in example_scripts]
    return render_template("home.html", user=current_user, example_script_names=example_script_names)


@views.route('/run', methods=['POST'])
def run():
    # form = AddScriptForm()
    # if request.method == 'POST':
    # if form.validate_on_submit():
    script = request.json['script']
    postcmds = run_simulation(script)
    return render_template("home.html", user=current_user, postcmds=postcmds.cmds)
    # return f"Script {script} finished successfully."
    # else:
    #     return render_template("home.html", user=current_user, form=form, postcmds=None)


# @views.route('/get_for_plot/<ids>')
# def get_for_plot(ids):
#     ids_list = ids.split(',')
#     return _get_for_plot(ids_list)


# @views.route('/get_for_plot_predef/<csv_list:ids_predef>')
# @login_required
# def get_for_plot_predef(ids_predef):
#     print(ids_predef)
#     return _get_for_plot(ids_predef, is_predef=True)


# @views.route('/get_for_plot_user/<csv_list:ids>')
# @login_required
# def get_for_plot_user(ids):
#     return _get_for_plot(ids, is_predef=False)


# def _get_for_plot(ids):
#     # ids is a list of integers (for user's data (id)) and strings (predefined data (id_predef))
#     xydata = []  # List of dicts
#     legends = []  # List of strings
#     data_is_qualitative = []
#     ind = 0
#     for id in ids:
#         if str.isdigit(id):
#             dataset = DataSet.query.get_or_404(int(id))
#         else:
#             dataset = DataSet.query.filter(DataSet.id_predef == id).first_or_404()
#         times = csv_to_list(dataset.time_values)
#         datas = csv_to_list(dataset.data_values)

#         for x, y in zip(times, datas):
#             if dataset.data_is_qualitative:
#                 xydata.append({"time" + str(ind): x,
#                                "value" + str(ind): "0",
#                                "text" + str(ind): y})
#             elif len(y) > 0:
#                 xydata.append({"time" + str(ind): x,
#                                "value" + str(ind): y})
#             else:  # amCharts interprets empty string as zero - for "no value" we need to omit the key "value"
#                 xydata.append({"time" + str(ind): x})
#         ind += 1
#         legend = dataset.legend
#         if dataset.data_scale is not None:
#             legend = legend + " (10^" + str(dataset.data_scale) + " " + dataset.data_unit + ")"
#         elif dataset.data_unit is not None:
#             legend = legend + " (" + dataset.data_unit + ")"
#         legends.append(legend)
#         data_is_qualitative.append(dataset.data_is_qualitative)

#     # Cannot return the list, must return a json
#     return jsonify(xydata=xydata, legends=legends, data_is_qualitative=data_is_qualitative)


def validate_script(name, id=None):
    err = None
    if len(name) == 0:
        err = "Script name must not be empty."
    else:
        if id is not None:
            id = int(id)
            users_scripts = Script.query.filter(Script.user_id == current_user.id).all()
            for script in users_scripts:
                if script.name == name and script.id != id:
                    err = f"There is already a script with the name '{name}'."
                    break
    return err


@views.route('/get/<int:id>')
@login_required
def get_script(id):
    script = Script.query.get_or_404(id)
    return {'name': script.name, 'code': script.code}


@views.route('/get_example/<int:index>')
def get_example_script(index):
    script = example_scripts[index - 1]
    return {'name': script['name'], 'code': script['code']}


@views.route('/save', methods=['POST'])
@login_required
def save_script():
    id = request.json['id']
    name = request.json['name']
    code = request.json['code']
    script_to_update = Script.query.get_or_404(id)
    err = validate_script(name, id)
    if err:
        return {'error': err}
    else:
        script_to_update.name = name
        script_to_update.code = code
        err = None
        try:
            db.session.commit()
            flash('Script saved!', category='success')
        except Exception as e:
            db.session.rollback()
            err = f"There was an error saving the script: {e}"
        return {'error': err}


@views.route('/add', methods=['POST'])
@login_required
def add():
    name = request.json['name']
    code = request.json['code']
    err = validate_script(name)
    new_script = Script(name=name,
                        code=code,
                        user_id=current_user.id)
    db.session.add(new_script)
    db.session.commit()
    # flash('Script added!', category='success')
    return {'id': new_script.id, 'errors': err}


@views.route('/delete', methods=['POST'])
def delete():
    ids_to_delete = request.json['ids']
    print(ids_to_delete)
    for id in ids_to_delete:
        script_to_delete = Script.query.get_or_404(id)
        try:
            db.session.delete(script_to_delete)
            db.session.commit()
        except Exception as e:
            err = "There was a problem deleting that script: " + str(e)
            return {'errors': err}
    return {'errors': None}

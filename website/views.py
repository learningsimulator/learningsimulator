import os

from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import Script
from .forms import AddScriptForm
from . import db
from .util import to_bool, list_to_csv, csv_to_list
from .webrunner import run_simulation

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
    form = AddScriptForm()
    return render_template("home.html", user=current_user, form=form)


@views.route('/run', methods=['POST'])
def run():
    form = AddScriptForm()
    # if request.method == 'POST':
    if form.validate_on_submit():
        script = request.form.get('script')
        postcmds = run_simulation(script)
        return render_template("home.html", user=current_user, form=form, postcmds=postcmds.cmds)
        # return f"Script {script} finished successfully."
    else:
        return render_template("home.html", user=current_user, form=form, postcmds=None)


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


def validate(name, id=None):
    err = None
    if len(name) == 0:
        err = "Script name must not be empty."
    else:
        if id is not None:
            id = int(id)
            users_scripts = Script.query.filter(Script.user_id == current_user.id).all()
            for script in users_scripts:
                if script.label == name and script.id != id:
                    err = f"There is already a script with the name '{name}'."
                    break
    return err


@views.route('/get/<int:id>')
@login_required
def get_script(id):
    script = Script.query.get_or_404(id)    
    return {'name': script.label, 'script': script.script}


# @views.route('/save/<int:id>', methods=['POST', 'GET'])
@views.route('/save', methods=['POST'])
@login_required
def save_script():
    id = request.json['id']
    label = request.json['name']
    script = request.json['script']
    script_to_update = Script.query.get_or_404(id)
    err = validate(label, id)
    if err:
        return {'error': err}
    else:
        script_to_update.label = label
        script_to_update.script = script
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
    label = request.json['name']
    script = request.json['script']
    err = validate(label)
    new_script = Script(label=label,
                        script=script,
                        user_id=current_user.id)
    db.session.add(new_script)
    db.session.commit()
    # flash('Script added!', category='success')
    return {'id': new_script.id, 'errors': err}

    # XXX
    # for i in range(1, 50):
    #     sc = Script.query.get(i)
    #     if sc is not None:
    #         if i >= 2:
    #             db.session.delete(sc)
    #             db.session.commit()
    #         print(sc.id)
    #     else:
    #         print("No " + str(i))    


# @views.route('/add', methods=['POST'])
# @login_required
# def add():
#     label = request.form['input-scriptlabel']
#     script = request.form['textarea-script']
    
#     form = AddScriptForm(formdata=None)
#     form.label = label
#     form.script = script
    
#     # if request.method == 'POST':
#     print(label)
#     print(script)
#     print(form.validate())
#     if form.validate_on_submit():
#         # label = form.get('label')
#         # script = form.get('script')
#         new_script = Script(label=label,
#                             script=script,
#                             user_id=current_user.id)
#         db.session.add(new_script)
#         db.session.commit()
#         flash('Script added!', category='success')
#         return {'aa': 1, 'bb': 2}
#         # return render_template("home.html", user=current_user)
#     else:
#         return {'a': 1, 'b': 2}
#         # return render_template("add_script.html", user=current_user, form=form)


@views.route('/delete/<int:id>')
def delete(id):
    script_to_delete = Script.query.get_or_404(id)
    err = None
    try:
        db.session.delete(script_to_delete)
        db.session.commit()
    except Exception as e:
        err = "There was a problem deleting that dataset: " + str(e)
    return {'errors': err}

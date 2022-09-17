import os
import json

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_from_directory  # flash
from flask_login import login_required, current_user
from .models import Script
from . import db
from .util import to_bool, list_to_csv, csv_to_list
from .webrunner import run_simulation
from .demo_scripts import demo_scripts

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
    demo_script_names = [script['name'] for script in demo_scripts]
    return render_template("home.html", user=current_user, demo_script_names=demo_script_names)


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


@views.route('/my_scripts')
@login_required
def my_scripts():
    return render_template("my_scripts.html", user=current_user)


@views.route('/get/<int:id>')
@login_required
def get_script(id):
    script = Script.query.get_or_404(id)
    return {'name': script.name, 'code': script.code}


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
            # flash('Script saved!', category='success')
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
    for id in ids_to_delete:
        script_to_delete = Script.query.get_or_404(id)
        try:
            db.session.delete(script_to_delete)
            db.session.commit()
        except Exception as e:
            err = "There was a problem deleting that script: " + str(e)
            return {'errors': err}
    return {'errors': None}


@views.route('/run', methods=['POST'])
def run():
    code = request.json['code']
    is_err, simulation_output = run_simulation(code)
    if is_err:
        err_msg, lineno, stack_trace = simulation_output
        return jsonify({'err_msg': err_msg, 'lineno': lineno, 'stack_trace': stack_trace})
    else:
        postcmds = simulation_output
        out = []
        for cmd in postcmds.cmds:
            out.append(cmd.to_dict())
        return jsonify(out)


@views.route('/run_mpl', methods=['POST'])
def run_mpl():
    code = request.json['code']
    is_err, simulation_output = run_simulation(code)
    if is_err:
        err_msg, lineno, stack_trace = simulation_output
        return jsonify({'err_msg': err_msg, 'lineno': lineno, 'stack_trace': stack_trace})
    else:
        postcmds = simulation_output
        out = postcmds.plot_js()
        return jsonify(out)


@views.route('/open/<int:id>', methods=['GET'])
def open(id):
    script = Script.query.get_or_404(id)
    demo_script_names = [ds['name'] for ds in demo_scripts]
    return render_template("home.html", user=current_user, script=script, demo_script_names=demo_script_names)


# @views.route('/run', methods=['POST'])
# def run():
#     script = request.json['script']
#     postcmds = run_simulation(script)
#     return render_template("home.html", user=current_user, postcmds=postcmds.cmds)

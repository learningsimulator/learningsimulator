from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Settings, SimulationTask
from .forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        rememeber = form.remember.data
        user = User.query.filter_by(email=email).first()
        if user:
            # if user.check_password(password):
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=rememeber)
                add_relations_to_user(user)
                return render_template("my_scripts.html", user=current_user)
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

        # return render_template("my_scripts.html", user=current_user)
    return render_template("login.html", user=current_user, form=form)


def add_relations_to_user(user):
    if not user.settings_id:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
        # After commit, settings has an id
        user.settings_id = settings.id
        db.session.commit()

    if not user.simulation_task_id:
        simulation_task = SimulationTask()
        db.session.add(simulation_task)
        db.session.commit()
        # After commit, simulation_task has an id
        user.simulation_task_id = simulation_task.id
        db.session.commit()


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.landing'))


@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        new_user = User(email=email, username=username,
                        password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        
        try:
            db.session.commit()
            # add_relations_to_user(new_user)
            flash("Account created!", category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.my_scripts'))
        except Exception as e:
            db.session.rollback()
            flash(f"There was an error adding the user: {e}", category='error')

    return render_template("sign_up.html", form=form, user=current_user)

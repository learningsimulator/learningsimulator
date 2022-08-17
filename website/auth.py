from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
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
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user, form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        new_user = User(email=email, username=username,
                        password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        
        try:
            db.session.commit()
            flash("Account created!", category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))
        except Exception as e:
            db.session.rollback()
            flash(f"There was an error saving the script: {e}", category='error')

    return render_template("sign_up.html", form=form, user=current_user)

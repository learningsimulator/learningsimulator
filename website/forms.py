from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from .global_variables import gvar

# from .models import SCRIPTNAME_MAXLENGTH, CODE_MAXLENGTH


# class AddScriptForm(FlaskForm):
#     name = StringField("Name of script:", default="",
#                        validators=[DataRequired(), Length(min=3, max=SCRIPTNAME_MAXLENGTH)])
#     script = TextAreaField("Script:",
#                            render_kw={'id':'script-textarea'},
#                            validators=[Length(max=CODE_MAXLENGTH)])


class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email(), Length(max=gvar['EMAIL_MAXLENGTH'])])
    username = StringField('Name:', validators=[DataRequired(), Length(max=gvar['USERNAME_MAXLENGTH'])])
    password = PasswordField('Password:', validators=[DataRequired(), Length(max=gvar['PASSWORD_MAXLENGTH'])])
    confirm_password = PasswordField('Confirm password:',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

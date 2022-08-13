from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

# from .models import SCRIPTNAME_MAXLENGTH, CODE_MAXLENGTH


# class AddScriptForm(FlaskForm):
#     name = StringField("Name of script:", default="",
#                        validators=[DataRequired(), Length(min=3, max=SCRIPTNAME_MAXLENGTH)])
#     script = TextAreaField("Script:",
#                            render_kw={'id':'script-textarea'},
#                            validators=[Length(max=CODE_MAXLENGTH)])


class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    username = StringField('Name:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password:',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

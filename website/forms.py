from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email

from .models import LABEL_MAXLENGTH, DESCRIPTION_MAXLENGTH, SCRIPT_MAXLENGTH


class AddScriptForm(FlaskForm):
    label = StringField("Name of script:", default="",
                        validators=[DataRequired(), Length(min=3, max=LABEL_MAXLENGTH)])
    # description = TextAreaField("Description:",
    #                             validators=[Length(max=DESCRIPTION_MAXLENGTH)])
    script = TextAreaField("Script:",
                            render_kw={'id':'script-textarea'},
                            validators=[Length(max=SCRIPT_MAXLENGTH)])

# XXX Use this (in auth.py and sign-up.html)
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     name = StringField('Email', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm password',
#                                      validators=[DataRequired(),
#                                                  EqualTo('password', message='Passwords must match.')])
#     submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

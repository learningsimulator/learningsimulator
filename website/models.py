from . import db  # From current package ("website") import db
from flask_login import UserMixin
from sqlalchemy.sql import func

SCRIPTNAME_MAXLENGTH = 50
CODE_MAXLENGTH = 10000


class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_predef = db.Column(db.Integer, unique=True, nullable=True)  # Unique if not null
    name = db.Column(db.String(SCRIPTNAME_MAXLENGTH))
    code = db.Column(db.String(CODE_MAXLENGTH))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # null means predefined script


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    scripts = db.relationship('Script')

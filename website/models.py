from . import db  # From current package ("website") import db
from flask_login import UserMixin
from sqlalchemy.sql import func

LABEL_MAXLENGTH = 50
DESCRIPTION_MAXLENGTH = 1000
SCRIPT_MAXLENGTH = 10000


class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_predef = db.Column(db.Integer, unique=True, nullable=True)  # Unique if not null
    label = db.Column(db.String(LABEL_MAXLENGTH))
    description = db.Column(db.String(DESCRIPTION_MAXLENGTH))
    script = db.Column(db.String(SCRIPT_MAXLENGTH))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # null means predefined script


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    scripts = db.relationship('Script')

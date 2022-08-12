from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.routing import BaseConverter
# from flask_cors import CORS


db = SQLAlchemy()
DB_NAME = "database.db"


# class ListConverter(BaseConverter):
#     # regex = r'\d+(?:,\d+)*,?'

#     def to_python(self, value):
#         # return [int(x) for x in value.split(',')]
#         return value.split(',')

#     def to_url(self, values):
#         # return ','.join(str(x) for x in value)
#         # return '+'.join([BaseConverter.to_url(value) for value in values])
#         return ','.join(values)

def create_app():
    app = Flask(__name__)  # __name__ is 'website'
    # app.url_map.converters['csv_list'] = ListConverter

    # Used to encrypt the cookie and session data related to our web app
    app.config['SECRET_KEY'] = '410d1f4eb7412ee625ed5a3562ec1cc6'

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # To avoid warning. We do not use the Flask-SQLAlchemy event system, anyway.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CORS(app)

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

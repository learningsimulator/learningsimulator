from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.routing import BaseConverter
# from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page"


def create_app():
    app = Flask(__name__)  # __name__ is 'website'

    # Sets app.config[KEY] for the keys in config.py
    app.config.from_pyfile('config.py')

    # This enables CORS for all routes in the app, used when you want to allow or enable web pages
    # from one domain to make requests to your Flask API, which is hosted on a different domain. 
    # CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .models import User

    # with app.app_context():
    #     if db.engine.url.drivername == 'sqlite':
    #         # Workaround for SQLite not handling ALTER/DROP: use render_as_batch=True
    #         migrate.init_app(app, db, render_as_batch=True)
    #     else:
    #         migrate.init_app(app, db)
    #     create_database(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app


def create_database(app):
    # SQLite
    # if not path.exists('website/' + DB_NAME):
    #     db.create_all(app=app)
    #     print('Created Database!')

    # db.create_all(app=app)
    db.create_all()
    print('Created Database!')

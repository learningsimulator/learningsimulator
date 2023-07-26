from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.routing import BaseConverter
# from flask_cors import CORS


db = SQLAlchemy()
# DB_NAME = "database.db"

migrate = Migrate()

def create_app():
    app = Flask(__name__)  # __name__ is 'website'
    # app.url_map.converters['csv_list'] = ListConverter

    # Used to encrypt the cookie and session data related to our web app
    app.config['SECRET_KEY'] = '410d1f4eb7412ee625ed5a3562ec1cc6'

    # The SQLite db
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # The MySQL db
    DB_USER = "birds"  # XXX Put these secret things in a config.py or similar
    DB_PW = "xBqjfrF.9H6BT4G"
    DB_HOST_ADDRESS = "birds.mysql.pythonanywhere-services.com"
    DB_NAME = f"{DB_USER}@default"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DB_USER}:{DB_PW}@{DB_HOST_ADDRESS}/{DB_NAME}"

    # When running locally:
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:hejsan123@localhost/db_weblesim'

    # To avoid warning. We do not use the Flask-SQLAlchemy event system, anyway.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CORS(app)

    db.init_app(app)

    from .models import User

    # Workaround for SQLite not handling ALTER/DROP: use render_as_batch=True
    with app.app_context():
        if db.engine.url.drivername == 'sqlite':  
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)
        create_database(app)
        # db.create_all() 

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    # SQLite
    # if not path.exists('website/' + DB_NAME):
    #     db.create_all(app=app)
    #     print('Created Database!')

    # db.create_all(app=app)
    db.create_all()
    print('Created Database!')

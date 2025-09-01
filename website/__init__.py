from flask import Flask
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Load DB credentials from .env
    db_username = os.getenv('DB_USERNAME')
    db_password = quote_plus(os.getenv('DB_PASSWORD'))
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    database_uri = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    db.init_app(app)
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from . import models as db_models
    create_db(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db_models.User.query.get(int(user_id))

    return app

def create_db(app):
    with app.app_context():
        db.create_all()
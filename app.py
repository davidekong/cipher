from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from events import socketio

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'  # Use blueprint name


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sigmoid'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    from routes import main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()

    return app

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

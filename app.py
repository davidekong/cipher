from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from events import socketio

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'  # Use blueprint name for login redirect

def create_app():
    # Create Flask app instance
    app = Flask(__name__)
    # Set secret key and database config
    app.config['SECRET_KEY'] = 'sigmoid'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Register blueprints
    from routes import main_blueprint
    app.register_blueprint(main_blueprint)

    # Create all database tables
    with app.app_context():
        db.create_all()

    return app

from models import User

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

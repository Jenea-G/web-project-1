# 1 Create the Flask application and database.
import os
from dotenv import load_dotenv
from flask import (Flask, render_template, request, url_for, redirect, flash, session)
from flask_login import (LoginManager, login_user, logout_user, current_user, login_required)

from models import (db, User, Picnic, Item, Guest, ItemCategory)
from routes.user import user_bp
from routes.picnic import picnic_bp
from routes.item import item_bp
from routes.guest import guest_bp

from datetime import datetime

app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(picnic_bp)
app.register_blueprint(item_bp)
app.register_blueprint(guest_bp)

app.config["SQLALCHEMY_DATABASE_URI"] = ("sqlite:///picnic_app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# set the secret key from an envrionment variable.
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# bind database to the application
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template(
        "index.html"
    )
# login
login_manager = LoginManager()      # Create the login manager
login_manager.login_view = "user_bp.login"  # Redirect unauthenticated users to /login
login_manager.init_app(app)         # Attach manager to the app

# load user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
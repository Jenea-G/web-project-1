# 1 Create the Flask application and database.
import os
from dotenv import load_dotenv
from flask import (Flask, render_template)

from models import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = ("sqlite:///picnic_app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# set the secret key from an envrionment variable.
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# bind database to the application
db.init_app(app)

# with app.app_context():
#     db.create_all()

@app.route("/")
def home():
    return render_template(
        "index.html"
    )
# 1 Create the Flask application and database.
import os
from dotenv import load_dotenv
from flask import (Flask, render_template, request, url_for, redirect, flash, session)
from flask_login import (LoginManager, login_user, logout_user, current_user, login_required)

from models import (db, User, Picnic, Item, Guest, ItemCategory)
from routes.user import user_bp
from routes.picnic import picnic_bp
from routes.item import item_bp

from datetime import datetime

app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(picnic_bp)
app.register_blueprint(item_bp)

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


# ===== Guest logic =====
# importing module for secure random number generation
import secrets

# generate unique pin per picnic
def generate_guest_pin(picnic):
    while True:
        pin = f"{secrets.randbelow(1_000_000):06d}"

        if not any(guest.pin == pin for guest in picnic.guests):
            return pin

# join picnic as guest
@app.route("/join", methods=["GET", "POST"])
def join_picnic():

    # restriction to join as a guest when user logged in
    if current_user.is_authenticated:
        flash("Please log out before joining a picnic as a guest.", "error")
        return redirect(url_for("user_bp.picnics"))

    if request.method == "POST":
        picnic_name = request.form.get(
            "picnic_name", ""
        ).strip()

        invitation_code = request.form.get(
            "invitation_code", ""
        ).strip()

        guest_name = request.form.get(
            "guest_name", ""
        ).strip()

        errors = []

        if not picnic_name:
            errors.append("Picnic name is required.")

        if not invitation_code:
            errors.append("Invitation code is required.")

        if not guest_name:
            errors.append("Your name is required.")
        elif len(guest_name) > 155:
            errors.append(
                "Your name may contain at most 155 characters."
            )

        picnic = None

        if picnic_name and invitation_code:
            picnic = Picnic.query.filter_by(
                picnic_name=picnic_name,
                invitation_code=invitation_code
            ).first()

            if picnic is None:
                errors.append(
                    "No picnic was found with this name "
                    "and invitation code."
                )

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "join_picnic.html",
                picnic_name=picnic_name,
                invitation_code=invitation_code,
                guest_name=guest_name
            )

        guest = Guest(
            name=guest_name,
            pin=generate_guest_pin(picnic),
            picnic=picnic
        )

        db.session.add(guest)
        db.session.commit()

        flash(
            f"You joined the picnic. Your guest PIN is "
            f"{guest.pin}. Save it so you can return later.",
            "success"
        )

        session["guest_id"] = guest.id # add guest to the session to remember him/her for further actions

        return render_template(
            "picnic.html",
            picnic=picnic,
            guest=guest,
            guest_pin=guest.pin,
            is_organizer=False
        )

    return render_template("join_picnic.html")

@app.route("/join/return", methods=["GET", "POST"])
def returning_guest():
    if request.method == "POST":
        invitation_code = request.form.get(
            "invitation_code", ""
        ).strip()

        guest_pin = request.form.get(
            "guest_pin", ""
        ).strip()

        errors = []

        if not invitation_code:
            errors.append("Invitation code is required.")

        if not guest_pin:
            errors.append("Guest PIN is required.")

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "join_picnic.html",
                invitation_code=invitation_code
            )

        guest = (
            Guest.query
            .join(Picnic)
            .filter(
                Picnic.invitation_code == invitation_code,
                Guest.pin == guest_pin
            )
            .first()
        )

        if guest is None:
            flash(
                "Invalid invitation code or guest PIN.",
                "error"
            )

            return render_template(
                "join_picnic.html",
                invitation_code=invitation_code
            )

        session["guest_id"] = guest.id # add guest to the session to remember him/her for further actions

        return render_template(
            "picnic.html",
            picnic=guest.picnic,
            guest=guest,
            guest_pin=guest.pin,
            is_organizer=False
        )

    return render_template("join_picnic.html")
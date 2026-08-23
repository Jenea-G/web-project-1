# 1 Create the Flask application and database.
import os
from dotenv import load_dotenv
from flask import (Flask, render_template, request, url_for, redirect, flash, session)
from flask_login import (LoginManager, login_user, logout_user, current_user, login_required)

from models import (db, User, Picnic, Item, Guest, ItemCategory)
from routes.user import user_bp
from routes.picnic import picnic_bp

from datetime import datetime

app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(picnic_bp)

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


# add items to the picnic by user or by guest
@app.route("/picnic/<int:picnic_id>/items/add", methods=["POST"])
def add_item(picnic_id):
    picnic = Picnic.query.get_or_404(picnic_id)

    # Guest
    guest = Guest.query.filter_by(
            id=session.get("guest_id"),
            picnic_id=picnic.id
        ).first()
    
    # Guest or registered user
    if guest or (current_user.is_authenticated and picnic.user_id == current_user.id):

        item_name = request.form.get("item_name", "").strip()
        category_name = request.form.get("category", "").strip()

        if not item_name:
            flash("The item name is required.", "error")
            return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

        if len(item_name) > 155:
            flash("The item name is too long.", "error")
            return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

        try:
            category = ItemCategory[category_name]
        except KeyError:
            flash("Invalid item category.", "error")
            return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

        if category not in picnic.selected_categories:
            flash("This category is not available for this picnic.", "error")
            return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

        item = Item(
            name=item_name,
            category=category,
            picnic=picnic
        )

        db.session.add(item)
        db.session.commit()

        flash("Item added successfully.", "success")
       
    else:
        flash("You cannot add items to this picnic.", "error")

    return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))
    

# claim items by user(organizer) or guest
@app.route("/items/<int:item_id>/grab", methods=["POST"])
def grab_item(item_id):
    item = Item.query.get_or_404(item_id)
    picnic = item.picnic

    if not item.is_claimed:

        guest = Guest.query.filter_by(
            id=session.get("guest_id"),
            picnic_id=picnic.id
        ).first()

        # Claim by organizer
        if (current_user.is_authenticated and picnic.user_id == current_user.id):
            item.claim_by_user(current_user)
            db.session.commit()
            flash("You claimed the item.", "success")

        # Claim by guest
        elif guest:
            item.claim_by_guest(guest)
            db.session.commit()
            flash("You claimed the item.", "success")

        else:
            flash("You cannot claim items from this picnic.", "error")

    else:
        flash("This item has already been claimed.", "error")

    return redirect(
        url_for("picnic_bp.picnic", picnic_id=item.picnic_id)
    )

# drop items by user or guest who have claimed them
@app.route("/items/<int:item_id>/drop", methods=["POST"])
def drop_item(item_id):
    item = Item.query.get_or_404(item_id)
    picnic = item.picnic

    guest = Guest.query.filter_by(
        id=session.get("guest_id"),
        picnic_id=picnic.id
    ).first()

    can_drop = False

    if (current_user.is_authenticated and item.claimed_by_user_id == current_user.id):
        can_drop = True

    elif (guest and item.claimed_by_guest_id == guest.id):
        can_drop = True

    if can_drop:
        item.drop()
        db.session.commit()
        flash("Item dropped successfully.", "success")

    else:
        flash("You can only drop items you have claimed.", "error")

    return redirect(url_for("picnic_bp.picnic", picnic_id=item.picnic_id))

# delete items by guests or users
@app.route("/items/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    picnic = item.picnic

    # Check guest
    guest = Guest.query.filter_by(
        id=session.get("guest_id"),
        picnic_id=picnic.id
    ).first()

    # Check organizer
    organizer = (current_user.is_authenticated and picnic.user_id == current_user.id)

    # Must belong to the picnic
    if not organizer and not guest:
        flash("You cannot delete items from this picnic.", "error")
        return redirect(
            url_for("picnic_bp.picnic", picnic_id=picnic.id))

    # Cannot delete a claimed item
    if item.is_claimed:
        flash("You cannot delete an item that has been claimed.", "error")
        return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

    db.session.delete(item)
    db.session.commit()

    flash("Item deleted successfully.", "success")

    return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

# edit items logic
@app.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    picnic = item.picnic

    guest = Guest.query.filter_by(
        id=session.get("guest_id"),
        picnic_id=picnic.id
    ).first()

    organizer = (current_user.is_authenticated and picnic.user_id == current_user.id)

    # Must belong to this picnic
    if not organizer and not guest:
        flash("You cannot edit items from this picnic.", "error")
        return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

    # Item must be free or claimed by this participant
    can_edit = (not item.is_claimed
                or (organizer and item.claimed_by_user_id == current_user.id)
                or (guest and item.claimed_by_guest_id == guest.id))

    if not can_edit:
        flash("You can only edit unclaimed items or items you have claimed.", "error")
        return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

    # GET -> show form
    if request.method == "GET":
        return render_template("edit_item.html", item=item, picnic=picnic)

    # POST
    # Process submitted form
    item_name = request.form.get("item_name", "").strip()
    category_name = request.form.get("category", "").strip()

    errors = []

    if not item_name:
        errors.append("The item name is required.")

    if len(item_name) > 155:
        errors.append("The item name is too long.")

    try:
        category = ItemCategory[category_name]
    except KeyError:
        category = None
        errors.append("Invalid item category.")

    if category and category not in picnic.selected_categories:
        errors.append("This category is not available for this picnic.")

    if errors:
        for error in errors:
            flash(error, "error")

        return render_template("edit_item.html", item=item, picnic=picnic) 

    item.name = item_name
    item.category = category

    db.session.commit()

    flash("Item updated successfully.", "success")

    return redirect(
        url_for("picnic_bp.picnic", picnic_id=picnic.id)
    )


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
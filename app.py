# 1 Create the Flask application and database.
import os
from dotenv import load_dotenv
from flask import (Flask, render_template, request, url_for, redirect, flash, session)
from flask_login import (LoginManager, login_user, logout_user, current_user, login_required)

from models import (db, User, Picnic, Item, Guest, ItemCategory)

from datetime import datetime

app = Flask(__name__)

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
login_manager.login_view = "login"  # Redirect unauthenticated users to /login
login_manager.init_app(app)         # Attach manager to the app

# load user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Registeration Validation
def validate_password(password):

    if len(password) < 8:
        return("Password must contain at least 8 characters.")
    if len(password) > 20:
        return("Password must contain at most 20 characters.") 
    if not any(character.isupper() for character in password):
        return("Password must contain at least one uppercase letter.")
    if not any(character.isdigit() for character in password):
        return("Password must contain a digit.")
    if any(character.isspace() for character in password):
        return("Password may not contain whitespace.")
    
    return None


# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        name = request.form["name"].strip()

        errors = []

        if not username:
            errors.append("Username is required.")
        if len(username) > 50:
            errors.append("Username may contain at most 50 characters.") 
        if any(character.isspace() for character in username):
            errors.append("Username may not contain whitespace.")

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            errors.append("This username is already in use!")

        password_error = validate_password(password)
        if password_error:
            errors.append(password_error)

        if not name:
            errors.append("Name is required.")
        if len(name) > 155:
            errors.append("Name may contain at most 155 characters.") 

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template("register.html", username=username, name=name)
        
        # no errors
        user = User(username=username, name=name)

        # hash the password
        user.set_password(password)

        # add it to the table
        db.session.add(user)
        db.session.commit()

        flash("Your account has been created!", "success")

        return redirect(url_for("login"))
        #return redirect(url_for("home")) #to check if /registration works
    
    return render_template("register.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home")) # will return to pincnics once created
    
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        # username or passwrod error
        if user is None or not user.check_password(password):
            flash("Invalid username or password", "error")

            return render_template("login.html", username=username)
        
        # when no errors
        login_user(user)

        flash("You are now logged in.", "success")

        return redirect(url_for("home"))
    
    return render_template("login.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()

    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

# picnics
@app.route("/picnics", methods=["GET"])
@login_required
def picnics():
    user_picnics = Picnic.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "picnics.html",
        picnics=user_picnics
    )

# create_picnic
@app.route("/picnics/create", methods=["GET", "POST"])
@login_required
def create_picnic():
    if request.method == "POST":
        picnic_name = request.form.get("picnic_name").strip()
        location = request.form.get("location").strip()
        date_str = request.form.get("date")
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        invitation_code = request.form.get("invitation_code").strip()

        errors = []

        if not picnic_name:
            errors.append("Picnic name is required.")
        
        if not location:
            errors.append("Location is required.")

        if not invitation_code:
            errors.append("Invitation code is required.")

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template("create_picnic.html")

        picnic = Picnic(
            picnic_name=picnic_name,
            invitation_code=invitation_code,
            location=location,
            date=date,
            categories="Food,Drinks",
            user=current_user
        )

        db.session.add(picnic)
        db.session.commit()

        return redirect(url_for("picnics"))

    return render_template("create_picnic.html")

# picnic
@app.route("/picnic/<int:picnic_id>")
def picnic(picnic_id):
    picnic = Picnic.query.get_or_404(picnic_id)

    # Check guest
    guest = Guest.query.filter_by(
        id=session.get("guest_id"),
        picnic_id=picnic.id
    ).first()

    # Organizer
    if current_user.is_authenticated and picnic.user_id == current_user.id:
        return render_template(
            "picnic.html",
            picnic=picnic,
        )

    # Guest
    if guest:
        return render_template(
            "picnic.html",
            picnic=picnic,
            guest=guest,
        )

    # Neither organizer nor valid guest
    flash("You do not have access to this picnic.", "error")
    return redirect(url_for("home"))

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
            return redirect(url_for("picnic", picnic_id=picnic.id))

        if len(item_name) > 155:
            flash("The item name is too long.", "error")
            return redirect(url_for("picnic", picnic_id=picnic.id))

        try:
            category = ItemCategory[category_name]
        except KeyError:
            flash("Invalid item category.", "error")
            return redirect(url_for("picnic", picnic_id=picnic.id))

        if category not in picnic.selected_categories:
            flash("This category is not available for this picnic.", "error")
            return redirect(url_for("picnic", picnic_id=picnic.id))

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

    return redirect(url_for("picnic", picnic_id=picnic.id))
    

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
        url_for("picnic", picnic_id=item.picnic_id)
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

    return redirect(url_for("picnic", picnic_id=item.picnic_id))

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
            url_for("picnic", picnic_id=picnic.id))

    # Cannot delete a claimed item
    if item.is_claimed:
        flash("You cannot delete an item that has been claimed.", "error")
        return redirect(url_for("picnic", picnic_id=picnic.id))

    db.session.delete(item)
    db.session.commit()

    flash("Item deleted successfully.", "success")

    return redirect(url_for("picnic", picnic_id=picnic.id))

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
                "returning_guest.html",
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
                "returning_guest.html",
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

    return render_template("returning_guest.html")
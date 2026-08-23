from flask import (Blueprint, redirect, request, url_for, flash, render_template)
from flask_login import (LoginManager, current_user, login_user, login_required, logout_user )
from models import (db, User, Picnic, ItemCategory)

user_bp = Blueprint("user_bp", __name__)

# Registration Validation
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
@user_bp.route("/register", methods=["GET", "POST"])
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

        return redirect(url_for("user_bp.login"))
        #return redirect(url_for("home")) #to check if /registration works
    
    return render_template("register.html")

# Login route
@user_bp.route("/login", methods=["GET", "POST"])
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

        return redirect(url_for("user_bp.picnics"))
    
    return render_template("login.html")

# Logout
@user_bp.route("/logout")
@login_required
def logout():
    logout_user()

    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

# picnics
@user_bp.route("/picnics", methods=["GET"])
@login_required
def picnics():
    user_picnics = Picnic.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "picnics.html",
        picnics=user_picnics
    )
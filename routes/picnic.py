from flask import (Blueprint, request, url_for, redirect, flash, session, render_template)
from models import (db, User, Picnic, ItemCategory, Guest)
from flask_login import (login_required, current_user)
from datetime import datetime

picnic_bp = Blueprint("picnic_bp", __name__)

# create_picnic
@picnic_bp.route("/picnics/create", methods=["GET", "POST"])
@login_required
def create_picnic():
    if request.method == "POST":
        picnic_name = request.form.get("picnic_name").strip()
        location = request.form.get("location").strip()
        date_str = request.form.get("date")
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        invitation_code = request.form.get("invitation_code").strip()

        categories = request.form.getlist("categories")

        existing_code = Picnic.query.filter_by(invitation_code=invitation_code).first()

        errors = []

        if not picnic_name:
            errors.append("Picnic name is required.")
        
        if not location:
            errors.append("Location is required.")

        if not invitation_code:
            errors.append("Invitation code is required.")
                
        if existing_code:
            errors.append("This invitation code is already in use. Please choose another one.")

        if not categories:
            errors.append("Please select at least one category.")

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template("create_picnic.html", name=picnic_name, location=location, date=date_str, categories=categories)

        picnic = Picnic(
            picnic_name=picnic_name,
            invitation_code=invitation_code,
            location=location,
            date=date,
            categories=",".join(categories),
            user=current_user
        )

        db.session.add(picnic)
        db.session.commit()

        flash("Picnic created successfully.", "success")

        return redirect(url_for("user_bp.picnics"))

    return render_template("create_picnic.html")

# edit picnic logic
@picnic_bp.route("/picnics/<int:picnic_id>/edit", methods=["GET", "POST"])
@login_required
def edit_picnic(picnic_id):
    picnic = Picnic.query.get_or_404(picnic_id)

    # create a set of used categories to avoid removing them as they have items inside (& sending them to the template)
    used_categories = set()
    for item in picnic.items:
        category = item.category.value
        used_categories.add(category)

    # print(used_categories)

    # Only the organizer can edit this picnic
    if picnic.user_id != current_user.id:
        flash("You cannot edit this picnic.", "error")
        return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

    if request.method == "POST":
        picnic_name = request.form.get("picnic_name").strip()
        location = request.form.get("location").strip()
        date_str = request.form.get("date")
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        invitation_code = request.form.get("invitation_code").strip()

        categories = request.form.getlist("categories")
        removed_categories = used_categories - set(categories)
        
        errors = []

        if not picnic_name:
            errors.append("Picnic name is required.")
        
        if not location:
            errors.append("Location is required.")

        if not invitation_code:
            errors.append("Invitation code is required.")

        if not categories:
            errors.append("Please select at least one category.")

        # Prevent removing categories that already contain items
        if removed_categories:
            errors.append(
                "You cannot remove categories that already contain items.")

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template("picnic_bp.edit_picnic.html",picnic=picnic,ItemCategory=ItemCategory, used_categories=used_categories)

        picnic.picnic_name = picnic_name
        picnic.invitation_code = invitation_code
        picnic.location = location
        picnic.date = date
        picnic.categories = ",".join(categories)

        db.session.commit()

        flash("Picnic updated successfully.", "success")

        return redirect(url_for("picnic_bp.picnic", picnic_id=picnic.id))

    return render_template("edit_picnic.html",picnic=picnic,ItemCategory=ItemCategory, used_categories=used_categories)

# picnic
@picnic_bp.route("/picnic/<int:picnic_id>")
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

# delete picnic
@picnic_bp.route("/picnics/<int:picnic_id>/delete", methods=["POST"])
@login_required
def delete_picnic(picnic_id):
    # get current user's selected picnic
    picnic = Picnic.query.filter_by(id=picnic_id, user_id=current_user.id).first_or_404()
          
    # delete
    db.session.delete(picnic)
    db.session.commit()

    flash("Your picnic was successfully deleted", "success")
    return redirect(url_for("user_bp.picnics"))
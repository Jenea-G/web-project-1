from flask import (Blueprint, render_template, request, url_for, redirect, flash, session)
from models import (db, Picnic, Item, Guest, ItemCategory)
from flask_login import current_user

item_bp = Blueprint("item_bp", __name__)

# add items to the picnic by user or by guest
@item_bp.route("/picnic/<int:picnic_id>/items/add", methods=["POST"])
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
@item_bp.route("/items/<int:item_id>/grab", methods=["POST"])
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
@item_bp.route("/items/<int:item_id>/drop", methods=["POST"])
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
@item_bp.route("/items/<int:item_id>/delete", methods=["POST"])
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
@item_bp.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
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
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import (check_password_hash, generate_password_hash)

from enum import Enum


db = SQLAlchemy()

# User model
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable = False, unique = True)
    name = db.Column(db.String(155), nullable = False)

    password_hash = db.Column(db.String(255), nullable = False)

    picnics = db.relationship(
        "Picnic",
        back_populates="user" #refers to Picnic.user
    )
    claimed_items = db.relationship("Item", back_populates="claimed_by_user") # user - items relationship

    # methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_picnic(self, picnic):
        self.picnics.append(picnic) # collect picnic objects

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"
    
# Picnic model
class Picnic(db.Model):
    __tablename__ = "picnic"
    
    id = db.Column(db.Integer, primary_key = True)
    picnic_name = db.Column(db.String(155), nullable = False)
    invitation_code = db.Column(db.String(155), nullable = False)
    location = db.Column(db.String(155), nullable = False)
    date = db.Column(db.Date, nullable = False)
    categories =  db.Column(db.String(255), nullable = False) # fixed selection of categories

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", back_populates="picnics" # refers to the attribute on User.picnics
    )

    # creating `picnic - items` relationship
    items = db.relationship("Item", back_populates="picnic", cascade="all, delete-orphan") # 'cascade all...' is essential to allow deleting picnic with its items

    # creating `picnic - guests` relationship
    guests = db.relationship("Guest", back_populates="picnic", cascade="all, delete-orphan") # guests will get removed together with picnic deletion

    # get list of selected categories
    @property
    def selected_categories(self):
        selected = []

        categories = self.categories.split(",")
        for category in categories:
            selected.append(ItemCategory(category))

        return selected

    # get list of items by category
    def get_items_by_category(self, category):
        items_by_category = []

        for item in self.items:
            if item.category == category:
                items_by_category.append(item)
        
        return items_by_category
    
    def __repr__(self):
        return f"<Picnic {self.id}: '{self.picnic_name}'>"
    
    # ! need to store all the guests to display names on the page and to show who claimed items
    
class ItemCategory(Enum):
    FOOD = "Food"
    DRINKS = "Drinks"
    EQUIPMENT = "Equipment"
    DESSERTS = "Desserts"
    ENTERTAINMENT = "Entertainment"
    SNACKS = "Snacks"

# create Item model
class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(155), nullable=False)
    category = db.Column(db.Enum(ItemCategory), nullable=False)

    claimed_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True) # will store the user.id if claimed_by_user
    claimed_by_guest_id = db.Column(db.Integer, db.ForeignKey("guest.id"), nullable=True) # will store the guest.id if claimed by guest

    picnic_id = db.Column(db.Integer, db.ForeignKey("picnic.id"), nullable=False)

    picnic = db.relationship("Picnic", back_populates="items")
    claimed_by_user = db.relationship("User", back_populates="claimed_items") # 'items to user' relationship
    claimed_by_guest = db.relationship("Guest", back_populates="claimed_items") # 'items to guest' relationship

    @property
    def is_claimed(self):
        return (
            self.claimed_by_user_id is not None
            or self.claimed_by_guest_id is not None
        )

    @property
    def claimant_type(self):
        if self.claimed_by_user_id is not None:
            return "user"

        if self.claimed_by_guest_id is not None:
            return "guest"

        return None

    def claim_by_user(self, user):
        if self.is_claimed:
            return False

        self.claimed_by_user = user
        self.claimed_by_guest = None
        return True

    def claim_by_guest(self, guest):
        if self.is_claimed:
            return False
        
        self.claimed_by_guest = guest
        self.claimed_by_user = None
        return True
    
    def drop(self):
        self.claimed_by_user = None
        self.claimed_by_guest = None

    def __repr__(self):
        return f"<Item {self.id}: {self.name}>"
    
    # each item has a property is_claimed and methods: claim_by_user /claim_by_guest and drop


# create Guest model
class Guest(db.Model):
    __tablename__= "guest"
    
    __table_args__ = (
        db.UniqueConstraint(
            "picnic_id",
            "pin",
            name="unique_guest_pin_per_picnic"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(155), nullable=False)
    pin = db.Column(db.String(6), nullable=False)

    picnic_id = db.Column(db.Integer,db.ForeignKey("picnic.id"), nullable=False)

    picnic = db.relationship("Picnic", back_populates="guests") # 'guests to picnic' relationship
    claimed_items = db.relationship("Item", back_populates="claimed_by_guest") # 'guest to items' relationship



from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import (check_password_hash, generate_password_hash)


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
        back_populates="user" # refers to Picnic.user
    )

    # methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_picnic(self, picnic):
        self.picnics.append(picnic) # collect picnic objects

    def __repr__(self):
        return f"<User {self.user_id}: {self.username}>"

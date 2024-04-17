from datetime import datetime

from flask_login import UserMixin

from app import bcrypt, db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    authProvider = db.Column(db.String, nullable=False, default="credentials")
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable = True)
    avatar_url = db.Column(db.String, nullable = True)
    created_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, *args, **kwargs):
        self.authProvider = kwargs.get("authProvider")
        self.email = kwargs.get("email")
        self.password = bcrypt.generate_password_hash(kwargs.get("password"))
        self.username = kwargs.get("username") or kwargs.get("email").split("@")[0]
        self.avatar_url = kwargs.get("avatar_url")
        self.created_on = datetime.now()
        self.is_admin = kwargs.get("is_admin")
        self.is_confirmed = kwargs.get("is_confirmed")
        self.confirmed_on = kwargs.get("confirmed_on")

        
    def __repr__(self):
        return f"<email {self.email}>"

from flask_login import UserMixin
from app import db
from cryptography.fernet import Fernet


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    pw_salt = db.Column(db.String(100), nullable=False, unique=True)
    key = db.Column(db.BLOB, nullable=False, unique=True)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    # Define the relationship to Draw
    draws = db.relationship('Draw')

    def __init__(self, email, firstname, lastname, phone, password, pw_salt, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.pw_salt = pw_salt
        self.role = role
        self.key = Fernet.generate_key()


class Draw(db.Model):
    __tablename__ = 'draws'

    id = db.Column(db.Integer, primary_key=True)

    # ID of user who submitted draw
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # 6 draw numbers submitted
    numbers = db.Column(db.String(100), nullable=False)

    # Draw has already been played (can only play draw once)
    been_played = db.Column(db.BOOLEAN, nullable=False, default=False)

    # Draw matches with master draw created by admin (True = draw is a winner)
    matches_master = db.Column(db.BOOLEAN, nullable=False, default=False)

    # True = draw is master draw created by admin. User draws are matched to master draw
    master_draw = db.Column(db.BOOLEAN, nullable=False)

    # Lottery round that draw is used
    lottery_round = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, numbers, master_draw, lottery_round):
        self.user_id = user_id
        self.numbers = encrypt(numbers, User.query.filter_by(id=user_id).first().key)
        self.been_played = False
        self.matches_master = False
        self.master_draw = master_draw
        self.lottery_round = lottery_round


def encrypt(data, key):
    return Fernet(key).encrypt(bytes(data, 'utf-8'))


def decrypt(data, key):
    return Fernet(key).decrypt(data).decode('utf-8')

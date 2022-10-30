# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for
import re
import bcrypt
from cryptography.fernet import Fernet

from app import db
from models import User
from users.forms import RegisterForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        email = form.email.data
        fname = form.firstname.data
        lname = form.lastname.data
        phone = form.phone.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()
        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # regex for matching inputs
        email_match = re.fullmatch('([A-Za-z\d]+[\-_+.]*)*[A-Za-z\d]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email)
        fname_match = re.fullmatch('([A-Za-z])+', fname)
        lname_match = re.fullmatch('([A-Za-z])+', lname)
        phone_match = re.fullmatch('([0-9]{4}-[0-9]{3}-[0-9]{4})', phone)
        password_match = re.fullmatch('(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^a-zA-Z0-9])[\s\S]{6,12}', password)

        # check all inputs are filled
        if len(email) == 0:
            flash('Email not entered!')
            return render_template('users/register.html', form=form)
        elif len(fname) == 0:
            flash('First name not entered!')
            return render_template('users/register.html', form=form)
        elif len(lname) == 0:
            flash('Last name not entered!')
            return render_template('users/register.html', form=form)
        elif len(phone) == 0:
            flash('Phone number not entered!')
            return render_template('users/register.html', form=form)
        elif len(password) == 0:
            flash('Password not entered!')
            return render_template('users/register.html', form=form)

        # check passwords match
        elif password != confirm_password:
            flash('Passwords do not match!')
            return render_template('users/register.html', form=form)

        # check inputs are valid using regex expressions
        elif email_match is None:
            flash('Email address is invalid!')
            return render_template('users/register.html', form=form)
        elif fname_match is None:
            flash('First name is invalid!')
            return render_template('users/register.html', form=form)
        elif lname_match is None:
            flash('Last name is invalid!')
            return render_template('users/register.html', form=form)
        elif phone_match is None:
            flash('Phone number is invalid!')
            return render_template('users/register.html', form=form)
        elif password_match is None:
            flash('Password is invalid!')
            return render_template('users/register.html', form=form)

        else:
            # hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('UTF-8'), salt)
            # create a new user with the form data
            new_user = User(email=email, firstname=fname, lastname=lname,
                            phone=phone, password=hashed_password, pw_salt=salt, role='user')

            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()

            # sends user to login page
            return redirect(url_for('users.login'))

    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


# view user login
@users_blueprint.route('/login')
def login():
    return render_template('users/login.html')


# view user profile
@users_blueprint.route('/profile')
def profile():
    return render_template('users/profile.html', name="PLACEHOLDER FOR FIRSTNAME")


# view user account
@users_blueprint.route('/account')
def account():
    return render_template('users/account.html',
                           acc_no="PLACEHOLDER FOR USER ID", email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME", lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")

# IMPORTS
import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from flask_login import login_user
import re
import bcrypt
from markupsafe import Markup
from flask_login import logout_user, current_user
from datetime import datetime

from app import db, logger
from models import User
from users.forms import RegisterForm, LoginForm

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

            logger.warning("SECURITY - User Registration [%s, %s]", form.email.data, request.remote_addr)

            # sends user to login page
            return redirect(url_for('users.login'))

    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get("login_attempts"):
        session["login_attempts"] = 0

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        salt = user.pw_salt
        hashed_password = bcrypt.hashpw(password.encode('UTF-8'), salt)
        pin = pyotp.TOTP(user.pin_key)

        if not user or hashed_password != user.password or not pin.verify(form.pin.data):
            logger.warning("SECURITY - Invalid login attempt [%s, %s]", form.email.data, request.remote_addr)

            session["login_attempts"] += 1
            if session.get("login_attempts") >= 3:
                flash(Markup('Number of incorrect login attempts exceeded. Please click <a href="/reset">here</a> to '
                             'reset.'))
                return render_template('users/login.html')
            else:
                flash(f"Some information you entered was incorrect! You have {3 - session.get('login_attempts')}"
                      f" attempts remaining.")
                return render_template('users/login.html', form=form)
        else:
            login_user(user)
            logger.warning("SECURITY - User Login [%s, %s, %s]", user.id, user.email, request.remote_addr)

            user.last_login = user.current_login
            user.current_login = datetime.now()
            db.session.add(user)
            db.session.commit()

            if user.role == "user":
                return redirect(url_for("users.profile"))
            else:
                return redirect(url_for("admin.admin"))

    return render_template('users/login.html', form=form)


# view user profile
@users_blueprint.route('/profile')
def profile():
    if current_user.is_anonymous:
        logger.warning("SECURITY - Invalid access attempt [%s, %s] accessing /profile", "ANONYMOUS", request.remote_addr)
        return redirect(url_for("users.login"))

    user = User.query.filter_by(id=current_user.id).first()
    return render_template('users/profile.html', name=user.firstname)


# view user account
@users_blueprint.route('/account')
def account():
    if current_user.is_anonymous:
        logger.warning("SECURITY - Invalid access attempt [%s, %s] accessing /account", "ANONYMOUS", request.remote_addr)
        return redirect(url_for("users.login"))

    user = User.query.filter_by(id=current_user.id).first()
    return render_template('users/account.html',
                           acc_no=user.id, email=user.email,
                           firstname=user.firstname, lastname=user.lastname,
                           phone=user.phone)


# reset login attempts
@users_blueprint.route('/reset')
def reset():
    session["login_attempts"] = 0
    return redirect(url_for('users.login'))


# logout
@users_blueprint.route('/logout')
def logout():
    if current_user.is_anonymous:
        logger.warning("SECURITY - Invalid access attempt [%s, %s] accessing /logout", "ANONYMOUS", request.remote_addr)
        return redirect(url_for('index'))

    logger.warning("SECURITY - User Logout [%s, %s, %s]", current_user.id, current_user.email, request.remote_addr)

    logout_user()

    return redirect(url_for('index'))

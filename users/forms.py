from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField


class RegisterForm(FlaskForm):
    email = StringField()
    firstname = StringField()
    lastname = StringField()
    phone = StringField()
    password = PasswordField()
    confirm_password = PasswordField()
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = StringField()
    password = PasswordField()
    pin = StringField()
    recaptcha = RecaptchaField()
    submit = SubmitField()

# IMPORTS
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_talisman import Talisman
from logs import SecurityFilter
import bcrypt
import logging


logger = logging.getLogger()
file_handler = logging.FileHandler("lottery.log", "a")
file_handler.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf41H4iAAAAALCDw0esznqOX1-uxAKABhCYQ51_'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf41H4iAAAAALw_t1vVYYcr9fUvBkqR7yjZqCwN'

# initialise database
db = SQLAlchemy(app)


csp = {
    'default-src': ['\'self\'', 'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css'],
    'frame-src': ['\'self\'', 'https://www.google.com/recaptcha/', 'https://recaptcha.google.com/recaptcha/'],
    'script-src': ['\'self\'', '\'unsafe-inline\'', 'https://www.google.com/recaptcha/', 'https://www.gstatic.com/recaptcha/']
}
talisman = Talisman(app, content_security_policy=csp)


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('main/index.html')


# BLUEPRINTS
# import blueprints
from users.views import users_blueprint
from admin.views import admin_blueprint
from lottery.views import lottery_blueprint

#
# # register blueprints with app
app.register_blueprint(users_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(lottery_blueprint)

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    from models import User
    return User.query.get(int(id))


# error handlers
@app.errorhandler(400)
def bad_request(error):
    print(error)
    return render_template('400.html'), 400


@app.errorhandler(403)
def forbidden(error):
    print(error)
    return render_template('403.html'), 403


@app.errorhandler(404)
def not_found(error):
    print(error)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    print(error)
    return render_template('500.html'), 500


@app.errorhandler(503)
def service_unavailable(error):
    print(error)
    return render_template('503.html'), 503


if __name__ == "__main__":
    app.run()


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        from models import User
        admin = User(email='admin@email.com',
                     password='Admin1!',
                     pw_salt=bcrypt.gensalt(),
                     firstname='Alice',
                     lastname='Jones',
                     phone='0191-123-4567',
                     role='admin')

        db.session.add(admin)
        db.session.commit()

# test pin key: DFDFQZUR4C5JT2U4EJ2N4KCQ7QCJIRQI

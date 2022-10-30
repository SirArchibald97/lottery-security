# IMPORTS
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import bcrypt

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialise database
db = SQLAlchemy(app)


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


# error handlers
@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400


@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.errorhandler(503)
def service_unavailable(error):
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

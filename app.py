from os import path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config

app = Flask(__name__) # Creates Flask app
app.config.from_object(Config) # Loads config.py
app.jinja_env.filters['zip'] = zip # Allows zip() to be used in Jinja templates

db = SQLAlchemy(app) # Creates SQLAlchemy object
login_manager = LoginManager(app) # Creates LoginManager object
login_manager.login_view = 'login' # Sets the login route

from views import *
from models import *
from mock_data import insert_mock_data
if not path.exists('webalance.db'):
    with app.app_context():
        db.create_all()
        insert_mock_data(db)
else:
    with app.app_context():
        db.create_all()

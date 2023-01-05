import os
from secrets import token_hex

BASE_DIR = os.path.dirname(os.path.abspath(__name__)) # Gets the current directory

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'webalance.db') # Sets the database path
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disables a feature that we don't need
    SECRET_KEY = token_hex() # Generates a random secret key for the app
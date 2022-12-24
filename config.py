import os
from secrets import token_hex

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'webalance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = token_hex()
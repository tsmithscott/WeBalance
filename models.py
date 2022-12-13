from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Companies(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    addressLine1 = db.Column(db.String(50))
    addressLine2 = db.Column(db.String(50))
    postcode = db.Column(db.String(50))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))


    def __init__(self, name, addressLine1, addressLine2,
                 postcode, city, country):
        self.name = name
        self.addressLine1 = addressLine1
        self.addressLine2 = addressLine2
        self.postcode = postcode
        self.city = city
        self.country = country


class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    firstname = db.Column(db.String(50))
    surname = db.Column(db.String(50))


    def __init__(self, email, password, firstname, surname):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.surname = surname


class Preferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    max = db.Column(db.Float, nullable=False)
    
    def __init__(self, task, user_id, max):
        self.user_id = user_id
        self.task = task
        self.max = max


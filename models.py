from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(50))


    def __init__(self, name, surname, email):
        self.name = name
        self.surname = surname
        self.email = email


class Company(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(50))


    def __init__(self, name, surname, email):
        self.name = name
        self.surname = surname
        self.email = email


class Preferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    max = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id
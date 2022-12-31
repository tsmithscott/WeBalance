from flask_login import UserMixin

from app import db


class Companies(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)
    address_line_1 = db.Column(db.String(50), nullable=False)
    address_line_2 = db.Column(db.String(50))
    postcode = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)

    def __init__(self, name, address_line_1, postcode, city, country):
        self.name = name
        self.address_line_1 = address_line_1
        self.postcode = postcode
        self.city = city
        self.country = country
    
    def __repr__(self) -> str:
        return f"Company('{self.name}', '{self.address_line_1}', '{self.address_line_2}', '{self.postcode}', '{self.city}', '{self.country}')"


class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id'), nullable=False)
    records = db.relationship('Records', backref='employees', lazy=True)
    
    def __init__(self, user_id, employer_id):
        self.user_id = user_id
        self.employer_id = employer_id


class Employers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    employees = db.relationship('Employees', backref='employers', lazy=True)
    
    def __init__(self, user_id, company_id):
        self.user_id = user_id
        self.company_id = company_id


class Preferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    max_hours_weekly = db.Column(db.Float, nullable=False)
    max_emails_daily = db.Column(db.Integer, nullable=False)
    max_calls_daily = db.Column(db.Integer, nullable=False)
    
    def __init__(self, user_id, max_hours_weekly, max_emails_daily, max_calls_daily):
        self.user_id = user_id
        self.max_hours_weekly = max_hours_weekly
        self.max_emails_daily = max_emails_daily
        self.max_calls_daily = max_calls_daily


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    is_employer = db.Column(db.Boolean, nullable=False)

    def __init__(self, email, password, firstname, surname, is_employer):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.surname = surname
        self.is_employer = is_employer


class Records(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    emails_sent = db.Column(db.Integer, nullable=False)
    calls_made = db.Column(db.Integer, nullable=False)
    
    def __init__(self, employee_id, start_time, end_time, emails_sent, calls_made):
        self.employee_id = employee_id
        self.start_time = start_time
        self.end_time = end_time
        self.emails_sent = emails_sent
        self.calls_made = calls_made
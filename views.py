from app import app, db, login_manager
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from models import Companies, Employees, Employers, Preferences, Records, Users
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route("/")
def index():
    # If user is logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if user exists
        user = Users.query.filter_by(email=request.form['email']).first()
        
        # If user exists, check password
        if user:
            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template("login.html", title="Login")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if Users.query.filter_by(email=request.form['email']).first() is None:
            if request.form['password'] != request.form['confirm_password']:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('signup'))
            else:
                if request.form.get('employer_check'):
                    is_employer = 1
                else:
                    is_employer = 0
                
                new_user = Users(email=request.form['email'],
                            password=generate_password_hash(request.form['password'], method='sha256'),
                            firstname=request.form['firstname'],
                            surname=request.form['surname'],
                            is_employer=is_employer)
                
                try:
                    db.session.add(new_user)
                    db.session.add
                    db.session.commit()
                    new_user_preferences = Preferences(new_user.id, max_hours_weekly=32, max_emails_daily=25, max_calls_daily=10)
                    db.session.add(new_user_preferences)
                    db.session.commit()
                    
                    company = request.form['company']
                    employer = Employers.query.filter_by(company_id=company).one()
                    if is_employer == 1:
                        new_employer = Employers(user_id=new_user.id, company_id=company)
                        db.session.add(new_employer)
                        db.session.commit()
                    elif is_employer == 0:
                        new_employee = Employees(user_id=new_user.id, employer_id=employer.id)
                        db.session.add(new_employee)
                        db.session.commit()
                        
                    flash('Account created! Please login.', 'success')
                    return redirect(url_for('login'))
                except:
                    flash('There was an issue creating your account!', 'error')
                    return redirect(url_for('signup'))
    return render_template("signup.html", title="Create an Account", companies=Companies.query.all())


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated:
        return render_template("dashboard.html", title="Dashboard")
    else:
        return redirect(url_for("login"))


@app.route("/preferences", methods=['GET', 'POST'])
@login_required
def preferences():
    preferences = Preferences.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        preferences.max_hours_weekly = request.form['weekly_hours']
        preferences.max_emails_daily = request.form['daily_emails']
        preferences.max_calls_daily = request.form['daily_calls']
        try:
            db.session.commit()
            flash('Preferences updated!', 'success')
            return redirect(url_for('preferences'))
        except:
            flash('There was an issue updating your preferences!', 'error')
        return redirect(url_for('preferences'))
    
    else:
        # Fetch user preferences from the database
        preferences = Preferences.query.filter_by(user_id=current_user.id).first()
        # Fetch user's employer default preferences from the database
        if not current_user.is_employer:
            employer_user_id = Employees.query.filter_by(user_id=current_user.id).first().employer_id
            employer_default = Preferences.query.filter_by(user_id=employer_user_id).first()
        else:
            employer_default=preferences
        return render_template('preferences.html', preferences=preferences, employer_default=employer_default, title="Preferences")


@app.route("/records")
@login_required
def records():
    if not current_user.is_employer:
        return render_template("records.html", title="Records")
    else:
        flash("You must be an employee to add records!", "error")
        return redirect(url_for("dashboard"))


@app.route("/about")
def about():
    # Populate index.html with info/animations/pictures
    return render_template("index.html", title="About Us")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
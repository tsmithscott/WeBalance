from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc

from app import app, db, login_manager
from models import Companies, Employees, Employers, Preferences, Records, Users


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


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
                    db.session.commit()
                    company = request.form['company']
                    if company != 'none':
                        employer = Employers.query.filter_by(company_id=company).first()
                        employer_default_preferences = Preferences.query.filter_by(user_id=employer.user_id).first()
                        if is_employer == 1:
                            new_employer = Employers(user_id=new_user.id, 
                                                    company_id=company)
                            db.session.add(new_employer)
                            db.session.commit()
                            # Create default preferences for new employer
                            new_user_preferences = Preferences(user_id=new_user.id, 
                                                            max_hours_weekly=32, 
                                                            max_emails_daily=25, 
                                                            max_calls_daily=10)
                            db.session.add(new_user_preferences)
                            db.session.commit()
                        elif is_employer == 0:
                            new_employee = Employees(user_id=new_user.id, 
                                                    employer_id=employer.id)
                            db.session.add(new_employee)
                            db.session.commit()
                            # Create default preferences for new employee based on employer's preferences
                            new_user_preferences = Preferences(user_id=new_user.id, 
                                                            max_hours_weekly=employer_default_preferences.max_hours_weekly, 
                                                            max_emails_daily=employer_default_preferences.max_emails_daily, 
                                                            max_calls_daily=employer_default_preferences.max_calls_daily)
                            db.session.add(new_user_preferences)
                            db.session.commit()
                    else:
                        raise Exception()
                        
                    flash('Account created! Please login.', 'success')
                    return redirect(url_for('login'))
                except:
                    flash('There was an issue creating your account! Please make sure you fill all fields.', 'error')
                    return redirect(url_for('signup'))
    return render_template("signup.html", title="Create an Account", companies=Companies.query.all())


@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    # If user is an employee, fetch all records for that user
    if not current_user.is_employer:
        employee_id = Employees.query.filter_by(user_id=current_user.id).first().id
        records = Records.query.filter(Records.employee_id==employee_id)
        
    # If user is an employer, fetch all records for their employees
    else:
        employer_id = Employers.query.filter_by(user_id=current_user.id).first().id
        employee_ids = []
        for employee in Employees.query.filter_by(employer_id=employer_id).all():
            employee_ids.append(employee.id)
            
        for employee_id in employee_ids:
            records = Records.query.filter(Records.employee_id.in_(employee_ids))
        
    records = records.order_by(desc(Records.start_time)).all()
    hours = []
    for record in records:
        # Calculate total hours worked and add to a list
        hours.append(round(timedelta.total_seconds(record.end_time - record.start_time) / 3600, 1)) 
            
    return render_template("dashboard.html", title="Dashboard", hours=hours, records=records)


@app.route("/preferences", methods=['GET', 'POST'])
@login_required
def preferences():
    # Fetch user's preferences from the database
    preferences = Preferences.query.filter_by(user_id=current_user.id).one()
    
    # If data is entered, update preferences
    if request.method == 'POST':
        hours = request.form['weekly_hours']
        emails = request.form['daily_emails']
        calls = request.form['daily_calls']
        if hours != "0":
            preferences.max_hours_weekly = hours
        if emails != "0":
            preferences.max_emails_daily = emails
        if calls != "0":
            preferences.max_calls_daily = calls

        try:
            db.session.commit()
            flash('Preferences updated!', 'success')
            return redirect(url_for('preferences'))
        except:
            flash('There was an issue updating your preferences!', 'error')
        return redirect(url_for('preferences'))
    
    # If no data is entered, display preferences
    else:
        # If user is an employee, set employer_default to employer's preferences
        if not current_user.is_employer:
            employer_id = Employees.query.filter_by(user_id=current_user.id).one().employer_id
            employer_user_id = Employers.query.filter_by(user_id=employer_id).one().user_id
            employer_default = Preferences.query.filter_by(user_id=employer_user_id).one()
            
        # If user is an employer, set employer_default to user's preferences
        else:
            employer_default=preferences
        return render_template('preferences.html', preferences=preferences, employer_default=employer_default, title="Preferences")


@app.route("/records", methods=['GET', 'POST'])
@login_required
def records():
    if not current_user.is_employer:
        if request.method == 'POST':
            date = dt.strptime(request.form['date'], '%Y-%m-%d').date()
            inputted_start_time = dt.strptime(request.form['start-time'], '%H:%M')
            inputted_end_time = dt.strptime(request.form['end-time'], '%H:%M')
            
            start_time = dt.combine(date, inputted_start_time.time(), tzinfo=timezone.utc)
            end_time = dt.combine(date, inputted_end_time.time(), tzinfo=timezone.utc)
            calls = request.form['calls']
            emails = request.form['emails']
            employee_id = Employees.query.filter_by(user_id=current_user.id).one().id
            
            new_record = Records(employee_id=employee_id, 
                                 start_time=start_time, 
                                 end_time=end_time, 
                                 emails_sent=emails, 
                                 calls_made=calls)
            try:
                db.session.add(new_record)
                db.session.commit()
                flash('Record added! View it on the dashboard.', 'success')
                return redirect(url_for('records'))
            except:
                flash('There was an issue adding the record!', 'error')
        return render_template("records.html", title="Records")
    else:
        flash("You must be an employee to add records!", "error")
        return redirect(url_for("dashboard"))


@app.route("/about")
def about():
    # Populate index.html with info/animations/pictures
    return render_template("index.html", title="About Us")

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        if request.form.get('deletion_check'):
            # Delete user from database and all associated data
            if current_user.is_employer:
                employer_id = Employers.query.filter_by(user_id=current_user.id).first().id
                Employees.query.filter_by(employer_id=employer_id).update(dict(employer_id=-1))
                Employers.query.filter_by(user_id=current_user.id).delete()
            else:
                user_employee_id = Employees.query.filter_by(user_id=current_user.id).first().id
                Records.query.filter_by(employee_id=user_employee_id).delete()
                Employees.query.filter_by(user_id=current_user.id).delete()
            Preferences.query.filter_by(user_id=current_user.id).delete()
            Users.query.filter_by(id=current_user.id).delete()
            db.session.commit()
        else:
            flash("You must confirm to delete your account & data!", "error")
            return redirect(url_for('account'))
        
        flash("Your account has been deleted!", "success")
        return redirect(url_for('logout'))
    return render_template("account.html", title="Account")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
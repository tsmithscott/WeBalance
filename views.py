import calendar
import json
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, extract, func

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
        # Check if user already exists
        if not Users.query.filter_by(email=request.form['email']).first():
            company = request.form['company']
            if request.form['password'] != request.form['confirm_password']:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('signup'))
            else:
                if company != 'none':
                    if request.form.get('employer_check'):
                        if Employers.query.filter_by(company_id=company).first():
                            flash('Company already has an employer!', 'error')
                            return redirect(url_for('signup'))
                        is_employer = 1
                    else:
                        if not Employers.query.filter_by(company_id=company).first():
                            flash('Company does not have an employer! Your employer must register first.', 'error')
                            return redirect(url_for('signup'))
                        is_employer = 0
                else:
                    flash("You must select a company!", 'error')
                    return redirect(url_for('signup'))
                
                new_user = Users(email=request.form['email'],
                            password=generate_password_hash(request.form['password'], method='sha256'),
                            firstname=request.form['firstname'],
                            surname=request.form['surname'],
                            is_employer=is_employer)
                
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    if is_employer == 1:
                        # Create new employer
                        new_employer = Employers(user_id=new_user.id, 
                                                company_id=company)
                        db.session.add(new_employer)

                        # Create default preferences for new employer
                        new_user_preferences = Preferences(user_id=new_user.id, 
                                                        max_hours_weekly=32, 
                                                        max_emails_daily=25, 
                                                        max_calls_daily=10)
                        db.session.add(new_user_preferences)
                        db.session.commit()
                    elif is_employer == 0:
                        employer = Employers.query.filter_by(company_id=company).first()
                        employer_default_preferences = Preferences.query.filter_by(user_id=employer.user_id).first()
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
                        
                    flash('Account created! Please login.', 'success')
                    return redirect(url_for('login'))
                except:
                    flash('There was an issue creating your account! Please make sure you fill all fields.', 'error')
                    return redirect(url_for('signup'))
        else:
            flash('Email already exists!', 'error')
            return redirect(url_for('signup'))
    return render_template("signup.html", title="Create an Account", companies=Companies.query.all())


@app.route("/company", methods=['GET', 'POST'])
def company():
    if request.method == 'POST':
        # Check if company already exists
        if not Companies.query.filter_by(name=request.form['name']).first():
            # Create new company
            new_company = Companies(name=request.form['name'],
                                    address_line_1=request.form['address_line_1'],
                                    postcode=request.form['postcode'],
                                    city=request.form['city'],
                                    country=request.form['country'])
            
            # Check if address line 2 is empty
            address_line_2 = request.form['address_line_2']
            if address_line_2:
                new_company.address_line_2 = address_line_2
            else:
                new_company.address_line_2 = None
            try:
                # Add new company to database
                db.session.add(new_company)
                db.session.commit()
                flash('Company created! Please create an employer account.', 'success')
                return redirect(url_for('signup'))
            except:
                flash('There was an issue creating your company!', 'error')
                return redirect(url_for('company'))
        else:
            flash('Company already exists!', 'error')
            return redirect(url_for('company'))
    return render_template("company.html", title="Register Company")


@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    seven_days_ago = dt.now().date() - timedelta(days=7)
    seven_days_ago = dt.combine(seven_days_ago, dt.min.time())
    thirty_days_ago = dt.now().date() - timedelta(days=30)
    thirty_days_ago = dt.combine(seven_days_ago, dt.min.time())
    
    # If user is an employee, fetch all records for that user
    if not current_user.is_employer:
        employee_id = Employees.query.filter_by(user_id=current_user.id).first().id
        all_time_records = (Records.query
                   .filter(Records.employee_id==employee_id)
                   .order_by(desc(Records.start_time))
                   .all()
                   )
        seven_day_records = (Records.query
                             .filter(Records.employee_id==employee_id)
                             .filter(Records.start_time >= seven_days_ago)
                             .order_by(desc(Records.start_time))
                             .all()
                             )
        thirty_day_records = (Records.query
                             .filter(Records.employee_id==employee_id)
                             .filter(Records.start_time >= thirty_days_ago)
                             .order_by(desc(Records.start_time))
                             .all()
                             )
        company = Companies.query.filter_by(id=Employers.query.filter_by(id=Employees.query.filter_by(user_id=current_user.id).first().employer_id).first().company_id).first()
        
    # If user is an employer, fetch all records for their employees
    else:
        # Get all employees for current employer
        employees = Employees.query.filter_by(employer_id=Employers.query.filter_by(user_id=current_user.id).first().id).all()
        employee_ids = []
        for employee in employees:
            employee_ids.append(employee.id)
        
        # Get records for all employees 
        all_time_records = (Records.query
                   .filter(Records.employee_id.in_(employee_ids))
                   .order_by(desc(Records.start_time))
                   .all()
                   )
        seven_day_records = (Records.query
                             .filter(Records.employee_id.in_(employee_ids))
                             .filter(Records.start_time >= seven_days_ago)
                             .order_by(desc(Records.start_time))
                             .all()
                             )
        thirty_day_records = (Records.query
                              .filter(Records.employee_id.in_(employee_ids))
                              .filter(Records.start_time >= thirty_days_ago)
                              .order_by(desc(Records.start_time))
                              .all()
                             )
        company = Companies.query.filter_by(id=Employers.query.filter_by(user_id=current_user.id).first().company_id).first()

    # Add hours to a list
    hours = []
    for record in all_time_records:
        hours.append(round(timedelta.total_seconds(record.end_time - record.start_time) / 3600, 1))

    # Add hours, emails and calls over different timeframes for data analysis
    all_time = []
    week = []
    month = []
    def add_records(records, data):
        for record in records:
            data.append({
                'hours': round(timedelta.total_seconds(record.end_time - record.start_time) / 3600, 1),
                'emails': record.emails_sent,
                'calls': record.calls_made
            })
    add_records(all_time_records, all_time)
    add_records(seven_day_records, week)
    add_records(thirty_day_records, month)
    
    # Calculate totals of hours, emails and calls over different timeframes
    def calculate_totals(records, keys):
        totals = {key: sum(record[key] for record in records) for key in keys}
        return totals
    totals = {
        'all_time': calculate_totals(all_time, ['hours', 'emails', 'calls']),
        'week': calculate_totals(week, ['hours', 'emails', 'calls']),
        'month': calculate_totals(month, ['hours', 'emails', 'calls'])
    }

    # Calculate averages of hours, emails and calls over different timeframes
    def calculate_averages(records, keys):
        def calculate_average(records, key):
            return round(sum(record[key] for record in records) / len(records), 2)
        averages = {key: calculate_average(records, key) for key in keys}
        return averages
    # Add averages to a dictionary
    averages = {
        'all_time': {'hours': 0, 'emails': 0, 'calls': 0},
        'week': {'hours': 0, 'emails': 0, 'calls': 0},
        'month': {'hours': 0, 'emails': 0, 'calls': 0}
    }
    if len(all_time) > 0:
        averages['all_time'] = calculate_averages(all_time, ['hours', 'emails', 'calls'])
    if len(week) > 0:
        averages['week'] = calculate_averages(week, ['hours', 'emails', 'calls'])
    if len(month) > 0:
        averages['month'] = calculate_averages(month, ['hours', 'emails', 'calls'])
        
    # Get the current time
    current_time = dt.now()

    # Calculate the start time for each week
    week1_start = current_time - timedelta(days=7)
    week2_start = current_time - timedelta(days=14)
    week3_start = current_time - timedelta(days=21)
    week4_start = current_time - timedelta(days=28)

    week1_records = [0, 0, 0]
    week2_records = [0, 0, 0]
    week3_records = [0, 0, 0]
    week4_records = [0, 0, 0]
    # If user is an employee, fetch all records for them
    if not current_user.is_employer:
        employee_id = Employees.query.filter_by(user_id=current_user.id).first().id
        # Query the records for each week
        week1_records = (
            db.session.query(
                func.avg(Records.emails_sent),
                func.avg(Records.calls_made),
                func.avg(
                    (
                        extract("epoch", Records.end_time) - extract("epoch", Records.start_time)
                    ) / 3600
                )
            )
            .filter(Records.employee_id == employee_id)
            .filter(Records.start_time.between(week1_start, current_time))
            .all()
        )
        week2_records = (
            db.session.query(
                func.avg(Records.emails_sent),
                func.avg(Records.calls_made),
                func.avg(
                    (
                        extract("epoch", Records.end_time) - extract("epoch", Records.start_time)
                    ) / 3600
                )
            )
            .filter(Records.employee_id == employee_id)
            .filter(Records.start_time.between(week2_start, week1_start))
            .all()
        )
        week3_records = (
            db.session.query(
                func.avg(Records.emails_sent),
                func.avg(Records.calls_made),
                func.avg(
                    (
                        extract("epoch", Records.end_time) - extract("epoch", Records.start_time)
                    ) / 3600
                )
            )
            .filter(Records.employee_id == employee_id)
            .filter(Records.start_time.between(week3_start, week2_start))
            .all()
        )
        week4_records = (
            db.session.query(
                func.avg(Records.emails_sent),
                func.avg(Records.calls_made),
                func.avg(
                    (
                        extract("epoch", Records.end_time) - extract("epoch", Records.start_time)
                    ) / 3600
                )
            )
            .filter(Records.employee_id == employee_id)
            .filter(Records.start_time.between(week4_start, week3_start))
            .all()
        )
    else:
        employee_ids = []
        for employee in Employees.query.filter_by(employer_id=Employers.query.filter_by(user_id=current_user.id).first().id).all():
            employee_ids.append(employee.id)
        # Query the records for each week
        week1_records = (
            db.session.query(
                func.avg(Records.emails_sent),
                func.avg(Records.calls_made),
                func.avg(
                    (
                        extract("epoch", Records.end_time) - extract("epoch", Records.start_time)
                    ) / 3600
                )
            )
            .filter(Records.employee_id.in_(employee_ids))
            .filter(Records.start_time.between(week1_start, current_time))
            .all()
        )
        week2_records = (
            db.session.query(
                func.avg(Records.emails_sent),
                func.avg(Records.calls_made),
                func.avg(
                    (
                        extract("epoch", Records.end_time) - extract("epoch", Records.start_time)
                    ) / 3600
                )
            )
            .filter(Records.employee_id.in_(employee_ids))
            .filter(Records.start_time.between(week2_start, week1_start))
            .all()
        )
        week3_records = (
            db.session.query(
                func.avg(Records.emails_sent),
                func.avg(Records.calls_made),
                func.avg(
                    (
                        extract("epoch", Records.end_time) - extract("epoch", Records.start_time)
                    ) / 3600
                )
            )
            .filter(Records.employee_id.in_(employee_ids))
            .filter(Records.start_time.between(week3_start, week2_start))
            .all()
        )
        week4_records = (
            db.session.query(
                func.avg(Records.emails_sent),
                func.avg(Records.calls_made),
                func.avg(
                    (
                        extract("epoch", Records.end_time) - extract("epoch", Records.start_time)
                    ) / 3600
                )
            )
            .filter(Records.employee_id.in_(employee_ids))
            .filter(Records.start_time.between(week4_start, week3_start))
            .all()
        )

    try:
        # Calculate the averages for each week
        week1_averages = [    sum(record[0] for record in week1_records) / len(week1_records),
            sum(record[1] for record in week1_records) / len(week1_records),
            sum(record[2] for record in week1_records) / len(week1_records),
        ]
        week2_averages = [    sum(record[0] for record in week2_records) / len(week2_records),
            sum(record[1] for record in week2_records) / len(week2_records),
            sum(record[2] for record in week2_records) / len(week2_records),
        ]
        week3_averages = [    sum(record[0] for record in week3_records) / len(week3_records),
            sum(record[1] for record in week3_records) / len(week3_records),
            sum(record[2] for record in week3_records) / len(week3_records),
        ]
        week4_averages = [    sum(record[0] for record in week4_records) / len(week4_records),
            sum(record[1] for record in week4_records) / len(week4_records),
            sum(record[2] for record in week4_records) / len(week4_records),
        ]
    except TypeError:
        week1_averages = [0, 0, 0]
        week2_averages = [0, 0, 0]
        week3_averages = [0, 0, 0]
        week4_averages = [0, 0, 0]
    
    graph_averages = {'week1': week1_averages, 'week2': week2_averages, 'week3': week3_averages, 'week4': week4_averages}
    
    if not current_user.is_employer:
        return render_template("dashboard.html", title="Dashboard", hours=hours, records=all_time_records,
                               company=company, averages=averages, totals=totals, graph_averages=json.dumps(graph_averages))
    else:
        return render_template("dashboard.html", title="Dashboard", hours=hours, records=all_time_records,
                               company=company, averages=averages, totals=totals, employees=employees, graph_averages=json.dumps(graph_averages))


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
            employer_user_id = Employers.query.filter_by(id=employer_id).one().user_id
            employer_default = Preferences.query.filter_by(user_id=employer_user_id).one()
            
        # If user is an employer, set employer_default to user's preferences
        else:
            employer_default = preferences
        return render_template('preferences.html', preferences=preferences, employer_default=employer_default, title="Preferences")


@app.route("/records", methods=['GET', 'POST'])
@login_required
def records():
    if not current_user.is_employer:
        if request.method == 'POST':
            inputted_start_time = dt.strptime(request.form['start-time'], '%H:%M')
            inputted_end_time = dt.strptime(request.form['end-time'], '%H:%M')
            
            # Convert date and time to datetime object
            date = dt.strptime(request.form['date'], '%Y-%m-%d').date()
            start_time = dt.combine(date, inputted_start_time.time(), tzinfo=timezone.utc)
            # If end time is before start time, add a day to the end time
            if inputted_end_time < inputted_start_time:
                date += timedelta(days=1)
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


@app.route("/reports", methods=['GET', 'POST'])
@login_required
def reports():
    if not current_user.is_employer:
        flash("You must be an employer to view reports!", "error")
        return redirect(url_for("dashboard"))
    else:
        # Get all employees for the current user
        employees = Employees.query.join(Employers).filter(Employers.user_id == current_user.id).all()

        # Create a dictionary to store the total hours for each employee
        total_hours = {}
        
        # Get the previous month and year
        if dt.now().month == 1:
            prev_month = 12
            prev_year = dt.now().year - 1
        else:
            prev_month = dt.now().month - 1
            prev_year = dt.now().year
            
        # Iterate over the employees
        for employee in employees:

            # Get all records for the employee from the previous month and year
            records = Records.query.filter(
                Records.employee_id == employee.id,
                extract('month', Records.start_time) == prev_month,
                extract('year', Records.start_time) == prev_year
            ).all()

            # Calculate the total hours for the employee in the previous month
            employee_total_hours = 0
            for record in records:
                duration = record.end_time - record.start_time
                if record.end_time.date() != record.start_time.date():
                    duration += timedelta(days=1) - (record.end_time.date() - record.start_time.date())
                # Add the total duration in hours to the employee's total hours
                employee_total_hours += duration.total_seconds() / 3600
            
            # Add the total hours to the dictionary, using the employee_id as the key
            total_hours[employee.id] = round(employee_total_hours, 1)
    
        # Get preferences of each employee
        preferences = {employee.id: Preferences.query.filter_by(user_id=employee.user_id).first() for employee in employees}
        
        tally = {'under_limit': 0, 'over_limit': 0, 'near_limit': 0}
        for employee in employees:
            if total_hours[employee.id] > (preferences[employee.id].max_hours_weekly)*4:
                tally['over_limit'] += 1
            else:
                if total_hours[employee.id] >= 0.75*((preferences[employee.id].max_hours_weekly)*4):
                    tally['near_limit'] += 1
                else:
                    tally['under_limit'] += 1

    return render_template("reports.html", title="Reports", employees=employees, hours=total_hours, preferences=preferences,
                           prev_month=calendar.month_name[prev_month], prev_year=prev_year, tally=json.dumps(tally))


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
                # Get all employees for current user
                employees_ids = [employee.id for employee in Employees.query.filter_by(employer_id=employer_id).all()]
                employees_user_ids = [employee.user_id for employee in Employees.query.filter_by(employer_id=employer_id).all()]
                # Delete all data associated with user's employees
                for user in employees_user_ids:
                    Preferences.query.filter_by(user_id=user).delete(synchronize_session=False)
                    Employees.query.filter_by(user_id=user).delete(synchronize_session=False)
                    Users.query.filter_by(id=user).delete(synchronize_session=False)
                
                for user in employees_ids:
                    Records.query.filter_by(employee_id=user).delete(synchronize_session=False)
                
                # Delete employer object for current user
                company_id = Employers.query.filter_by(user_id=current_user.id).first().company_id
                Employers.query.filter_by(user_id=current_user.id).delete(synchronize_session=False)
                Companies.query.filter_by(id=company_id).delete(synchronize_session=False)
            else:
                user_employee_id = Employees.query.filter_by(user_id=current_user.id).first().id
                Records.query.filter_by(employee_id=user_employee_id).delete(synchronize_session=False)
                Employees.query.filter_by(user_id=current_user.id).delete(synchronize_session=False)
            Preferences.query.filter_by(user_id=current_user.id).delete(synchronize_session=False)
            Users.query.filter_by(id=current_user.id).delete(synchronize_session=False)
            db.session.commit()
        else:
            flash("You must confirm to delete your account & data!", "error")
            return redirect(url_for('account'))
        
        flash("Your account has been deleted!", "success")
        return redirect(url_for('logout'))
    else:
        if current_user.is_employer:
            company = Companies.query.filter_by(id=Employers.query.filter_by(user_id=current_user.id).first().company_id).one()
            company_email = Users.query.filter_by(id=current_user.id).first().email
        else:
            company = Companies.query.filter_by(id=Employers.query.filter_by(id=Employees.query.filter_by(user_id=current_user.id).first().employer_id).first().company_id).first()
            company_email = Users.query.filter_by(id=Employers.query.filter_by(id=Employees.query.filter_by(user_id=current_user.id).first().employer_id).first().user_id).first().email
    return render_template("account.html", title="Account", company=company, company_email=company_email)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
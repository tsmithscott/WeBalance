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
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Users.query.filter_by(email=request.form['email']).first()
        if user:
            print(type(user.password))
            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                return redirect(url_for('dashboard'))
        return 'Invalid username or password'
    return render_template("login.html", title="Login")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if Users.query.filter_by(email=request.form['email']).first() is None:
            if request.form['password'] != request.form['confirm_password']:
                flash('Passwords do not match!', 'error')
                return 'Passwords do not match!'
            else:
                new_user = Users(email=request.form['email'],
                                password=generate_password_hash(request.form['password'], method='sha256'),
                                firstname=request.form['firstname'],
                                surname=request.form['surname'])
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    return redirect(url_for('login'))
                except:
                    return 'There was an issue adding your user!'
    return render_template("signup.html", title="Create an Account")


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
    if request.method == 'POST':
        new_task = request.form['hours_weekly']
        new_max = request.form['max']
        new_preference = Preferences(task = new_task, max = new_max)

        try:
            db.session.add(new_preference)
            db.session.commit()
            return redirect('#')
        except:
            return 'There was an issue adding your preference!'
    else:
        preferences = Preferences.query.filter_by(id=current_user.id).all()
        return render_template('preferences.html', preferences = preferences , title="Preferences")


@app.route("/about")
def about():
    # Populate index.html with info/animations/pictures
    return render_template("index.html", title="About Us")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
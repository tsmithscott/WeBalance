from flask import Flask, url_for, redirect, render_template, request

from models import db

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db.init_app(app)

from models import User, Company


@app.route("/")
def home():
    return redirect(url_for("about"))


@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html", title="Login")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    return render_template("signup.html", title="Create an Account")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", title="Dashboard")


@app.route("/preferences", methods=['GET', 'POST'])
def preferences():
    return render_template("preferences.html", title="Preferences")


@app.route("/about")
def about():
    # Populate index.html with info/animations/pictures
    return render_template("index.html", title="About Us")


@app.route("/logout")
def logout():
    # Clear session data
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

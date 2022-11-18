from flask import Flask, url_for, redirect, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return redirect(url_for("about"))


@app.route("/login")
def login():
    return render_template("login.html", title="Login")


@app.route("/signup")
def signup():
    return render_template("signup.html", title="Create an Account")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", title="Dashboard")


@app.route("/preferences")
def preferences():
    return render_template("preferences.html", title="Preferences")


@app.route("/about")
def about():
    return render_template("index.html", title="About Us")


@app.route("/logout")
def logout():
    # Clear session data
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

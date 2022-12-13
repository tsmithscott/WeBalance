from flask import Flask, url_for, redirect, render_template, request

from models import db

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db.init_app(app)

from models import Users, Companies, Preferences

with app.app_context():
    db.create_all()


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
    if request.method == 'POST':
        new_task = request.form['task']
        new_max = request.form['max']
        new_preference = Preferences(task = new_task, max = new_max)

        try:
            db.session.add(new_preference)
            db.session.commit()
            return redirect('#')
        except:
            return 'There was an issue adding your preference!'
    else:
        preferences = Preferences.query.order_by(Preferences.task).all()
        return render_template('preferences.html', preferences = preferences , title="Preferences")


@app.route('/preferences/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    preference = Preferences.query.get_or_404(id)

    if request.method == 'POST':
        preference.task = request.form['task']
        preference.max = request.form['max']

        try:
            db.session.commit()
            return redirect(url_for("home"))
        except:
            return 'There was an issue updating the preference.'

    else:
        return render_template('preferences.html', preference = preference, title="Preferences")


@app.route("/about")
def about():
    # Populate index.html with info/animations/pictures
    return render_template("index.html", title="About Us")


@app.route("/logout")
def logout():
    # Clear session data
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)

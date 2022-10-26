from flask import Flask, url_for, redirect, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", title="Home Page")


@app.route("/signup")
def signup():
    return render_template("signup.html", title="Create an Account")


if __name__ == '__main__':
    app.run(debug=True)

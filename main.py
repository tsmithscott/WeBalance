from flask import Flask, url_for, redirect, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", title="Home Page")

if __name__ == '__main__':
    app.run(debug=True)
from flask.ext.mysqldb import MySQL
from flask import Flask, session, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import DB
app = Flask(__name__)
app.secret_key = "A secret I can never share :-)"
db = DB(app)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login_authenticate", methods=["GET", "POST"])
def login_authenticate():
    error = None
    if request.method == "POST":
        if request.form["username"] and request.form["password"]:
            username = request.form["username"].strip()
            password = request.form["password"].strip()
            # Get the matching user from database
            user = db.fetch_user(username)
            return str(user)
        else:
            flash("You must fill in all fields!")
            return redirect("/login")
    else:
        return "Akuna"





if __name__ == "__main__":
    app.run(debug=True)
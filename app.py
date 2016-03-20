from flask import Flask, session, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "A secret I can never share :-)"


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
            session["username"] = request.form["username"]
            return session["username"]
        else:
            flash("You must fill in all fields!")
            return render_template("login.html")
    else:
        return "Akuna"





if __name__ == "__main__":
    app.run(debug=True)
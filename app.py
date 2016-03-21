from flask import Flask, session, render_template, request, redirect, url_for, flash, json
from werkzeug.security import generate_password_hash, check_password_hash
from db import DB
app = Flask(__name__)
app.secret_key = "A secret I can never share :-)"
db = DB(app)

@app.route("/")
def index():
    """
    Redirects users to the home route which places them
    in their appropriate home pages defined for their user type
    :return:
    """
    return redirect("/home")


@app.route("/login")
def login():
    """
    Renders the login template
    :return:
    """
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login_authenticate", methods=["POST"])
def login_authenticate():
    """
    Validates user input submitted via login form and logs them in only if they have provided valid credentials
    :return:
    """

    if request.method == "POST":
        if request.get_json(force=True)["username"] and request.get_json(force=True)["password"]:
            username = request.get_json(force=True)["username"].strip()
            password = request.get_json(force=True)["password"].strip()
            # Get the matching user from database
            user = db.fetch_user(username)
            if len(user) == 1:
                if check_password_hash(user[0][8], password):
                    user = [detail for detail in user[0]]
                    session["idUsers"],session["UserTypes_idUserTypes"],session["FirstName"], session["LastName"] = user[0], user[1],user[3],user[4]
                    session["email"], session["Username"] = user[6], user[7]
                    print str(session)
                    return json.jsonify(session)

                else:
                    return json.jsonify(error="The password you entered is incorrect!")

            else:
                return json.jsonify(error="User not found. Invalid Details")
        else:
            return json.jsonify(error="You must fill in all fields!")
    else:
        return json.jsonify(error="There is a problem with your request. You are sending POST \
                                   instead of GET requests to this API.")

@app.route("/home")
def home():
    """
    redirects Users to their respective homepages defined for their kind of user type
    :return:
    """
    if session["UserTypes_idUserTypes"] == 1:
        return redirect("/home_admin")
    elif session["UserTypes_idUserTypes"] == 2:
        return redirect("/home_event_manager")
    else:
        return redirect("/home_alumni")

@app.route("/logout")
def logout():
    for data in session:
        session.pop(data)
    return redirect("/login")





if __name__ == "__main__":
    app.run(debug=True)
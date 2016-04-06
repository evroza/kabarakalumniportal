from flask import Flask, session, render_template, request, redirect, url_for, flash, json, Markup
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
            user = db.fetch_user(username=username)
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



@app.route("/register")
def register():
    """
    Renders the register template
    :return:
    """
    return render_template("register.html")


@app.route("/register_authenticate", methods=["GET", "POST"])
def register_authenticate():
    """
    Will be used to both check whether user or email exists;
    and also perform user registration
    :return:
    """
    if request.method == "GET":

        #Will hold a user if he exists
        user = dict()
        # Check whether typed email or username is available
        if request.args.get("username"):
            username = request.args.get("username")
            user["user"] = db.fetch_user(username=username)
        elif request.args.get("email"):
            email = request.args.get("email")
            user["user"] = db.fetch_user(email=email)
        elif request.args.get("nationalid"):
            nationalid = request.args.get("nationalid")
            user["user"] = db.fetch_user(nationalid=nationalid)
        else:
            print "there 5"
            return json.jsonify(error="Malformed request. Missing required parameters, username or password.")

        #Alert user if username/email/nationalID already exists in database
        if len(user["user"]) >= 1:
            return json.jsonify(user=user["user"][0], error="Input detail already exists in database!")
        else:
            return json.jsonify(success="User submission is unique. Proceed with registration!")
    elif request.method == "POST":
        if request.get_json(force=True)["Username"] and request.get_json(force=True)["Email"] and request.get_json(force=True)["FirstName"] and request.get_json(force=True)["LastName"] and request.get_json(force=True)["NationalID"]:
            user_data = request.get_json(force=True)
            # Escape the input
            for entry in user_data:
                user_data[entry] = Markup.escape(user_data[entry])
            insert_id = db.insert_user(user_data)
            print insert_id
            return json.jsonify(insert_id=insert_id, success="User was successfully created!", clear_data =True)



@app.route("/home")
def home():
    """
    redirects Users to their respective homepages defined for their kind of user type
    :return:
    """
    if "UserTypes_idUserTypes" in session:
        if session["UserTypes_idUserTypes"] == 1:
            return redirect("/home_admin")
        elif session["UserTypes_idUserTypes"] == 2:
            return redirect("/home_event_manager")
        elif session["UserTypes_idUserTypes"] == 3:
            return redirect("/home_alumni")
    else:
        flash("You must be logged in to perform that action!")
        return redirect("/login")


@app.route("/home_admin")
def home_admin():
    """
    Route for admin's home
    :return:
    """
    if "idUsers" in session and session["UserTypes_idUserTypes"] == 1:
        return render_template("home_admin.html")
    else:
        session.clear()
        return redirect("/login")


@app.route("/home_admin_data")
def home_admin_data():
    """
    Returns the data to populate on admin's home panel
    :return: json - The data
    """
    logged_in = is_logged_in()
    if logged_in and logged_in == 1:
        # User is logged in as admin
        discussions = db.get_discussions(limit=30)
        events = db.get_events(limit=7)

        data = events + discussions
        data_list = list(enumerate(data))
        print data
        return json.jsonify(data_list)






@app.route("/get_user_data")
def get_user_data():
    # Returns all the user's details stored in session
    user_data = {detail: session[detail] for detail in session if detail != "_flashes"}
    return json.jsonify(user_data)

@app.route("/get_last_verified_usernames")
def get_last_verified_usernames():
    # Returns all the user's details stored in session
    usernames = db.get_last_verified_usernames()
    return json.jsonify(usernames)

@app.route("/get_last_registered_usernames")
def get_last_registered_usernames():
    # Returns all the user's details stored in session
    usernames = db.get_last_registered_usernames()
    return json.jsonify(usernames)



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


def is_logged_in():
    """
    Checks whether the user is logged in and returns their user type id otherwise false
    :return:
    """
    if "idUsers" in session:
        return session["UserTypes_idUserTypes"]
    else:
        session.clear()
        return False





if __name__ == "__main__":
    app.run(debug=True)
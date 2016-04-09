from flask import Flask, session, render_template, request, redirect, url_for, flash, json, Markup
from werkzeug.security import generate_password_hash, check_password_hash
from db import DB
from flask.ext.mail import Mail, Message
app = Flask(__name__)
app.secret_key = "A secret I can never share :-)"
db = DB(app)
mail = Mail(app)
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=False,
	MAIL_USERNAME = 'evansrutoh@gmail.com',
	MAIL_PASSWORD = 'ribashongilogasheshiakili'
	)

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
                    session["email"], session["Username"], session["UserType"] = user[6], user[7], user[12]
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

@app.route("/home_alumni")
def home_alumni():
    """
    Route for alumni's home
    :return:
    """
    if "idUsers" in session and session["UserTypes_idUserTypes"] == 3:
        return redirect("/discussions")
    else:
        session.clear()
        return redirect("/login")

@app.route("/home_event_manager")
def home_event_manager():
    """
    Route for alumni's home
    :return:
    """
    if "idUsers" in session and session["UserTypes_idUserTypes"] == 2:
        return redirect("/events")
    else:
        session.clear()
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
        return json.jsonify(data_list)




@app.route("/users/<user_type>/")
def users(user_type):
    """
    Displays all registered users by default
    :param user_type: string - all: All Users; admin : Administrators; alumni: Alumni; event_manager: Event Manager;
    verified: Verified; pending: Pending
    :return: User list view
    """
    logged_in = is_logged_in()
    if not logged_in or logged_in != 1:
        return redirect("/logout")

    return render_template("admin_users_view.html")


@app.route("/get_users_data/<filter>/")
def get_users_data(filter):
    """
    Returns users in db based on submitted filter
    :param filter:
    :return:
    """
    # presets - filter must be in one of the lists
    filter_presets = {"RegistrationStatus": ["Pending", "Verified"], "userTypeName": ["Administrator", "Event Manager", "Alumni"]}
    if filter.title() in filter_presets["RegistrationStatus"]:
        users_data = db.get_users(RegistrationStatus=filter)
    elif filter.title() in filter_presets["userTypeName"]:
        users_data = db.get_users(userTypeName=filter)
    else:
        #filter doesn't exist return all users
        users_data = db.get_users()
    users_data = list(enumerate(users_data))
    return json.jsonify(users_data)

@app.route("/approve_user/<user_email>/")
def approve_user(user_email):
    """
    Approves user with ID user_email
    :param user_id:
    :return:
    """
    if user_email:
        DEFAULT_PASSWORD = generate_password_hash("1234")
        update_id = db.verify_user(user_email, DEFAULT_PASSWORD)

        #Sending Emails Not working for now, Will fix bug later
        # send_verified_email(user_email)

        return json.jsonify(success="The user was successfully Verified", update_id=update_id)
    else:
        return json.jsonify(error="There was an error approving that user!")

@app.route("/reject_user/<user_email>/")
def reject_user(user_email):
    """
    Rejects user with ID user_email
    :param user_id:
    :return:
    """
    if user_email:
        DEFAULT_PASSWORD = ""
        update_id = db.unverify_user(user_email, DEFAULT_PASSWORD)
        return json.jsonify(success="The user was successfully disable!", update_id=update_id)
    else:
        return json.jsonify(error="There was an error disabling that user!")

def send_verified_email(email):
    """
    Send success message to users who have been approved
    :param email:
    :return:
    """
    msg = Message()
    msg.html = "<h1/> Successful registration! </h1> <br /> <div>Your registration request was succesfully approved by" \
               "<strong>Kabarak Web Admin</strong> <br /> <code> email: {} </code> <br /> <code> password: {} </code>" \
               "<h5>Welcome to the Alumni community!</h5></div".format(email, "1234")
    mail.send(msg)


@app.route("/discussions")
def discussions():
    """
    Renders the discussions view
    :return:
    """
    if is_logged_in():
        return render_template("/discussions.html")

@app.route("/get_discussions/<discussion_id>/")
def get_discussions(discussion_id):
    if discussion_id.isdecimal():
        # If discussion id is set fetch and return single discussion
        discussions = db.get_discussions(discussion_id=discussion_id)
    else:
        discussions = db.get_discussions()

    discussions = list(enumerate(discussions))
    return json.jsonify(discussions)

@app.route("/events")
def events():
    """
    Renders the discussions view
    :return:
    """
    if is_logged_in():
        return render_template("/events.html")


@app.route("/get_events/<event_id>/")
def get_events(event_id):
    if event_id.isnumeric():
        events = db.get_events(event_id=event_id)
    else:
        #fetch all events instead
        events = db.get_events()
    events = list(enumerate(events))
    return json.jsonify(events)


@app.route("/single_discussion/<post_id>/")
def single_discussion(post_id):
    """
    Renders template for single
    :param category:
    :param post_id:
    :return:
    """
    return render_template("single_discussion.html")

@app.route("/single_event/<event_id>/")
def single_event(event_id):
    return render_template("single_event.html")



@app.route("/get_user_data")
def get_user_data():
    # Returns all the currently logged in user's details stored in session
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


@app.route("/new_discussion")
def new_discussion():
    return render_template("new_discussion.html")


@app.route("/create_discussion", methods=["POST"])
def create_discussion():
    """
    Organizes form data and creates discussion
    :return:
    """
    if is_logged_in():
        if request.method == "POST":
            if request.get_json(force=True)["Title"] and request.get_json(force=True)["Content"] and request.get_json(force=True)["DateEvent"]:
                data = {}
                data["Title"] = request.get_json(force=True)["Title"].strip()
                data["Content"] = request.get_json(force=True)["Content"].strip()
                data["DiscusionTags_idDiscusionTags"] = request.get_json(force=True)["DiscusionTags_idDiscusionTags"].strip()
                data["Users_idUsers"] = session["idUsers"]

                insert_id = db.insert_discussion(data)
                return json.jsonify(success="Discussion was successfully created!", insert_id=insert_id)

            else:
                return json.jsonify(error="You must fill in all fields!")
        else:
            return json.jsonify(error="There is a problem with your request. You are sending GET \
                                   instead of POST requests to this API.")

@app.route("/get_discussion_comments/<post_id>")
def get_discussion_commnets(post_id):
    """
    Returns all comments associated with a post
    :param post_id:
    :return:
    """
    comments = db.get_discussion_comments(post_id)
    comments = list(enumerate(comments))
    return json.jsonify(comments)

@app.route("/new_event")
def new_event():
    return render_template("new_event.html")

@app.route("/create_event", methods=["POST"])
def create_event():
    """
    Organizes form data and creates event
    :return:
    """
    if is_logged_in():
        if request.method == "POST":
            if request.get_json(force=True)["Title"] and request.get_json(force=True)["Content"] and request.get_json(force=True)["DateEvent"]:
                data = {}
                data["Title"] = request.get_json(force=True)["Title"].strip()
                data["Content"] = request.get_json(force=True)["Content"].strip()
                data["DateEvent"] = request.get_json(force=True)["DateEvent"].strip()
                data["Fundraiser"] = request.get_json(force=True)["Fundraiser"]
                data["FundraiseAmount"] = request.get_json(force=True)["FundraiseAmount"]
                data["Users_idUsers"] = session["idUsers"]

                insert_id = db.insert_event(data)
                return json.jsonify(success="Event was successfully created!", insert_id=insert_id)

            else:
                return json.jsonify(error="You must fill in all fields!")
        else:
            return json.jsonify(error="There is a problem with your request. You are sending GET \
                                   instead of POST requests to this API.")




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
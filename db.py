from flask.ext.mysqldb import MySQL

class DB(object):
    """
      This uses the flaskmyqldb extension to perform CRUD operations against
      a MySql database
    """
    instance = None

    def __init__(self, config_dict):
        """
            Initializes a singleton DB object
            :param config_dict: a dictionary contaning all config variables to be passed to the flask.ext.mysqldb extension
            :return: None
        """
        if DB.instance is None:
            DB.instance = MySQL(config_dict)

    def fetch_user(self, username=None,email=None, nationalid=None):
        """
        Fetches a user in the database with the given username
        :param username: The username to lookup
        :param email: The email to lookup
        :param nationalid: The Nationa ID to lookup
        :return: the user's details
        """
        #Specify query param to use depending on set parameters
        lookup = username if username else email if email else nationalid
        #Specify field to use depending on set parameters
        lookup_name = "Username" if username else "Email" if email else "NationalID"

        cursor = DB.instance.connection.cursor()
        query = "SELECT * FROM users WHERE {} = '{}'".format(lookup_name,lookup)
        cursor.execute(query)

        return cursor.fetchall()

    def fetch_users(self, username_list=None):
        """
        Fetches all user in the database by default
        If username_list is set then it returns all matching users in list
        :return:
        """
        cursor = DB.instance.connection.cursor()
        # create string to fetch multiple usernames specified in username_list
        if len(username_list) is not None and isinstance(username_list, list):
            searches = "','".join(username_list)
            query = " SELECT * FROM users WHERE Username in ('{}')".format(searches)
            cursor.execute(query)
        else:
            cursor.execute(''' SELECT * FROM users ''')

        return cursor.fetchall()


    def fetch_user_types(self, user_type_list=None):
        """
        Fetches all user types in the database by default
        If user_type_list is set then it returns all matching user types in list
        :return:
        """
        cursor = DB.instance.connection.cursor()
        # create string to fetch multiole usertypes specified in user_type_list
        if len(user_type_list) is not None and isinstance(user_type_list, list):
            searches = "','".join(user_type_list)
            query = " SELECT * FROM usertypes WHERE Name in ('{}')".format(searches)
            cursor.execute(query)
        else:
            cursor.execute("SELECT * FROM usertypes")

        return cursor.fetchall()

    def insert_user(self, details):
        """
        writes a user to the database when registering after submitting valid details
        :param details: dictionary with user details
        :return:
        """
        print "uuuuwiiii", details, type(details)
        query = "INSERT INTO users (UserTypes_idUserTypes, NationalID, FirstName, LastName, Telephone, Email, Username, RegistrationStatus, DateVerified) VALUES (3, '{}', '{}', '{}', '{}', '{}', '{}', 'Pending', '0000-00-00 00:00:00')".format(details["NationalID"], details["FirstName"], details["LastName"], details["Telephone"], details["Email"], details["Username"])

        print query

        cursor = DB.instance.connection.cursor()
        cursor.execute(query)
        DB.instance.connection.commit()
        return cursor.lastrowid

    def get_last_verified_usernames(self, limit=10):
        """
        returns the usernames of the last 10 verified users by default and orders by last registered
        :return:
        """
        query = "SELECT Username, NationalID FROM users WHERE DateVerified <> '0000-00-00 00:00:00' ORDER BY DateVerified DESC LIMIT {}".format(limit)
        cursor = DB.instance.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_last_registered_usernames(self, limit=10):
        """
        returns the usernames of the last 10 verified users by default and orders by last registered
        :return: disct with usernames
        """
        query = "SELECT Username, NationalID FROM users WHERE DateVerified = '0000-00-00 00:00:00' ORDER BY DateRegistered DESC LIMIT {}".format(limit)
        cursor = DB.instance.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_discussions(self, limit=5, tags=[]):
        """
        Returns last 5 discussions with any tags if unspecified or with specified tags if so provided
        Discussions ordered by latest first
        :param limit: integer - number of discussions to fetch
        :param tags: list - The tag(s) to match
        :return: fetched posts
        """
        if len(tags) == 0:
            query = "SELECT discusiontags.Name, users.Username AS tagName, discussions.* FROM (discusiontags, users) INNER JOIN discussions on (discusiontags.idDiscusionTags = discussions.DiscusionTags_idDiscusionTags and discussions.Users_idUsers = users.idUsers) ORDER BY discussions.DateCreated DESC LIMIT {}".format(limit)
        else:
            tags = str(tags).strip("[]")
            query = "SELECT discusiontags.Name AS tagName, discussions.* FROM discusiontags LEFT JOIN discussions on (discusiontags.idDiscusionTags = discussions.DiscusionTags_idDiscusionTags)  WHERE discusiontags.Name in ({}) ORDER BY discussions.DateCreated DESC LIMIT {}".format(tags, limit)

        cursor = DB.instance.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_events(self, limit=5, fundraiser=2):
        """
        Returns latest posted event limited to 5 events by default
        :param limit: int max number of events to fetch
        :param fundraiser: int 2: all events; 1: fundraisers only; 0: non-fundraiser events
        :return: fetched events
        """
        if fundraiser == 2:
            query = "SELECT users.Username, events.* FROM events LEFT JOIN users ON (events.Users_idUsers = users.idUsers) LIMIT {}".format(limit)
        elif fundraiser == 1 or fundraiser == 0:
            query = "SELECT users.Username, events.* FROM events LEFT JOIN users ON (events.Users_idUsers = users.idUsers) WHERE Fundraiser = {} LIMIT {}".format(fundraiser, limit)

        cursor = DB.instance.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()














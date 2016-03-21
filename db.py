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

    def fetch_user(self, username):
        """
        Fetches a user in the database with the given username and password
        :return: the user's details
        """
        cursor = DB.instance.connection.cursor()
        query = "SELECT * FROM users WHERE Username = '{}'".format(username)
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

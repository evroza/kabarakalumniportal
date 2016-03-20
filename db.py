from flask.ext.mysqldb import MySQL

class DB(object):
    """
        This uses the flask-myqldb extension to perform CRUD operations against
        a MySql database
    """

    def __init__(self, config_dict):


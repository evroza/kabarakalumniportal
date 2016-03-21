from flask.ext.mysqldb import MySQL

class DB(object):
    """
        This uses the flask-myqldb extension to perform CRUD operations against
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
            DB.instance == MySQL(config_dict)


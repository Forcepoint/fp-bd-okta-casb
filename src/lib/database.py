#
# Database class implements a database to store user's risk score.
# the used database engine sqlite3. it is in the python3 std lib
#
# Author:  Dlo Bagari
# created Date: 12-17-2019
#


import sqlite3
from sqlite3 import Error

CREATE_USER_TABLE = """CREATE TABLE IF NOT EXISTS user (
                            id integer PRIMARY KEY,
                            login_name text NOT NULL,
                            risk_score integer NOT NULL,
                             group_name text NOT NULL);"""
INSERT_INTO_USERS = '''INSERT INTO user(login_name, risk_score, group_name)
                        VALUES (?,?,?)'''


class Database:
    def __init__(self, settings, parser, logger):
        self._settings = settings
        self._parser = parser
        self._connect = None
        self._cursor = None
        self._logger = logger
        self._connect_to_database()
        self._create_tables()

    def _connect_to_database(self):
        """
        connect with database file or created it if does not exist
        :return: None
        :exception: connection error
        """
        try:
            self._connect = sqlite3.connect(self._settings["database_path"])
            self._cursor = self._connect.cursor()
        except Error as e:
            self._logger.error(self, e)
            self._parser.error("Failed in connecting with database")

    def _create_tables(self):
        """
        create users table is not exists
        :return: None
        :exception connection error
        """
        try:
            self._cursor.execute(CREATE_USER_TABLE)
            self._connect.commit()
        except Error as e:
            self._logger.error(self, e)
            self._parser.error("Failed in creating the user table")

    def add_row(self, login_name, risk_score, group_name=""):
        """
        insert a new row into the user table
        :param login_name: the user's login name
        :param risk_score: the user's risk level
        :param group_name: okta group name
        :return: boolean: the result of the row insertion
        :exception connection error
        """
        try:
            result = self._cursor.execute(INSERT_INTO_USERS, (login_name, risk_score, group_name))
            self._connect.commit()
            return False if result is None else True
        except Error as e:
            self._logger.error(self, e)
            self._parser.error("Failed in inserting data into user table")
            return False

    def get_risk_score(self, user_login_name):
        """
        query the risk score from the user table
        :param user_login_name: the users login name
        :return: boolean, user's risk score
        """
        query = 'SELECT * FROM user WHERE login_name = "{}"'.format(user_login_name)
        self._cursor.execute(query)
        row = self._cursor.fetchall()
        if len(row) == 0:
            return False, -1
        row_to_dict = self.row_to_dict(row[0])
        return True, row_to_dict["risk_score"]

    def get_group_name(self, user_login_name):
        """
        query the group name from the user table
        :param user_login_name: the users login name
        :return: boolean, user's okta group name
        """
        query = 'SELECT * FROM user WHERE login_name = "{}"'.format(user_login_name)
        self._cursor.execute(query)
        row = self._cursor.fetchall()
        if len(row) == 0:
            return False, -1
        row_to_dict = self.row_to_dict(row[0])
        return True, row_to_dict["group_name"]

    def is_user_exists(self, user_login_name):
        """
        check if a user is exists in the database
        :param user_login_name:
        :return:boolean
        """
        result, risk_score = self.get_risk_score(user_login_name)
        return result

    def row_to_dict(self, row):
        """
        Create a dict from the row
        :param row: a database record
        :return: dictionary
        """
        result = {}
        for idx, col in enumerate(self._cursor.description):
            result[col[0]] = row[idx]
        return result

    def update_risk_score(self, login_name, risk_score):
        """
        Update the user's risk score in the database
        :param login_name:
        :param risk_score:
        :return: boolean
        """
        update_risk_level = f"UPDATE user SET risk_score = {risk_score} WHERE  login_name= '{login_name}'"
        try:
            self._cursor.execute(update_risk_level)
            self._connect.commit()
        except Error as e:
            self._logger.error(self, e.args[0])
            return False
        return True

    def update_group(self, login_name, new_group):
        """
        Update the user's group name
        :param login_name: the user's login name
        :param new_group: the user's new group
        :return:  boolean
        """
        update_group = f"UPDATE user SET group_name = '{new_group}' WHERE  login_name= '{login_name}'"
        try:
            self._cursor.execute(update_group)
            self._connect.commit()
        except Error as e:
            self._logger.error(self, e.args[0])
            return False
        return True

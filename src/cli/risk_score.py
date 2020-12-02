#
# class RiskScore implements the entry point for CLI application.
# the __call__ method is required to be override in order to be callable by the argparse lib
#
# Author:  Dlo Bagari
# created Date: 12-17-2019

import yaml
import requests
from sys import exit
from lib.logger import Logger
from lib.database import Database
from lib.changepolicy import ChangePolicy
from lib.user import User
from lib.group import Group


class RiskScore:
    def __init__(self, parser):
        self._parser = parser
        self._logger = None
        self._database = None
        self._change_policy = None
        self._user = None

    def __call__(self, args):
        self._args = args
        try:
            with open(self._args.config_file) as f:
                self._settings = yaml.load(f, yaml.SafeLoader)
        except Exception as e:
            self._parser.error("Failed in loading the settings.yml file:{}".format(e))
        self._logger = Logger(self._settings["logs_locations"])
        self._database = Database(self._settings, self._parser, self._logger)
        self._user = User(self._settings["okta_token"], self._settings["okta_organization_url"])
        self._group = Group(self._settings["okta_token"], self._settings["okta_organization_url"])
        self._change_policy = ChangePolicy(self._settings, self._user, self._group)

        self._run_risk_score_monitor()

    def _run_risk_score_monitor(self):
        """
        login to CASB website , pull csv file and process it.
        :return: None
        """
        self._get_risk_core_cvs()

    def _get_risk_core_cvs(self):
        """
        login to CASB and download csv file
        :return: csv
        :exception: KeyboardInterrupt: to terminate the application
        """
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            login_data = {"j_username": self._settings["casb_login_name"],
                          "j_password": self._settings["casb_login_password"],
                          "submit": "Login"}
            with requests.session() as session_1:
                session_1.post(self._settings["casb_ligin_form_action_url"],
                               data=login_data, headers=headers)
                response = session_1.get(self._settings["casb_users_csv_url"])
                print("DEBUG: status code ", response.status_code)
                if response.status_code == 200:
                    if len(list(response.iter_lines())) > 1:
                        accounts = self.map_account_name_to_login_name(list(response.iter_lines())[1:])
                        for account in accounts:
                            for login_name in accounts[account]["login_names"]:
                                # validate if the user is an okta user
                                error_code, error_message, result = self._user.get_user(login_name)
                                print("DEBUG: is a okta user: ", error_code, error_message, result)
                                if error_code != 0:
                                    continue
                                risk_score = accounts[account]["score"]
                                change_user_policy, insert_result = self._user_database(login_name,
                                                                                          risk_score)
                                print("DEBUG: change policy", change_user_policy, insert_result)
                                if change_user_policy is True and insert_result is True:
                                    # get the user's group name in the database
                                    result, group_name = self._database.get_group_name(login_name)
                                    print("DEBUG: ", result, group_name)
                                    if result is False:
                                        self._logger.error(self, "Failed to read the group name from the database")
                                        self._parser.error("Failed to read the group name from the database")
                                    error_code, error_message, response = self._change_policy.change_policy(login_name,
                                                                                                            risk_score,
                                                                                                            group_name)
                                    if error_code != 0:
                                        self._logger.error(self, error_message)
                                    else:
                                        if len(response) != 0 and "new_group_name" in response:
                                            result = self._database.update_group(login_name, response["new_group_name"])
                                            if result is False:
                                                self._logger.error(self, "Failed in updating the group name")
                else:
                    self._parser.error("Failed in downloading risk score csv file"
                                       " with response code: {}".format(response.status_code))

            return None
        except KeyboardInterrupt:
            print()
            exit()

    def _user_database(self, login_name, risk_score):
        """
        process one line of csv. interacts with database in order to add user's record or update user's record
        :param login_name: user login name
        :param risk_score: user's risk_score
        :return: boolean: define if the processed line needs changing the user's policy,
                 boolean: result of interacting with database
        """
        result, risk_score_in_database = self._database.get_risk_score(login_name)
        # user is not exists
        if result is False:
            result = self._database.add_row(login_name, risk_score)
            if result is False:
                self._parser.error("Failed in inserting a new row into user's table")
                return False, False,
            return True, True
        # user exists in the database
        else:
            if risk_score != int(risk_score_in_database):
                result = self._database.update_risk_score(login_name, risk_score)
                if result is False:
                    self._logger.error(self, f"Failed in updating the risk score for user {login_name}")
                    return False, False
                return True, True
            return True, False

    @staticmethod
    def map_account_name_to_login_name(accounts):
        """
        Maps the accounts name to the login name. this method simply groups the csv rows by the account name
        :param accounts: list of accounts records
        :return: dict
        """
        accounts_dict = {}
        for account in accounts:
            line_parts = account.decode('utf-8').split(',')
            if len(account) >= 10:
                account, login_name, risk_score, full_name, asset = line_parts[0], line_parts[1], line_parts[2],\
                                                                    line_parts[6], line_parts[10]
                if account not in accounts_dict:
                    accounts_dict[account] = {"login_names": set(), "score": 0}
                accounts_dict[account]["login_names"].add(login_name)
                if accounts_dict[account]["score"] < int(float(risk_score)):
                    accounts_dict[account]["score"] = int(float(risk_score))
        return accounts_dict

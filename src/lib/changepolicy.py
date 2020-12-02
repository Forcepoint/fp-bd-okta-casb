#
# the ChangePolicy  class implement API changing the okta user's login policies
#
# Author:  Dlo Bagari
# created Date: 12-17-2019
from lib.constvalue import ConstValues


class ChangePolicy:
    def __init__(self, settings, user, group):
        self._settings = settings
        self._user = user
        self._group = group

    def change_policy(self, login_name, risk_score, group_name):
        """
        Apply polices on the user's account according to the user's risk score
        :param login_name: the user's login name
        :param risk_score: the user's score
        :param group_name: the okta group name
        :return: error_code, error_message, result
        """
        conditions = self.generate_conditions(risk_score)
        for condition in conditions:
            if eval(condition[0]) is True:
                if condition[1] != group_name:
                    print("DEBUG:", login_name, condition)
                    return self.apply_policy(condition[1], login_name, group_name)
                return 0, "", {}
        return 1, "No match found", {}

    def session_termination(self, login_name):
        return self._user.terminate_session(login_name)

    def suspend(self, login_name):
        """
        Suspend the user's account
        :param login_name: the user's login name
        :return: error_code, error_message, response
        """
        error_code, error_message, response = self._user.suspend(login_name)
        if error_code == 0:
            if self._settings["terminate_user_session_after_policy_change"] is True:
                self.session_termination(login_name)
        return error_code, error_message, response

    def generate_conditions(self, risk_score):
        """
        Generates conditions for if statement. the conditions are generated based on the
        configurations in the settings.yml
        :param risk_score: user's risk score
        :return: list of conditions
        """
        conditions = []
        risk_score_map = self._settings["risk_score_map"]
        for i in risk_score_map:
            if "-" in i:
                parts = i.split("-")
                if len(parts) > 1:
                    conditions.append((f"{parts[0]} <= {risk_score} <= {parts[-1]}", risk_score_map[i]))
            elif "+" in i:
                parts = i.split("+")
                if (len(parts)) >= 1:
                    conditions.append((f"{parts[0]} <= {risk_score}", risk_score_map[i]))
        return conditions

    def apply_policy(self, policy, login_name, group_name):
        """
        apply a policy to a user
        :param policy: the policy name
        :param login_name: the user's login name
        :param group_name: the user's current group name
        :return: error_code, error_message, response from okta
        """
        # map of the predefined policies
        callback_functions = {"suspend": self.suspend}

        if policy in callback_functions:
            if group_name != "":
                error_code, error_message, current_group = self._group.filter_groups_by_name(group_name)
                if error_code == ConstValues.ERROR_CODE_ZERO:
                    current_group_id = current_group["id"]
                    error_code, error_message, user_object = self._user.get_user(login_name)
                    user_id = user_object["id"]
                    error_code, error_message, output = self._group.remove_user_from_group(current_group_id, user_id)
            error_code, error_message, response = callback_functions[policy](login_name)
        else:
            error_code, error_message, response = self.change_group(login_name, policy, group_name)
        if error_code == 0:
            if self._settings["terminate_user_session_after_policy_change"] is True:
                self.session_termination(login_name)
        return error_code, error_message, response

    def change_group(self, login_name, group_name, current_group_name):
        """
        change user's group
        :param login_name: the user login name
        :param group_name: the new group name
        :param current_group_name: the current group name
        :return: error_code, error_message, response from okta
        """
        # find user io
        error_code, error_message, user_object = self._user.get_user(login_name)
        if error_code != 0:
            return error_code, error_message, user_object
        if current_group_name == "suspended_predefine":
            self._user.unsuspend(login_name)
            current_group_name = ""
        return self._group.change_group(user_object["id"], group_name, current_group_name)

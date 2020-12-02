#
# the Group class implement API to communicate with Okta for group operations
#
# Author:  Dlo Bagari
# created Date: 12-17-2019

from time import sleep
from lib.constvalue import ConstValues
from lib.execmd import ExeCmd


class Group:
    def __init__(self, okta_token, okta_url):
        self._token = okta_token
        self._url = okta_url
        self._exe_cmd = ExeCmd()

    def change_group(self, user_id, new_group, current_group):
        """
                removes users from current group and add it to the new group
                :param user_id: the user's id
                :param current_group: the user's current group
                :param new_group: the user's new group
                :return: error_code, error_message, response_data
                """
        error_code, error_message, new_group = self.filter_groups_by_name(new_group)
        if error_code != ConstValues.ERROR_CODE_ZERO:
            return error_code, error_message, {}
        if current_group != "":
            error_code, error_message, current_group = self.filter_groups_by_name(current_group)
            if error_code != ConstValues.ERROR_CODE_ZERO:
                return error_code, error_message, {}
            current_group_id = current_group["id"]
            error_code, error_message, output = self.remove_user_from_group(current_group_id, user_id)
            if error_code != ConstValues.ERROR_CODE_ZERO:
                return error_code, error_message, output
            error_code, error_message, group_user = self.get_group_users(current_group_id)
            for u in group_user:
                if u["id"] == user_id:
                    error_code, error_message, output = self.remove_user_from_group(current_group_id, user_id)
                    if error_code != ConstValues.ERROR_CODE_ZERO:
                        return error_code, error_message, output
            sleep(3)
        new_group_id = new_group["id"]
        error_code, error_message, group_id = self.add_user_to_group(new_group_id, user_id)
        if error_code != ConstValues.ERROR_CODE_ZERO:
            return error_code, error_message, group_id
        return 0, "", {"status": "success",
                       "new_group_name": new_group["profile"]["name"],
                       "new_group_id": group_id}

    def get_group_users(self, group_id):
        """
        get the user_app in a specific group
        :param group_id: the group id
        :return: error_code, error_message, user_app
        """
        cmd = 'curl -X GET -H "Accept: application/json" -H "Content-Type: application/json"' \
              ' -H "Authorization: SSWS {}" "https://{}/api/v1/groups/{}/users"'.format(self._token, self._url, group_id)
        output, error = self._exe_cmd.run(cmd)
        if "errorCode" in output:
            return ConstValues.ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ConstValues.ERROR_CODE_ZERO, "", output

    def add_user_to_group(self, group_id, user_id):
        """
        add a user to an exist group
        :param group_id: the group id
        :param user_id: the user id
        :return: error_code, error_message, user
        """
        # check if user is exists:
        error_code, error_message, users = self.get_group_users(group_id)
        if len(users) != 0:
            for i in users:
                if i["id"] == user_id:
                    self.remove_user_from_group(group_id, user_id)
                    sleep(3)
        cmd = 'curl -X PUT -H "Accept: application/json" -H "Content-Type: application/json" -H ' \
                '"Authorization: SSWS %s"  "https://%s/api/v1/groups/%s/users/%s"' % (self._token, self._url,
                                                                                        group_id, user_id)
        output, error = self._exe_cmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ConstValues.ERROR_CODE_ONE, output["errorSummary"], ""
        else:
            return ConstValues.ERROR_CODE_ZERO, "", group_id

    def remove_user_from_group(self, group_id, user_id):
        """
        remove a user from a group
        :param group_id: group id
        :param user_id: user id
        :return: error_code, error_message, user
        """
        cmd = 'curl -X DELETE -H "Accept: application/json" -H "Content-Type: application/json" -H ' \
              '"Authorization: SSWS %s"  "https://%s/api/v1/groups/%s/users/%s"' % (self._token, self._url,
                                                                                    group_id, user_id)
        output, error = self._exe_cmd.run(cmd)

        if output is not None and "errorCode" in output:
            return ConstValues.ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ConstValues.ERROR_CODE_ZERO, "", output

    def filter_groups_by_name(self, group_name):
        """
        Filter groups by name
        :param group_name: the group name
        :return:
        """
        cmd = 'curl -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS {}"' \
              ' "https://{}/api/v1/groups?q={}"'.format(self._token, self._url, group_name)
        output, error = self._exe_cmd.run(cmd)
        if len(output) != 0:
            for group in output:
                if group["profile"]["name"].lower() == group_name.lower():
                    return ConstValues.ERROR_CODE_ZERO, "", group

        if output is not None and "errorCode" in output:
            return ConstValues.ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ConstValues.ERROR_CODE_ONE, "the group {} is not found on organization side".format(group_name),\
                   output

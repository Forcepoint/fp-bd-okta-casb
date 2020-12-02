#
# the User class implement API to communicate with Okta for User operations
#
# Author:  Dlo Bagari
# created Date: 12-17-2019

import urllib.parse
from lib.execmd import ExeCmd

ERROR_CODE_ONE = 1
ERROR_CODE_ZERO = 0


class User:
    def __init__(self, okta_token, okta_url):
        self._url = okta_url
        self._token = okta_token
        self._execmd = ExeCmd()

    def create_user(self, first_name, last_name, email, mobile,  password,
                    recovery_question, recovery_answer, groups=None):
        """
        Creates a new user with a password and recovery question & answer
        :param first_name: the user's first name
        :param last_name: the user_app last name
        :param email: the user's email address
        :param mobile: the mobile number of the user
        :param password: the user password
        :param recovery_question: the user recovery question
        :param recovery_answer: the user recovery answer
        :param groups: list of groups to add the user_app into these groups
        :return: error_code, error_message, user
        """
        if groups is None:
            groups = ""
        else:
            group_str = ''
            for group in groups:
                group_str += '"{}", '.format(group)
            groups = group_str[:-2]

        cmd = 'curl -X POST -H "Accept: application/json"' \
              ' -H "Content-Type: application/json"' \
              ' -H "Authorization: SSWS %s" -d \'{"profile": {"firstName": "%s","lastName": "%s",' \
              ' "email": "%s","login": "%s",' \
              '"mobilePhone": "%s"}, "credentials": { "password" : { "value": "%s" },' \
              ' "recovery_question":{"question": "%s", "answer": "%s"}}%s}\' ' \
              '"https://%s/api/v1/users?activate=false"' % (self._token, first_name,
                                                            last_name, email, email, mobile, password,
                                                            recovery_question, recovery_answer,  groups, self._url)
        output, error = self._execmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def get_user(self, user_id=None):
        """
        Fetches a user from the organization, if no user id is given, fetch all exist user_app
        :param user_id:the user id or the user login email
        :return: error_code, error_message, user_app
        """
        if user_id is None:
            user_id = ""
        else:
            user_id = "/" + user_id
        cmd = 'curl -v -X GET -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users%s"' % (self._token,  self._url, user_id)
        output, error = self._execmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def find_user(self, query):
        """
        Finds user_app who match the specified query
        The value of query is matched against firstName, lastName, or email.
        :param query:
        :return:
        """
        cmd = 'curl -v -X GET -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users?q=%s"' % (self._token,  self._url, query)
        output, error = self._execmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def find_user_by_name(self, first_name, last_name):
        """
        find a specific user
        :param first_name: user_app first name
        :param last_name: user_app last name
        :return: error_code, error_message, user
        """
        query = 'profile.firstName eq "{}" and profile.lastName eq "{}"'.format(first_name, last_name)
        query = urllib.parse.quote(query)
        query = "filter={}".format(query)

        cmd = 'curl -X GET -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users?%s"' % (self._token, self._url, query)
        output, error = self._execmd.run(cmd)
        if "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def delete_user(self, user_id):
        """
        delete an exists user
        :return:
        """
        cmd = 'curl -X DELETE -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users/%s"' % (self._token, self._url, user_id)
        output, error = self._execmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def get_users_group(self, user_id):
        cmd = 'curl -X GET -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users/%s/groups"' % (self._token, self._url, user_id)
        output, error = self._execmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        return ERROR_CODE_ZERO, output

    def active_user(self, user_id):
        cmd = 'curl -X POST -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users/%s/lifecycle/activate?sendEmail=false"' % (self._token, self._url, user_id)
        output, error = self._execmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def terminate_session(self, login_name):
        """
        Removes all active identity provider sessions. This forces the user to authenticate on the next operation
        :param login_name: the user's login name
        :return:error_code, error_message, response
        """
        # find the users by user's login name
        error_code, error_message, user_object = self.get_user(login_name)
        if error_code != 0:
            return error_code, error_message, user_object
        user_id = user_object["id"]
        cmd = 'curl -X DELETE -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users/%s/sessions"' % (self._token, self._url, user_id)
        output, error = self._execmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output

    def suspend(self, login_name):
        """
        Suspend user's account
        :param login_name: the user's log in name
        :return: error_code, error_message, response
        """
        # find the users by user's login name
        error_code, error_message, user_object = self.get_user(login_name)
        if error_code != 0:
            return error_code, error_message, user_object
        user_id = user_object["id"]
        cmd = 'curl -X POST -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users/%s/lifecycle/suspend"' % (self._token, self._url, user_id)
        output, error = self._execmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", {"new_group_name": "suspended_predefine"}

    # TODO: to be removed. is used for testing only
    def unsuspend(self, login_name):
        """
        THIS IS USED FOR TESTING ONLY
        :param login_name: the user's log in name
        :return: error_code, error_message, response
        """
        # find the users by user's login name
        error_code, error_message, user_object = self.get_user(login_name)
        if error_code != 0:
            return error_code, error_message, user_object
        user_id = user_object["id"]
        cmd = 'curl -X POST -H "Accept: application/json"' \
              ' -H "Content-Type: application/json" -H' \
              ' "Authorization: SSWS %s"' \
              ' "https://%s/api/v1/users/%s/lifecycle/unsuspend"' % (self._token, self._url, user_id)
        output, error = self._execmd.run(cmd)
        if output is not None and "errorCode" in output:
            return ERROR_CODE_ONE, output["errorSummary"], {}
        else:
            return ERROR_CODE_ZERO, "", output


# DO NOT RUN THIS IS FOR TEST ONLY
if __name__ == "__main__":
    user = User("00-wme3BiJ6M_Hrl1YzLutOSEJtG_yN_BhgBHaCCJO", "forcepointbizdev.okta.com")

   # error_code2, error_message2, use_data = user.create_user("Eran", "Amir", "eran@redkites.onmicrosoft.com",
    #                                                         "0053587001234", "Forcepoint1!",
    #                                                         "what is your answer", "blablabla")
    #print(error_code2, error_message2, use_data)
    #if error_code2 == 0 and "id" in use_data:
    #    print(user.active_user(use_data["id"]))
    # print(user.active_user("00u291mnj4yr2kdGv357"))
    # print(user.get_user("pennie@redkites.onmicrosoft.com"))
    # print(user.terminate_session("pennie@redkites.onmicrosoft.com"))
    print(user.unsuspend("eran@redkites.onmicrosoft.com"))




#!/usr/bin/env python3

# CLI tool to download CASB risk core
# Author:  Dlo Bagari
# email: dlo.bagari@forcepoint.com
# created Date: 08/07/2020

# Requirements
# this script requires python3.6 or above, requests module ( you can use pip3 install requests if
# your system does not have this module)

# Usage
# to display the help page run: risk_score_exporter.py -h


import argparse
import requests
import csv
from time import sleep
from datetime import datetime


casb_ligin_form_action_url = "https://{}/cm/j_spring_security_check"
casb_users_csv_url = "https://{}/cm/rs/0/human_risk/accounts/reports/csv?search=%2BriskScore%3A" \
                     "(%22%5B1%20TO%20*%5D%22)&sortBy=riskScore&sortDirection=DESC"


class PullRiskScore:
    """Pull Risk Score from CASB"""
    def __init__(self, arg_parser):
        self._parser = parser

    def __call__(self, arg):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        login_data = {"j_username": arg.username,
                      "j_password": arg.password,
                      "submit": "Login"}

        with requests.session() as session_1:
            session_1.post(casb_ligin_form_action_url.format(arg.login_url), data=login_data, headers=headers)
            while True:
                if arg.over_write is False:
                    now = datetime.now()
                    date_time = now.strftime("%Y_%m_%d_%H:%M:%S")
                    output_file = f"{arg.save_to}/casb_risk_score_{date_time}.csv"
                else:
                    output_file = f"{arg.save_to}/casb_risk_score.csv"
                response = session_1.get(casb_users_csv_url.format(arg.login_url))
                with open(output_file, 'w') as f:
                    writer = csv.writer(f)
                    for line in response.iter_lines():
                        writer.writerow(line.decode('utf-8').split(','))
                sleep(arg.interval * 60)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(prog="risk_score_exporter.py")
        pull_risk_score = PullRiskScore(parser)
        # required args
        parser.add_argument("--username", "-u", action="store", dest="username", required=True,
                            help="CASB username")
        parser.add_argument("--password", "-p", action="store", dest="password", required=True,
                            help="CASB password. if your password contains a special character add "
                                 "your password between two single quote marks")
        # optional args
        parser.add_argument("--save-to", "-s", action="store", dest="save_to", default="/tmp",
                            help="a directory where the risk score CSV file will be stored. the default directory "
                                 "is /tmp")
        parser.add_argument("--login-url", "-l", action="store", dest="login_url", default="my.skyfence.com",
                            help="CASB login url. default is my.skyfence.com ")
        parser.add_argument("--interval", "-i", action="store", dest="interval", default=10, type=int,
                            help="the interval time in minutes for pulling risk score from casb."
                                 " the default is 10 minutes")
        parser.add_argument("--over-write", "-o", action="store_true", dest="over_write", default=False,
                            help="overwrite the CSV file. set this argument to True if you DO NOT want to "
                                 "save each risk score pull in a separate file")
        parser.set_defaults(function=pull_risk_score)
        args = parser.parse_args()
        args.function(args)
    except KeyboardInterrupt:
        print()
        exit(0)



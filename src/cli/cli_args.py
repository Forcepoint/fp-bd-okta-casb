#
# CliArgs class implements an argument parser for CLI. all args and their possible values are defined in this class.
# Author:  Dlo Bagari
# created Date: 12-17-2019


import argparse
from .risk_score import RiskScore
from .create_service import CreateService


class CliArgs:
    def __init__(self, name):
        self._parser = argparse.ArgumentParser(prog=name)
        self._risk_score = RiskScore(self._parser)
        self._create_service = CreateService(self._parser)
        self._build_args()

    def _build_args(self):
        """
        Define all possible args with their possible values
        :return: None
        """
        subparsers = self._parser.add_subparsers(title="sub-commands")
        run_cli = subparsers.add_parser("run",
                                        description="Runs the risk level service")
        service_cli = subparsers.add_parser("service", description="create Systemd Service for okta_casb.service")

        run_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                             help="the config file path", required=True)
        run_cli.set_defaults(function=self._risk_score)

        service_cli.add_argument("--start", "-s", action="store_true",
                                 default=False, dest="start", help="Start systemd service(okta_casb.service)")
        service_cli.add_argument("--name", "-n", action="store",
                                 default="okta_casb", dest="name", help="the service name, "
                                                                        "default name is 'okta_casb.service'")
        service_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                                 help="the config file path", required=True)
        service_cli.set_defaults(function=self._create_service)

    def get_parser(self):
        """
        Return a defined argument parser for CLI
        :return: parser
        """
        return self._parser

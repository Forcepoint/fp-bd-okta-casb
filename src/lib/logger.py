#
# Author:  Dlo Bagari
# created Date: 26-11-2019
import logging


class Logger:
    def __init__(self, log_directory):
        self._log_directory = log_directory
        self._log = logging
        self._set_config()

    def _set_config(self):

        file_name = self._log_directory + "/risk_score_service.log"
        log_format = '%(asctime)s - %(levelname)s -  %(message)s'
        self._log.basicConfig(filename=file_name,
                              level=logging.INFO,
                              format=log_format)

    def warning(self, class_name, message):
        message = "{}: {}".format(class_name.__class__.__name__, message)
        self._log.warning(message)

    def critical(self,  class_name, message):
        message = "{}: {}".format(class_name.__class__.__name__, message)
        self._log.critical(message)

    def error(self,  class_name, message):
        message = "{}: {}".format(class_name.__class__.__name__, message)
        self._log.error(message)

    def debug(self,  class_name, message):
        message = "{}: {}".format(class_name.__class__.__name__, message)
        self._log.debug(message)

    def info(self,  class_name, message):
        message = "{}: {}".format(class_name.__class__.__name__, message)
        self._log.info(message)
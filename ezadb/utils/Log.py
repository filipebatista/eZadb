import logging
import os
from logging.handlers import RotatingFileHandler

# Initialize logger
main_logger = logging.getLogger('ezADB')
main_logger.setLevel(logging.DEBUG)
DEFAULT_LOG_FOLDER = os.path.expanduser('~') + "/.ezadb/logs/"
DEFAULT_LOG_FILENAME = 'ezADB.log'
LOG_FILE_PATH = DEFAULT_LOG_FOLDER + DEFAULT_LOG_FILENAME

# create the folders if they don't exist
if not os.path.exists(DEFAULT_LOG_FOLDER):
    os.makedirs(DEFAULT_LOG_FOLDER)

# Add the log message handler to the logger
rotatingHandler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=2000, backupCount=100)
rotatingHandler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotatingHandler.setFormatter(formatter)

main_logger.addHandler(rotatingHandler)


class Log:
    @staticmethod
    def debug(cls, *text):
        Log._get_logger_(cls).debug(text)

    @staticmethod
    def info(cls, *text):
        Log._get_logger_(cls).info(text)

    @staticmethod
    def error(cls, *text):
        Log._get_logger_(cls).error(text)

    @staticmethod
    def warn(cls, *text):
        Log._get_logger_(cls).warning(text)

    @staticmethod
    def _get_logger_(_class_):
        if _class_ is None:
            class_logger = main_logger
        else:
            class_logger = logging.getLogger(_class_.__name__)

        # ensure that the logger has an handler
        if not class_logger.handlers:
            class_logger.setLevel(logging.DEBUG)
            class_logger.addHandler(rotatingHandler)
        return class_logger

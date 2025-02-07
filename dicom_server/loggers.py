import os, logging, json
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from services.loggers_service import ILoggers


class Loggers(ILoggers):

    def __init__(
        self, main_logger_directory, simplified_log_directory, exception_log_directory
    ):
        self.main_logger = self.setup_logger(
            "pynetdicom", main_logger_directory, logging.DEBUG
        )
        self.simplified_logger = self.setup_logger(
            "simplified_logger", simplified_log_directory, logging.INFO
        )
        self.exceptions_logger = self.setup_logger(
            "exceptions", exception_log_directory, logging.ERROR
        )

    def setup_logger(
        self, name, log_directory, level=logging.INFO, when="midnight", interval=1
    ):
        handler = TimedRotatingFileHandler(
            os.path.join(log_directory, name), when=when, interval=interval
        )
        handler.suffix = "_%Y-%m-%d.log"
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger


class SimplifiedLogsFormatter(logging.Formatter):
    def format(self, record):
        msg = str(record)
        start_index = msg.find('"') + 1
        end_index = msg.rfind('"')
        log_message = msg[start_index:end_index]
        log_object = json.loads(log_message.replace("'", '"'))

        keys_to_remove = {
            "lock",
            "main_operation",
            "known_scanner",
            "status",
            "matches",
        }
        for key in keys_to_remove:
            log_object.pop(key, None)

        return json.dumps(log_object, default=str)

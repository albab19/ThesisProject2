import os, logging, json, sys
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from services.loggers_service import ILoggers
import traceback


class SimplifiedLogsFormatter(logging.Formatter):
    def __init__(
        self,
        is_production,
        fmt=None,
        datefmt=None,
        style="%",
        validate=True,
        *,
        defaults=None
    ):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        self.is_production = is_production

    def format(self, record):
        msg = str(record.msg)

        log_object = json.loads(msg.replace("'", '"'))

        keys_to_remove = {"lock", "main_operation", "known_scanner", "status"}
        for key in keys_to_remove:
            log_object.pop(key, None)
        if (
            log_object["request_Type"] == "Association Aborted"
            or log_object["request_Type"] == "Association Released"
        ):
            # Remove none subprocess info
            log_object["session_parameters"] = "N/A"
            log_object["query_level"] = "N/A"
            log_object["matches"] = "N/A"

        return json.dumps(log_object, default=str)


class ExceptionFormatter(logging.Formatter):
    def __init__(
        self,
        is_production,
        fmt=None,
        datefmt=None,
        style="%",
        validate=True,
        *,
        defaults=None
    ):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        self.is_production = is_production

    def format(self, record):

        # Start building the exception message with the timestamp
        excep = (
            "Exception at "
            + datetime.now().strftime("%d-%m-%Y : %H-%M-%S")
            + "\n.............................................\n"
        )
        trace = ""

        if record.exc_info:
            trace = "".join(traceback.format_exception(*record.exc_info))

            tb = record.exc_info[2]
            while tb.tb_next:
                tb = tb.tb_next
            frame = tb.tb_frame
            class_name = (
                frame.f_locals.get("self", None).__class__.__name__
                if "self" in frame.f_locals
                else "No class"
            )
            excep += "In " + frame.f_globals["__name__"] + "\n"
            if self.is_production:
                print(
                    "An exception in "
                    + frame.f_globals["__name__"]
                    + "\n"
                    + "Message: "
                    + record.msg
                    + "\nSee\033[91m exceptions.log \033[0m file for more details\n.......................................\n"
                )

        # Append the log message
        excep += (
            "Message: "
            + str(record.msg)
            + "\n"
            + "Traceback :\n ............\n"
            + trace
        )

        return excep


class Loggers(ILoggers):

    def __init__(
        self,
        is_production,
        main_logger_directory,
        simplified_log_directory,
        exception_log_directory,
    ):
        self.is_production = is_production
        self.main_logger = self.setup_logger(
            "pynetdicom", main_logger_directory, logging.DEBUG, "midnight", 1, None
        )
        self.simplified_logger = self.setup_logger(
            "simplified_logger",
            simplified_log_directory,
            logging.INFO,
            "midnight",
            1,
            SimplifiedLogsFormatter(is_production),
        )
        self.exceptions_logger = self.setup_logger(
            "exceptions",
            exception_log_directory,
            logging.ERROR,
            "midnight",
            1,
            ExceptionFormatter(is_production),
        )

    def setup_logger(
        self,
        name,
        log_directory,
        level=logging.INFO,
        when="midnight",
        interval=1,
        formatter=None,
    ):
        handler = TimedRotatingFileHandler(
            os.path.join(log_directory, name + ".log"), when=when, interval=interval
        )
        handler.suffix = "%Y-%m-%d"
        handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if not self.is_production:
            logger.addHandler(stream_handler)
        logger.addHandler(handler)
        return logger

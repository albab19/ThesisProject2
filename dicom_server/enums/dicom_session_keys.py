from aenum import Enum


class Sessionkeys(Enum):
    _init_ = "key default"

    LOCK = "lock", 0
    SESSION_ID = "session_id", 0
    REQUEST_TYPE = "request_type", "N/A"
    SESSION_MAIN_OPERATION = "main_operation", "N/A"
    QUERY_LEVEL = "query_level", "N/A"
    SESSION_PARAMETERS = "session_parameters", "N/A"
    LOG_LEVEL = "log_level", "N/A"
    VERSION = "version", "N/A"
    IP = "ip", "N/A"
    PORT = "port", "N/A"
    KNOWN_SCANNER = "known_scanner", "N/A"
    MATCHES = "matches", "N/A"
    STATUS = "status", "N/A"
    TIMESTAMP = "time_stamp", "N/A"

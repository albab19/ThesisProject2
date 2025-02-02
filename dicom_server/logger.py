import logging
import os
import json
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import time
import config
import redis_handler
import network_threat_handler as network_handler


class DicomLogger:
    def __init__(self):
        self.log_info = {
            "lock": 0,
            "version_name": "N/A",
            "session_id": 0,
            "Request_Type": "N/A",
            "query_level": "N/A",
            "term": "N/A",
            "identifier": "N/A",
            "level": "N/A",
            "version": "N/A",
            "ip": "N/A",
            "port": "N/A",
            "matches": "N/A",
            "status": "N/A",
        }
        self.redis_data = {}
        self.setup_loggers()

    def setup_loggers(self):
        try:
            simplified_log_file_path = os.path.join(
                config.SIMPLIFIED_LOG_DIRECTORY, "dicom_simplified.log"
            )
            exception_log_file_path = os.path.join(
                config.LOG_DIRECTORY, "exception.log"
            )

            self.simplified_logger = self.setup_logger(
                "simplified_logger", simplified_log_file_path
            )
            self.exception_logger = self.setup_logger(
                "exception_logger", exception_log_file_path, logging.ERROR
            )
        except Exception as e:
            print(e)

    def setup_logger(
        self, name, log_file, level=logging.INFO, when="midnight", interval=1
    ):
        handler = TimedRotatingFileHandler(log_file, when=when, interval=interval)
        handler.suffix = "%Y%m%d"
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler())
        return logger

    def log_simplified_message(self):
        message = {
            "ID": self.log_info["session_id"],
            "Term": self.log_info["term"],
            "Command": self.log_info["Request_Type"],
            "level": self.log_info["level"],
            "QueryRetrieveLevel": self.log_info["query_level"],
            "identifier": self.log_info["term"],
            "timestamp": datetime.now().isoformat(),
            "Matches": self.log_info["matches"],
            "IP": self.log_info["ip"],
            "Port": self.log_info["port"],
        }
        if self.log_info["Request_Type"] == "Association Requested":
            message["Version"] = str(self.log_info["version"])
        if self.log_info["status"] == "Finished":
            message["Command"] = "Association Released"
        if self.log_info["status"] == "Aborted":
            message["Command"] = "Association Aborted"
        try:
            json_message = json.dumps(message)
            self.simplified_logger.info(json_message)
        except (TypeError, ValueError) as e:
            self.exception_logger.error(
                f"Failed to log simplified message: {message} - {e}"
            )

    def start_log_session(self, ip, port, v_name):
        if not self.logging_locked():
            rep_dat = {}
            ip_scanned = redis_handler.is_ip_scanned(ip)
            current_time = time.time()
            known_scanner = network_handler.is_known_scanner(ip)
            self.log_info["known_scanner"] = known_scanner
            self.log_info["Request_Type"] = "Association Requested"
            self.log_info["ip"] = str(ip)
            self.log_info["port"] = port
            self.log_info["level"] = "Warning"
            self.set_session_id(str(int(current_time * 1000000)))
            self.log_simplified_message()
            if not ip_scanned:
                redis_handler.add_scanned_ip(ip)
                network_handler.get_reputation_data(rep_dat, ip, ip_scanned)
                redis_handler.add_reputation_data(rep_dat)
            self.set_lock(1)
        else:
            self.log_info["version"] = v_name

    def set_log_info(self, params):
        for key, value in params.items():
            self.log_info[key] = value

    def log_release_or_abort(self):
        self.set_redis_log_data()
        self.log_simplified_message()
        self.set_lock(0)
        self.set_session_id(0)
        redis_handler.add_request_data(self.redis_data)
        self.reset_log_object()

    def reset_log_object(self):
        self.log_info = {
            "lock": 0,
            "version_name": "N/A",
            "session_id": 0,
            "Request_Type": "N/A",
            "query_level": "N/A",
            "term": "N/A",
            "identifier": "N/A",
            "level": "N/A",
            "version": "N/A",
            "ip": "N/A",
            "port": "N/A",
            "matches": "N/A",
            "status": "N/A",
        }

    def set_redis_log_data(self):
        current_time = time.time()
        self.redis_data["matches"] = self.log_info["matches"]
        self.redis_data["Request_parameters"] = self.log_info["term"]
        self.redis_data["QueryRetrieveLevel"] = self.log_info["query_level"]
        self.redis_data["Known_scanner"] = self.log_info["known_scanner"]
        self.redis_data["timestamp"] = str(current_time)
        self.redis_data["id"] = self.log_info["session_id"]
        self.redis_data["ip"] = self.log_info["ip"]
        self.redis_data["port"] = str(self.log_info["port"])
        self.redis_data["Request_Type"] = self.log_info["Request_Type"]
        self.log_info["Request_Type"] = "N/A"
        self.log_info["query_level"] = "N/A"
        self.log_info["term"] = "N/A"
        self.log_info["matches"] = "N/A"

    def set_lock(self, value):
        self.log_info["lock"] = value

    def logging_locked(self):
        return self.log_info["lock"] == 1

    def set_session_id(self, s_id):
        self.log_info["session_id"] = s_id


# from logging.handlers import TimedRotatingFileHandler
# import logging,os,json
# from datetime import datetime
# import redis_handler
# import network_threat_handler as network_handler
# import time
# import config

# redis_data={}
# log_info={
# "lock":0,
# "version_name":"N/A",
# "session_id":0,
# "Request_Type" : "N/A",
# "query_level" : "N/A",
# "term" : "N/A",
# "identifier" : "N/A",
# "level" : "N/A",
# "version" : "N/A",
# "ip" : "N/A",
# "port" : "N/A",
# "matches" : "N/A",
# "status":"N/A"}


# def setup_logger(name, log_file, level=logging.INFO, when="midnight", interval=1):

#     handler = TimedRotatingFileHandler(log_file, when=when, interval=interval)
#     handler.suffix = "%Y%m%d"
#     logger = logging.getLogger(name)
#     logger.setLevel(level)
#     logger.addHandler(handler)
#     logger.addHandler(logging.StreamHandler())
#     return logger


# try:
#     log_file_path = os.path.join(config.LOG_DIRECTORY, 'dicom_server.log')
#     simplified_log_file_path = os.path.join(config.SIMPLIFIED_LOG_DIRECTORY, 'dicom_simplified.log')
#     exception_log_file_path = os.path.join(config.LOG_DIRECTORY, 'exception.log')
#     #detailed_logger = setup_logger('detailed_logger', log_file_path, logging.DEBUG)
#     simplified_logger = setup_logger('simplified_logger', simplified_log_file_path)
#     exception_logger = setup_logger('exception_logger', exception_log_file_path, logging.ERROR)

# except Exception as e:
#     print(e)


# def log_simplified_message():
#     global log_info

#     message= {
#                 "ID": log_info["session_id"],
#                 "Term": log_info["term"],
#                 "Command": log_info["Request_Type"],
#                 "level": log_info["level"],
#                 "QueryRetrieveLevel": log_info["query_level"],
#                 "identifier": log_info["term"],
#                 "timestamp": datetime.now().isoformat(),
#                 "Matches":log_info["matches"],
#                 "IP":log_info["ip"],
#                 "Port":log_info["port"]
#                 }
#     if log_info["Request_Type"]=="Association Requested":
#         message["Version"]= str(log_info["version"])
#     if log_info["status"]== "Finished":
#         message["Command"]="Association Released"
#     if log_info["status"]== "Aborted":
#          message["Command"]="Association Aborted"
#     try:
#         json_message = json.dumps(message)
#         simplified_logger.info(json_message)
#     except (TypeError, ValueError) as e:
#         exception_logger.error(f"Failed to log simplified message: {message} - {e}")


# def start_log_session(ip,port,v_name):
#     global log_info

#     if  not logging_locked() :
#         rep_dat={}
#         ip_scanned= redis_handler.is_ip_scanned(ip)
#         current_time= time.time()
#         known_scanner= network_handler.is_known_scanner(ip)
#         log_info["known_scanner"]= known_scanner
#         log_info["Request_Type"]= "Association Requested"
#         log_info["ip"]= str(ip)
#         log_info["port"]=port
#         log_info["level"]="Warning"
#         set_session_id(str(int( current_time * 1000000)))
#         log_simplified_message()
#         if not ip_scanned:
#             redis_handler.add_scanned_ip(ip)
#             network_handler.get_reputation_data(rep_dat, ip, ip_scanned)
#             redis_handler.add_reutation_data(rep_dat)
#         set_lock(1)
#     else:
#         log_info["version"]=v_name


# def set_log_info(params):
#      global log_info
#      global session_id
#      for key , value in params.items():
#          log_info[key]= value


# def log_relaese_or_abort():
#     set_redis_log_data()
#     log_simplified_message()
#     set_lock(0)
#     set_session_id(0)
#     redis_handler.add_request_data(redis_data)
#     reset_log_object()


# def reset_log_object():
#     global log_info
#     log_info={
#         "lock":0,
#         "version_name":"N/A",
#         "session_id":0,
#         "Request_Type" : "N/A",
#         "query_level" : "N/A",
#         "term" : "N/A",
#         "identifier" : "N/A",
#         "level" : "N/A",
#         "version" : "N/A",
#         "ip" : "N/A",
#         "port" : "N/A",
#         "matches" : "N/A",
#         "status":"N/A"
#         }


# def set_redis_log_data():
#     global redis_data
#     global log_info
#     current_time= time.time()
#     redis_data["matches"]=log_info["matches"]
#     redis_data["Request_parameters"]=log_info["term"]
#     redis_data["QueryRetrieveLevel"] = log_info["query_level"]
#     redis_data["Known_scanner"]= log_info["known_scanner"]
#     redis_data["timestamp"]=  str(current_time)
#     redis_data["id"]= log_info["session_id"]
#     redis_data["ip"]=log_info["ip"]
#     redis_data["port"]=str(log_info["port"])
#     redis_data["Request_Type"]= log_info["Request_Type"]
#     log_info["Request_Type"]="N/A"
#     log_info["query_level"]="N/A"
#     log_info["term"]="N/A"
#     log_info["matches"]="N/A"


# def set_lock(value):
#     global log_info
#     log_info["lock"] = value

# def logging_locked():
#     global log_info
#     return log_info["lock"] == 1

# def set_session_id(s_id):
#     global log_info
#     log_info["session_id"]=s_id

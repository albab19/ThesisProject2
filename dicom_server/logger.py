from logging.handlers import TimedRotatingFileHandler
import logging,os,json
from datetime import datetime
Docker_ENV = os.getenv('Docker_ENV', 'False')


def setup_logger(name, log_file, level=logging.INFO, when="midnight", interval=1):
    
    handler = TimedRotatingFileHandler(log_file, when=when, interval=interval)
    handler.suffix = "%Y%m%d"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger



if Docker_ENV == "True":
    log_directory = './app/'
    simplified_log_directory = './app/'
else:
    log_directory = '../flask_logging_server/'
    simplified_log_directory = '../flask_logging_server/'
try:
    log_file_path = os.path.join(log_directory, 'dicom_server.log')
    simplified_log_file_path = os.path.join(simplified_log_directory, 'dicom_simplified.log')
    exception_log_file_path = os.path.join(log_directory, 'exception.log')
    #detailed_logger = setup_logger('detailed_logger', log_file_path, logging.DEBUG)
    simplified_logger = setup_logger('simplified_logger', simplified_log_file_path)
    exception_logger = setup_logger('exception_logger', exception_log_file_path, logging.ERROR)

except Exception as e:
    print(e)
        
  
        
def log_simplified_message(assoc_id,request_type,query_level,term,identifier,level,version,ip,port,matches):
    message= {
                "ID": assoc_id,
                "Term": term,
                "Command": request_type,
                "level": level,
                "QueryRetrieveLevel": query_level,
                "identifier": identifier,
                "timestamp": datetime.now().isoformat(),
                "Matches":matches
                }
    if request_type=="Association Requested" or request_type == "Association Released":
        message["Version"]=version
        message["IP"]=ip
        message["Port"]=port
    try:
        json_message = json.dumps(message)
        simplified_logger.info(json_message)
    except (TypeError, ValueError) as e:
        exception_logger.error(f"Failed to log simplified message: {message} - {e}")
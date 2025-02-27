""" This module defines configuration constants and paths for the server service.
    Many values can be overridden via environment variables 
    
    TCIA Serviceconstants: 
    ---------------------
    * TCIA_USER_NAME
    * TCIA_ACTIVATED
    * TCIA_PASSWORD
    * TCIA_PERIOD_UNIT
    * TCIA_PERIOD
    * TCIA_FILES_DIRECTORY
    * MODALITIES
    * MINIMUM_TCIA_FILES_IN_SERIE
    * MAXIMUM_TCIA_FILES_IN_SERIE
    * TCIA_STUDIES_PER_MODALITY
    
    Logging Server: 
    ---------------------
    * FLASK_ACTIVATED (Important to avoid logging on test environment)
    * MAIN_LOG_DIRECTORY
    * SIMPLIFIED_LOG_DIRECTORY
    * EXCEPTIONS_LOG_DIRECTORY
    
    Integrity Check: 
    ---------------------
    * INTEGRITY_CHECK
    * HASH_STORAGE_PATH
    
    Threat Intelligence:
    ---------------------
    * ABUSE_IP_API_KEY
    * IP_QUALITY_SCORE_API_KEY
    * VIRUS_TOTAL_API_KEY
    
    Blackhole:
    ---------------------
    * BLOCK_SCANNERS
    * BLACKHOLE_FILE_PATH
    
    DICOM server:
    ---------------------
    * PROD (environment will be production if this constant is true and development if it is false)
    * DICOM_STORAGE_DIR
    * C_STORE_STORAGE
    * DICOM_PORT
    * DICOM_SERVER_HOST
    * REDIS_HOST
    * DICOM_DATABASE
    * CANARY_PDF_PATH
    
    """

import os, json

TRUE_LIST = ["true", "1", "t", "yes"]
"""Envirnoment"""
PROD = os.getenv("PROD", "False").lower() in TRUE_LIST

"""Flask server status"""
FLASK_ACTIVATED = os.getenv("FLASK_ACTIVATED", "True").lower() in TRUE_LIST

"""Null routing the incomming requests if belong a known mass scanner """
BLOCK_SCANNERS = os.getenv("BLOCK_SCANNERS", "False").lower() in TRUE_LIST

"""Blackhole list file"""
BLACKHOLE_FILE_PATH = os.getenv("BLACKHOLE_FILE_PATH", "./storage/blackhole_list.txt")

"""DICOM files storage"""

DICOM_STORAGE_DIR = "./storage/dicom_storage"

"""DICOM files recieved through the server storage"""

C_STORE_STORAGE = "./storage/c_store_files"

"""DICOM server port configuration"""
DICOM_PORT = 11112

"""DICOM server host ip configuration"""

DICOM_SERVER_HOST = "localhost" if not PROD else "172.29.0.3"


"""Redis host configuration"""
REDIS_HOST = "localhost" if not PROD else os.getenv("REDIS_HOST", "172.29.0.4")

"""Logs directories"""
MAIN_LOG_DIRECTORY, SIMPLIFIED_LOG_DIRECTORY, EXCEPTIONS_LOG_DIRECTORY = (
    ("/app/logs/pynetdicom", "/app/logs/simplified", "/app/logs/exceptions")
    if PROD
    else (
        "../flask_logging_server/logs/pynetdicom",
        "../flask_logging_server/logs/simplified",
        "../flask_logging_server/logs/exceptions",
    )
)

"""The sqlite file path"""
DICOM_DATABASE = "/app/db.db" if PROD else "./storage/db.db"

"""TCIA username and password to use it in API calls"""
TCIA_USER_NAME = os.getenv("TCIA_USER_NAME", "Nawras")
TCIA_PASSWORD = os.getenv("TCIA_PASSWORD", "mrmr@gmail.com")

"""Time unit to schedule tcia files retrieval"""
TCIA_PERIOD_UNIT = os.getenv("TCIA_PERIOD_UNIT", "minutes")


"""Default update dicom files from tcia API each 1 week"""
TCIA_PERIOD = int(os.getenv("TCIA_PERIOD", 10))

"""The path where TCIA dicom files save on retrieval"""
TCIA_FILES_DIRECTORY = "./tcia_data"
"""Files stagger directory"""
TCIA_FILES_STAGGER_DIRECTORY = "./storage/stagger"
""" API key Abuseipdb """
ABUSE_IP_API_KEY = os.getenv(
    "ABUSE_IP_API_KEY",
    "95c2c4b357f46e9fb9ce626d06295c1002454709007a43ed5ea49de785a7e3bb0db670e44bb10875",
)

""" API key Abuseipdb """
IP_QUALITY_SCORE_API_KEY = os.getenv(
    "IP_QUALITY_SCORE_API_KEY",
    "JyGDPZk1kg5Y6Cqqiagx4y1YBkDmJ7tP",
)

""" API key Virus Total """
VIRUS_TOTAL_API_KEY = os.getenv(
    "VIRUS_TOTAL_API_KEY",
    "715bccfb503dc801d1fdc5f095bb3c0c2a4412a7b81cca1a2f5c15e14361f1fa",
)

"""Canary pdf path"""
CANARY_PDF_PATH = "./storage/can.pdf"


"""TCIA activated"""
TCIA_ACTIVATED = os.getenv("TCIA_ACTIVATED", "True").lower() in TRUE_LIST


""" Modalities of the studies should be retrieved from TCIA """
MODALITIES = json.loads(os.getenv("MODALITIES", '["CT", "MR", "US", "DX"]'))

"""Minimum number of files in each serie retrieved from The Cancer Imaging Archeive API"""
MINIMUM_TCIA_FILES_IN_SERIE = int(os.getenv("MINIMUM_TCIA_FILES_IN_SERIE", 1))

"""Maximum number of files in each serie retrieved from The Cancer Imaging Archeive API"""

MAXIMUM_TCIA_FILES_IN_SERIE = int(os.getenv("MAXIMUM_TCIA_FILES_IN_SERIE", 3))

"""Number of studies for each modality from TCIA"""
TCIA_STUDIES_PER_MODALITY = int(os.getenv("TCIA_STUDIES_PER_MODALITY", 10))

"""Honeytoken URL"""
WEB_HOOK_HONEY_TOKEN_URL = (
    "https://webhook.site/#!/view/b4a77406-3736-4637-a11d-293cc00decee"
)

"""Activate DICOM files integrity checks every 6 hours"""
INTEGRITY_CHECK = os.getenv("INTEGRITY_CHECK", "True").lower() in TRUE_LIST

"""Integrity checker file storage path"""
HASH_STORAGE_PATH = "./storage/hash_store.json"

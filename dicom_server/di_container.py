"""
This module defines the ApplicationContext class using the Dependency Injector library to manage dependencies throughout the start of the application.

The ApplicationContext class serves as a central configuration hub for all services on the server

The design of the server followed a components-based architecture to make the product reusable, testable, and maintainable
"""

"""
The setup includes adding the following providers:
 
 data-access agents:
 
    - dicom_db: Manages the DICOM database service, responsible for storing/retrieving dicom files information maintained at the storage block.
    
    - redis_handler: Implements a redis service responsible for storing of dicom sessions information, provides rapid access for external analysis/visualization middleware.

 TCIA providers:
 
    - tcia_api: Responsible for handling communication between the application and The Cancer Imaging Archive API.
    
    - tcia_manager: Handles file exchange by removing old files, organizing new ones, injectting new files with honeytokens and initializing the database. 
    
    - tcia_scheduler: Schedules the retrieval of new DICOM files on a periodic basis.
    
 Threat Intelligence:
 
    - threat_intelligence provider: provides IP information from three Threat Intelligence services (AbuseIPdatabase, IPQualityScore, and VirusTotal).
 
 Files Integrity Checker:
    - files_checker: compares the hashes of the dicom files stored at the dicom storage every seven hours to verify their content, detecting any unauthorized access attemp.
 
 Network Management:
 
    - blackhole: responsible for null routing the requests with IP addresses that belong to one of the known mass-scanners mitigitating the potential of the heneypot been identified as a honeypot in the future

    - session_collector: collects and manages data from dicom sessions in order to ensure consistency in data analysis and visualization 
 
 DICOM Services:
 
    - dicom_handler: implements the standard dicom operations, acting as a SCP (Service Provider) on C-Echo and C-Store first part of C-Get, C-Find and C-Move (receiving and responding to requests) operations
        and as a SCU (Serive User) for the second part of C-Get, C-Find and C-Move (initiating requests) operations
 
    - dicom_application: handles the configuration, initialization of the DICOM application entity and starts the DICOM server.


"""


from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis
import config
from loggers import Loggers
from dicomdb import DicomDatabase
from redis_handler import RedisClient
from integrity_checker import FilesChecker
from dicom_session_manager import SessionCollector
from dicom_handlers import DICOMHandlers
from dicom_application import DicomStarter
from threat_intelligence_handler import ThreatIntelligence
from tcia_management import TCIAAPI
from tcia_management import TCIAManager
from tcia_management import TCIAScheduler
from network_manager import Blackhole
import logging


class ApplicationContext(containers.DeclarativeContainer):
    # Loggers service
    loggers = providers.Factory(
        Loggers,
        config.MAIN_LOG_DIRECTORY,
        config.SIMPLIFIED_LOG_DIRECTORY,
        config.EXCEPTIONS_LOG_DIRECTORY,
    )

    if config.FLASK_ACTIVATED:
        loggers()

    exceptions_logger = providers.Singleton(logging.getLogger, "exceptions")
    simplified_logger = providers.Singleton(logging.getLogger, "simplified_logger")

    # DICOM database session configuration
    engine = providers.Singleton(create_engine, f"sqlite:///{config.DICOM_DATABASE}")
    session_factory = providers.Singleton(sessionmaker, bind=engine)
    session = providers.Singleton(lambda sf: sf(), session_factory)
    # DICOM_database provider
    dicom_db = providers.Singleton(
        DicomDatabase, exceptions_logger, config.DICOM_STORAGE_DIR, session
    )

    # Redis provider
    redis_client = providers.Singleton(redis.Redis, config.REDIS_HOST, 6379)
    redis_handler = providers.Singleton(RedisClient, exceptions_logger, redis_client)

    # TCIA providers

    tcia_api = providers.Factory(
        TCIAAPI,
        exceptions_logger,
        config.TCIA_USER_NAME,
        config.TCIA_PASSWORD,
        config.MINIMUM_TCIA_FILES_IN_SERIE,
        config.MAXIMUM_TCIA_FILES_IN_SERIE,
        config.MODALITIES,
        config.TCIA_STUDIES_PER_MODALITY,
    )
    tcia_manager = providers.Singleton(
        TCIAManager,
        exceptions_logger,
        config.DICOM_STORAGE_DIR,
        config.TCIA_FILES_DIRECTORY,
        config.CANARY_PDF_PATH,
        dicom_db,
        redis_handler,
        tcia_api,
    )

    tcia_scheduler = providers.Singleton(
        TCIAScheduler,
        exceptions_logger,
        config.TCIA_PERIOD,
        config.TCIA_PERIOD_UNIT,
        tcia_manager,
    )

    # IP Threat Intelligence provider
    threat_intelligence = providers.Singleton(
        ThreatIntelligence,
        exceptions_logger,
        config.ABUSE_IP_API_KEY,
        config.IP_QUALITY_SCORE_API_KEY,
        config.VIRUS_TOTAL_API_KEY,
    )

    # DICOM files integrity cheacker provider
    files_checker = providers.Singleton(
        FilesChecker,
        exceptions_logger,
        config.DICOM_STORAGE_DIR,
        config.HASH_STORAGE_PATH,
        redis_handler,
    )

    # Blackholee service provider
    blackhole = providers.Singleton(
        Blackhole, exceptions_logger, config.BLOCK_SCANNERS, config.BLACKHOLE_FILE_PATH
    )

    # A DICOM connection comprises multiple DICOM requests. A collector service provider is added to manage session information before logging.
    session_collector = providers.Singleton(
        SessionCollector,
        simplified_logger,
        exceptions_logger,
        redis_handler,
        threat_intelligence,
    )

    # The implementation of the standard handlers provided through
    dicom_handlers = providers.Singleton(
        DICOMHandlers, exceptions_logger, session_collector, dicom_db
    )

    # The DICOM application handles the application entity configuration
    dicom_application = providers.Singleton(
        DicomStarter,
        exceptions_logger,
        config.DEBUG_MODE,
        config.DICOM_PORT,
        config.DICOM_SERVER_HOST,
        dicom_handlers,
    )

    if config.TCIA_ACTIVATED:
        tcia_scheduler()

    if config.INTEGRITY_CHECK:
        files_checker()

    if config.BLOCK_SCANNERS:
        blackhole()

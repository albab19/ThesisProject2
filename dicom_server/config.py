import os
import logging
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelFind,
    Verification,
    StudyRootQueryRetrieveInformationModelMove,
    PatientRootQueryRetrieveInformationModelGet,
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelGet,
)
from pydicom.uid import CTImageStorage, JPEG2000
from pynetdicom import (
    AE,
    debug_logger,
    AllStoragePresentationContexts,
    StoragePresentationContexts,
)

DOCKER_ENV = os.getenv("Docker_ENV", "False")
BLOCK_SCANNERS = os.getenv("blackhole", "False")
DICOM_STORAGE_DIR = "./dicom_files/received"
DICOM_PORT = 11112
DICOM_SERVER_HOST = "localhost" if DOCKER_ENV == "False" else "172.29.0.3"
REDIS_HOST = "localhost" if DOCKER_ENV == "False" else "172.29.0.4"
LOG_DIRECTORY, SIMPLIFIED_LOG_DIRECTORY = (
    ("./app/", "./app/")
    if DOCKER_ENV == "True"
    else ("../flask_logging_server/", "../flask_logging_server/")
)
DICOM_DATABASE = (
    "/app/db.db" if os.getenv("Docker_ENV", "False") == "True" else "./../db.db"
)
MAIN_LOG_PATH = os.path.join(LOG_DIRECTORY, "dicom_server.log")


def blackhole_activated():
    return BLOCK_SCANNERS


def assign_runtime_contexts_support(assoc):
    for context in assoc.accepted_contexts:
        context._as_scp = True
        context._as_scu = True
        context.scu_role = True
        context.scp_role = True


def initialize_storage_contexts(StoragePresentationContexts):
    for context in StoragePresentationContexts:
        context._as_scp = True
        context._as_scu = True
        context.scp_role = True
        context.scu_role = True


def initialize_application_entity():
    try:
        ae = AE()
        ae.supported_contexts = AllStoragePresentationContexts
        ae.requested_contexts = StoragePresentationContexts
        ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)
        ae.add_supported_context(PatientRootQueryRetrieveInformationModelGet)
        ae.add_supported_context(StudyRootQueryRetrieveInformationModelGet)
        ae.add_supported_context(StudyRootQueryRetrieveInformationModelFind)
        ae.add_supported_context(StudyRootQueryRetrieveInformationModelMove)
        ae.add_supported_context(Verification)
        ae.add_supported_context(CTImageStorage, JPEG2000)

        initialize_storage_contexts(StoragePresentationContexts)
        return ae
    except Exception as e:
        print("Exception while initializing AE", e)


def initialize_logging():
    pynetdicom_logger = logging.getLogger("pynetdicom")
    handler = logging.FileHandler(MAIN_LOG_PATH)
    pynetdicom_logger.setLevel(logging.DEBUG)
    pynetdicom_logger.addHandler(handler)
    debug_logger()


def is_docker_envirnoment():
    return DOCKER_ENV

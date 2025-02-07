import socket
from pynetdicom import evt
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


class DicomStarter:
    def __init__(self, exceptions_logger, debug_mode, port, ip, handlers):
        self.port = port
        self.ip = ip
        self.debug_mode = debug_mode
        self.handlers = handlers
        self.exceptions_logger = exceptions_logger

    def register_dicom_handlers(self):
        handlers = [
            (evt.EVT_ACSE_RECV, self.handlers.handle_assoc),
            (evt.EVT_RELEASED, self.handlers.handle_release),
            (evt.EVT_C_FIND, self.handlers.handle_find),
            (evt.EVT_C_STORE, self.handlers.handle_store),
            (evt.EVT_C_ECHO, self.handlers.handle_echo),
            (evt.EVT_C_MOVE, self.handlers.handle_move),
            (evt.EVT_C_GET, self.handlers.handle_get),
            (evt.EVT_ABORTED, self.handlers.handle_abort),
        ]
        return handlers

    def start_the_application(self):
        if self.debug_mode:
            debug_logger()
        ae = self.initialize_application_entity()
        handlers = self.register_dicom_handlers()
        print("DICOM Server Started")
        if not self.is_port_in_use():
            ae.start_server(
                (self.ip, self.port),
                evt_handlers=handlers,
            )

    # Initializing the application entity object

    def initialize_application_entity(self):
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

            self.initialize_storage_contexts(StoragePresentationContexts)
            return ae
        except Exception as e:
            print("Exception while initializing AE", e)

    # Ensure the presentation context used when initializing the server can act as SCU to handle STORE operation

    def initialize_storage_contexts(self, StoragePresentationContexts):
        for context in StoragePresentationContexts:
            context._as_scp = True
            context._as_scu = True
            context.scp_role = True
            context.scu_role = True

    def is_port_in_use(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self.ip, self.port)) == 0

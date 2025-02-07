from datetime import datetime
from dependency_injector.wiring import inject
from services.redis_service import IRedisService
from services.dicom_session_service import ISessionCollector
from services.threat_intelligence_service import IThreatIntelligence
import json
import time
import utilities.dicom_util as dicom_util
from enums.dicom_session_keys import Sessionkeys as sk


class SessionCollector(ISessionCollector):
    @inject
    def __init__(
        self,
        simp_logger,
        exceptions_logger,
        redis_handler: IRedisService = None,
        threat_intelligence: IThreatIntelligence = None,
    ):

        self.session_info = {key.key: key.default for key in sk}
        self.redis_data = {}
        self.redis_handler = redis_handler or IRedisService()
        self.simp_logger = simp_logger
        self.exceptions_logger = exceptions_logger
        self.threat_intelligence = threat_intelligence

    def session_started(self, ip, port, v_name):
        try:
            if not self.session_locked():
                self.initialize_session_info(ip, port)
                self.get_session_requestor_reputation(ip)
                self.set_session_lock(1)
            else:
                self.session_info[sk.VERSION.key] = v_name
        except:
            self.exceptions_logger.exception("Exception while starting a DICOM session")

    def get_session_requestor_reputation(self, ip):
        rep_dat = {}
        ip_scanned = self.redis_handler.is_ip_scanned(ip)

        if not ip_scanned:
            self.redis_handler.add_scanned_ip(ip)
            rep_dat = self.threat_intelligence.get_reputation_data(ip, ip_scanned)
            self.redis_handler.add_reputation_data(rep_dat)

    def initialize_session_info(self, ip, port):
        current_time = time.time()
        known_scanner = dicom_util.is_known_scanner(ip)
        self.session_info[sk.KNOWN_SCANNER.key] = known_scanner
        self.session_info[sk.REQUEST_TYPE.key] = "Association Requested"
        self.session_info[sk.IP.key] = str(ip)
        self.session_info[sk.PORT.key] = port
        self.session_info[sk.LOG_LEVEL.key] = "Warning"
        self.set_session_id(str(int(current_time * 1000000)))
        self.collect_session_info({}, True)

    def collect_session_info(self, params, sub_process_finished=False):
        for key, value in params.items():
            self.session_info[key] = value
        if sub_process_finished:
            current_time = datetime.now()
            self.session_info[sk.TIMESTAMP.key] = str(current_time)
            self.simp_logger.info(self.session_info)

    def session_ended(self):
        self.set_session_lock(0)
        self.set_session_id(0)
        self.redis_handler.add_request_data(self.build_redis_object())
        self.reset_session()

    def reset_session(self):
        self.session_info = {key.key: key.default for key in sk}

    def build_redis_object(self):
        redis_object = self.session_info.copy()
        redis_object[sk.REQUEST_TYPE.key] = self.session_info[
            sk.SESSION_MAIN_OPERATION.key
        ]
        redis_object[sk.STATUS.key] = (
            "Finished"
            if self.session_info[sk.REQUEST_TYPE.key] == "Association released"
            else "Aborted"
        )

        return json.dumps(self.session_info)

    def set_session_lock(self, value):
        self.session_info[sk.LOCK.key] = value

    def session_locked(self):

        return self.session_info[sk.LOCK.key] == 1

    def set_session_id(self, s_id):
        self.session_info[sk.SESSION_ID.key] = s_id

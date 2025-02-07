import json
from services.redis_service import IRedisService


class RedisClient(IRedisService):

    def __init__(self, exceptions_logger, redis_client):

        self.redis_client = redis_client
        self.exceptions_logger = exceptions_logger

    def is_ip_scanned(self, ip):
        try:
            return ip.encode() in self.redis_client.lrange("scannedIPs", 0, -1)
        except Exception as e:
            print("Exception while checking IPs list", e)

    def add_scanned_ip(self, ip):
        try:
            self.redis_client.rpush("scannedIPs", ip)
        except Exception as e:
            print("Exception while adding a scanned IP to the scanned list", e)

    def add_reutation_data(self, rep_dat):
        try:
            self.redis_client.rpush("reputation", json.dumps(rep_dat))
        except Exception as e:
            print("Exception while pushing repution object", e)

    def add_request_data(self, redis_log_data):
        try:
            self.redis_client.rpush("requests", json.dumps(redis_log_data))
        except Exception as e:
            print("Exception while adding a request information to Redis", e)

    def get_TCI_existing_studies(
        self,
    ):
        try:
            return set(self.redis_client.lrange("TCIA_studies", 0, -1))
        except Exception as e:
            print("Exception while checking TCIA studies", e)

    def add_TCI_study(self, study_uid):
        try:
            self.redis_client.rpush("TCIA_studies", study_uid)
        except Exception as e:
            print("Exception while adding a TCIA studyInstanceUID", e)

    def add_injcted_file(self, patient_name, modality):
        try:
            self.redis_client.rpush(
                "injected_files",
                str({"patient_name": patient_name, "modality": modality}),
            )
        except Exception as e:
            print("Exception while adding injected file identifiers to redis", e)

    def get_honey_url(
        self,
    ):
        try:
            self.redis_client.get("webhook")
        except Exception as e:
            print("Exception while getting webhook key", e)

    def update_files_integrity_state(self, changed_files):
        try:
            self.redis_client.rpush("fileChange", json.dumps(changed_files))
        except Exception as e:
            print("Exception while adding integrity check identifier", e)

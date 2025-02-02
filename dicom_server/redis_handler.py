import config
import redis
import json

redis_client = redis.Redis(config.REDIS_HOST, 6379)


def is_ip_scanned(ip):
    return ip.encode() in redis_client.lrange("scannedIPs", 0, -1)


def add_scanned_ip(ip):
    redis_client.rpush("scannedIPs", ip)


def add_reutation_data(rep_dat):
    redis_client.rpush("reputation", json.dumps(rep_dat))


def add_request_data(redis_log_data):
    redis_client.rpush("requests", json.dumps(redis_log_data))
    pass


def get_TCI_existing_studies():
    return set(redis_client.lrange("TCIA_studies", 0, -1))


def add_TCI_study(study_uid):
    redis_client.rpush("TCIA_studies", study_uid)


def add_injcted_file(patient_name, modality):
    redis_client.rpush(
        "injected_files", str({"patient_name": patient_name, "modality": modality})
    )


def get_honey_url():
    redis_client.get("webhook")


def update_files_integrity_state(changed_files):
    redis_client.rpush("fileChange", json.dumps(changed_files))

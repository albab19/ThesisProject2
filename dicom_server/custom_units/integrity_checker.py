import os, hashlib, threading, json, schedule, time
from dependency_injector.wiring import inject
from services.redis_service import IRedisService
from services.integrity_checker_service import IIntegrityChecker


class FilesChecker(threading.Thread, IIntegrityChecker):
    @inject
    def __init__(
        self,
        exceptions_logger,
        storage_directory,
        hash_store_path,
        redis_handler: IRedisService = None,
    ):

        super().__init__(daemon=True)
        self.storage_directory = storage_directory
        self.hash_store_path = hash_store_path
        # self.event= event
        self.redis_handler = redis_handler or IRedisService()
        self.start()
        self.exceptions_logger = exceptions_logger

    def run(self):
        try:
            schedule.every(6).hours.do(self.check_hashes)
            print("Checking files integrity each 6 hours")
        except Exception:
            self.exceptions_logger.exception(
                "Unable to schedule files integrity cheack"
            )
        while True:
            schedule.run_pending()
            time.sleep(10300)

    def hash_file(self, filename):
        hash_sha256 = hashlib.sha256()
        try:
            with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
        except Exception:
            self.exceptions_logger.exception(
                f"Exception while generating hash value for file {filename}"
            )
            return None
        return hash_sha256.hexdigest()

    def check_hashes(self):

        print("Checking files integrity")
        new_hashes = {}
        changed_files = []
        try:
            with open(self.hash_store_path, "r") as f:
                old_hashes = json.load(f)
        except FileNotFoundError:
            old_hashes = {}

        for path in os.listdir(self.storage_directory):
            full_path = os.path.join(self.storage_directory, path)
            try:
                file_hash = self.hash_file(full_path)
                if file_hash:
                    new_hashes[path] = file_hash
                    if path in old_hashes and old_hashes[path] != file_hash:
                        changed_files.append(path)

            except Exception:
                self.exceptions_logger.exception(
                    f"Exception while proccessing hashes in {full_path}"
                )
                pass

        with open(self.hash_store_path, "w") as f:
            json.dump(new_hashes, f)

        if changed_files:
            try:
                self.redis_handler.update_files_integrity_state(changed_files)
            except Exception:
                self.exceptions_logger.exception(
                    "Exception while populating file integrity checks to Redis"
                )
            print("Changed files:", changed_files)
        else:

            print("No changes detected.")

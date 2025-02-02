import os, hashlib, threading, json, schedule, time,redis_handler


class hash_checker(threading.Thread):

    def __init__(self, storage_directory,hash_store_path):
            super().__init__(daemon=True)
            self.storage_directory = storage_directory
            self.hash_store_path= hash_store_path
            #self.event= event
            print("Checking files integrity each 6 hours")

      
    def run(self):
        
        #self.event.wait()
        #schedule.every(3).seconds.do(self.check_hashes)
        schedule.every(6).hours.do(self.check_hashes)
        #self.event.clear()
        while True:
            # if not self.event.is_set():  
            schedule.run_pending()
            time.sleep(10300)

        

    def hash_file(self,filename):
        hash_sha256 = hashlib.sha256()
        try:
            with open(filename, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
        except Exception as e:
            return None
        return hash_sha256.hexdigest()

    def check_hashes(self):
        
        print("Checking files integrity")
        new_hashes = {}
        changed_files = []
        try:
            with open(self.hash_store_path, 'r') as f:
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
        
            except Exception as e:
                print(f"Error processing {path}: {e}")
                pass
        
        
        with open(self.hash_store_path, 'w') as f:
            json.dump(new_hashes, f)

        if changed_files:
            redis_handler.update_files_integrity_state(changed_files)
            
            print("Changed files:", changed_files)
        else:
            
            print("No changes detected.")


    

import threading, pydicom
import schedule, requests
import os
import json
import zipfile
import io
from pydicom import dcmread
from faker import Faker
import random, shutil
from datetime import datetime
from datetime import datetime, timedelta
import redis_handler


class tcia_management(threading.Thread):

    def __init__(self, storage_directory, week, dicomdb):
        super().__init__(daemon=True)
        self.username = os.getenv("tcia_username", "Nawras")
        self.password = os.getenv("tcia_password", "mrmr@gmail.com")
        self.week = week
        self.fake = Faker("da_DK")
        self.dicomdb = dicomdb
        self.storage_directory = storage_directory
        self.tcia_dir = "./tcia_data"
        print("TCIA retrieving schedule is started")

    def get_access_token(self):
        try:
            res = requests.post(
                "https://services.cancerimagingarchive.net/nbia-api/oauth/token",
                data={
                    "username": self.username,
                    "password": self.password,
                    "client_id": "NBIA",
                    "grant_type": "password",
                },
            )
            json_object = json.loads(res.content)
            return [json_object["access_token"], json_object["refresh_token"]]
        except Exception as e:
            print("Access token retrieval failed:", e)

    def refresh_access_token(self):
        try:
            requests.post(
                "https://services.cancerimagingarchive.net/nbia-api/oauth/token",
                data={
                    "refresh_token": self.refresh_token,
                    "client_id": "nbia",
                    "grant_type": "refresh_token",
                },
            )
        except Exception as e:
            print("Token refresh failed:", e)

    def delete_old_files(self):
        try:
            for file in os.listdir(self.storage_directory):
                os.remove(os.path.join(self.storage_directory, file))
        except Exception as e:
            print("Old files deletion failed:", e)

    def change_dicom_files(self):
        print("Scheduled change of dicom files started")
        try:
            self.access_token = self.get_access_token()[0]
            self.delete_old_files()
            self.delete_temps()
            self.get_new_files()
            self.organize_downloaded_files()
            self.dicomdb.initialize_database()
        except Exception as e:
            print("Dicom files scheduled retrieve failed:", e)

    def get_new_files(self):
        try:
            existing_studies = redis_handler.get_TCI_existing_studies()
            modalities = ["CT", "MR", "US", "DX"]
            _json = {}
            for mod in modalities:
                metadata = {}
                try:
                    res = requests.get(
                        "https://services.cancerimagingarchive.net/nbia-api/services/v1/getSeries",
                        params={f"Modality": {mod}},
                    )
                    _json = json.loads(res.content)
                except Exception as e:
                    print("Series retrieval failed:", e)
                    pass
                if _json:
                    a = 0
                    for entry in _json:
                        modality = entry["Modality"]
                        study_uid = entry["StudyInstanceUID"]
                        series_uid = entry["SeriesInstanceUID"]
                        image_count = int(entry["ImageCount"])

                        if (
                            os.getenv("minimum_file_por_serie", 1)
                            <= image_count
                            <= os.getenv("maximum_file_serie", 3)
                        ):
                            if (
                                study_uid.encode() not in existing_studies
                                and a <= os.getenv("Number_studies_modality", 9)
                            ):
                                if study_uid not in metadata:
                                    a += 1
                                    metadata[study_uid] = []
                                metadata[study_uid].append(
                                    {"se_uid": series_uid, "modality": modality}
                                )
                            else:
                                pass

                    for st_uid, se_uids in metadata.items():
                        for se_uid_dict in se_uids:
                            se_uid = se_uid_dict["se_uid"]
                            mod = se_uid_dict["modality"]
                            response = requests.get(
                                f"https://services.cancerimagingarchive.net/nbia-api/services/v2/getImage?SeriesInstanceUID={se_uid}",
                                headers={
                                    "Authorization": f"Bearer {self.access_token}"
                                },
                            )
                            response.raise_for_status()

                            with zipfile.ZipFile(
                                io.BytesIO(response.content)
                            ) as the_zip:
                                the_zip.extractall(
                                    path=f"{self.tcia_dir}/{mod}/{st_uid}/{se_uid}/"
                                )
            metadata = {}
        except Exception as e:
            print("New files retrieval failed:", e)
            pass

    def organize_downloaded_files(self):
        directory = os.path.join(self.storage_directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
        files_counter = 0
        for modality in os.listdir(self.tcia_dir):
            for study_uid in os.listdir(os.path.join(self.tcia_dir, modality)):
                try:
                    redis_handler.add_TCI_study(study_uid)
                except Exception as e:
                    print("Study addition failed:", e)
                    pass
                study_files_counter = 0
                (
                    patient_name,
                    patient_id,
                    patient_sex,
                    birth_date,
                    study_id,
                    study_date,
                    accession_number,
                ) = self.generate_patient_info()
                institution = self.get_random_institution()
                for se_uid in os.listdir(
                    os.path.join(self.tcia_dir, modality, study_uid)
                ):
                    for file in os.listdir(
                        os.path.join(self.tcia_dir, modality, study_uid, se_uid)
                    ):
                        if file != "LICENSE":
                            study_files_counter += 1
                            files_counter += 1
                            dataset = dcmread(
                                os.path.join(
                                    self.tcia_dir, modality, study_uid, se_uid, file
                                )
                            )
                            dataset.StudyInstanceUID = study_uid
                            dataset.InstitutionName = institution
                            dataset.SeriesInstanceUID = se_uid
                            dataset.PatientName = patient_name
                            dataset.PatientID = patient_id
                            dataset.PatientSex = patient_sex
                            dataset.PatientBirthDate = birth_date
                            dataset.StudyID = study_id
                            dataset.AccessionNumber = accession_number
                            dataset.StudyDate = study_date
                            dataset.SeriesDate = study_date
                            if (
                                files_counter == 4
                                or files_counter == 12
                                or files_counter == 18
                                or files_counter == 24
                            ):
                                dataset.SOPClassUID = pydicom.uid.EncapsulatedPDFStorage
                                dataset.MIMETypeOfEncapsulatedDocument = (
                                    "application/pdf"
                                )
                                dataset.RetrieveURL = str(redis_handler.get_honey_url())
                                dataset.EncapsulatedDocument = self.get_canary_token()
                                redis_handler.add_injcted_file(patient_name, modality)

                            filename = (
                                f"{modality}_{patient_name}_{study_files_counter}.dcm"
                            )
                            filepath = os.path.join(directory, filename)
                            try:
                                dataset.save_as(filepath)
                            except Exception as e:
                                print("File save failed:", e)

    def delete_temps(self):
        if os.path.isdir("./tcia_data"):
            try:
                shutil.rmtree(self.tcia_dir)
            except Exception as e:
                print("Temp deletion failed:", e)

    def get_canary_token(self):
        pdf_path = "./dicom_files/can.pdf"
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
                return pdf_data
        except Exception as e:
            print("Canary token retrieval failed:", e)

    def get_random_institution(self):
        medical_institutions = [
            "Københavns Sundhedscenter",
            "Aarhus Kliniken",
            "Odense Patienthus",
            "Nordjylland Med Institut",
        ]

        return random.choice(medical_institutions)

    def generate_patient_info(self):
        name = ""
        sex = ""

        if random.choice([True, False]):
            name = self.fake.first_name_male() + " " + self.fake.last_name_male()
            sex = "M"
        else:
            name = self.fake.first_name_female() + " " + self.fake.last_name_female()
            sex = "F"

        start_birth_date = datetime(1955, 12, 10)
        end_birth_date = datetime(1999, 12, 1)
        random_birth_date = start_birth_date + timedelta(
            days=random.randint(0, (end_birth_date - start_birth_date).days)
        )
        formatted_birth_date = random_birth_date.strftime("%Y%m%d")

        start_study_date = datetime(2010, 12, 10)
        end_study_date = datetime(2024, 12, 1)
        random_study_date = start_study_date + timedelta(
            days=random.randint(0, (end_study_date - start_study_date).days)
        )
        formatted_study_date = random_study_date.strftime("%Y%m%d")

        return (
            name,
            str(random.randint(10, 7400)),
            sex,
            formatted_birth_date,
            str(random.randint(35241, 567331169)),
            formatted_study_date,
            str(random.randint(3528941, 5673331169)),
        )

    def run(self):
        schedule.every(1).weeks.do(self.change_dicom_files)

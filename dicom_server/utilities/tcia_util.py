import random
import os
from datetime import datetime, timedelta
import logging
import zipfile
import io
from faker import Faker
import random
from pydicom import dcmread
import shutil


fake = Faker("da_DK")

exceptions_logger = logging.getLogger("exceptions")


def generate_patient_info():
    try:
        name = ""
        sex = ""

        if random.choice([True, False]):
            name = fake.first_name_male() + " " + fake.last_name_male()
            sex = "M"
        else:
            name = fake.first_name_female() + " " + fake.last_name_female()
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
    except Exception:
        exceptions_logger.exception("Exception while generating random patient data")
    return (
        name,
        str(random.randint(10, 7400)),
        sex,
        formatted_birth_date,
        str(random.randint(35241, 567331169)),
        formatted_study_date,
        str(random.randint(3528941, 5673331169)),
    )


def delete_old_files(storage_directory):
    try:
        for file in os.listdir(storage_directory):
            os.remove(os.path.join(storage_directory, file))
    except Exception:
        exceptions_logger.exception("Old files deletion failed:")


def delete_temps(tcia_dir):
    if os.path.isdir(tcia_dir):
        try:
            shutil.rmtree(tcia_dir)
        except Exception:
            exceptions_logger.exception("Temp deletion failed:")


def filter_retrieved_studies(
    existing_studies,
    _json,
    study_counter,
    number_of_studies_in_each_retrieved_modality,
    minimum_files,
    maximum_files,
):
    metadata = {}
    for entry in _json:
        modality = entry["Modality"]
        study_uid = entry["StudyInstanceUID"]
        series_uid = entry["SeriesInstanceUID"]
        image_count = int(entry["ImageCount"])

        if satisfies_series_count_per_study(image_count, minimum_files, maximum_files):
            if never_downloaded_study(
                existing_studies, study_counter, study_uid
            ) and studies_count_satisfied(
                study_counter, number_of_studies_in_each_retrieved_modality
            ):
                if is_valid_study(metadata, study_uid):
                    study_counter += 1
                    metadata[study_uid] = []
                metadata[study_uid].append({"se_uid": series_uid, "modality": modality})
    return metadata


def extract_and_save_zip_data(mod, st_uid, se_uid, response, tcia_dir):
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        zip_file.extractall(path=f"{tcia_dir}/{mod}/{st_uid}/{se_uid}/")


def is_valid_study(metadata, study_uid):
    return study_uid not in metadata


def never_downloaded_study(existing_studies, study_uid):
    return study_uid.encode() not in existing_studies


def studies_count_satisfied(
    study_counter, number_of_studies_in_each_retrieved_modality
):
    return study_counter < number_of_studies_in_each_retrieved_modality


def satisfies_series_count_per_study(image_count, minimum_files, maximum_files):
    return minimum_files <= image_count <= maximum_files


def get_random_institution():
    medical_institutions = [
        "Københavns Sundhedscenter",
        "Aarhus Kliniken",
        "Odense Patienthus",
        "Nordjylland Med Institut",
    ]

    return random.choice(medical_institutions)


def store_retrieved_file(
    self, directory, modality, study_files_counter, patient_name, dataset
):
    filename = f"{modality}_{patient_name}_{study_files_counter}.dcm"
    filepath = os.path.join(directory, filename)
    try:
        dataset.save_as(filepath)
    except Exception:
        self.exceptions_logger.exception("File save failed:")


def get_series_per_study(modality, study_uid, se_uid, tcia_dir):
    return os.listdir(os.path.join(tcia_dir, modality, study_uid, se_uid))


def get_downloaded_studies_per_modality(modality, study_uid, tcia_dir):
    return os.listdir(os.path.join(tcia_dir, modality, study_uid))


def build_file_dataset(
    self,
    modality,
    study_uid,
    patient_name,
    patient_id,
    patient_sex,
    birth_date,
    study_id,
    study_date,
    accession_number,
    institution,
    se_uid,
    file,
    tcia_dir,
):
    dataset = dcmread(os.path.join(tcia_dir, modality, study_uid, se_uid, file))
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
    return dataset


def get_downloaded_modalitis(tcia_dir):
    return os.listdir(tcia_dir)


def get_studies_from_modality(modality, tcia_dir):
    return os.listdir(os.path.join(tcia_dir, modality))


def initialize_dicom_directory_if_not_exist(storage_directory):
    directory = os.path.join(storage_directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def is_licience_file(file):
    return file == "LICENSE"

import os, traceback
from pydicom import dcmread
from sqlalchemy import create_engine, String, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pynetdicom.apps.qrscp import db
from sqlalchemy import cast, String
import config
from contextlib import contextmanager

storagedirectory = config.DICOM_STORAGE_DIR
database_file = config.DICOM_DATABASE
Base = declarative_base()
engine = create_engine(f"sqlite:///{database_file}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@contextmanager
def session_scope():
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Session rollback due to exception: {e}")
        raise


def initialize_database():
    try:
        print("FromTest", database_file)
        delete_database()
        fill_database_tables_from_dicom_files()
        print("Database initialized from DICOM storage")
    except Exception as e:
        print("Exception while initializing the database from dicom files", e)
        pass


def fill_database_tables_from_dicom_files():
    with session_scope() as session:
        try:
            for path in os.listdir(storagedirectory):
                instance = dcmread(os.path.join(storagedirectory, path))
                db.add_instance(instance, session, path)
            session.commit()
        except Exception as e:
            session.rollback()
            print("Exception while filling database", e)


def delete_database():
    with session_scope() as session:
        try:
            delete_statement = delete(db.Instance)
            session.execute(delete_statement)
            session.commit()
            print("Database cleared")
        except Exception as e:
            session.rollback()
            print("Exception clearing database", e)


def query_all_studies():
    try:
        with session_scope() as session:
            studyQuery = session.query(db.Study)
            all_studies = studyQuery.all()
            print("Alll", database_file)
            return all_studies
    except Exception as e:
        print("Exception querying all studies", e)


def query_all_series():
    try:
        with session_scope() as session:
            studyQuery = session.query(db.Series)
            all_studies = studyQuery.all()
            session.commit()
            return all_studies
    except Exception as e:
        print("Exception querying all series", e)


def query_all_patients():
    try:
        with session_scope() as session:
            studyQuery = session.query(db.Patient)
            all_patients = studyQuery.all()
            return all_patients
    except Exception as e:
        print("Exception querying all patients", e)


def query_study_level(identifier):
    with session_scope() as session:
        try:
            matchedInstances = db.search(
                "1.2.840.10008.5.1.4.1.2.2.1", identifier, session
            )
            uniqueStudies = get_uniqueStudies(matchedInstances)
            studyQuery = session.query(db.Study)
            studyQuery = studyQuery.filter(
                db.Study.study_instance_uid.in_(uniqueStudies)
            )
            matches = studyQuery.all()
            return matches
        except Exception as e:
            print(e)
            pass


def query_series_level(identifier):
    with session_scope() as session:
        try:
            matchedInstances = db.search(
                "1.2.840.10008.5.1.4.1.2.2.1", identifier, session
            )
            uniqueSeries = get_uniqueSeries(matchedInstances, identifier)
            seriesQuery = session.query(db.Series)
            seriesQuery = seriesQuery.filter(
                db.Series.series_instance_uid.in_(uniqueSeries)
            )
            matches = seriesQuery.all()
            return matches
        except Exception:
            traceback.print_exc()
            pass


def query_patient_level(identifier):
    with session_scope() as session:
        try:
            matchedInstances = db.search(
                "1.2.840.10008.5.1.4.1.2.1.1", identifier, session
            )
            uniquePatients = get_unique_patients(matchedInstances)
            patientQuery = session.query(db.Patient)
            patientQuery = patientQuery.filter(
                db.Patient.patient_id.in_(uniquePatients)
            )
            matches = patientQuery.all()
            return matches
        except Exception:
            traceback.print_exc()
            pass


def get_response_data(identifier, instance, response_dataset):

    if identifier.QueryRetrieveLevel == "STUDY":
        get_studyRoot_dataset(instance, response_dataset)
    elif identifier.QueryRetrieveLevel == "SERIES":
        get_seriesRoot_dataset(identifier, instance, response_dataset)
    elif identifier.QueryRetrieveLevel == "PATIENT":
        get_patientRoot_dataset(identifier, instance, response_dataset)


def get_patientRoot_dataset(identifier, instance, response_dataset):

    response_dataset.PatientID = getattr(instance, "patient_id")
    response_dataset.PatientName = getattr(instance, "patient_name")


def get_seriesRoot_dataset(identifier, instance, response_dataset):
    if len(identifier) == 1:
        response_dataset.Modality = get_other_levels_tags(
            "STUDY", "modality", getattr(instance, "study_instance_uid")
        )
        response_dataset.SeriesInstanceUID = get_other_levels_tags(
            "STUDY", "series_instance_uid", getattr(instance, "study_instance_uid")
        )
        response_dataset.SeriesNumber = get_other_levels_tags(
            "STUDY", "series_number", getattr(instance, "study_instance_uid")
        )
    else:
        response_dataset.Modality = getattr(instance, "modality")
        response_dataset.SeriesInstanceUID = getattr(instance, "series_instance_uid")
        response_dataset.SeriesNumber = getattr(instance, "series_number")
    response_dataset.PatientName = get_other_levels_tags(
        "SERIES", "patient_name", getattr(instance, "series_instance_uid")
    )
    response_dataset.PatientID = get_other_levels_tags(
        "SERIES", "patient_id", getattr(instance, "series_instance_uid")
    )
    response_dataset.NumberOfSeriesRelatedInstances = get_other_levels_tags(
        "SERIES",
        "NumberOfSeriesRelatedInstances",
        getattr(instance, "series_instance_uid"),
    )


# def get_studyRoot_dataset(instance, response_dataset):
#     response_dataset.StudyInstanceUID = getattr(instance, "study_instance_uid")
#     response_dataset.StudyDate = getattr(instance, "study_date")
#     response_dataset.StudyTime = getattr(instance, "study_time")
#     response_dataset.AccessionNumber = getattr(instance, "accession_number")
#     response_dataset.StudyID = getattr(instance, "study_id")
#     response_dataset.InstitutionName = get_other_levels_tags(
#         "STUDY", "institution_name", getattr(instance, "study_instance_uid")
#     )
#     response_dataset.PatientBirthDate = get_other_levels_tags(
#         "STUDY", "birth_date", getattr(instance, "study_instance_uid")
#     )
#     response_dataset.PatientSex = get_other_levels_tags(
#         "STUDY", "patient_sex", getattr(instance, "study_instance_uid")
#     )
#     response_dataset.PatientName = get_other_levels_tags(
#         "STUDY", "patient_name", getattr(instance, "study_instance_uid")
#     )
#     response_dataset.PatientID = get_other_levels_tags(
#         "STUDY", "patient_id", getattr(instance, "study_instance_uid")
#     )
#     response_dataset.NumberOfStudyRelatedInstances = get_other_levels_tags(
#         "STUDY",
#         "NumberOfStudyRelatedInstances",
#         getattr(instance, "study_instance_uid"),
#     )
#     response_dataset.ModalitiesInStudy = get_other_levels_tags(
#         "STUDY", "modality", getattr(instance, "study_instance_uid")
#     )


def get_studyRoot_dataset(instance, response_dataset):
    # tags from the instance
    direct_attributes = {
        "StudyInstanceUID": "study_instance_uid",
        "StudyDate": "study_date",
        "StudyTime": "study_time",
        "AccessionNumber": "accession_number",
        "StudyID": "study_id",
    }

    # require tags from other levels
    other_level_attributes = {
        "InstitutionName": "institution_name",
        "PatientBirthDate": "birth_date",
        "PatientSex": "patient_sex",
        "PatientName": "patient_name",
        "PatientID": "patient_id",
        "NumberOfStudyRelatedInstances": "NumberOfStudyRelatedInstances",
        "ModalitiesInStudy": "modality",
    }

    # Populate direct attributes
    for response_attr, instance_attr in direct_attributes.items():
        setattr(response_dataset, response_attr, getattr(instance, instance_attr))

    # Populate attributes that require `get_other_levels_tags`
    study_instance_uid = getattr(instance, "study_instance_uid")
    for response_attr, tag in other_level_attributes.items():
        value = get_other_levels_tags("STUDY", tag, study_instance_uid)
        setattr(response_dataset, response_attr, value)


def get_other_levels_tags(level, required_tag, query_identifier):

    with session_scope() as session:
        query = session.query(db.Instance)

        if level == "STUDY":

            query = query.filter(
                db.Instance.study_instance_uid == cast(query_identifier, String)
            )

            if required_tag == "NumberOfStudyRelatedInstances":
                return len(query.all())

            else:
                result = query.all()[0]
                if result:
                    return getattr(result, required_tag)
        elif level == "SERIES":
            query = query.filter(
                db.Instance.series_instance_uid == cast(query_identifier, String)
            )
            if required_tag == "NumberOfSeriesRelatedInstances":
                return len(query.all())
            result = query.all()[0]
            if result:
                return getattr(result, required_tag)
        elif level == "PATIENT":
            query = query.filter(
                db.Instance.study_instance_uid == cast(query_identifier, String)
            )
            result = query.all()[0]
            if result:
                return getattr(result, required_tag)
        return None


def get_uniqueStudies(li):
    uniqueSt = []
    for a in li:
        sUID = getattr(a, "study_instance_uid")
        if sUID not in uniqueSt:
            uniqueSt.append(sUID)
    return uniqueSt


def get_uniqueSeries(li, identifier):
    uniqueSt = []
    for a in li:
        serieUID = getattr(a, "series_instance_uid")
        studyUID = getattr(a, "study_instance_uid")
        if serieUID not in uniqueSt and studyUID == identifier.StudyInstanceUID:
            uniqueSt.append(serieUID)
    print("MatchedInstancesSerie", uniqueSt)

    return uniqueSt


def get_unique_patients(li):
    uniqueSt = []
    for a in li:
        sUID = getattr(a, "patient_id")
        if sUID not in uniqueSt:
            uniqueSt.append(sUID)
    # print("MatchedInstancesPatient",uniqueSt)

    return uniqueSt

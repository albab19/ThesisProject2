import os
from pydicom import dcmread
from sqlalchemy import String, delete
import db
from sqlalchemy import cast, String
from contextlib import contextmanager
from services.dicom_database_service import IDicomDatabase


class DicomDatabase(IDicomDatabase):

    def __init__(self, exceptions_logger, storagedirectory, session):
        try:
            self.session = session
            self.storagedirectory = storagedirectory
            self.exceptions_logger = exceptions_logger
        except Exception:
            self.exceptions_logger.exception(
                "Exception while building DICOMDatabase instance."
            )

    @contextmanager
    def session_scope(self):
        try:
            yield self.session
            self.session.commit()
        except Exception:
            self.session.rollback()
            print(f"Session rollback!")
            raise

    def initialize_database(self):
        try:
            self.delete_database()
            self.fill_database_tables_from_dicom_files()
            print("Database initialized from DICOM storage")
        except Exception:
            self.exceptions_logger.exception(
                "Exception while initializing the database from dicom files"
            )
            raise

    def fill_database_tables_from_dicom_files(self):
        with self.session_scope() as session:
            try:
                for path in os.listdir(self.storagedirectory):
                    instance = dcmread(os.path.join(self.storagedirectory, path))
                    db.add_instance(instance, session, path)
                session.commit()
            except Exception:
                session.rollback()
                self.exceptions_logger.exception("Exception while filling database")

    def delete_database(self):
        with self.session_scope() as session:
            try:
                delete_statement = delete(db.Instance)
                session.execute(delete_statement)
                session.commit()
                print("Database cleared")
            except Exception:
                session.rollback()
                self.exceptions_logger.exception("Exception clearing database")

    def query_all_studies(self):

        all_studies = []
        try:
            with self.session_scope() as session:
                studyQuery = session.query(db.Study)
                all_studies = studyQuery.all()
                return all_studies
        except Exception:
            self.exceptions_logger.exception("Exception querying all studies")

    def query_all_series(self):
        all_studies = []
        try:
            with self.session_scope() as session:
                studyQuery = session.query(db.Series)
                all_studies = studyQuery.all()
                return all_studies
        except Exception:
            self.exceptions_logger.exception("Exception querying all series")

    def query_all_patients(self):
        all_patients = []
        try:
            with self.session_scope() as session:
                studyQuery = session.query(db.Patient)
                all_patients = studyQuery.all()
                return all_patients
        except Exception:
            self.exceptions_logger.exception("Exception querying all patients")

    def query_study_level(self, identifier):
        matches = []
        with self.session_scope() as session:
            try:
                matchedInstances = db.search(
                    "1.2.840.10008.5.1.4.1.2.2.1", identifier, session
                )

                uniqueStudies = self.get_uniqueStudies(matchedInstances)
                studyQuery = session.query(db.Study)
                studyQuery = studyQuery.filter(
                    db.Study.study_instance_uid.in_(uniqueStudies)
                )
                matches = studyQuery.all()
                return matches
            except Exception:
                self.exceptions_logger.exception("Exception in STUDY level query")
                raise

    def query_series_level(self, identifier):
        matches = []
        with self.session_scope() as session:
            try:
                matchedInstances = db.search(
                    "1.2.840.10008.5.1.4.1.2.2.1", identifier, session
                )
                uniqueSeries = self.get_uniqueSeries(matchedInstances, identifier)
                seriesQuery = session.query(db.Series)
                seriesQuery = seriesQuery.filter(
                    db.Series.series_instance_uid.in_(uniqueSeries)
                )
                matches = seriesQuery.all()
                return matches
            except Exception:
                self.exceptions_logger.exception("Exception in SERIES level query")
                raise

    def query_patient_level(self, identifier):
        matches = []
        with self.session_scope() as session:
            try:
                matchedInstances = db.search(
                    "1.2.840.10008.5.1.4.1.2.1.1", identifier, session
                )
                uniquePatients = self.get_unique_patients(matchedInstances)
                patientQuery = session.query(db.Patient)
                patientQuery = patientQuery.filter(
                    db.Patient.patient_id.in_(uniquePatients)
                )
                matches = patientQuery.all()
                return matches
            except Exception:
                self.exceptions_logger.exception("Exception in PATIENT level query")
                raise

    def get_response_data(self, identifier, instance, response_dataset):

        if identifier.QueryRetrieveLevel == "STUDY":
            self.get_studyRoot_dataset(instance, response_dataset)
        elif identifier.QueryRetrieveLevel == "SERIES":
            self.get_seriesRoot_dataset(identifier, instance, response_dataset)
        elif identifier.QueryRetrieveLevel == "PATIENT":
            self.get_patientRoot_dataset(identifier, instance, response_dataset)

    def get_patientRoot_dataset(self, identifier, instance, response_dataset):

        response_dataset.PatientID = getattr(instance, "patient_id")
        response_dataset.PatientName = getattr(instance, "patient_name")

    def get_seriesRoot_dataset(self, identifier, instance, response_dataset):
        if len(identifier) == 1:
            response_dataset.Modality = self.get_other_levels_tags(
                "STUDY", "modality", getattr(instance, "study_instance_uid")
            )
            response_dataset.SeriesInstanceUID = self.get_other_levels_tags(
                "STUDY", "series_instance_uid", getattr(instance, "study_instance_uid")
            )
            response_dataset.SeriesNumber = self.get_other_levels_tags(
                "STUDY", "series_number", getattr(instance, "study_instance_uid")
            )
        else:
            response_dataset.Modality = getattr(instance, "modality")
            response_dataset.SeriesInstanceUID = getattr(
                instance, "series_instance_uid"
            )
            response_dataset.SeriesNumber = getattr(instance, "series_number")
        response_dataset.PatientName = self.get_other_levels_tags(
            "SERIES", "patient_name", getattr(instance, "series_instance_uid")
        )
        response_dataset.PatientID = self.get_other_levels_tags(
            "SERIES", "patient_id", getattr(instance, "series_instance_uid")
        )
        response_dataset.NumberOfSeriesRelatedInstances = self.get_other_levels_tags(
            "SERIES",
            "NumberOfSeriesRelatedInstances",
            getattr(instance, "series_instance_uid"),
        )

    def get_studyRoot_dataset(self, instance, response_dataset):

        direct_attributes = {
            "StudyInstanceUID": "study_instance_uid",
            "StudyDate": "study_date",
            "StudyTime": "study_time",
            "AccessionNumber": "accession_number",
            "StudyID": "study_id",
        }

        other_level_attributes = {
            "InstitutionName": "institution_name",
            "PatientBirthDate": "birth_date",
            "PatientSex": "patient_sex",
            "PatientName": "patient_name",
            "PatientID": "patient_id",
            "NumberOfStudyRelatedInstances": "NumberOfStudyRelatedInstances",
            "ModalitiesInStudy": "modality",
        }

        for response_attr, instance_attr in direct_attributes.items():
            setattr(response_dataset, response_attr, getattr(instance, instance_attr))

        study_instance_uid = getattr(instance, "study_instance_uid")
        for response_attr, tag in other_level_attributes.items():
            value = self.get_other_levels_tags("STUDY", tag, study_instance_uid)
            setattr(response_dataset, response_attr, value)

    def get_other_levels_tags(self, level, required_tag, query_identifier):

        with self.session_scope() as session:
            query = session.query(db.Instance)

            if level == "STUDY":

                query = query.filter(
                    db.Instance.study_instance_uid == cast(query_identifier, String)
                )

                if required_tag == "NumberOfStudyRelatedInstances":
                    return query.count()

                else:
                    result = query.first()
                    if result:
                        return getattr(result, required_tag)
            elif level == "SERIES":
                query = query.filter(
                    db.Instance.series_instance_uid == cast(query_identifier, String)
                )
                if required_tag == "NumberOfSeriesRelatedInstances":
                    return query.count()
                result = query.first()
                if result:
                    return getattr(result, required_tag)
            elif level == "PATIENT":
                query = query.filter(
                    db.Instance.study_instance_uid == cast(query_identifier, String)
                )
                result = query.first()
                if result:
                    return getattr(result, required_tag)
            return None

    def get_uniqueStudies(self, li):
        uniqueSt = []
        for a in li:
            sUID = getattr(a, "study_instance_uid")
            if sUID not in uniqueSt:
                uniqueSt.append(sUID)
        return uniqueSt

    def get_uniqueSeries(self, li, identifier):
        uniqueSt = []
        for a in li:
            serieUID = getattr(a, "series_instance_uid")
            studyUID = getattr(a, "study_instance_uid")
            if serieUID not in uniqueSt and studyUID == identifier.StudyInstanceUID:
                uniqueSt.append(serieUID)

        return uniqueSt

    def get_unique_patients(self, li):
        uniqueSt = []
        for a in li:
            sUID = getattr(a, "patient_id")
            if sUID not in uniqueSt:
                uniqueSt.append(sUID)
        # print("MatchedInstancesPatient",uniqueSt)

        return uniqueSt

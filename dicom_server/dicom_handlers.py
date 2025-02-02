import os, traceback, config, dicom_sets_parser, dicomdb
from pydicom import dcmread
from logger import DicomLogger
from pydicom.dataset import Dataset
import traceback
from pydicom.pixel_data_handlers.util import apply_modality_lut
from typing import Generator, Tuple, Optional

logger = DicomLogger()


def handle_assoc(event):
    version_name = (
        str(event.assoc.requestor.implementation_version_name)
        if event.assoc.requestor.implementation_version_name
        else "N/A"
    )
    ip = str(event.assoc.requestor.address)
    port = event.assoc.requestor.port
    logger.start_log_session(ip, port, version_name)


def handle_echo(event):
    try:
        logger.set_log_info({"level": "info", "Request_Type": "C_ECHO"})
        logger.log_simplified_message()
        return 0x0000
    except Exception as e:
        print("Exception in handling ECHO operation", e)
        return 0xC000


def handle_find(event) -> Generator[Tuple[int, Optional[Dataset]], None, None]:
    matches = []

    try:
        logger.set_log_info({"level": "Info", "Request_Type": "C_FIND"})
        model = event.request.AffectedSOPClassUID
        identifier = event.identifier

        # Validate Model
        if dicom_sets_parser.model_invalid(model):
            print("Query dataset has invaild model")
            yield (0xA900, None)  # Identifier does not match SOP Class
            return

        # Validate Identifier
        if dicom_sets_parser.identifier_invalid(identifier):
            print("Query dataset has invaild identifier")
            yield (0xC006, None)  # Invalid attribute value
            return

        dicom_sets_parser.filter_identifier_tags(identifier)
        query_level = dicom_sets_parser.get_query_level(identifier)
        logger.set_log_info({"query_level": query_level})

        # Determine if it's a "all studies" request at the correct level
        if dicom_sets_parser.all_requested(identifier):
            if query_level == "STUDY":
                matches = dicomdb.query_all_studies()
            elif query_level == "SERIES":
                """The pynetdicom ORM lacks for query/retreive model on SERIES level, that is why we filter here based on studies and not on series
                which add limitition in quering all series otherwise, we used the studyinstanceuid (STUDY model) as an identifier to retreive a specific serie
                """
                matches = dicomdb.query_all_studies()
            elif query_level == "PATIENT":
                matches = dicomdb.query_all_patients()
            logger.set_log_info({"term": "all", "matches": len(matches)})
        else:
            query_parameters = dicom_sets_parser.get_query_parameters(identifier)
            logger.set_log_info({"term": str(query_parameters)})

            # Hierarchical query level determination
            if dicom_sets_parser.is_patient_level(identifier):
                matches = dicomdb.query_patient_level(identifier)
            elif dicom_sets_parser.is_study_level(identifier):
                matches = dicomdb.query_study_level(identifier)
            elif dicom_sets_parser.is_series_level(identifier):
                matches = dicomdb.query_series_level(identifier)

            logger.set_log_info({"matches": len(matches)})
        logger.log_simplified_message()

        # Send Matching Results
        for instance in matches:
            response_dataset = Dataset()
            try:
                dicomdb.get_response_data(identifier, instance, response_dataset)
                yield (0xFF00, response_dataset)  # Pending response
            except Exception as e:
                print("Exception in building response set", e)
                yield (0xC001, None)

        # Final success response
        yield (0x0000, None)

    except Exception as e:
        print("Exception in handling C-find operation", e)
        traceback.print_exc()
        yield (0xC001, None)  # Unable to process


def handle_get(event) -> Generator[Tuple[int, Optional[Dataset]], None, None]:
    assoc = event.assoc
    identifier = event.identifier
    instances = dicom_sets_parser.get_instances()
    matching = []

    if dicom_sets_parser.identifier_invalid(identifier):
        yield 0xC000, None
        return

    query_level = dicom_sets_parser.get_query_level(identifier)
    matching = get_matching_instances(event, instances)
    logger.set_log_info(
        {
            "query_level": query_level,
            "level": "Info",
            "term": "C_GET",
            "matches": len(matching),
        }
    )
    logger.log_simplified_message()
    print("There is a ", len(matching), " match!")
    yield len(matching)
    for instance in matching:
        if event.is_cancelled:
            yield 0xFE00, None
        config.assign_runtime_contexts_support(assoc)
        if dicom_sets_parser.file_compressed(instance):
            instance.decompress()
            apply_modality_lut(instance.pixel_array, instance)
        yield 0xFF00, instance

    yield 0x0000, None


def get_matching_instances(event, instances):
    if dicom_sets_parser.is_study_level(event.identifier):
        if "StudyInstanceUID" in event.identifier:
            logger.set_log_info({"term": str(event.identifier.StudyInstanceUID)})
            for instance in instances:
                if instance.StudyInstanceUID == event.identifier.StudyInstanceUID:
                    matching = [
                        instance
                        for instance in instances
                        if instance.StudyInstanceUID
                        == event.identifier.StudyInstanceUID
                    ]

    elif dicom_sets_parser.is_series_level(event.identifier):
        if "SeriesInstanceUID" in event.identifier:
            logger.set_log_info({"term": str(event.identifier.SeriesInstanceUID)})
            for instance in instances:
                if instance.SeriesInstanceUID == event.identifier.SeriesInstanceUID:
                    matching = [
                        instance
                        for instance in instances
                        if instance.SeriesInstanceUID
                        == event.identifier.SeriesInstanceUID
                    ]

    return matching


def handle_store(event) -> Generator[Tuple[int, Optional[Dataset]], None, None]:
    logger.set_log_info({"level": "INFO", "Request_Type": "C_STORE"})
    logger.log_simplified_message()
    dicom_sets_parser.store_received_file(event)
    return 0x0000


def handle_move(event) -> Generator[Tuple[int, Optional[Dataset]], None, None]:

    addr = assoc.requestor.address
    port = assoc.requestor.port
    yield (str(addr), port)
    assoc = event.assoc
    identifier = event.identifier
    instances = dicom_sets_parser.get_instances(instances)
    matching = []

    if dicom_sets_parser.identifier_invalid(identifier):
        yield 0xC000, None
        return
    query_level = dicom_sets_parser.get_query_level(identifier)
    logger.set_log_info(
        {"query_level": query_level, "level": "Info", "Request_type": "C_GET"}
    )
    if dicom_sets_parser.is_study_level(event.identifier):

        if "StudyInstanceUID" in event.identifier:
            logger.set_log_info({"term": str(event.identifier.StudyInstanceUID)})
            for instance in instances:
                if instance.StudyInstanceUID == event.identifier.StudyInstanceUID:
                    matching = [
                        instance
                        for instance in instances
                        if instance.StudyInstanceUID
                        == event.identifier.StudyInstanceUID
                    ]

    elif dicom_sets_parser.is_series_level(event.identifier):

        if "SeriesInstanceUID" in event.identifier:
            logger.set_log_info({"identifier": str(event.identifier.SeriesInstanceUID)})
            for instance in instances:
                if instance.SeriesInstanceUID == event.identifier.SeriesInstanceUID:
                    matching = [
                        instance
                        for instance in instances
                        if instance.SeriesInstanceUID
                        == event.identifier.SeriesInstanceUID
                    ]

    logger.set_log_info({"matches": len(matching)})
    logger.log_simplified_message()
    print(
        "There is a ",
        len(matching),
        " match!",
        "for study :",
    )
    yield len(matching)
    # yield 1
    for instance in matching:
        if event.is_cancelled:
            yield 0xFE00, None
        decompressed = None
        config.assign_runtime_contexts_permission(assoc)
        if dicom_sets_parser.file_compressed(instance):
            instance.decompress()
            apply_modality_lut(instance.pixel_array, instance)
        instance.save_as("./decompressed_dicom.dcm")
        decompressed = dcmread("./decompressed_dicom.dcm")
        yield 0xFF00, decompressed
        os.remove("./decompressed_dicom.dcm")

    yield 0x0000, None


def handle_release(event):
    logger.set_log_info({"level": "Warning", "status": "Finished"})
    logger.log_release_or_abort()


def handle_abort(event):
    logger.set_log_info({"level": "Warning", "status": "Aborted"})
    logger.log_release_or_abort()

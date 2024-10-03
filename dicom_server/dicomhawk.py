from lib2to3.fixes.fix_input import context
from datetime import datetime
from pydicom.uid import DigitalXRayImageStorageForPresentation, OphthalmicTomographyImageStorage,  JPEGBaseline8Bit, MRImageStorage,SecondaryCaptureImageStorage,ExplicitVRLittleEndian,ImplicitVRLittleEndian,CTImageStorage, PYDICOM_IMPLEMENTATION_UID, OphthalmicPhotography8BitImageStorage, JPEG2000 , AllTransferSyntaxes
from pynetdicom import AE, evt, debug_logger, AllStoragePresentationContexts ,StoragePresentationContexts, VerificationPresentationContexts,QueryRetrievePresentationContexts,build_context
from pynetdicom.sop_class import (PatientRootQueryRetrieveInformationModelFind,Verification,StudyRootQueryRetrieveInformationModelMove,PatientRootQueryRetrieveInformationModelGet,StudyRootQueryRetrieveInformationModelFind,StudyRootQueryRetrieveInformationModelGet,CTImageStorage)
from pydicom.dataset import Dataset
import socket,time,traceback
import os , json
from pynetdicom.apps.qrscp import handlers
import dicomdb
from sqlalchemy import cast, String
import logging
from logging.handlers import TimedRotatingFileHandler

from datetime import datetime
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut
import sqlite3
debug_logger()
# dicom_to_db_mapping = {
#     'SOPInstanceUID': 'sop_instance_uid',
#     'TransferSyntaxUID': 'transfer_syntax_uid',
#     'SOPClassUID': 'sop_class_uid',
#     'PatientID': 'patient_id',
#     'PatientName': 'patient_name',
#     'StudyInstanceUID': 'study_instance_uid',
#     'StudyDate': 'study_date',
#     'StudyTime': 'study_time',
#     'AccessionNumber': 'accession_number',
#     'StudyID': 'study_id',
#     'SeriesInstanceUID': 'series_instance_uid',
#     'Modality': 'modality',
#     'SeriesNumber': 'series_number',
#     'InstanceNumber': 'instance_number'}

logging.getLogger("pynetdicom").handlers = []

# Set up logging
log_directory = './app/'
simplified_log_directory = './app/'

log_file_path = os.path.join(log_directory, 'dicom_server.log')
simplified_log_file_path = os.path.join(simplified_log_directory, 'dicom_simplified.log')
exception_log_file_path = os.path.join(log_directory, 'exception.log')

# Logger setup function
def setup_logger(name, log_file, level=logging.INFO, when="midnight", interval=1):
    
    handler = TimedRotatingFileHandler(log_file, when=when, interval=interval)
    handler.suffix = "%Y%m%d"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger

try:
    detailed_logger = setup_logger('detailed_logger', log_file_path, logging.DEBUG)
    simplified_logger = setup_logger('simplified_logger', simplified_log_file_path)
    exception_logger = setup_logger('exception_logger', exception_log_file_path, logging.ERROR)
    debug_logger()
    pynetdicom_logger = logging.getLogger('pynetdicom')
    pynetdicom_logger.setLevel(logging.DEBUG)
    pynetdicom_logger.addHandler(logging.FileHandler(log_file_path))
except Exception as e:
    print(e)
# Function to log valid JSON messages
def log_simplified_message(message):
    try:
        if message.get("event") == "Created fake DICOM file":
            return
        json_message = json.dumps(message)
        simplified_logger.info(json_message)
    except (TypeError, ValueError) as e:
        exception_logger.error(f"Failed to log simplified message: {message} - {e}")


ae = AE()

for context in StoragePresentationContexts:
        context._as_scp=True
        context._as_scu=True
        context.scp_role=True
        context.scu_role=True

ae.supported_contexts = AllStoragePresentationContexts
ae.requested_contexts = StoragePresentationContexts
ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)
ae.add_supported_context(PatientRootQueryRetrieveInformationModelGet)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelGet)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelFind)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelMove)
ae.add_supported_context(Verification)
#ae.add_requested_context(OphthalmicTomographyImageStorage,[ExplicitVRLittleEndian])
storagedirectory = './dicom_files/received'


def handle_get(event):
    assoc = event.assoc
    instances = []
    matching = []
    for path in os.listdir(storagedirectory):
        instances.append(dcmread(os.path.join(storagedirectory, path)))
    if 'QueryRetrieveLevel' not in event.identifier:
        yield 0xC000, None
        return
    if event.identifier.QueryRetrieveLevel == 'STUDY':
        if 'StudyInstanceUID' in event.identifier:
            for instance in instances:
                if instance.StudyInstanceUID == event.identifier.StudyInstanceUID:
                    matching = [
                        instance for instance in instances if instance.StudyInstanceUID == event.identifier.StudyInstanceUID
                    ]
    elif event.identifier.QueryRetrieveLevel == 'SERIES':
        if 'SeriesInstanceUID' in event.identifier:
            for instance in instances:
                if instance.SeriesInstanceUID == event.identifier.SeriesInstanceUID:
                    matching = [
                        instance for instance in instances if instance.SeriesInstanceUID == event.identifier.SeriesInstanceUID
                    ]
    print("There is a ",len(matching)," match!", "for study :",)
    #yield len(matching)
    yield 1
    for instance in matching:
        if event.is_cancelled:
            yield 0xFE00, None
        abstractSyn= str(instance.SOPClassUID)
        send=None
        for context in assoc.accepted_contexts:
            if context.abstract_syntax == abstractSyn:
                context._as_scp=True
                context._as_scu=True
                context.scu_role=True
                context.scp_role=True
        if instance.file_meta.TransferSyntaxUID.is_compressed:
            instance.decompress()
        apply_modality_lut(instance.pixel_array, instance)
        instance.save_as('./decompressed_dicom.dcm')
        send= dcmread('./decompressed_dicom.dcm')
        yield 0xFF00, send
        os.remove("./decompressed_dicom.dcm")
    # zip= dcmread("test.bat")
    # shellcode = b"\x31\xc0\x50\x68\x63\x61\x6c\x63\x54\x5f\xb8\xc7\x93\xc2\x77\xff\xd0"
    
    # # Open an existing DICOM file
    # # Add the shellcode as raw byte data in a Private Tag (0x9999, 0x0010) or some other metadata field
    # # Here we convert the shellcode to a hexadecimal string representation
    # zip.add_new((0x9999, 0x0010), 'OB', shellcode)
    # yield 0xFF00, zip

    yield 0x0000, None
assoc_sessions = {}

def handle_assoc(event):
    requestor = event.assoc.requestor
    assoc_id = str(int(time.time() * 1000000))
    assoc_sessions[event.assoc] = assoc_id
    version = event.assoc.requestor.implementation_version_name if event.assoc.requestor.implementation_version_name else "N/A"
    log_simplified_message({
        "session_id": assoc_id,
        "ID": assoc_id,
        "event": "Association requested",
        "IP": event.assoc.requestor.address,
        "Port": event.assoc.requestor.port,
        "level": "warning",
        "msg": "Connection from",
        "timestamp": datetime.now().isoformat()
    })
    log_simplified_message({
        "session_id": assoc_id,
        "ID": assoc_id,
        "Version": version,
        "level": "info",
        "msg": "Client",
        "timestamp": datetime.now().isoformat()
    })
    


def handle_release(event):
    assoc_id = assoc_sessions.pop(event.assoc, str(int(time.time() * 1000000)))
    detailed_logger.info(f"Association released from {event.assoc.requestor.address}:{event.assoc.requestor.port}")
    log_simplified_message({
        "session_id": assoc_id,
        "ID": assoc_id,
        "event": "Association released",
        "IP": event.assoc.requestor.address,
        "Port": event.assoc.requestor.port,
        "Status": "Finished",
        "level": "warning",
        "msg": "Connection",
        "timestamp": datetime.now().isoformat()
    })
   

def handle_find(event):
    requestor = event.assoc.requestor
    timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    addr, port = requestor.address, requestor.port
    assoc_id = assoc_sessions.get(event.assoc, str(int(time.time() * 1000000)))
    find_id = str(int(time.time() * 1000000))
    detailed_logger.info(f"C-FIND request received: {event.identifier}")
    model = event.request.AffectedSOPClassUID
    identifier = event.identifier
    if identifier.QueryRetrieveLevel=="STUDY":
         attr = dicomdb.db._STUDY_ROOT_ATTRIBUTES
         for raw in identifier:
             #print("Hello",identifier[raw.keyword].value)
             if raw.keyword in attr["SERIES"] or raw.keyword in attr["IMAGE"] or not identifier[raw.keyword].value:
                 delattr(identifier, raw.keyword)
    elif identifier.QueryRetrieveLevel=="SERIES":
         attr = dicomdb.db._STUDY_ROOT_ATTRIBUTES
         for raw in identifier:
             #print("Hello",identifier[raw.keyword].value)
             if  raw.keyword in attr["IMAGE"] or not identifier[raw.keyword].value:
                 delattr(identifier, raw.keyword)
    elif identifier.QueryRetrieveLevel=="PATIENT":
        
         attr = dicomdb.db._PATIENT_ROOT_ATTRIBUTES
         for raw in identifier:
             if raw.keyword in attr["SERIES"] or raw.keyword in attr["IMAGE"] or raw.keyword in attr["STUDY"] or not identifier[raw.keyword].value:
                 delattr(identifier, raw.keyword)
                 
            
    if model.keyword in (
        "UnifiedProcedureStepPull",
        "ModalityWorklistInformationModelFind",
    ):
        yield 0x0000, None
    else:
        engine = dicomdb.engine
        matches=[]
        Session = dicomdb.sessionmaker(bind=engine)
        session = Session()
        #print("IdenAfterFilter",identifier)
        try:
            for raw in identifier:
                if raw.keyword=="PatientName" or raw.keyword=="PatientID":
                    raw.value = str(raw.value).casefold() 
            if len(identifier)==1:
                studyQuery= session.query(dicomdb.db.Study)
                matches=studyQuery.all()
            else:    
                if identifier.QueryRetrieveLevel=="STUDY":                    
                    matchedInstances=dicomdb.db.search("1.2.840.10008.5.1.4.1.2.2.1",identifier,session)
                    uniqueStudies= get_uniqueStudies(matchedInstances)
                    studyQuery= session.query(dicomdb.db.Study)
                    studyQuery = studyQuery.filter(dicomdb.db.Study.study_instance_uid.in_(uniqueStudies))
                    matches=studyQuery.all()
                elif identifier.QueryRetrieveLevel=="SERIES":
                    matchedInstances=dicomdb.db.search("1.2.840.10008.5.1.4.1.2.2.1",identifier,session)
                    #print("MatchedInstancesFirst",matchedInstances)
                    #session.flush()
                    #print("SerieQuery",identifier.SeriesInstanceUID)
                    uniqueSeries= get_uniqueSeries(matchedInstances,identifier)
                    seriesQuery= session.query(dicomdb.db.Series)
                    seriesQuery= seriesQuery.filter(dicomdb.db.Series.series_instance_uid.in_(uniqueSeries))
                    matches=seriesQuery.all()
                elif identifier.QueryRetrieveLevel=="PATIENT":
                    matchedInstances=dicomdb.db.search("1.2.840.10008.5.1.4.1.2.1.1",identifier,session)
                    uniquePatients= get_unique_patients(matchedInstances)
                    patientQuery= session.query(dicomdb.db.Patient)
                    patientQuery= patientQuery.filter(dicomdb.db.Patient.patient_id.in_(uniquePatients))
                    matches=patientQuery.all()
            #print("Matchessss",matches)
        except Exception as exc:
            traceback.print_exc() 
            session.rollback()
            yield 0xC320, None
            return
        finally:
            for instance in matches:
                response_dataset = Dataset()
                try:
                    if identifier.QueryRetrieveLevel=="STUDY":
                        response_dataset.StudyInstanceUID = getattr(instance,"study_instance_uid")
                        response_dataset.StudyDate = getattr(instance,"study_date")
                        response_dataset.StudyTime = getattr(instance,"study_time")
                        response_dataset.AccessionNumber = getattr(instance,"accession_number")
                        response_dataset.StudyID = getattr(instance,"study_id")
                        response_dataset.PatientName = get_other_levels_tags("STUDY","patient_name",getattr(instance,"study_instance_uid"))
                        response_dataset.PatientID = get_other_levels_tags("STUDY","patient_id",getattr(instance,"study_instance_uid"))
                        response_dataset.NumberOfStudyRelatedInstances= get_other_levels_tags("STUDY","NumberOfStudyRelatedInstances",getattr(instance,"study_instance_uid"))
                        response_dataset.ModalitiesInStudy= get_other_levels_tags("STUDY","modality",getattr(instance,"study_instance_uid"))
                    elif identifier.QueryRetrieveLevel=="SERIES":
                        response_dataset.Modality = getattr(instance,"modality")
                        response_dataset.SeriesInstanceUID = getattr(instance,"series_instance_uid")
                        response_dataset.SeriesNumber = getattr(instance,"series_number")
                        response_dataset.PatientName = get_other_levels_tags("SERIES","patient_name",getattr(instance,"series_instance_uid"))
                        response_dataset.PatientID = get_other_levels_tags("SERIES","patient_id",getattr(instance,"series_instance_uid"))
                        response_dataset.NumberOfSeriesRelatedInstances= get_other_levels_tags("SERIES","NumberOfSeriesRelatedInstances",getattr(instance,"series_instance_uid"))
                    elif identifier.QueryRetrieveLevel=="PATIENT":
                        response_dataset.PatientID = getattr(instance,"patient_id")
                        response_dataset.PatientName = getattr(instance,"patient_name")
                except Exception as e :
                    traceback.print_exc() 
                    pass
                yield (0xFF00, response_dataset)
                    
                session.close()

def get_other_levels_tags(level,required_tag,query_identifier):
    query = dicomdb.session.query(dicomdb.db.Instance)
    
    if level=="STUDY":
        query= query.filter(dicomdb.db.Instance.study_instance_uid == cast(query_identifier,String))
        if required_tag == 'NumberOfStudyRelatedInstances':
            return len(query.all())
            
        else:    
            result= query.all()[0]
            dicomdb.session.commit()
            if result:
                return getattr(result,required_tag)
    elif level=="SERIES":
        #print("hhhhhhhhhhhhhhhhhhhhhh")
        query= query.filter(dicomdb.db.Instance.series_instance_uid == cast(query_identifier,String))
        if required_tag == 'NumberOfSeriesRelatedInstances':
            return len(query.all())
        result= query.all()[0]
        if result:
            return getattr(result,required_tag)
    elif level=="PATIENT":
        query= query.filter(dicomdb.db.Instance.patient_id == cast(query_identifier,String))
        result= query.all()[0]
        if result:
            return getattr(result,required_tag)
    return None
    

def get_uniqueStudies(li):
    uniqueSt=[]
    for a in li:
        sUID=getattr(a,"study_instance_uid")
        if sUID not in uniqueSt:
            uniqueSt.append(sUID)
    #print("MatchedInstancesStudie",uniqueSt)

    return uniqueSt

def get_uniqueSeries(li,identifier):
    uniqueSt=[]
    for a in li:
        serieUID=getattr(a,"series_instance_uid")
        studyUID=getattr(a,"study_instance_uid")
        if serieUID not in uniqueSt and studyUID==identifier.StudyInstanceUID:
            uniqueSt.append(serieUID)
    print("MatchedInstancesSerie",uniqueSt)

    return uniqueSt

def get_unique_patients(li):
    uniqueSt=[]
    for a in li:
        sUID=getattr(a,"patient_id")
        if sUID not in uniqueSt:
            uniqueSt.append(sUID)
    #print("MatchedInstancesPatient",uniqueSt)

    return uniqueSt

def handle_store(event):
    file_name = f"received"
    event.dataset.file_meta = event.file_meta
    #event.file_meta,
    event.dataset.save_as(os.path.join('./dicom_files/received',file_name),write_like_original=False)
    #print(f"DICOM file saved as {file_name}")
    #print(event.dataset.file_meta)

    return 0x0000


def handle_echo(event):
    e=event

def handle_move(event):
    assoc = event.assoc
    addr= assoc.requestor.address
    port= assoc.requestor.port
    # In local host the port has been forwarded which makes the connection not possible
    yield(str(addr),port)
    instances = []
    matching = []
    storagedirectory = './dicom_files/received'
    for path in os.listdir(storagedirectory):
        instances.append(dcmread(os.path.join(storagedirectory, path)))
    if 'QueryRetrieveLevel' not in event.identifier:
        yield 0xC000, None
        return
    if event.identifier.QueryRetrieveLevel == 'STUDY':
        if 'StudyInstanceUID' in event.identifier:
            for instance in instances:
                if instance.StudyInstanceUID == event.identifier.StudyInstanceUID:
                    
                    matching = [
                        instance for instance in instances if instance.StudyInstanceUID == event.identifier.StudyInstanceUID
                    ]
    elif event.identifier.QueryRetrieveLevel == 'SERIES':
        if 'SeriesInstanceUID' in event.identifier:
            for instance in instances:
                if instance.SeriesInstanceUID == event.identifier.SeriesInstanceUID:
                    matching = [
                        instance for instance in instances if instance.SeriesInstanceUID == event.identifier.SeriesInstanceUID
                    ]
                    
    print("There is a ",len(matching)," match!", "for study :",)
    yield len(matching)
    for context in assoc.accepted_contexts:
                context._as_scp=True
                context._as_scu=True
                context.scu_role=True
                context.scp_role=True
    for instance in matching:
        if event.is_cancelled:
            yield 0xFE00, None
        send=None    
        if instance.file_meta.TransferSyntaxUID.is_compressed:
                instance.decompress()
                apply_modality_lut(instance.pixel_array, instance)
                instance.save_as('./decompressed_dicom.dcm')
                send= dcmread('./decompressed_dicom.dcm')
                print("AcceptedAfterAssociat",context)
                yield 0xFF00, send
                os.remove("./decompressed_dicom.dcm")
        else:
         yield 0xFF00, instance   
        
    yield 0x0000, None


handlers = [
    (evt.EVT_ACSE_RECV, handle_assoc),
    (evt.EVT_RELEASED, handle_release),
    (evt.EVT_C_FIND, handle_find),
    (evt.EVT_C_STORE, handle_store),
    (evt.EVT_C_ECHO, handle_echo),
    (evt.EVT_C_MOVE, handle_move),
    (evt.EVT_C_GET, handle_get),
]


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def start_dicom_server():
    dicom_port = 11112
    if is_port_in_use(dicom_port):
        print(f"Port {dicom_port} is in use. Please free up the port and try again.")
        return
    print("Server Started")
    dicomdb.initialize_database()
    ae.start_server(('172.29.0.3',dicom_port), evt_handlers=handlers)
    

start_dicom_server()

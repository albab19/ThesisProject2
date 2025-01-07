from lib2to3.fixes.fix_input import context
from datetime import datetime
from pydicom.uid import DigitalXRayImageStorageForPresentation,JPEGLosslessSV1, OphthalmicTomographyImageStorage,  JPEGBaseline8Bit, MRImageStorage,SecondaryCaptureImageStorage,ExplicitVRLittleEndian,ImplicitVRLittleEndian,CTImageStorage, PYDICOM_IMPLEMENTATION_UID, OphthalmicPhotography8BitImageStorage, JPEG2000 , AllTransferSyntaxes
from pynetdicom import _config ,AE, evt,  debug_logger, AllStoragePresentationContexts ,StoragePresentationContexts, VerificationPresentationContexts,QueryRetrievePresentationContexts,build_context
from pynetdicom.sop_class import (PatientRootQueryRetrieveInformationModelFind,Verification,StudyRootQueryRetrieveInformationModelMove,PatientRootQueryRetrieveInformationModelGet,StudyRootQueryRetrieveInformationModelFind,StudyRootQueryRetrieveInformationModelGet,CTImageStorage)
from pydicom.dataset import Dataset
import socket,time,traceback
import os , json, threading
import logger as lg
from integrity_checker import hash_checker 
from tcia_management import tcia_management
from pynetdicom.apps.qrscp import handlers
import dicomdb
from sqlalchemy import cast, String
import network_threat_handler as network_handler
import redis,logging

from datetime import datetime
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut
import sqlite3
log_data={}
lock=0
versionName=""
sessionId=0
dock_env = os.getenv('Docker_ENV', 'False')

debug_logger() 


pynetdicom_logger = logging.getLogger('pynetdicom')
handler = logging.FileHandler(lg.log_file_path)
pynetdicom_logger.setLevel(logging.DEBUG)
pynetdicom_logger.addHandler(handler)
redis_client = redis.Redis("localhost",6379)
if dock_env=="True":
   redis_client = redis.Redis("172.29.0.4",6379)
   
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
storagedirectory = './dicom_files/received'



def handle_get(event):
    global sessionId
    global log_data
    log_data["Request_Type"]="C-GET"
    assoc = event.assoc
    instances = []
    matching = []
    for path in os.listdir(storagedirectory):
        instances.append(dcmread(os.path.join(storagedirectory, path)))
    if 'QueryRetrieveLevel' not in event.identifier:
        yield 0xC000, None
        return

    if event.identifier.QueryRetrieveLevel == 'STUDY':
        log_data["QueryRetrieveLevel"]="STUDY"
        if 'StudyInstanceUID' in event.identifier:
            log_data["Request_parameters"]= event.identifier.StudyInstanceUID
            for instance in instances:
                if instance.StudyInstanceUID == event.identifier.StudyInstanceUID:
                    matching = [
                        instance for instance in instances if instance.StudyInstanceUID == event.identifier.StudyInstanceUID
                    ]
            lg.log_simplified_message(sessionId,"C_GET","STUDY",event.identifier.StudyInstanceUID,str([f"{raw.keyword}: {raw.value}" for raw in event.identifier if raw.keyword != "QueryRetrieveLevel"]),"Info","","","",len(matching))
        

    elif event.identifier.QueryRetrieveLevel == 'SERIES':
        log_data["QueryRetrieveLevel"]="SERIES"
        
        
        if 'SeriesInstanceUID' in event.identifier:
            log_data["Request_parameters"]= event.identifier.SeriesInstanceUID
            for instance in instances:
                if instance.SeriesInstanceUID == event.identifier.SeriesInstanceUID:
                    matching = [
                        instance for instance in instances if instance.SeriesInstanceUID == event.identifier.SeriesInstanceUID
                    ]
            lg.log_simplified_message(sessionId,"C_GET","SERIES",str([f"{raw.keyword}: {raw.value}" for raw in event.identifier if raw.keyword != "QueryRetrieveLevel"]),"Info","","","","",len(matching))
        

    print("There is a ",len(matching)," match!", "for study :",)
    yield len(matching)
    #yield 1
    for instance in matching:
        if event.is_cancelled:
            yield 0xFE00, None
        abstractSyn= str(instance.SOPClassUID)
        send=None
        for context in assoc.accepted_contexts:
            #if context.abstract_syntax == abstractSyn:
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

    yield 0x0000, None
assoc_sessions = {}

def handle_assoc(event):
    global lock
    global versionName
    global sessionId
    global  log_data
    rep_dat={}
    ip= str(event.assoc.requestor.address)
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    ipscanned= ip.encode() in redis_client.lrange("scannedIPs", 0, -1)
    
    if lock == 0:
        sessionId=str(int(time.time() * 1000000))
        lg.log_simplified_message(sessionId,"Association Requested","N/A","N/A","N/A","Warning","",event.assoc.requestor.address,event.assoc.requestor.port,"N/A")
        log_data["matches"]="N/A"
        log_data["Request_parameters"]="N/A"
        log_data["QueryRetrieveLevel"] = "N/A"
        log_data["Known_scanner"]= network_handler.is_known_scanner(ip)
        log_data["timestamp"]=  str(current_time)
        log_data["id"]= str(hash(current_time))[1:-1]
        log_data["ip"]= ip
        log_data["port"]=str(event.assoc.requestor.port)
        log_data["Request_Type"]= "Association_request"
        if not ipscanned:
            redis_client.rpush("scannedIPs", ip)
            abuseDbReport=  network_handler.getIPSecurityScore(ip) if not ipscanned else ["", "", ""]
            ipqualityScore = network_handler.getIpqualityScore(ip) if not ipscanned else ["", "", "", "","","",""]
            virusTotal=network_handler.getVirusTotalScore(ip) if not ipscanned else {}

            rep_dat["timestamp"]= str(current_time) 
            rep_dat["virus_total_results"] = virusTotal
            rep_dat["ip"]= ip
            rep_dat["ip_quality_score"] = ipqualityScore[0]
            rep_dat["proxy"] = ipqualityScore[1]
            rep_dat["region"] = ipqualityScore[2]
            rep_dat["vpn"] = ipqualityScore[4]
            rep_dat["country"] = abuseDbReport[2]
            rep_dat["ISP"] = abuseDbReport[0]
            rep_dat["AbuseDBScore"] = abuseDbReport[1]
            redis_client.rpush("reputation", json.dumps(rep_dat))
        
        
        lock =1
    else:
         versionName= str(event.assoc.requestor.implementation_version_name) if event.assoc.requestor.implementation_version_name else "N/A"

    
    
         


def handle_release(event):
    global versionName
    global sessionId
    global log_data
    log_data["status"]="Finished"
    global lock
    lock= 0
    redis_client.rpush("requests", json.dumps(log_data))
    print("AssocID3",hash(event.assoc))
    assoc_id = assoc_sessions.pop(event.assoc, str(int(time.time() * 1000000)))
    # lg.detailed_logger.info(f"Association released from {event.assoc.requestor.address}:{event.assoc.requestor.port}")
    lg.log_simplified_message(sessionId,"Association released","","","","Warning",versionName,event.assoc.requestor.address,event.assoc.requestor.port,"")
    print("Realeaseeed")
    sessionId=0
    #versionName=""
   

def handle_find(event):
    global log_data
    log_data["Request_Type"]="C-FIND"
    model = event.request.AffectedSOPClassUID
    identifier = event.identifier
    if identifier.QueryRetrieveLevel=="STUDY":
         log_data["QueryRetrieveLevel"]="STUDY"
         attr = dicomdb.db._STUDY_ROOT_ATTRIBUTES
         for raw in identifier:
             if raw.keyword in attr["SERIES"] or raw.keyword in attr["IMAGE"] or not identifier[raw.keyword].value:
                 delattr(identifier, raw.keyword)
    elif identifier.QueryRetrieveLevel=="SERIES":
         log_data["QueryRetrieveLevel"]="SERIES"
         attr = dicomdb.db._STUDY_ROOT_ATTRIBUTES
         for raw in identifier:
             if  raw.keyword in attr["IMAGE"] or not identifier[raw.keyword].value:
                 delattr(identifier, raw.keyword)
    elif identifier.QueryRetrieveLevel=="PATIENT":
         log_data["QueryRetrieveLevel"]="PATIENT"        
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
        try:
            # for raw in identifier:
                # if raw.keyword=="PatientName" or raw.keyword=="PatientID":
                #     raw.value = str(raw.value).capitalize() 
            if len(identifier)==1:
                log_data["Request_parameters"]="all_studies"
                lg.log_simplified_message(sessionId,"C_FIND","STUDY","All studies","All studies requested","info","","","","All")
                studyQuery= session.query(dicomdb.db.Study)
                matches=studyQuery.all()
            else:
                log_data["Request_parameters"] = [f"{raw.keyword}: {raw.value}" for raw in identifier if raw.keyword != "QueryRetrieveLevel"]
                if identifier.QueryRetrieveLevel=="STUDY":
                    matchedInstances=dicomdb.db.search("1.2.840.10008.5.1.4.1.2.2.1",identifier,session)
                    uniqueStudies= get_uniqueStudies(matchedInstances)
                    studyQuery= session.query(dicomdb.db.Study)
                    studyQuery = studyQuery.filter(dicomdb.db.Study.study_instance_uid.in_(uniqueStudies))
                    matches=studyQuery.all()
                    lg.log_simplified_message(sessionId,"C_FIND","STUDY","",str([f"{raw.keyword}: {raw.value}" for raw in identifier if raw.keyword != "QueryRetrieveLevel"]),"Info","","","",len(matches))
                elif identifier.QueryRetrieveLevel=="SERIES":
                    matchedInstances=dicomdb.db.search("1.2.840.10008.5.1.4.1.2.2.1",identifier,session)
                    uniqueSeries= get_uniqueSeries(matchedInstances,identifier)
                    seriesQuery= session.query(dicomdb.db.Series)
                    seriesQuery= seriesQuery.filter(dicomdb.db.Series.series_instance_uid.in_(uniqueSeries))
                    matches=seriesQuery.all()
                    lg.log_simplified_message(sessionId,"C_FIND","SERIES","",str([f"{raw.keyword}: {raw.value}" for raw in identifier if raw.keyword != "QueryRetrieveLevel"]),"Info","","","",len(matches))
                elif identifier.QueryRetrieveLevel=="PATIENT":
                    matchedInstances=dicomdb.db.search("1.2.840.10008.5.1.4.1.2.1.1",identifier,session)
                    uniquePatients= get_unique_patients(matchedInstances)
                    patientQuery= session.query(dicomdb.db.Patient)
                    patientQuery= patientQuery.filter(dicomdb.db.Patient.patient_id.in_(uniquePatients))
                    matches=patientQuery.all()
                    lg.log_simplified_message(sessionId,"C_FIND","PATIENT","",str([f"{raw.keyword}: {raw.value}" for raw in identifier if raw.keyword != "QueryRetrieveLevel"]),"Info","","","",len(matches))
            log_data["matches"]= len(matches)
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
                        response_dataset.InstitutionName = get_other_levels_tags("STUDY","institution_name",getattr(instance,"study_instance_uid"))
                        response_dataset.PatientBirthDate = get_other_levels_tags("STUDY","birth_date",getattr(instance,"study_instance_uid"))
                        response_dataset.PatientSex = get_other_levels_tags("STUDY","patient_sex",getattr(instance,"study_instance_uid"))
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
ae.add_supported_context(CTImageStorage,JPEG2000)


def handle_store(event):
    global log_data
    log_data["Request_Type"]="C-STORE"
    # lg.detailed_logger.info(f"C-STORE request received: {event.dataset}")
    file_name = f"received"
    event.dataset.file_meta = event.file_meta
    event.dataset.save_as(os.path.join('./dicom_files/received',file_name),write_like_original=False)

    return 0x0000


def handle_echo(event):
    assoc_id = assoc_sessions.get(event.assoc, str(int(time.time() * 1000000)))
   
    lg.log_simplified_message(sessionId,"C_ECHO","","","","Info","","","","")
    global log_data
    log_data["Request_Type"]="C-ECHO"
    print("Loggg",log_data)
    # lg.detailed_logger.info(f"C-ECHO request received")
    e=event
    return 0x0000

def handle_move(event):
    assoc = event.assoc
    assoc_id = assoc_sessions.get(event.assoc, str(int(time.time() * 1000000)))
    move_id = str(int(time.time() * 1000000))
    addr= assoc.requestor.address
    port= assoc.requestor.port
    # lg.detailed_logger.info(f"C-MOVE request received: {event.identifier}")
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
        lg.log_simplified_message(sessionId,"C_Move","STUDY",event.identifier.StudyInstanceUID,{tag: str(value) for tag, value in event.identifier.items()},"Info","","","",len(matching))

        if 'StudyInstanceUID' in event.identifier:
            for instance in instances:
                if instance.StudyInstanceUID == event.identifier.StudyInstanceUID:
                    
                    matching = [
                        instance for instance in instances if instance.StudyInstanceUID == event.identifier.StudyInstanceUID
                    ]
       
    elif event.identifier.QueryRetrieveLevel == 'SERIES':
        lg.log_simplified_message(sessionId,"C_Move","SERIES",event.identifier.StudyInstanceUID,{tag: str(value) for tag, value in event.identifier.items()},"Info","","","",len(matching))
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

def handle_abort(event):
    global log_data
    global sessionId
    log_data["status"]="Aborted"
    global lock
    lock= 0
    redis_client.rpush("requests", json.dumps(log_data))
    lg.log_simplified_message(sessionId,"Association aborted","","","","Warning",versionName,event.assoc.requestor.address,event.assoc.requestor.port,"")
    sessionId=0
    print("Abooort")
    



handlers = [
    (evt.EVT_ACSE_RECV, handle_assoc),
    (evt.EVT_RELEASED, handle_release),
    (evt.EVT_C_FIND, handle_find),
    (evt.EVT_C_STORE, handle_store),
    (evt.EVT_C_ECHO, handle_echo),
    (evt.EVT_C_MOVE, handle_move),
    (evt.EVT_C_GET, handle_get),
    (evt.EVT_ABORTED,handle_abort),
    # (evt.EVT_CONN_CLOSE,handle_con_closed),
    # (evt.EVT_PDU_RECV,handle_con_open),
    
]




def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def start_dicom_server():
    block_scanners=os.getenv('blackhole', "False")
    #print("ABC",block_scanners)
    try:
        if block_scanners=="True":
            network_handler.block_known_scanners("bl.txt","known_scanners")
        else:
            a=0
            #network_handler.allow_scanners("known_scanners")
    except Exception as e:
        #print(e)
        pass    
    #ip='172.18.204.133'
    ip="localhost"
    #print("aaaaaaaaaaa",dock_env)
    if dock_env =="True":
        ip= '172.29.0.3'
    dicom_port = 11112
    if is_port_in_use(dicom_port):
        print(f"Port {dicom_port} is in use. Please free up the port and try again.")
        return
    print("Server Started on port", ip,dicom_port)
    dicomdb.initialize_database()
    ae.start_server((ip,dicom_port), evt_handlers=handlers,)
    
tci = tcia_management(storagedirectory,redis_client,1,dicomdb)
tci.start()
hs = hash_checker(storagedirectory, redis_client,"hash_store.json")
hs.start()


start_dicom_server()

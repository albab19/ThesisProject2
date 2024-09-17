from lib2to3.fixes.fix_input import context
from datetime import datetime
from pydicom.uid import DigitalXRayImageStorageForPresentation,  JPEGBaseline8Bit, MRImageStorage,SecondaryCaptureImageStorage,ExplicitVRLittleEndian,ImplicitVRLittleEndian,CTImageStorage, PYDICOM_IMPLEMENTATION_UID, OphthalmicPhotography8BitImageStorage, JPEG2000 , AllTransferSyntaxes
from pynetdicom import AE, evt, debug_logger, AllStoragePresentationContexts ,StoragePresentationContexts, VerificationPresentationContexts,QueryRetrievePresentationContexts,build_context
from pynetdicom.sop_class import (PatientRootQueryRetrieveInformationModelFind,Verification,StudyRootQueryRetrieveInformationModelMove,PatientRootQueryRetrieveInformationModelGet,StudyRootQueryRetrieveInformationModelFind,StudyRootQueryRetrieveInformationModelGet,CTImageStorage)
from pydicom.dataset import Dataset
import socket,time
import os 
from datetime import datetime
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut
import sqlite3
debug_logger()

ae = AE()

for context in StoragePresentationContexts:
        context._as_scp=True
        context._as_scu=True
        context.scp_role=True
        context.scu_role=True
        #context.transfer_syntax=[ JPEGBaseline8Bit] 
        #print("AllStoragePresentationContexts",context.scp_role)

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
    print("There is a ",len(matching)," match!", "for study :",)
    yield len(matching)
    

    for instance in matching:
        if event.is_cancelled:
            yield 0xFE00, None
        abstractSyn= str(instance.SOPClassUID)
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
                #instance.is_implicit_VR = True
                #instance.is_little_endian = True
                #context.transfer_syntax[0]=UID(instance.file_meta.TransferSyntaxUID)
                #instance.decompress()
                #instance.decompress()
                # Set the transfer syntax to Implicit VR Little Endian
                #instance.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
                print("AcceptedAfterAssociat",context)
                yield 0xFF00, send
                os.remove("./decompressed_dicom.dcm")
        
    yield 0x0000, None


def handle_assoc(event):
    e=event


def handle_release(event):
    e=event
   

def handle_find(event):

    instances = []
    matching = []

    storagedirectory = './dicom_files/received'

    for path in os.listdir(storagedirectory):
        instances.append(dcmread(os.path.join(storagedirectory, path)))

    if 'QueryRetrieveLevel' not in event.identifier:
        yield 0xC000, None
        return
    def date_in_range(datestr, date_range):
        if '-' in event.identifier.StudyDate:
            startdate, enddate = event.identifier.StudyDate.split('-')
            startdateobject = datetime.strptime(startdate, '%Y%m%d')
            enddateobject = datetime.strptime(enddate, '%Y%m%d')
        else:
            startdate= enddate = date_range
        return startdateobject <= datetime.strptime(datestr, '%Y%m%d') <= enddateobject
    

    if event.identifier.QueryRetrieveLevel == 'STUDY' or event.identifier.QueryRetrieveLevel == 'PATIENT':
        if 'PatientName' in event.identifier:
            print("mr", event.identifier.PatientName)
            if event.identifier.PatientName not in ['*', '', '?']:
                for instance in instances:
                    print("mr2", instance.PatientName)
                    print("stripped value", event.identifier.PatientName)
                    if instance.PatientName == event.identifier.PatientName:
                        print("aaaaaaa", str(instance.PatientName))
                        matching.append(instance)
                        print("matchinginstance", instance)


        #study_date = datetime.strptime(event.identifier.StudyDate, '%Y%m%d').date()
        if 'PatientID' in event.identifier:
            print("mr",event.identifier.PatientID)
            if event.identifier.PatientID not in ['*', '', '?']:
                for instance in instances:
                    print("mr2", instance.PatientID)
                    print("stripped value", event.identifier.PatientID.strip('*'))
                    if  instance.PatientID == event.identifier.PatientID.strip('*'):
                        print("aaaaaaa",str(instance.PatientID))
                        matching.append(instance)
                        print("matchinginstance", instance)


        elif 'StudyDate' in event.identifier:
            if 'StudyDate' in event.identifier:
                if event.identifier.StudyDate not in ['*', '', '?']:
                    for instance in instances:
                        print("typeo of instance", type(instance.StudyDate))
                        print("typeo of event identifier", type(event.identifier.StudyDate))
                        if instance.StudyDate == event.identifier.StudyDate:
                            print("work?")
                            print("matchinginstance", instance)
                            matching.append(instance)


        elif 'StudyDesctiption' in event.identifier:
            if 'StudyDescription' in event.identifier:
                if event.identifier.StudyDescription not in ['*', '', '?']:
                    for instance in instances:
                        print("typeo of instance", type(instance.StudyDescription))
                        print("typeo of event identifier", type(event.identifier.StudyDescription))
                        if instance.StudyDescription == event.identifier.StudyDescription:
                            print("work?")
                            print("matchinginstance", instance)
                            matching.append(instance)


        elif 'AccessionNumber' in event.identifier:
            if 'AccessionNumber' in event.identifier:
                if event.identifier.AccessionNumber not in ['*', '', '?']:
                    for instance in instances:
                        print("typeo of instance", type(instance.AccessionNumber))
                        print("typeo of event identifier", type(event.identifier.AccessionNumber))
                        if instance.AccessionNumber == event.identifier.AccessionNumber:
                            print("work?")
                            print("matchinginstance", instance)
                            matching.append(instance)

    for instance in matching:
        print("INST", instance)

        if event.is_cancelled:
            yield 0xC000, None
            return

        identifier = Dataset()

        identifier.PatientID = instance.get('PatientID')
        identifier.StudyInstanceUID = instance.get('StudyInstanceUID')
        identifier.QueryRetrieveLevel = event.identifier.QueryRetrieveLevel
        identifier.SOPInstanceUID = instance.get('SOPInstanceUID')
        identifier.SOPClassUID= instance.get('SOPClassUID')

        identifier.QueryRetrieveLevel = event.identifier.QueryRetrieveLevel

        print("MYIDENTIFIER", identifier)
        #GET with instance and
        # Pending
        yield (0xFF00, identifier)




def handle_store(event):
    file_name = f"received"
    event.dataset.file_meta = event.file_meta
    #event.file_meta,
    event.dataset.save_as(os.path.join('./dicom_files/received',file_name),write_like_original=False)
    print(f"DICOM file saved as {file_name}")
    #print(event.dataset.file_meta)

    return 0x0000




def handle_echo(event):
    e=event

def handle_move(event):
    assoc = event.assoc
    addr= assoc.requestor.address
    port= assoc.requestor.port
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


def initialize_database():
    conn = sqlite3.connect('database.db')
    conn.executescript("BEGIN; " + "".join([f"DELETE FROM {row[0]}; " for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")]) + "COMMIT;")
    cursor = conn.cursor()

    for path in os.listdir(storagedirectory):
        instance = dcmread(os.path.join(storagedirectory, path))
        print("instance", instance)
        patientId = instance.PatientID
        if instance.get('NumberOfFrames') == None:
              instance.NumberOfFrames='1'
        
        try:
            patient_attrs = {
            'PatientID': 'PATIENT_ID',
            'PatientName': 'PATIENT_NAME',
            'PatientBirthDate': 'PATIENT_BIRTHDATE',
            'PatientSex': 'PATIENT_SEX'
            }
            available_attrs = {attr: db_column for attr, db_column in patient_attrs.items() if hasattr(instance, attr)}
            if available_attrs:
                columns = ', '.join(available_attrs.values())
                placeholders = ', '.join(['?'] * len(available_attrs))
                values = tuple(str(getattr(instance, attr)) for attr in available_attrs)
                #print("columns", columns)
                #print("values", values)
                
                # Insert patient data
                query = f"INSERT INTO PATIENT ({columns}) VALUES ({placeholders})"
                cursor.execute(query, values)
                
                # Fetch PATIENT_PRKEY
                PATIENT_PRKEY_query = "SELECT PATIENT_PRKEY FROM PATIENT WHERE PATIENT_ID = ?"
                cursor.execute(PATIENT_PRKEY_query, (patientId,))
                PATIENT_PRKEY = cursor.fetchone()[0]

                # Prepare study attributes
                study_attrs = {
                    'StudyInstanceUID': 'STUDY_INSTANCE_UID',
                    'StudyID': 'STUDY_ID',
                    'StudyDate': 'STUDY_DATE',
                    'StudyTime': 'STUDY_TIME',
                    'StudyDescription': 'STUDY_DESCRIPTION',
                    'AccessionNumber': 'ACCESSION_NUMBER',
                    'ReferringPhysicianName': 'REFER_PHYSICIAN',
                    'Modality': 'MODALITIES_IN_STUDY',
                    'StationName': 'STATION_NAME',
                    'InstitutionalDepartmentName': 'INSTITUTIONAL_DEPARTMENT_NAME',
                    'PatientAge': 'PATIENT_AGE',
                    'PatientWeight': 'PATIENT_WEIGHT',
                    'InstitutionName': 'INSTITUTION_NAME',
                    'StudyStatusID': 'STUDY_STATUS',
                    'SeriesNumber': 'SERIES_COUNT',
                    'StudyComments': 'STUDY_COMMENTS',
                    'SpecificCharacterSet': 'CHARACTER_SET'
                }

                available_study_attrs = {attr: db_column for attr, db_column in study_attrs.items() if hasattr(instance, attr)}
                if available_study_attrs:
                    columns = ', '.join(available_study_attrs.values()) + ', PATIENT_PRKEY'
                    placeholders = ', '.join(['?'] * (len(available_study_attrs) + 1))
                    values = tuple(str(getattr(instance, attr)) for attr in available_study_attrs) + (PATIENT_PRKEY,)
                    #print("columns", columns)
                    #print("values", values)
                    
                    # Insert study data
                    query = f"INSERT INTO STUDY ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, values)
                    
                    # Get StudyInstanceUID for series attributes
                    studyInstanceUID = instance.get("StudyInstanceUID", None)
                    serie_attrs = {
                        'SeriesInstanceUID': 'SERIES_INSTANCE_UID',
                        'SeriesNumber': 'SERIES_NUMBER',
                        'SeriesDate': 'SERIES_DATE',
                        'SeriesTime': 'SERIES_TIME',
                        'SeriesDescription': 'SERIES_DESCRIPTION',
                        'Modality': 'MODALITY',
                        'PatientPosition': 'PATIENT_POSITION',
                        'ContrastBolusAgent': 'CONTRAST_BOLUS_AGENT',
                        'Manufacturer': 'MANUFACTURER',
                        'ModelName': 'MODEL_NAME',
                        'BodyPartExamined': 'BODY_PART_EXAMINED',
                        'ProtocolName': 'PROTOCOL_NAME',
                        'NumberOfFrames': 'IMAGE_COUNT',
                        'FrameOfReferenceUID': 'FRAME_OF_REFERENCE_UID',
                        'LocalizerInstanceUID': 'LOCALIZER_INSTANCE_UID'
                    }
                    available_serie_attrs = {attr: db_column for attr, db_column in serie_attrs.items() if hasattr(instance, attr)}
                    if available_serie_attrs:
                        columns = ', '.join(available_serie_attrs.values()) + ', STUDY_INSTANCE_UID'
                        placeholders = ', '.join(['?'] * (len(available_serie_attrs) + 1))
                        values = tuple(str(getattr(instance, attr)) for attr in available_serie_attrs) + (studyInstanceUID,)
                        print("columns", columns)
                        print("values", values)
                        
                        # Insert series data
                        query = f"INSERT INTO SERIES ({columns}) VALUES ({placeholders})"
                        cursor.execute(query, values)
                    else:
                        print("No series attributes available to insert")
                else:
                    print("No study attributes available to insert")
        except Exception as e:
            print(f"Error occurred: {e}")

    conn.commit()
    conn.close()

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def start_dicom_server():
    dicom_port = 11112
    if is_port_in_use(dicom_port):
        print(f"Port {dicom_port} is in use. Please free up the port and try again.")
        return
    print("Server Started")
    initialize_database()
    ae.start_server(('172.30.160.1', dicom_port), evt_handlers=handlers)
    

start_dicom_server()

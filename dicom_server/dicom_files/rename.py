import pydicom, random
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid 

# ds = pydicom.dcmread('./PX2')
# # print(ds.SeriesInstanceUID)
# # ds.Modality="MR"
# # ds.SeriesInstanceUID="1.2.826.0.1.3680043.8.1055.1.20111102150758591.96842950.07877444"
# # ds.StudyInstanceUID= "1.2.826.0.1.3680043.8.1055.1.20111102150758591.92402465.76095229"
# # ds.PatientName="Jonathan Vestergaard"
# # ds.PatientID= str(random.randint(273,2938383))
# ds.PatientName="Klaus Damsgaard"
# ds.save_as("./PX2")
# #ds.save_as('./ct/CT (24).dcm')
import os
# a=0
# danish_full_names = [
#     "Anders Petersen", "Mikkel Jensen", "Jørgen Hansen", "Lars Nørgaard", "Henrik Madsen",
#     "Magnus Jørgensen", "Rasmus Carlsen", "Søren Kjær", "Frederik Mortensen", "Kasper Lund",
#     "Emil Kristensen", "Tobias Svendsen", "Mads Thomsen", "Jesper Lauridsen", "Nikolaj Winther",
#     "Freja Rasmussen", "Astrid Poulsen", "Ida Mogensen", "Malene Dam", "Sofie Bech",
#     "Mette Dahl", "Helle Bertelsen", "Anne Dideriksen", "Lærke Brodersen", "Signe Mathiesen",
#     "Karoline Lund", "Gitte Gregersen", "Line Frank", "Agnete Koch", "Pernille Eriksen",
#     "Cecilie Thorsen"
# ]
pat= "./received/"
for f in os.listdir(pat):
     
    # p=str(random.randint(277853,29383783))
    # s=str(random.randint(1,632))
    ds = pydicom.dcmread(os.path.join(pat,f))
    if(ds.StudyInstanceUID=="1.2.826.0.1.3680043.8.1055.1.20111102150758591.92402465.76075429" or ds.StudyInstanceUID=="1.2.826.0.1.3680043.8.1055.1.20111102150758591.92402465.76095829"):
         print(ds.PatientName)
    # if ds.PatientName=="Christian Niassen":
    #     ds.PatientName="Klaus Damsgaard"
    # ds.SeriesInstanceUID="1.2.826.0.1.3680043.8.1055.1.20111102150758591.96842950.078774"+str(a)
    # ds.StudyInstanceUID= "1.2.826.0.1.3680043.8.1055.1.20111102150758591.92402465.760929"+str(a)
    # ds.PatientName=danish_full_names[a]
    # ds.PatientID= p
    #ds.StudyID= str(random.randint(5,100))
    #ds.AccessionNumber=p
    import random
    from datetime import datetime, timedelta

    # Define the range
    start_date = datetime(2023, 12, 10)
    end_date = datetime(2024, 12, 1)

    # Generate a random date within the range
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    # Format the date as YYYY/MM/DD
    formatted_date = random_date.strftime("%Y%m%d")
    formatted_date
    # ds.StudyDate=formatted_date
    # #print(formatted_date)
    
    # ds.save_as(os.path.join("./received/",f))
#     a+=1
#     print(ds.PatientName)
    
    
    
    
# if ds.PatientName=="Anonymized^^" :
#         ds.PatientName="Ronnie Nikolajsen"
#         ds.PatientID= p
#         ds.save_as(os.path.join("./received/",f))
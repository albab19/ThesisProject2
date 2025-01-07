
import sqlite3, os, traceback
from pydicom import dcmread , Dataset
from pydicom.uid import UID
from sqlalchemy import create_engine, Column, Integer, String, MetaData,text, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pynetdicom.apps.qrscp import db
Base = declarative_base()
storagedirectory= './dicom_files/received/'
db_file = './../db.db'
if os.getenv('Docker_ENV', 'False')=="True":
    db_file = '/app/db.db'

#engine=db.create("sqlite:///db.db")
engine = create_engine(f'sqlite:///{db_file}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()



#print("Seeeeeeeeeeesion",session)


def initialize_database():
    try:
        delete_statement = delete(db.Instance)
        session.execute(delete_statement)
        session.commit()
    
        #print("hhhhh",os.listdir("./"))
        for path in os.listdir(storagedirectory):
            instance = dcmread(os.path.join(storagedirectory, path))
            # for raw in instance:
            #     if raw.keyword=="PatientName" or raw.keyword=="PatientID":
            #         raw.value = str(raw.value).capitalize()              
            db.add_instance(instance,session,path)
            session.commit()
        print("Database initialized from DICOM storage")
    except Exception as e:
        print(e) 
        pass

""" query = Dataset()
query.QueryRetrieveLevel = "PATIENT"
query.PatientID = 1 """

""" q = db._search_single_value(query["PatientID"], session)
with engine.connect() as connection:
   print("search singleValue",q)
   r= connection.execute(text(str(q))) """
   
    
    
def search_study_in_db(event_identifier):

    
    result=db._search_single_value(UID("1.2.840.10008.5.1.4.1.2.2.1"),event_identifier,session)
    return result    
        
"""  conn = sqlite3.connect('database.db')
cursor = conn.cursor()
for a in event_identifier.items():
    print("event_id",event_identifier.get_item(a[0]).name)
studyKeywords={
    'StudyInstanceUID': 'STUDY_INSTANCE_UID',
    'StudyDate': 'STUDY_DATE',
    'StudyDescription': 'STUDY_DESCRIPTION',

}
keyword_to_column = {
'PatientID': 'PATIENT_ID',
'PatientName': 'PATIENT_NAME',
'PatientBirthDate': 'PATIENT_BIRTHDATE',
'PatientSex': 'PATIENT_SEX',
'SeriesInstanceUID': 'SERIES_INSTANCE_UID',  # Optional, add this if needed
'ModalitiesInStudy': 'MODALITIES_IN_STUDY',
'AccessionNumber': 'ACCESSION_NUMBER',
'ReferringPhysicianName': 'REFER_PHYSICIAN'
}

# Initialize the query parts
base_query = "SELECT * FROM STUDY WHERE "
conditions = []
values = []

# Iterate over the keywords and check if they exist in the event identifier
for keyword, column in keyword_to_column.items():
    if keyword in event_identifier and event_identifier.get(keyword):
        conditions.append(f"{column} = ?")
        values.append(str(event_identifier.get(keyword)))

# Build the final query if any conditions were found
if conditions:
    query = base_query + " AND ".join(conditions)
    print(f"Executing query: {query} with values {values}")
    cursor.execute(query, values)
    results = cursor.fetchall()

    return results  # Return the results of the query
else:
    print("No matching DICOM attributes found in the event identifier.")
    return None """
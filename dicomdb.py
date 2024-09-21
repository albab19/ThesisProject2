
import sqlite3, os, traceback
from pydicom import dcmread , Dataset
from pydicom.uid import UID
from sqlalchemy import create_engine, Column, Integer, String, MetaData,text, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pynetdicom.apps.qrscp import db
Base = declarative_base()
storagedirectory= './dicom_files/received/'
db_file = './db.db'





def get_table_schema(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Query to get the schema of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema = {}
    for table_name in tables:
        table_name = table_name[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = columns

    conn.close()
    return schema


#engine=db.create("sqlite:///db.db")
engine = create_engine(f'sqlite:///{db_file}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()



#print("Seeeeeeeeeeesion",session)


def initialize_database():
    
    delete_statement = delete(db.Instance)
    session.execute(delete_statement)
    session.commit()
    
    for path in os.listdir(storagedirectory):
        instance = dcmread(os.path.join(storagedirectory, path))
        db.add_instance(instance,session,path)
        #db.remove_instance("1.2.826.0.1.3680043.8.1055.1.20111102150758591.03296050.69180943",session)
        session.commit()
    print("Database initialized from DICOM storage")

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
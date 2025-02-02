import sys, os

sys.path.append(os.path.abspath(".."))
import dicomdb
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


def get_mock_db_session():
    Base = declarative_base()
    engine = create_engine(f'sqlite:///{"./mock_database.db"}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


database_patcher = patch.multiple(
    "dicomdb",
    session_scope=Mock(return_value=get_mock_db_session()),
    storagedirectory="./mock_dicom_files/",
)
logger_patcher = patch.multiple(
    "logger.DicomLogger",
    set_log_info=Mock(return_value="nothing"),  # Ignorring logging
    log_simplified_message=Mock(return_value="nothing"),
)

configuration_patcher = patch.multiple(
    "config",
    DICOM_STORAGE_DIR="./mock_dicom_files/",
    assign_runtime_contexts_support=Mock(return_value=""),
)


database_patcher.start()
logger_patcher.start()
configuration_patcher.start()


def setup_mock_db():

    dicomdb.initialize_database()

    # Verify the mock database is set up correctly
    assert len(dicomdb.query_all_studies()) == 5
    assert len(dicomdb.query_all_patients()) == 5

    yield
    # Clean up the mock database after all tests are done
    dicomdb.delete_database()

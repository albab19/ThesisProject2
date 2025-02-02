# This module utilizes the Event-Driven Model in pynetdicom to provide a specific implemimentation of the dicom server
# The module

from lib2to3.fixes.fix_input import context
from pynetdicom import evt
import socket, traceback
import logger as lg
from integrity_checker import hash_checker
from tcia_management import tcia_management
from pynetdicom.apps.qrscp import handlers
import dicomdb
import network_threat_handler as network_handler
import config
import dicom_handlers

config.initialize_logging()

ae = config.initialize_application_entity()

handlers = [
    (evt.EVT_ACSE_RECV, dicom_handlers.handle_assoc),
    (evt.EVT_RELEASED, dicom_handlers.handle_release),
    (evt.EVT_C_FIND, dicom_handlers.handle_find),
    (evt.EVT_C_STORE, dicom_handlers.handle_store),
    (evt.EVT_C_ECHO, dicom_handlers.handle_echo),
    (evt.EVT_C_MOVE, dicom_handlers.handle_move),
    (evt.EVT_C_GET, dicom_handlers.handle_get),
    (evt.EVT_ABORTED, dicom_handlers.handle_abort),
]


def start_functional_threads():
    tci = tcia_management(config.DICOM_STORAGE_DIR, 1, dicomdb)
    tci.start()
    hs = hash_checker(config.DICOM_STORAGE_DIR, "hash_store.json")
    hs.start()


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("0.0.0.0", port)) == 0


def start_dicom_server():
    cheack_blackhole_status()
    ip = config.DICOM_SERVER_HOST
    dicom_port = config.DICOM_PORT
    if is_port_in_use(dicom_port):
        print(f"Port {dicom_port} is in use. Please free up the port and try again.")
        return
    print("Server Started on port", ip, dicom_port)
    dicomdb.initialize_database()
    ae.start_server(
        (ip, dicom_port),
        evt_handlers=handlers,
    )


def cheack_blackhole_status():
    try:
        if config.blackhole_activated():
            network_handler.block_known_scanners("bl.txt", "known_scanners")
        else:
            network_handler.allow_scanners("known_scanners")
    except Exception as e:
        pass


try:
    start_functional_threads()
    start_dicom_server()
except Exception:
    traceback.print_exc()

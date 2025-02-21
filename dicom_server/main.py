import sys, os

sys.path.append(os.path.abspath("./core/"))
from app_container import ApplicationContainer


app = ApplicationContainer()
app.dicom_application().start_the_application()

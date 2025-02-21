FROM python:3.9-slim
USER root

COPY ./storage/db.db app/

COPY . .



WORKDIR /.
RUN pip install --upgrade pip  && pip install -r requirements.txt && apt-get update &&  apt-get -qq install iptables ipset


COPY ./core//service_class.py   /usr/local/lib/python3.9/site-packages/pynetdicom/service_class.py
COPY ./core/db.py ./usr/local/lib/python3.9/site-packages/pynetdicom/apps/qrscp/db.py
COPY ./core/valuerep.py /usr/local/lib/python3.9/site-packages/pydicom/valuerep.py
EXPOSE 11112
CMD ["python","-u" ,"main.py"]

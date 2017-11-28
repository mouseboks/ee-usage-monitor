FROM ubuntu:latest

RUN apt-get update
RUN apt-get install --no-install-recommends --no-install-suggests -y python3-setuptools ca-certificates
RUN easy_install3 pip
RUN pip install flask flask-jsonpify flask-restful influxdb python-json-logger

ADD conf/* /ee-monitor-api/conf/
ADD ee-monitor-api.py /ee-monitor-api/

WORKDIR /ee-monitor-api/

CMD python3 /ee-monitor-api/ee-monitor-api.py

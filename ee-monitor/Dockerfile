FROM ubuntu:latest

RUN apt-get update
RUN apt-get install --no-install-recommends --no-install-suggests -y python3-setuptools ca-certificates
RUN easy_install3 pip
RUN pip install urllib3 requests lxml bs4 influxdb python-json-logger

ADD conf/* /ee_monitor/conf/
ADD /ee_monitor/* /ee_monitor/

WORKDIR /ee_monitor/

CMD python3 /ee_monitor/ee_monitor.py

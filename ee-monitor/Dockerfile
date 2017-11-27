FROM ubuntu:latest

RUN apt-get update
RUN apt-get install --no-install-recommends --no-install-suggests -y python3-setuptools ca-certificates
RUN easy_install3 pip
RUN pip install urllib3 requests lxml bs4 influxdb

ADD conf/* /ee-monitor/conf/
ADD ee-monitor.py /ee-monitor/

CMD python3 /ee-monitor/ee-monitor.py

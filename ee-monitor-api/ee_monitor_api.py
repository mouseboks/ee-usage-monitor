"""Provide a REST API to retrieve remaining days and data from InfluxDB"""
import logging
import logging.config

from configparser import ConfigParser

from flask import Flask
from flask_restful import Resource, Api

from influxdb import InfluxDBClient


CONFIG = ConfigParser()
CONFIG.read('conf/ee-monitor-api.ini')

logging.config.fileConfig('conf/ee-monitor-api-logging.ini')
LOGGER = logging.getLogger(CONFIG.get("Logging", "logger_name"))

INFLUX = "Influx"
MYCLIENT = InfluxDBClient(CONFIG.get(INFLUX, "host"), \
                            CONFIG.getint(INFLUX, "port"), \
                            CONFIG.get(INFLUX, "user"), \
                            CONFIG.get(INFLUX, "password"), \
                            CONFIG.get(INFLUX, "dbname"))

APP = Flask(__name__)
API = Api(APP)

class EEData(Resource):
    def get(self):
        result = MYCLIENT.query('select * from "ee-data-remaining" order by time desc limit 1;')
        return list(result.get_points())

API.add_resource(EEData, '/eedata')

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port='5002')

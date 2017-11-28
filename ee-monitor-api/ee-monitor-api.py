from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask.ext.jsonpify import jsonify

from influxdb import InfluxDBClient

import logging
import logging.config

from configparser import ConfigParser

config = ConfigParser()
config.read('conf/ee-monitor-api.ini')

logging.config.fileConfig('conf/ee-monitor-api-logging.ini')
logger = logging.getLogger(config.get("Logging", "logger_name"))

influxSection = "Influx"
myclient = InfluxDBClient(config.get(influxSection, "host"), config.getint(influxSection, "port"), config.get(influxSection, "user"), config.get(influxSection, "password"), config.get(influxSection, "dbname"))


app = Flask(__name__)
api = Api(app)

class EEData(Resource):
    def get(self):
         query = 'select * from "ee-data-remaining" order by time desc limit 1;'
         result = myclient.query(query)
         return list(result)


api.add_resource(EEData, '/eedata')

if __name__ == '__main__':
     app.run(host='0.0.0.0', port='5002')
import urllib3
import json
import requests
import logging
import logging.config
from pythonjsonlogger import jsonlogger

import sys
import os
import time

#import loggly.handlers

from configparser import ConfigParser

from bs4 import BeautifulSoup

from influxdb import InfluxDBClient
from influxdb import SeriesHelper


config = ConfigParser()
config.read('conf/ee-monitor.ini')

accountconfig = ConfigParser()
config.read('conf/ee-accounts.ini')

logging.config.fileConfig('conf/ee-monitor-logging.ini')
logger = logging.getLogger(config.get("Logging", "logger_name"))

influxSection = "Influx"
myclient = InfluxDBClient(config.get(influxSection, "host"), config.getint(influxSection, "port"), config.get(influxSection, "user"), config.get(influxSection, "password"), config.get(influxSection, "dbname"))


class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = myclient

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = 'ee-data-remaining'

        # Defines all the fields in this time series.
        fields = ['mifi_data_remaining', 'phone_data_remaining']

        # Defines all the tags for the series.
        tags = []

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 1

        # autocommit must be set to True when using bulk_size
        autocommit = True


def retrieveDataRemaining(page_source):
    soup = BeautifulSoup(page_source, 'lxml')

    scripts = soup.find('span', { 'class': 'usage-datapass-header-text2 usage-datapass-header-text2--lg'})
    return float(scripts.contents[1].text)


def login(username, password):
    # FIXME exception trace out of here will contain password in plain text!!!!!
    start_url = 'https://id.ee.co.uk/id/login'
    login_url = 'https://api.ee.co.uk/v1/identity/authorize/login'

    session = requests.Session();

    request = session.get(start_url)
    if request.status_code != 200:
        raise ValueError('Received unexpected status code ' + str(request.status_code) + ' from ' + start_url)

    soup = BeautifulSoup(request.text, 'lxml')
    csrf = soup.find(id="csrf")['value']
    # print csrf
    requestId = soup.find(id="requestId")['value']
    # print requestId
    request_data = {'username': username, 'password': password, 'csrf': csrf, 'requestId': requestId}
    request = session.post(login_url, data = request_data)
    return session


def scrapeDataRemaining(session, url):

    request = session.get(url)
    if request.status_code != 200:
        raise ValueError('Received unexpected status code ' + str(request.status_code) + ' from ' + login_url)

    return retrieveDataRemaining(request.text)


def getDataPoints(mifi_session, phone_session):
    #client = hvac.Client()
    #client = hvac.Client(url='http://localhost:8200')
    phone_url = "https://myaccount.ee.co.uk/my-small-business/"
    mifi_url = "https://myaccount.ee.co.uk/my-mobile-broadband-pay-monthly/"

    try:
        mifi_data_remaining = scrapeDataRemaining(mifi_session, mifi_url)
        logger.info("Retrieved mifi data remaining value of " + str(mifi_data_remaining))
    except Exception as e:
        logger.exception("Failed to scrape mifi data remaining")
        mifi_data_remaining = -1.0

    try:
        phone_data_remaining = scrapeDataRemaining(phone_session, phone_url)
        logger.info("Retrieved phone data remaining value of " + str(phone_data_remaining))
    except Exception as e:
        logger.exception("Failed to scrape mobile data remaining")
        phone_data_remaining = -1.0

    MySeriesHelper(mifi_data_remaining=mifi_data_remaining, phone_data_remaining=phone_data_remaining)
    MySeriesHelper.commit()

def main():
    while True:
        try:
            mifi_session = login(config.get("mifi", "username"),config.get("mifi", "password"))
            phone_session = login(config.get("phone", "username"),config.get("phone", "password"))
            session_usage_count = 0

            #Renew the sessions every 5 hours
            while session_usage_count < (30 * 5):
                getDataPoints(mifi_session, phone_session)
                time.sleep(60*2)
                session_usage_count =  session_usage_count + 1
            session_usage_count = 0
        except Exception as e:
            logger.exception("Exception occurred while trying to scrape")



main()

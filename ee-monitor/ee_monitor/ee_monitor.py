import logging
import logging.config

import time

from configparser import ConfigParser

import requests

from bs4 import BeautifulSoup

from influxdb import InfluxDBClient
from influxdb import SeriesHelper

import page_parser

CONFIG = ConfigParser()
CONFIG.read('conf/ee-monitor.ini')



logging.config.fileConfig('conf/ee-monitor-logging.ini')
LOGGER = logging.getLogger(CONFIG.get("Logging", "LOGGER_name"))

INFLUX = "Influx"
MYCLIENT = InfluxDBClient(CONFIG.get(INFLUX, "host"), \
                            CONFIG.getint(INFLUX, "port"), \
                            CONFIG.get(INFLUX, "user"), \
                            CONFIG.get(INFLUX, "password"), \
                            CONFIG.get(INFLUX, "dbname"))


class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = MYCLIENT

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = 'ee-data-remaining'

        # Defines all the fields in this time series.
        fields = ['mifi_data_remaining', 'mifi_days_remaining', 'phone_data_remaining', 'phone_days_remaining']

        # Defines all the tags for the series.
        tags = []

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 1

        # autocommit must be set to True when using bulk_size
        autocommit = True





def login(username, password):
    # FIXME exception trace out of here will contain password in plain text!!!!!
    start_url = 'https://id.ee.co.uk/id/login'
    login_url = 'https://api.ee.co.uk/v1/identity/authorize/login'

    session = requests.Session()

    request = session.get(start_url)
    if request.status_code != 200:
        raise ValueError('Received unexpected status code ' + str(request.status_code) + ' from ' + start_url)

    soup = BeautifulSoup(request.text, 'lxml')
    csrf = soup.find(id="csrf")['value']
    # print csrf
    request_id = soup.find(id="requestId")['value']
    # print requestId
    request_data = {'username': username, 'password': password, 'csrf': csrf, 'requestId': request_id}
    request = session.post(login_url, data=request_data)
    return session


def get_page_text(session, url):

    request = session.get(url)
    if request.status_code != 200:
        raise ValueError('Received unexpected status code ' + str(request.status_code))

    return request.text


def get_data_points(mifi_session, phone_session):
    #client = hvac.Client()
    #client = hvac.Client(url='http://localhost:8200')
    phone_url = "https://myaccount.ee.co.uk/my-small-business/"
    mifi_url = "https://myaccount.ee.co.uk/my-mobile-broadband-pay-monthly/"

    try:
        text = get_page_text(mifi_session, mifi_url)
        mifi_data_remaining = page_parser.retrieveDataRemaining(text)
        mifi_days_remaining = page_parser.retrieveDaysRemaining(text)
        LOGGER.info("Retrieved mifi data remaining value of " + str(mifi_data_remaining))
    except Exception:
        LOGGER.exception("Failed to scrape mifi data remaining")
        mifi_data_remaining = -1.0

    try:
        text = get_page_text(phone_session, phone_url)
        phone_data_remaining = page_parser.retrieveDataRemaining(text)
        phone_days_remaining = page_parser.retrieveDaysRemaining(text)

        LOGGER.info("Retrieved phone data remaining value of " + str(phone_data_remaining))
    except Exception:
        LOGGER.exception("Failed to scrape mobile data remaining")
        phone_data_remaining = -1.0

    MySeriesHelper(mifi_data_remaining=mifi_data_remaining, mifi_days_remaining=mifi_days_remaining, phone_data_remaining=phone_data_remaining, phone_days_remaining=phone_days_remaining)
    MySeriesHelper.commit()

def main():

    accountconfig = ConfigParser()
    accountconfig.read('conf/ee-accounts.ini')
    while True:
        try:
            mifi_session = login(accountconfig.get("mifi", "username"), accountconfig.get("mifi", "password"))
            phone_session = login(accountconfig.get("phone", "username"), accountconfig.get("phone", "password"))
            session_usage_count = 0

            #Renew the sessions every 5 hours
            while session_usage_count < (30 * 5):
                get_data_points(mifi_session, phone_session)
                time.sleep(60*2)
                session_usage_count = session_usage_count + 1
            session_usage_count = 0
        except Exception:
            LOGGER.exception("Exception occurred while trying to scrape")

if __name__ == "__main__":
    main()

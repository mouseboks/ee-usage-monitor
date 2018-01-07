"""Scrapes remaining data and days from two EE account pages and stores the data in InfluxDB"""
import logging
import logging.config

import collections

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
    request_id = soup.find(id="requestId")['value']

    request_data = {'username': username, 'password': password, 'csrf': csrf, 'requestId': request_id}
    request = session.post(login_url, data=request_data)
    if request.status_code != 200:
        raise ValueError('Received unexpected status code ' + str(request.status_code) + ' from ' + login_url)

    return session


def get_page_text(session, url):

    request = session.get(url)
    if request.status_code != 200:
        raise ValueError('Received unexpected status code ' + str(request.status_code))

    return request.text


def get_data_points(session, url):
    try:
        text = get_page_text(session, url)
        data_remaining = page_parser.retrieveDataRemaining(text)
        days_remaining = page_parser.retrieveDaysRemaining(text)
        LOGGER.info("Retrieved data remaining value of " + str(data_remaining) + " from " + url)
    except Exception:
        LOGGER.exception("Failed to scrape data remaining from " + url)
        data_remaining = -1.0
        days_remaining = -1.0

    return collections.namedtuple('data_points','data,days')(data_remaining,days_remaining)



def main():

    accountconfig = ConfigParser()
    accountconfig.read('conf/ee-accounts.ini')

    while True:
        mifi_data = collections.namedtuple('data_points','data,days')(-1.0,-1.0)
        phone_data = collections.namedtuple('data_points','data,days')(-1.0,-1.0)

        try:
            mifi_session = login(accountconfig.get("mifi", "username"), accountconfig.get("mifi", "password"))
            mifi_data = get_data_points(mifi_session, "https://myaccount.ee.co.uk/my-mobile-broadband-pay-monthly/")
        except Exception as e:
            LOGGER.exception("Exception occurred while trying to scrape mifi data")

        try:
            phone_session = login(accountconfig.get("phone", "username"), accountconfig.get("phone", "password"))
            mifi_data = get_data_points(phone_session, "https://myaccount.ee.co.uk/my-small-business/")
        except Exception as e:
            LOGGER.exception("Exception occurred while trying to scrape phone data")

        MySeriesHelper(mifi_data_remaining=mifi_data.data, mifi_days_remaining=mifi_data.days, phone_data_remaining=phone_data.data, phone_days_remaining=phone_data.days)
        MySeriesHelper.commit()

        time.sleep(60*60) #Wait 1 hour before trying again


if __name__ == "__main__":
    main()

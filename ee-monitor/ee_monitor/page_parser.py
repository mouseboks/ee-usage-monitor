"""Finds the data and days values from the HTML from an EE account page"""
import re

from bs4 import BeautifulSoup

def retrieveDataRemaining(page_source):
    soup = BeautifulSoup(page_source, 'lxml')

    scripts = soup.find('span', { 'class': 'usage-datapass-header-text-bold'})
    return float(scripts.contents[1].text)

def retrieveDaysRemaining(page_source):
    soup = BeautifulSoup(page_source, 'lxml')

    scripts = soup.find('span', { 'class': 'pull-right'})
    if re.search('Ends today',scripts.contents[0]):
        return 0
    else:
        content = re.search('[0-9]+',scripts.contents[0])
        return int(content.group(0))

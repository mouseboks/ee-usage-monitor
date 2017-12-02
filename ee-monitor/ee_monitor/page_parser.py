import re

from bs4 import BeautifulSoup

def retrieveDataRemaining(page_source):
    soup = BeautifulSoup(page_source, 'lxml')

    scripts = soup.find('span', { 'class': 'usage-datapass-header-text2 usage-datapass-header-text2--lg'})
    return float(scripts.contents[1].text)

def retrieveDaysRemaining(page_source):
    soup = BeautifulSoup(page_source, 'lxml')

    scripts = soup.find('span', { 'class': 'usage-datapass-info-1'})
    content = re.search('[0-9]+',scripts.contents[0])
    return int(content.group(0))

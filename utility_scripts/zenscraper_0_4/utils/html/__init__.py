""" utils.html v0_1 function to scrape data from html"""
from os.path import dirname, join, abspath
import sys
import random
from ..files import create_directory
from ..logger import logger

from lxml import etree
from bs4 import BeautifulSoup

sys.path.insert(0, abspath(join(dirname(__file__), "../../..")))
from pyersq.requests_wrapper import RequestsWrapper


def save_html(url='', htmldir='', filename='', driver=None):
    """
    :param url: url of the html page you want to save
    :param htmldir: directory on where to save the html
    :param filename: the filename on the saved directory
    :param driver: this is for selenium, if driver is stated that means
    that we will download the page from selenium, url not needed
    :return:
    """
    logger.info('saving HTML files')
    create_directory(htmldir)

    if driver:
        with open(f'{htmldir}/{filename}.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
    else:
        req = RequestsWrapper()
        res = req.get(url)
        with open(f'{htmldir}/{filename}.html', 'w', encoding='utf-8') as file:
            file.write(res.text)


def get_html_table(driver=None, table_index=0, just_header=False, with_header=False,
                   **kwargs):  # pylint: disable=too-many-locals,too-many-branches
    """
    Getting HTMl Table from <table> tag inside an html
    :param driver: selenium driver to scrape table data
    :param table_index: index of the table to be sraped
    :param just_header: return an array of table header
    :param with_header: boolean if table header will be included in the scrape
    :return: list of dict if with_header == True, list of list if with_header == False
    """
    try:
        logger.info('scraping HTML table from page_source')
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if len(kwargs) > 0:
            tables = soup.find_all('table', **kwargs)
        else:
            tables = soup.find_all('table')

        table_body = tables[table_index].find('tbody')

        if just_header:
            logger.info('scraping the header of the HTML table')
            table_header = tables[table_index].find('thead')
            header = []
            for row in table_header.find_all('tr'):
                for count, col in enumerate(row.find_all('th')):
                    val = col.text.strip()
                    if len(val) == 0:
                        header.append(str(count))
                        continue
                    header.append(col.text.strip())
                return header

        if with_header:
            logger.info('Scraping header of the HTML table with content')
            table_header = tables[table_index].find('thead')
            header = []
            table_data = []
            for row in table_header.find_all('tr'):
                for count, col in enumerate(row.find_all('th')):
                    val = col.text.strip()
                    if len(val) == 0:
                        header.append(str(count))
                        continue
                    header.append(col.text.strip())

            for row in table_body.find_all('tr'):
                data = {}
                for count, col in enumerate(row.find_all('td')):
                    val = col.text.strip()
                    data.update({header[count]: val})
                table_data.append(data)
            return table_data

        logger.info('Scraping the body of the HTML table')
        table_data = []
        for row in table_body.find_all('tr'):
            data = []
            for col in row.find_all('td'):
                data.append(col.text.strip())
            table_data.append(data)
        return table_data
    except Exception as err:  # pylint: disable=broad-except
        logger.error('HTML Table scraping failed!!!')
        logger.error(err)
        return []


def check_link(url, sleep_seconds=None):
    """
    :param url: url of the link to check
    :return: check if link exists
    """
    logger.info('Checking link %s', url)
    if sleep_seconds is None:
        sleep_seconds = random.randint(1, 3)
    req = RequestsWrapper()
    response = req.get(url, sleep_seconds=sleep_seconds)
    logger.info(response.status_code)
    return response.status_code == 200


def print_html(doc=None, is_print=True):
    """
    Print the HTMl file on the console.
    :return: HTML File as a String
    """
    logger.info('Printing HTML')
    if is_print:
        print(etree.tostring(doc, pretty_print=True))
    return etree.tostring(doc, pretty_print=True)

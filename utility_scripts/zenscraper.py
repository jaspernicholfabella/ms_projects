"""Zenscraper Python Library"""
from enum import Enum
import os
import shutil
import re
import csv
import sys
import random
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import lxml.html
from lxml import etree
import pandas as pd
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
sys.path.append('../../scripts')
from pyersq.requests_wrapper import RequestsWrapper

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class ZenScraper:
    """ ZenScraper , stealth scraping that follows selenium rules. """
    doc = None
    response = None

    def __find_elements_list(self, err_message="", xpath="", doc=None):
        """ find multiple elements in the class """
        try:
            element_list = []
            if doc is None:
                doc = self.doc
            elements = doc.xpath(xpath)
            for element in elements:
                element_list.append(ZenElement(element))
            if len(element_list) != 0:
                logger.info('element list generated') #
                return element_list
            logger.warning('no element list found')
            return []
        except (IndexError, lxml.etree.XPathEvalError,
                lxml.etree.Error, lxml.etree.XPathError) as err:
            logger.warning(err_message)
            logger.error(f'{err}') # pylint: disable=logging-fstring-interpolation
            return None

    def __find_element(self, err_message="", xpath="", doc=None):
        """ find single element from the class """
        try:
            if doc is None:
                doc = self.doc
            element = doc.xpath(xpath)
            logger.info(f'{ZenElement(element[0]).get_tag()} element found') # pylint: disable=logging-fstring-interpolation
            return ZenElement(element[0])
        except (IndexError, lxml.etree.XPathEvalError, lxml.etree.XPathError,
                lxml.etree.Error) as err:
            logger.warning(err_message)
            logger.error(f'{err}') # pylint: disable=logging-fstring-interpolation
            return None

    @staticmethod
    def __return_dict_values(by_mode, to_search, doc=None, tag="node()"):
        output_dict = {
            1: {'err_message': "<Error: id cannot be found on the html>",
                'xpath': f'//node()[@id="{to_search}"]',
                'doc': doc},
            2: {'err_message': "<Error: element cannot be found on the html>",
                'xpath': to_search,
                'doc': doc},
            3: {'err_message': f"<Error: no element that contains {to_search} in the html>",
                'xpath': f'//{tag}[normalize-space(text()) = "{to_search}"]',
                'doc': doc},
            4: {'err_message': f"<Error: no element that contains {to_search} in the html>",
                'xpath': f'//{tag}[contains(text(), "{to_search}")]',
                'doc': doc},
            6: {'err_message': "<Error: tagname cannot be found on the html>",
                'xpath': f"//{to_search}",
                'doc': doc},
        }
        return output_dict[by_mode.value]

    def get(self, url, sleep_seconds=None):
        """
        :param url: destination url to get document body
        :return:
        """
        if sleep_seconds == None:
            sleep_seconds=random.randint(1, 3)
        req = RequestsWrapper()
        response = req.get(url, sleep_seconds=sleep_seconds)
        self.response = response
        self.doc = lxml.html.fromstring(response.content)
        return response

    @staticmethod
    def download_file(url, destination_path=""):
        """
        :param url: url to download file
        :param destination_path: directory with file name to store image data
        :return:
        """
        req = RequestsWrapper()
        response = req.get(url)
        logger.info(f"downloading: {url}") # pylint: disable=logging-fstring-interpolation
        filename = url.split("/")[-1]
        if destination_path == "":
            file_destination = filename
        else:
            UtilFunctions().create_directory(destination_path)
            file_destination = f"{destination_path}/{filename}"

        with open(file_destination, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        logger.error('error on file download')

    @staticmethod
    def get_html_table(*args, driver=None, table_index=0, with_header=False):
        """
        Getting HTMl Table from <table> tag inside an html
        :param args: argument for bs4 soup.find_all
        :param driver: selenium driver to scrape table data
        :param table_index: index of the table to be sraped
        :param with_header: boolean if table header will be included in the scrape
        :return: list of dict if with_header == True, list of list if with_header == False
        """
        logger.warning('scraping HTML table from page_source')
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if len(args) > 0:
            tables = soup.find_all('table', *args)
        else:
            tables = soup.find_all('table')

        table_body = tables[table_index].find('tbody')
        if with_header:
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
                    data.update({header[count]:val})
                table_data.append(data)
            return table_data
        else:
            table_data = []
            for row in table_body.find_all('tr'):
                data = []
                for col in enumerate(row.find_all('td')):
                    data.append(col.text.strip())
                table_data.append(data)
            return table_data

    def find_elements(self, by_mode, to_search, doc=None, tag="node()"):
        """
        :param by_mode: By Enumerator to search for e.g. XPATH, ID, CLASSNAME
        :param tosearch: the string to search
        :param doc: document body
        :param tag: works best with LINK_TEXT, PARTIAL_LINK_TEXT
        :return: ZenElement Object
        """
        output_dict = self.__return_dict_values(by_mode, to_search, doc, tag)
        return self.__find_elements_list(**output_dict)

    def find_element(self, by_mode, to_search, doc=None, tag="node()"):
        """
        :param by: By Enumerator to search for e.g. XPATH, ID, CLASSNAME
        :param tosearch: the string to search
        :param doc: document body
        :param tag: works best with LINK_TEXT, PARTIAL_LINK_TEXT
        :return: ZenElement Object
        """
        output_dict = self.__return_dict_values(by_mode, to_search, doc, tag)
        return self.__find_element(**output_dict)

    def print_html(self):
        """
        Print the HTMl file on the console.
        :return: HTML File as a String
        """
        print(etree.tostring(self.doc, pretty_print=True))
        return etree.tostring(self.doc, pretty_print=True)

    def status_code(self):
        """
        Print status_code on console
        :return: return status_code as an integer
        """
        logger.info(self.response.status_code)
        return self.response.status_code

    @staticmethod
    def check_link(url, sleep_seconds=None):
        """
        :param url: url of the link to check
        :return: check if link exists
        """
        if sleep_seconds == None:
            sleep_seconds=random.randint(1, 3)
        req = RequestsWrapper()
        response = req.get(url, sleep_seconds=sleep_seconds)
        logger.info(response.status_code)
        return response.status_code == 200

    def show_url(self):
        """
        get the current URL Link
        :return:
        """
        return str(self.response.url)

    @staticmethod
    def get_json(url, sleep_seconds=None):
        """
        :param url: url to get json
        :return: json file
        """
        if sleep_seconds == None:
            sleep_seconds=random.randint(1, 3)
        req = RequestsWrapper()
        res = req.get(url, sleep_seconds=sleep_seconds)
        return res.json()

class ZenElement:
    """ ZenElement , work like selenium Element Object """
    element = None

    def __init__(self, element):
        """ Init ZenElement """
        self.element = element

    def __find_elements_list(self, err_message="", xpath=""):
        """ Find Elements """
        try:
            element_list = []
            elements = self.element.xpath(xpath)
            for element in elements:
                element_list.append(ZenElement(element))

            if len(element_list) != 0:
                logger.info('element list generated')
                return element_list
            logger.warning('no element list generated')
            return []

        except (IndexError, lxml.etree.XPathEvalError, lxml.etree.XPathError,
                lxml.etree.Error) as err:
            logger.error(err)
            return None

    def __find_element(self, err_message="", xpath=""):
        """ Find ELement"""
        try:
            logger.info(f'{ZenElement(self.element.xpath(xpath)[0]).get_tag()} element found') # pylint: disable=logging-fstring-interpolation
            return ZenElement(self.element.xpath(xpath)[0])
        except (lxml.etree.XPathEvalError, lxml.etree.XPathError, lxml.etree.Error) as err:
            logger.error(err)
            return None

    @staticmethod
    def __return_dict_values(by_mode, to_search, tag="node()"):
        output_dict = {
            1: {'err_message': "<Error: id cannot be found on the html>",
                'xpath': f'//node()[@id="{to_search}"]'},
            2: {'err_message': "<Error: element cannot be found on the html>",
                'xpath': to_search},
            3: {'err_message': f"<Error: no element that contains {to_search} in the html>",
                'xpath': f'//{tag}[normalize-space(text()) = "{to_search}"]'},
            4: {'err_message': f"<Error: no element that contains {to_search} in the html>",
                'xpath': f'//{tag}[contains(text(), "{to_search}")]'},
            6: {'err_message': "<Error: tagname cannot be found on the html>",
                'xpath': f"//{to_search}"},
        }
        return output_dict[by_mode.value]

    def __inner_text(self, inner_text_filter=None):
        """
        :param inner_text_filter: you can add an array if you want
        ot add additional filter for your inner_text
        :return: filtered string
        """
        element_str = self.__to_string()
        stripped = UtilFunctions().strip_html(element_str)
        if inner_text_filter:
            for rep in inner_text_filter:
                stripped = stripped.replace(rep, "")
        stripped = stripped.strip()
        return stripped

    def __to_string(self):
        """
        Get the innerHTML of an Element, and convert it to string
        :return: string
        """
        string = str(etree.tostring(self.element))
        string = string.replace("b'", "")[:-1]
        return string

    def find_elements(self, by_mode, to_search, tag="node()"):
        """
        :param by_mode: By Enumerator the guide on what to search e.g. By.XPATH, By.TAG_NAME
        :param to_search: tosearch on the document body
        :param tag: parent element tag , default node(), means all element
        :return: List of ZenElement Objects
        """
        output_dict = self.__return_dict_values(by_mode, to_search, tag)
        return self.__find_elements_list(**output_dict)

    def find_element(self, by_mode, to_search, tag="node()"):
        """
        :param by_mode: By Enumerator the guide on what to search e.g. By.XPATH, By.TAG_NAME
        :param to_search: tosearch on the document body
        :param tag: parent element tag , default node(), means all element
        :return: ZenElement Object
        """
        output_dict = self.__return_dict_values(by_mode, to_search, tag)
        return self.__find_element(**output_dict)

    def get_attribute(self, attribute="", inner_text_filter=None):
        """
        :param attribute: attribute like innerText, innerHTML,
         class, image, alt, title etc.
        :param inner_text_filter: if you want to filter your string ,
         only work on innerText attribute
        :return: string
        """
        err_message = (
            "<Error: attribute in the element cannot be found, try different attribute>"
        )
        try:
            if attribute == 'innerText':
                return self.__inner_text(inner_text_filter)
            if attribute == 'innerHTML':
                return self.__to_string()
            if self.element.attrib.get(attribute) is None:
                return err_message

            return str(self.element.attrib.get(attribute))
        except (lxml.etree.XPathEvalError, lxml.etree.Error, lxml.etree.XPathError):
            return err_message

    def get_tag(self):
        """
        get the current tag of the element
        :return:
        """
        err_message = "<Error: There is no Text inside the Element>"
        try:
            if self.element is None:
                return err_message

            string = str(self.element).split("Element")[1].strip()
            string = string.split("at")[0].strip()
            return string
        except (lxml.etree.XPathEvalError, lxml.etree.Error, lxml.etree.XPathError):
            return "<Error: There is no Text inside the Element!>"

    def get_text(self):
        """ get text inside the element , use get_attribute('innerText')
         if you want all the text inside the element """
        err_message = "<Error: There is no text inside this Element>"
        try:
            if self.element.text is None:
                return err_message

            return self.element.text
        except (lxml.etree.XPathEvalError, lxml.etree.Error, lxml.etree.XPathError):
            return err_message

    def get_parent(self):
        """get the parent element of the current element"""
        return ZenElement(self.element.xpath("./parent::node()")[0])

    def get_children(self, tagname="*"):
        """
        get the children of the current element
        :param tagname: you can select tag to filter the children,
         e.g. if you want to search a tag, just input a
        :return: List of ZenElement Object
        """
        return self.__find_elements_list(
            err_message="<Error: No Children Inside the element>",
            xpath=f"./children::{tagname}",
        )

class By(Enum):
    """ By Enumerator to make element searching same as Selenium Searching format. """
    ID = 1
    XPATH = 2
    LINK_TEXT = 3
    PARTIAL_LINK_TEXT = 4
    NAME = 5
    TAG_NAME = 6
    CLASS_NAME = 7
    CSS_SELECTOR = 8

class DataType:
    """Unique type class to decipher between attributes"""

    def __init__(self, key, value):
        """ ORM Type Key value to add on the ORM Object"""
        self.key = key
        self.value = value

    def __repr__(self):
        """Return value"""
        return str(self.value)

    def __index__(self):
        """Return Key"""
        return int(self.key)

class DataObject:
    """Basic ORM Class"""

    def __init__(self, **kwargs):
        """ORM to create classess with variables"""
        for key, value in kwargs.items():
            setattr(self, key, DataType(key, value))

    @staticmethod
    def attr_1():
        """Adding this for Pylint issues"""
        print("attr_1")

    @staticmethod
    def attr_2():
        """Adding this for Pylint issues"""
        print("attr_2")

class UtilFunctions:
    """ Utility Functions mostly used in Scraping """
    @staticmethod
    def strip_html(data):
        """ strip html tags from the string. """
        string = re.compile(r"<.*?>|=")
        return string.sub("", data)

    @staticmethod
    def create_directory(dir_name):
        """ Create a directory """
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    def save_html(self, url='', htmldir='', filename='', driver=None):
        """
        :param url: url of the html page you want to save
        :param htmldir: directory on where to save the html
        :param filename: the filename on the saved directory
        :param driver: this is for selenium, if driver is stated that means
        that we will download the page from selenium, url not needed
        :return:
        """
        self.create_directory(htmldir)

        if driver:
            with open(f'{htmldir}/{filename}.html', 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
        else:
            req = RequestsWrapper()
            res = req.get(url)
            with open(f'{htmldir}/{filename}.html', 'w', encoding='utf-8') as file:
                file.write(res.text)

    def save_json(self, url='', jsondir='', file_name='data.json' ):
        """
        :param url: url of the html page you want to save
        :param jsondir: directory on where to save the json
        :param file_name: the filename on the saved directory
        :return:
        """
        self.create_directory(jsondir)
        sold_items = requests.get(url)
        Path(f'{jsondir}/{file_name}.json').write_bytes(sold_items.content)

    def is_partial_run(self, parser):
        """ Create a Partial run based on an argument """
        return parser.parse_args().run

    def end_partial_run(self, fetch, header):
        """ End Partial Run based on an argument """
        length = len(header)
        fetch_arr = fetch
        fetch_arr.append(['#----------------------End of Partial Run---------------------#'])
        return fetch_arr
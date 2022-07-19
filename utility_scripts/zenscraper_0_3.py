"""Zenscraper Python Library v 0.2"""
from enum import Enum
import shutil
import re
import sys
import json
import time
import random
import logging
import glob
import os
from pathlib import Path
from threading import Thread
import pandas as pd
from bs4 import BeautifulSoup
import requests
import lxml.html
from lxml import etree
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
sys.path.append('../../scripts')
from pyersq.requests_wrapper import RequestsWrapper

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


# zenscraper 0.3
class ZenScraper:
    """ ZenScraper , stealth scraping that follows selenium rules. """
    doc = None
    response = None
    utils = None
    selenium_utils = None
    datastream = None
    logger = None

    def __init__(self):
        self.utils = _UtilFunctions()
        self.selenium_utils = _SeleniumUtils()
        self.datastream = _DataStream()
        self.logger = logger

    def _find_elements_list(self, err_message="", xpath="", doc=None):
        """ find multiple elements in the class """
        try:
            element_list = []
            if doc is None:
                doc = self.doc
            elements = doc.xpath(xpath)
            for element in elements:
                element_list.append(ZenElement(element))
            if len(element_list) != 0:
                logger.info('element list generated')  #
                return element_list
            logger.warning('no element list found')
            return []
        except (IndexError, lxml.etree.XPathEvalError,
                lxml.etree.Error, lxml.etree.XPathError) as err:
            logger.warning(err_message)
            logger.error(f'{err}')  # pylint: disable=logging-fstring-interpolation
            return None

    def _find_element(self, err_message="", xpath="", doc=None):
        """ find single element from the class """
        try:
            if doc is None:
                doc = self.doc
            element = doc.xpath(xpath)
            logger.info('%s element found', ZenElement(
                element[0]).get_tag())  # pylint: disable=logging-fstring-interpolation
            return ZenElement(element[0])
        except (IndexError, lxml.etree.XPathEvalError, lxml.etree.XPathError,
                lxml.etree.Error) as err:
            logger.warning(err_message)
            logger.error(f'{err}')  # pylint: disable=logging-fstring-interpolation
            return None

    @staticmethod
    def _return_dict_values(by_mode, to_search, doc=None, tag="node()"):
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
        logger.info('GET request on %s', url)
        if sleep_seconds is None:
            sleep_seconds = random.randint(1, 3)
        req = RequestsWrapper()
        response = req.get(url, sleep_seconds=sleep_seconds)
        self.response = response
        self.doc = lxml.html.fromstring(response.content)
        return response

    def find_elements(self, by_mode, to_search, doc=None, tag="node()"):
        """
        :param by_mode: By Enumerator to search for e.g. XPATH, ID, CLASSNAME
        :param tosearch: the string to search
        :param doc: document body
        :param tag: works best with LINK_TEXT, PARTIAL_LINK_TEXT
        :return: ZenElement Object
        """
        output_dict = self._return_dict_values(by_mode, to_search, doc, tag)
        return self._find_elements_list(**output_dict)

    def find_element(self, by_mode, to_search, doc=None, tag="node()"):
        """
        :param by: By Enumerator to search for e.g. XPATH, ID, CLASSNAME
        :param tosearch: the string to search
        :param doc: document body
        :param tag: works best with LINK_TEXT, PARTIAL_LINK_TEXT
        :return: ZenElement Object
        """
        output_dict = self._return_dict_values(by_mode, to_search, doc, tag)
        return self._find_element(**output_dict)

    def status_code(self):
        """
        Print status_code on console
        :return: return status_code as an integer
        """
        logger.info(self.response.status_code)
        return self.response.status_code

    def show_url(self):
        """
        get the current URL Link
        :return:
        """
        return str(self.response.url)


class ZenElement:
    """ ZenElement , work like selenium Element Object """
    element = None

    def __init__(self, element):
        """ Init ZenElement """
        self.element = element

    def _find_elements_list(self, err_message="", xpath=""):
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
            logger.error(err_message)
            logger.error(err)
            return None

    def _find_element(self, err_message="", xpath=""):
        """ Find ELement"""
        try:
            logger.info(  # pylint: disable=logging-fstring-interpolation
                '%s element found', ZenElement(self.element.xpath(xpath)[0]).get_tag())
            return ZenElement(self.element.xpath(xpath)[0])
        except (lxml.etree.XPathEvalError, lxml.etree.XPathError, lxml.etree.Error) as err:
            logger.error(err_message)
            logger.error(err)
            return None

    @staticmethod
    def _return_dict_values(by_mode, to_search, tag="node()"):
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

    def _inner_text(self, inner_text_filter=None):
        """
        :param inner_text_filter: you can add an array if you want
        ot add additional filter for your inner_text
        :return: filtered string
        """
        element_str = self._to_string()
        stripped = _UtilFunctions().strings.strip_html(element_str)
        if inner_text_filter:
            for rep in inner_text_filter:
                stripped = stripped.replace(rep, "")
        stripped = stripped.strip()
        return stripped

    def _to_string(self):
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
        output_dict = self._return_dict_values(by_mode, to_search, tag)
        return self._find_elements_list(**output_dict)

    def find_element(self, by_mode, to_search, tag="node()"):
        """
        :param by_mode: By Enumerator the guide on what to search e.g. By.XPATH, By.TAG_NAME
        :param to_search: tosearch on the document body
        :param tag: parent element tag , default node(), means all element
        :return: ZenElement Object
        """
        output_dict = self._return_dict_values(by_mode, to_search, tag)
        return self._find_element(**output_dict)

    def get_attribute(self, attribute="", inner_text_filter=None):
        """
        :param attribute: attribute like innerText, innerHTML,
         class, image, alt, title etc.
        :param inner_text_filter: if you want to filter your string ,
         only work on innerText attribute
        :return: string
        """
        logger.info('Get Element Attribute %s', attribute)
        err_message = (
            "<Error: attribute in the element cannot be found, try different attribute>"
        )
        try:
            if attribute == 'innerText':
                return self._inner_text(inner_text_filter)
            if attribute == 'innerHTML':
                return self._to_string()
            if self.element.attrib.get(attribute) is None:
                logging.error(err_message)
                return None

            return str(self.element.attrib.get(attribute))
        except (lxml.etree.XPathEvalError, lxml.etree.Error, lxml.etree.XPathError) as err:
            logging.error(err)
            logging.error(err_message)
            return None

    def get_tag(self):
        """
        get the current tag of the element
        :return:
        """
        logger.info('Get Element Tag')
        err_message = "<Error: There is no Text inside the Element>"
        try:
            if self.element is None:
                logging.error(err_message)
                return None

            string = str(self.element).split("Element")[1].strip()
            string = string.split("at")[0].strip()
            return string
        except (lxml.etree.XPathEvalError, lxml.etree.Error, lxml.etree.XPathError) as err:
            logging.error(err)
            logging.error(err_message)
            return None

    def get_text(self):
        """ get text inside the element , use get_attribute('innerText')
         if you want all the text inside the element """
        logger.info('Get text from element')
        err_message = "<Error: There is no text inside this Element>"
        try:
            if self.element.text is None:
                logging.error(err_message)
                return None

            return self.element.text
        except (lxml.etree.XPathEvalError, lxml.etree.Error, lxml.etree.XPathError) as err:
            logging.error(err)
            logging.error(err_message)
            return None

    def get_parent(self):
        """get the parent element of the current element"""
        logger.info('Getting Element Parent')
        return ZenElement(self.element.xpath("./parent::node()")[0])

    def get_children(self, tagname="*"):
        """
        get the children of the current element
        :param tagname: you can select tag to filter the children,
         e.g. if you want to search a tag, just input a
        :return: List of ZenElement Object
        """
        logger.info('Getting Element Children')
        return self._find_elements_list(
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


class _UtilFunctions:  # pylint: disable=too-few-public-methods
    """ Utility Functions mostly used in Scraping """
    strings = None
    files = None
    html = None
    json = None
    parse = None
    decorator = None
    data = None

    def __init__(self):
        self.strings = _UtilFunctionsStrings()
        self.files = _UtilFunctionsFiles()
        self.html = _UtilFunctionsHTML()
        self.json = _UtilFunctionsJSON()
        self.parse = _UtilFunctionsParse()
        self.decorator = _UtilFunctionsDecorator()
        self.data = _UtilFunctionsData()


class _UtilFunctionsStrings:

    @staticmethod
    def strip_html(value):
        """
        Strip HTML tags from string
        :param value: input a string
        :return:
        """
        logger.info('stripping HTML tags from string')
        string = re.compile(r"<.*?>|=")
        return string.sub("", value)

    @staticmethod
    def remove_non_digits(value):
        """
        remove non digit character from a string
        :param value: string
        :return: string
        """
        output = ''.join(c for c in value if c.isdigit())
        return output

    @staticmethod
    def remove_digits(value):
        """
        remove all digit character in a string
        :param value: string
        :return: string
        """
        output = ''.join(c for c in value if not c.isdigit())
        return output

    @staticmethod
    def remove_non_alpha_char(value):
        """
        remove non letters
        :param value: string
        :return: string
        """
        value = value.lower()
        output = ''
        letter = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                  'q', 'r', 's', 't', 'u',
                  'v', 'w', 'x', 'y', 'z']
        for char in value:
            if any(x == char for x in letter):
                output += char
        return output

    @staticmethod
    def is_month(month):
        """
        Check if the string is a month
        :param month: month string 3 characters only
        :return: bool
        """
        if any(x == month.lower() for x in
               ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov',
                'dec']):
            return True
        return False

    @staticmethod
    def spanish_months(month):
        """
        check for spanish month
        :param month: check month
        :return: return month equivalent in string 'jan, feb, mar'
        """
        spanish_months_dict = {
            'enero': 'jan', 'febrero': 'feb', 'marzo': 'mar',
            'abril': 'apr', 'mayo': 'may', 'junio': 'jun',
            'julio': 'jul', 'agosto': 'aug', 'septiembre': 'sep',
            'octubre': 'oct', 'noviembre': 'nov', 'diciembre': 'dec'
        }
        return spanish_months_dict[month.lower().strip()]

    @staticmethod
    def quarter1_to_month(month):
        """
        get quarter month based on quarter data
        :param month: input quarter e.g. q1 = mar
        :return: month string
        """
        quarter_dict = {
            'q1': 'mar',
            'q2': 'jun',
            'q3': 'sep',
            'q4': 'dec'
        }
        return quarter_dict[month.lower().strip()]

    @staticmethod
    def contains_number(value):
        """check if a string contains number"""
        for character in value:
            if character.isdigit():
                return True
        return False


class _UtilFunctionsFiles:
    @staticmethod
    def create_directory(dir_name):
        """ Create a directory """
        logger.info('Creating Directory')
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    def download_file(self, url, destination_path=""):
        """
        :param url: url to download file
        :param destination_path: directory with file name to store image data
        :return:
        """
        req = RequestsWrapper()
        response = req.get(url)
        logger.info(f"downloading: {url}")  # pylint: disable=logging-fstring-interpolation
        filename = url.split("/")[-1]
        if destination_path == "":
            file_destination = filename
        else:
            self.create_directory(destination_path)
            file_destination = f"{destination_path}/{filename}"

        with open(file_destination, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        logger.error('error on file download')

    @staticmethod
    def get_input_file(input_path, header='', sheet_number=0, to_dict_val=''):
        """
        :param input_path: path of input file
        :param header: the name of the header to scrape
        :param has_sheet: check if csv or excel file input
        :param to_dict_val: if this has value this will serve as the dictionary value and
        header is the dictionary key
        :return: list or dictionary if to_dict_val is not ''
        """
        logger.warning('importing file from %s', input_path)
        if 'xlsx' in input_path:
            to_find_data = pd.read_excel(os.path.abspath(input_path), sheet_name=sheet_number)
        else:
            to_find_data = pd.read_csv(os.path.abspath(input_path))

        if to_dict_val == '':
            return to_find_data[header].drop_duplicates().to_list()

        return to_find_data.set_index(header).to_dict()[to_dict_val]

    @staticmethod
    def get_file_list(file_dir='.', file_extension='txt', is_latest_only=False):
        """
        get list of all file in the directory
        :param file_dir: file directory string
        :param file_extension: file extension ('txt') is the default
        :param is_latest_only: if this is True, then return only the latest file in the directory
        :return: list of directory , or a single directory
        """
        try:
            list_of_files = glob.glob(
                f'{file_dir}/*.{file_extension}')  # * means all if need specific format then *.csv
            if is_latest_only:
                return max(list_of_files, key=os.path.getctime)
        except ValueError:
            logger.error('No %s files found', file_extension)
            return []
        return list_of_files


class _UtilFunctionsJSON:

    @staticmethod
    def save_json(url='', jsondir='', file_name='data.json', sleep_time=None):
        """
        :param url: url of the html page you want to save
        :param jsondir: directory on where to save the json
        :param file_name: the filename on the saved directory
        :return:
        """
        _UtilFunctions().files.create_directory(jsondir)
        if sleep_time is None:
            req = RequestsWrapper()
        else:
            req = RequestsWrapper(sleep_time=sleep_time)
        sold_items = req.get(url)
        Path(f'{jsondir}/{file_name}.json').write_bytes(sold_items.content)

    @staticmethod
    def get_json(url, sleep_seconds=None):
        """
        :param url: url to get json
        :return: json file
        """
        logger.info('Get JSON file from %s', url)
        if sleep_seconds is None:
            sleep_seconds = random.randint(1, 3)
        req = RequestsWrapper()
        res = req.get(url, sleep_seconds=sleep_seconds)
        return res.json()

    def get_json_from_html_script_tag(self, doc=None, index=0, **kwargs):
        """
        :param doc: response document object
        :param index: index on the <script/> tag
        :return: return a json dictionary
        """
        json_object = None
        logger.info('getting json from html script')
        soup = BeautifulSoup(_UtilFunctions().html.print_html(doc=doc, is_print=False), 'lxml')
        res = soup.find('script', **kwargs)
        try:
            json_object = json.loads(res.contents[index])
            return json_object
        except Exception as err:  # pylint: disable=broad-except
            logger.error(err)
            bad_json = res.contents[index]
            improved_json = self._improve_json_content(bad_json)
            json_object = self._bruteforce_json_fix(improved_json)
        return json_object

    @staticmethod
    def _improve_json_content(bad_json):
        """improve json content"""
        improved_json = re.sub(r'"\s*$', '",', bad_json, flags=re.MULTILINE)
        improved_json.replace('"\\', '')
        improved_json.replace("\'", '"')
        return improved_json

    @staticmethod
    def _bruteforce_json_fix(improved_json, retry_count=20):
        """
        private function to bruteforce json file
        :param improved_json: parsed json data
        :param retry_count: retry count
        :return: fixed json string
        """

        def add_strings(prefix, improved_json, retry_count, prefix_to_increment='}]'):
            for i in range(retry_count):
                suffix = ''
                for j in range(retry_count):
                    try:
                        suffix += '}'
                        json_object = json.loads(f'{improved_json}{prefix}{suffix}')
                        logger.warning('json bruteforce success.')
                        return json_object
                    except Exception:  # pylint: disable=broad-except
                        logger.info('fix_type #%s adding %s%s: retrying %s times.',
                                    i, prefix, suffix, j)
                prefix += prefix_to_increment
            return None

        for prefix_to_increment in ['}]', ']', ']}]']:
            for prefix in ['', '"', '"}']:
                json_object = add_strings(prefix, improved_json, retry_count,
                                          prefix_to_increment=prefix_to_increment)
                if json_object is not None:
                    return json_object
        logger.error('bruteforce failed.')
        return None


class _UtilFunctionsHTML:

    @staticmethod
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
        _UtilFunctions().files.create_directory(htmldir)

        if driver:
            with open(f'{htmldir}/{filename}.html', 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
        else:
            req = RequestsWrapper()
            res = req.get(url)
            with open(f'{htmldir}/{filename}.html', 'w', encoding='utf-8') as file:
                file.write(res.text)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def print_html(doc=None, is_print=True):
        """
        Print the HTMl file on the console.
        :return: HTML File as a String
        """
        logger.info('Printing HTML')
        if is_print:
            print(etree.tostring(doc, pretty_print=True))
        return etree.tostring(doc, pretty_print=True)


class _UtilFunctionsParse:

    @staticmethod
    def is_partial_run(parser):
        """ Create a Partial run based on an argument """
        logger.info('Executing Code on Partial Run')
        return parser.parse_args().run

    @staticmethod
    def end_partial_run(fetch, header=None):  # pylint: disable=unused-argument
        """ End Partial Run based on an argument """
        logger.info('Ending Partial Run')
        fetch_arr = fetch
        fetch_arr.append(['#----------------------End of Partial Run---------------------#'])
        return fetch_arr


class _UtilFunctionsDecorator:
    @staticmethod
    def retry(func, retry_times=3, sleep_seconds=1, false_output=None):
        """
        retry until output not equals to false_output
        :param func: input a function to retry
        :param retry_times: the number of retry
        :param sleep_seconds: sleep time
        :param false_output: output that should be disregarded on the retry
        :return: value or false_output
        """

        def retry_decorator():
            for i in range(retry_times + 1):
                if i > 0:
                    logger.warning('retrying a %s function %s times', func().__name__, i)
                try:
                    data = func()
                except Exception as err:  # pylint: disable=broad-except
                    logger.error(err)
                    time.sleep(sleep_seconds)
                    continue
                if false_output is None:
                    if data is not false_output:
                        break
                else:
                    if data != false_output:
                        break
                time.sleep(sleep_seconds)
            return data

        return retry_decorator

    @staticmethod
    def threaded(func):
        """
        Decorator that multithreads the target function
        with the given parameters. Returns the thread
        created for the function
        """

        def wrapper(*args, **kwargs):
            thread = Thread(target=func, args=args)
            thread.start()
            return thread

        return wrapper


class _UtilFunctionsData:  # pylint: disable=too-few-public-methods

    @staticmethod
    def split_list(alist, wanted_parts=1):
        """
        split list into several parts
        :param alist: list of values
        :param wanted_parts: how parts should the list have
        :return: list of lists
        """
        chunk_size = wanted_parts
        chunked_list = [alist[i:i + chunk_size] for i in range(0, len(alist), chunk_size)]
        return chunked_list

    @staticmethod
    def df_delete_col_except(dataframe, list_of_col, exception_list=None):
        """
        :param dataframe: dataframe to modify
        :param list_of_col: list of all column to remove
        :param exception_list: list of all exceptions
        :return:
        """
        temp_df = dataframe
        if exception_list is None:
            exception_list = []

        for col in list_of_col:
            if any(x == str(col) for x in exception_list):
                pass
            else:
                try:
                    temp_df.drop(str(col), inplace=True, axis=1)
                except Exception:  # pylint: disable=broad-except
                    pass

        return temp_df

    @staticmethod
    def df_col_pop(dataframe, col_name, is_int=False):
        """
        pop column(header) to the top of all column
        :param df: dataframe
        :param col_name: column to pop on top of all column
        :param is_int: is the value of the column int?
        :return:
        """
        cols = list(dataframe)
        cols.insert(0, cols.pop(cols.index(col_name)))
        # us ix to reorder (loc for str or boolean, iloc for int)
        if not is_int:
            dataframe = dataframe.loc[:, cols]
            return dataframe
        dataframe = dataframe.iloc[:, cols]
        return dataframe

    @staticmethod
    def df_sort_row(dataframe, col_name):
        """
        sort dataframe row based on column name
        :param dataframe: dataframe to sort
        :param col_name: column name to sort every value with
        :return: return dataframe with sorted value
        """
        return dataframe.sort_values(by=col_name, key=lambda col: col.str.lower())


class _DataStream:  # pylint: disable=too-few-public-methods

    class DataType:  # pylint: disable=too-few-public-methods
        """Unique type class to decipher between attributes"""

        def __init__(self, key, value):
            """ ORM Type Key value to add on the ORM Object"""
            self.key = key
            self.value = value

        def __repr__(self):
            """Return value"""
            return str(self.value)

    class DataObject:  # pylint: disable=too-few-public-methods
        """Basic ORM Class"""

        def __init__(self, **kwargs):
            """ORM to create classess with variables"""
            for key, value in kwargs.items():
                setattr(self, key, _DataStream().DataType(key, value))


class _SeleniumUtils:  # pylint: disable=too-few-public-methods
    # from selenium.common.exceptions import NoSuchElementException
    actions = None
    options = None

    def __init__(self):
        self.actions = _SeleniumUtilsActions()
        self.options = _SeleniumUtilsOptions()

    def wait_for_page_load(self, driver, wait_time=30):
        """
        :param driver:
        :param wait_time:
        :return:
        """
        while not self._page_is_loading(driver, wait_time=wait_time):
            continue

    @staticmethod
    def _page_is_loading(driver, wait_time=30):
        """
        :param driver:
        :param wait_time:
        :return:
        """
        for _ in wait_time:
            loading = driver.execute_script("return document.readyState")
            if loading == "complete":
                return True

            time.sleep(0.5)
            yield False
        return True

    def wait_for_element(self, driver, xpath, wait_time=30):
        """
        :param driver: Selenium webdriver
        :param wait_time: wait time in seconds
        :param xpath: xpath expression to wait
        :return:
        """
        try:
            WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((self.SeleniumBy.XPATH, xpath)))
        except Exception as e:
            print(e)

    @staticmethod
    def take_screenshot(driver, save_fn='test.png'):
        """
        get screenshot of website
        :param driver: selenium webdriver
        :param save_fn: save file location
        :return:
        """
        driver.execute_script("""
        (function () {
            var y = 0;
            var step = 100;
            window.scroll(0, 0)
            
            function f() {
                if(y < document.body.scrollHeight){
                    y += step;
                    window.scroll(0, y);
                    setTimeout(f, 100);
                } else {
                    window.scroll(0, 0);
                    document.title += "scroll-done";
                }
            }
            
            setTimeout(f, 1000);
        })();
        """)

        for i in range(30):
            if 'scroll-done' in driver.title:
                break
            time.sleep(10)
            print(i)

        driver.save_screenshshot(save_fn)


class _SeleniumUtilsActions:
    """Action Chains & Form Action"""

    def send_keys(self, driver, key):
        action = ActionChains(driver)

    def move_to_and_click(self, driver, move_to='', click=''):
        try:
            action = ActionChains(driver)
            element_move_to = driver.find_element(SeleniumBy.XPATH. move_to)
            if click != '':
                element_click = driver.find_element(SeleniumBy.XPATH, click)
            else:
                element_click = element_move_to

            action.move_to_element(element_move_to).perform()
            action.click(element_click).perform()
        except Exception as e:
            logger.error

class _SeleniumUtilsOptions:


    def __init__(self):
        self.user_agent = 'Mozzilla/5.0 (Windows NT 10.0; WOW64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'

    @staticmethod
    def set_options(opts, *args):
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--lang=en_US")
        opts.add_argument("--disable-gpu")

        if len(args) != 0:
            for val in args:
                opts.add_argument(val)


    def override_useragent(self, driver):
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {'userAgent': self.user_agent})
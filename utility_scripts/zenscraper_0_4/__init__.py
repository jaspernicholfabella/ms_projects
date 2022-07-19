"""Zenscraper Version 0.4"""
import random
import logging
import requests
import lxml.html
from lxml import etree
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .utils._strings import Strings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from .pyersq.requests_wrapper import RequestsWrapper

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

#zenscraper_0_4
class ZenScraper:
    """ ZenScraper , stealth scraping that follows selenium rules. """
    doc = None
    response = None
    logger = None

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
        stripped = Strings(logger).strip_html(element_str)
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

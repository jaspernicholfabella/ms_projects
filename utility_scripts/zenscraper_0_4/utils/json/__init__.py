""" utils.json v0_1 function to scrape json data from web """
from os.path import dirname, join, abspath
import sys
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

from ..logger import logger
from ..files import create_directory
from ..html import print_html

sys.path.insert(0, abspath(join(dirname(__file__), "../../..")))
from pyersq.requests_wrapper import RequestsWrapper



def save_json(url='', jsondir='', file_name='data.json', sleep_time=None):
    """
    :param url: url of the html page you want to save
    :param jsondir: directory on where to save the json
    :param file_name: the filename on the saved directory
    :return:
    """
    logger.info('Saving json file')
    create_directory(jsondir)
    if sleep_time is None:
        req = RequestsWrapper()
    else:
        req = RequestsWrapper(sleep_time=sleep_time)
    sold_items = req.get(url)
    Path(f'{jsondir}/{file_name}.json').write_bytes(sold_items.content)


def get_json(url, sleep_seconds=None):
    """
    :param url: url to get json
    :return: json file
    """
    logger.info('Get JSON file from %s', url)
    req = RequestsWrapper()
    if sleep_seconds is None:
        res = req.get(url)
    else:
        res = req.get(url, sleep_seconds=sleep_seconds)
    return res.json()


def get_json_from_html_script_tag(doc=None, index=0, **kwargs):
    """
    :param doc: response document object
    :param index: index on the <script/> tag
    :return: return a json dictionary
    """
    json_object = None
    logger.info('getting json from html script')
    soup = BeautifulSoup(print_html(doc=doc, is_print=False), 'lxml')
    res = soup.find('script', **kwargs)
    try:
        json_object = json.loads(res.contents[index])
        return json_object
    except Exception as err:  # pylint: disable=broad-except
        logger.error(err)
        bad_json = res.contents[index]
        improved_json = _improve_json_content(bad_json)
        json_object = _bruteforce_json_fix(improved_json)
    return json_object


def _improve_json_content(bad_json):
    """improve json content"""
    improved_json = re.sub(r'"\s*$', '",', bad_json, flags=re.MULTILINE)
    improved_json.replace('"\\', '')
    improved_json.replace("\'", '"')
    return improved_json


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
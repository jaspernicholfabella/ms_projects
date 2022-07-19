import re
import json
from pathlib import Path
from ._files import Files
from ._html import HTML
from bs4 import BeautifulSoup

from ..pyersq.requests_wrapper import RequestsWrapper


class JSON:
    logger = None

    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def save_json(url='', jsondir='', file_name='data.json', sleep_time=None):
        """
        :param url: url of the html page you want to save
        :param jsondir: directory on where to save the json
        :param file_name: the filename on the saved directory
        :return:
        """
        Files().create_directory(jsondir)
        if sleep_time is None:
            req = RequestsWrapper()
        else:
            req = RequestsWrapper(sleep_time=sleep_time)
        sold_items = req.get(url)
        Path(f'{jsondir}/{file_name}.json').write_bytes(sold_items.content)


    def get_json(self, url, sleep_seconds=None):
        """
        :param url: url to get json
        :return: json file
        """
        self.logger.info('Get JSON file from %s', url)
        req = RequestsWrapper()
        if sleep_seconds is None:
            res = req.get(url)
        res = req.get(url, sleep_seconds=sleep_seconds)
        return res.json()

    def get_json_from_html_script_tag(self, doc=None, index=0, **kwargs):
        """
        :param doc: response document object
        :param index: index on the <script/> tag
        :return: return a json dictionary
        """
        json_object = None
        self.logger.info('getting json from html script')
        soup = BeautifulSoup(HTML().print_html(doc=doc, is_print=False), 'lxml')
        res = soup.find('script', **kwargs)
        try:
            json_object = json.loads(res.contents[index])
            return json_object
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error(err)
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


    def _bruteforce_json_fix(self, improved_json, retry_count=20):
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
                        self.logger.warning('json bruteforce success.')
                        return json_object
                    except Exception:  # pylint: disable=broad-except
                        self.logger.info('fix_type #%s adding %s%s: retrying %s times.',
                                    i, prefix, suffix, j)
                prefix += prefix_to_increment
            return None

        for prefix_to_increment in ['}]', ']', ']}]']:
            for prefix in ['', '"', '"}']:
                json_object = add_strings(prefix, improved_json, retry_count,
                                          prefix_to_increment=prefix_to_increment)
                if json_object is not None:
                    return json_object
        self.logger.error('bruteforce failed.')
        return None
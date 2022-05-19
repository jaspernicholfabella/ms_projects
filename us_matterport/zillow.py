""" Robot creation for US Matterport 3D Listings  """
import sys
import os
import glob
import time
import random
import re
from datetime import datetime
from pathlib import Path
import geopy
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from lxml import etree

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW

from ms_projects.utility_scripts.zenscraper import ZenScraper, By, DataObject, UtilFunctions

class Zillow(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='zillow', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "out": ['FetchDate'],
        }

        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

    def get_raw(self, **kwargs):
        states = ['CA', 'WI', 'VT']
        state = 'CA'
        west, east, south, north = '-124.482045', '-114.131253', '32.528832', '42.009517'
        # state = 'AK'
        # west, east, south, north = '-179.148909', '179.77847', '51.214183', '71.365162'
        """ Get raw data from source"""
        url = 'https://www.zillow.com/search/GetSearchPageState.htm?' \
              'searchQueryState=%7B%22' \
              'pagination%22%3A%7B%7D%2C%22' \
              f'usersSearchTerm%22%3A%22{state}%22%2C%22' \
              'mapBounds%22%3A%7B%22' \
              f'west%22%3A{west}%2C%22' \
              f'east%22%3A{east}%2C%22' \
              f'south%22%3A{south}%2C%22' \
              f'north%22%3A{north}%7D%2C%22' \
              'mapZoom%22%3A6%2C%22' \
              'regionSelection%22%3A%5B%7B%22' \
              'regionId%22%3A9%2C%22' \
              'regionType%22%3A2%7D%5D%2C%22' \
              'isMapVisible%22%3Atrue%2C%22' \
              'filterState%22%3A%7B%22' \
              'is3dHome%22%3A%7B%22value%22%3Atrue%7D%2C%22' \
              'isAllHomes%22%3A%7B%22value%22%3Atrue%7D%2C%22' \
              'sortSelection%22%3A%7B%22value%22%3A%22' \
              'globalrelevanceex%22%7D%7D%2C%22' \
              'isListVisible%22%3Atrue%7D&wants={%22cat1%22:[%22mapResults%22]}&requestId=2'

        json_data = ZenScraper().get_json(url)
        print(json_data['categoryTotals'])

        # with SW.get_driver(desired_capabilities=SW.enable_log(), headless=False) as driver:
        #     # driver.get_url('https://www.zillow.com/ca/')
        #     driver.get('https://www.zillow.com/ca/')
        #     logs = list(SW.get_log_msg(driver, self._network_msg))



        # return self.fetch_out
    @staticmethod
    def _network_msg(log):
        if (log['method'] == 'Network.responseRecieved' and "params" in log.keys()):
            return '/search/GetSearchPageState' in log['params']['response']['url']
        return False

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame

def main(argv):
    """Main entry"""
    web = Zillow(argv)
    web.run2()

if __name__ == "__main__":
    main(sys.argv)

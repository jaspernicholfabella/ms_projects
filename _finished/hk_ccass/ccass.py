""" Robot creation for HK Ccass HKEXNEWS  """
import sys
import os
import glob
import time
import random
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from lxml import etree

sys.path.append('../../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW

from ms_projects.utility_scripts.zenscraper import ZenScraper, By, DataObject, UtilFunctions

class Ccass(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='ccass', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": [],
            "out": ['FetchDate', 'Website', 'StockCode', 'StockName', 'ParticipantID', 'Name', 'Shareholding'],
            "delivery": ['FetchDate', 'Website', 'StockCode']
        }

        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')
        self.stock_list = []

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        self.get_stock_list()
        return self.fetch_out


    def get_stock_list(self):
        current_date = datetime.now().strftime('%Y%m%d')
        json_data = ZenScraper.get_json(f'https://www3.hkexnews.hk/sdw/'
                                        f'search/stocklist.aspx?'
                                        f'sortby=stockcode&shareholdingdate={current_date}')
        for data in json_data:
            self.stock_list.append({data['c'] : data['n']})


    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame

def main(argv):
    """Main entry"""
    web = Ccass(argv)
    web.run2()

if __name__ == "__main__":
    main(sys.argv)


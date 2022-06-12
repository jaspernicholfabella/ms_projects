""" Robot creation for XBRL Data Extractor  """
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

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW
import pyersq.utils as squ

from ms_projects.utility_scripts.zenscraper import ZenScraper, By, DataObject, UtilFunctions

class Xbrl_Scraper(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='xbrl_scraper', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "out": ['FetchDate', 'Filename', 'Period', 'OperatingRevenues', 'OperatingExpenses',
                    'Depreciation', 'Amortization', 'Grand Total'],
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        xbrl_dir = os.path.abspath(f'{self.outdir}/input/xbrl')

        list_of_file = glob.glob(f'{xbrl_dir}/*xbrl')

        for file_path in list_of_file:
            openxbrl = open(file_path, 'r')
            doc = openxbrl.read()
            soup = BeautifulSoup(doc, 'lxml')
            tag_list = soup.find_all()
            period = self.search_xbrl(tag_list, 'reportperiod')
            
        return self.fetch_out

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame

def main(argv):
    """Main entry"""
    web = Xbrl_Scraper(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)

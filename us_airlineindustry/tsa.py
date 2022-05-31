""" Robot creation for US Airline Industry  """
import sys
import os
import glob
import time
import random
import re
import logging
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

from ms_projects.utility_scripts.zenscraper import ZenScraper

class Tsa(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='tsa', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": 'https://www.tsa.gov/coronavirus/passenger-throughput',
            "out": ['FetchDate', 'Date', 'Year', 'Passengers'],
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        with SW.get_driver() as driver:
            SW.get_url(driver, self.datapoints['base_url'], sleep_seconds=0)
            driver.implicitly_wait(7)
            table_data = ZenScraper().get_html_table(driver=driver, with_header=True)

            for data in table_data:
                for key, value in data.items():
                    self.out.fetchdate = self.fetch_date
                    self.out.date = data['Date']
                    if key != 'Date':
                        self.out.objectkey = self.out.compute_key()
                        self.out.year = key
                        self.out.passengers = value
                        self.fetch_out.append(self.out.values())

        return self.fetch_out

    def save_output(self, data, **kwargs):
        """Save final data to output file"""
        self.save_output_csv(data, index=True)

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header())
        # data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
        #            value=["", ""], regex=True, inplace=True)
        data_frame.set_index("ObjectKey", inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Tsa(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)


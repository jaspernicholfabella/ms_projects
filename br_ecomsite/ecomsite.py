""" Robot creation for BR eCommerce Sites  """
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

from ms_projects.utility_scripts.zenscraper import ZenScraper

class Ecomsite(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='ecomsite', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "out": ['FetchDate'],
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        input_data = pd.read_csv(os.path.abspath(f'{self.outdir}/input/ecomsite_input.csv'))
        url_list = input_data['Links'].drop_duplicates().to_list()

        for url in url_list:
            with SW.get_driver() as driver:
                SW.get_url(driver, url, sleep_seconds=0)
                WebDriverWait(driver, 60).until(
                    EC.frame_to_be_available_and_switch_to_it(
                        (By.XPATH, )
                    )
                )
                time.sleep(5)
                table_data = ZenScraper().get_html_table(driver=driver, with_header=True)
                for data in table_data:
                    print(data)

        return self.fetch_out

    def save_output(self, data, **kwargs):
        """Save final data to output file"""
        self.save_output_csv(data, index=True)

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)

        return data_frame

def main(argv):
    """Main entry"""
    web = Ecomsite(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)

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

from ms_projects.utility_scripts.zenscraper import ZenScraper, UtilFunctions

class Ecomsite(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='ecomsite', output_subdir="raw", output_type='excel')

        self.parser = squ.get_parser()
        self.header = ['FetchDate', 'Category', 'Geography']
        self.is_header_added = False
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        input_data = pd.read_csv(os.path.abspath(f'{self.outdir}/input/ecomsite_input.csv'))
        url_dict = input_data.set_index('Links').to_dict()['Geography']

        for count, (url, geog) in enumerate(url_dict.items()):
            try:
                with SW.get_driver() as driver:
                    SW.get_url(driver, url, sleep_seconds=1)

                    if UtilFunctions().is_partial_run(self.parser):
                        if count > 3:
                            self.fetch_out = UtilFunctions.end_partial_run(self.fetch_out)
                            break

                    WebDriverWait(driver, 60).until(
                        EC.frame_to_be_available_and_switch_to_it(
                            (By.XPATH, "//iframe[contains(@title, 'Table Master')]")
                        )
                    )

                    time.sleep(8)
                    if not self.is_header_added:
                        table_header = ZenScraper().get_html_table(driver=driver, just_header=True, id='theTable')
                        for header in table_header:
                            self.header.append(header)
                        self.is_header_added = True

                    print('table scraping on url: ', url)
                    table_data = ZenScraper().get_html_table(driver=driver, id='theTable')
                    for data in table_data:
                        self.fetch_out.append([self.fetch_date, self.get_sales_index(url), geog, *data])

            except Exception as e: #pylint: disable=broad-except
                self.fetch_out.append([self.fetch_date, self.get_sales_index(url), geog, *['' for _ in range(5)]])
                print(e)

        return self.fetch_out

    @staticmethod
    def get_sales_index(url):
        if 'de-faturamento' in url:
            return 'Sales Index'
        elif 'de-vendas' in url:
            return 'Orders Index'
        elif 'de-tiquete' in url:
            return 'Average Ticket Index'

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.header)
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Ecomsite(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)

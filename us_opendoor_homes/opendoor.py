""" Robot creation for US Opendoor Homes  """
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
from selenium.webdriver.common.by import By as SeleniumBy
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
import json

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper, By

class Opendoor(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='opendoor', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url" : "https://www.opendoor.com/homes",
            "out": ['Collection Date', 'Home ID', 'Street', 'City', 'State', 'Postal Code'
                    'Listing Status', 'Bedrooms', 'Bathrooms', 'Sqft', 'Lot Sqft', 'Location Breadcrumb',
                    'Description', 'Listed By', 'List Price', 'Buy w/ OD Price', 'For Sale Date', 'Year Built',
                    'Price per Sqft', 'Home Type', 'OpenDoor owned home', 'Monthly cost', 'Pay when you close',
                    'Estimated closing credit'],
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        with SW.get_driver(desired_capabilities=SW.enable_log()) as driver:
            SW.get_url(driver, 'https://www.opendoor.com/homes/atlanta')
            logs = self.get_networklogs(driver)
        return self.fetch_out

    def get_networklogs(self, driver):
        try:
            logs = list(SW.get_log_msg(driver, self.network_msg))
        except Exception as e: #pylint: disable:broad-except
            pass
        return None

    @staticmethod
    def network_msg(log):
        if (log['method'] == 'Network.responseRecieved' and "params" in log.keys()):
            # url = log['params']['response']['url']
            print(log)

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Opendoor(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)

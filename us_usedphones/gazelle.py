""" Robot creation for Gazelle Website  """
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
from selenium.webdriver.common.by import SeleniumBy
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

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper, By

class Gazelle(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='gazelle', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "out": ['FetchDate', 'Website', 'Device', 'Model',
                    'Carrier', 'Capacity', 'Condition', 'Capacity',
                    'PriceType', 'Price', 'Description', 'SKU'],
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        return self.fetch_out

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame


@squ.retry(tries=3)
def main(argv):
    """Main entry"""
    web = Gazelle(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)v)  main(sys.argv)v)ys.argv)v)
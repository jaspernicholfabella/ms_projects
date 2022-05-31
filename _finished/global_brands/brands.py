""" Robot creation for Global Brands Foot Traffic  """
import sys
import logging
from urllib import parse
import os
import glob
import time
import json
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
import pyersq.utils as squ

from ms_projects.utility_scripts.zenscraper import ZenScraper, DataObject, UtilFunctions

class Brands(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='brand_foot_traffic', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": 'https://tableau-prod.placer.ai/t/TheSquare/views/BrandTracker/Corona_brandtracker?comparison='
                        '{comparison}&%3Aembed=y&RegionParam=United%20States&'
                        'BrandParam={brand}&%3Atoolbar=n&%3Asize=1022%2C501&%3Atabs=n',
            "brands" : ["Macy's", "Khol's", "Nordstrom", "Nordstrom Rack", "Ross Dress for Less",
                        "Burlington", "T.J. Maxx", "HomeGoods", "Marshalls"],
            "compare_years" : {'Three Years Ago': -3, 'Two Years Ago': -2, 'Previous Year': -1},
        }

        self.dfall = None
        self.driver = None
        self._wait = None

    @staticmethod
    def set_options(opts):
        """Set Chrome Options for Selenium Web Driver"""
        if os.environ.get('headless', None):
            opts.add_argument('--headless')

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        self.driver = SW.get_driver(desired_capabilities= SW.enable_log(), option_callback=self.set_options)
        self._wait = WebDriverWait(self.driver, 30)
        dfall = None
        for brand in self.datapoints['brands']:
            for comparison in self.datapoints['compare_years']:
                logging.info("Collect for: brand=%s, comparison=%s", brand, comparison)
                dfy = self.collect_brand(brand, comparison)
                dfall = pd.concat([dfall, dfy])

        self.driver.quit()
        self.dfall = dfall

    def collect_brand(self, brand, comparison):
        """ Collect Brand """
        url = self.datapoints['base_url'].format(brand=parse.quote(brand), comparison=parse.quote(comparison))
        _ = self.driver.get_log('performance') #Clear up previous logs
        SW.get_url(self.driver, url)

        df = self.get_data()
        df.insert(0, 'brand', brand)
        df.insert(1, 'compare_year', self.datapoints['compare_years'][comparison])
        return df

    def switch_date(self):
        date_dropbox = self._wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'tabComboBoxNameContainer')]")))[0]
        logging.info("Select date range: dropbox=%s", date_dropbox.text)
        date_dropbox.click()

        date_range = self._wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH,
                "//span[contains(@class, 'tabMenuItemName') and contains(text(), 'Since')]"
                )
            )
        )[0]

        logging.info("Pick up date: date_range=%s", date_range.text)
        _ = self.driver.get_log('performance') #Clear up previous logs
        date_range.click()
        time.sleep(5) #Stabilize

    def get_data(self):
        """Get data from cache"""
        logging.info("Get raw message from the first boot call")
        raw = self.get_raw_msg()
        print(raw)

        logging.info("Get data from boot message: raw=%d",len(raw))
        boot_values, boot_dates, boot_msg = self.get_boot_data(raw)

        logging.info('Switch to earliest date range')
        self.switch_date()

        logging.info("get data from next msg")
        next_values, next_dates, idx, next_msg, = self.get_next_data(raw)

        logging.info("Combine data from index: next_values=%d, next_dates=%d, idx=%d, next_msg=%s",
                     len(next_values), len(next_dates), next_msg.keys())

        all_values = boot_values + next_values
        tracker_values = [all_values[i] for i in idx]
        tracker_dates = sorted(next_dates + boot_dates)
        df = pd.DataFrame({'date': tracker_dates, 'foot_traffic_change': tracker_values})
        return df

    @staticmethod
    def get_boot_data(raw):
        """Get data from the first boot message"""
        msg = json.loads(raw[raw.find(';{', raw.find(';{') + 1) + 1:])
        data = squ.deep_get(msg, )

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Brands(argv)
    web.run2()

if __name__ == "__main__":
    main(sys.argv)



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
            "out": ['FetchDate', 'State', 'County', 'PropertyLink', 'Address', 'ListingPrice', 'BuyWithRedfin', 'Vendor',
                   'Status', 'PropertyType', 'Style', 'LotSize', 'TimeOnRedfin', 'YearBuilt', 'Community', 'MlsNo',
                    'ListPrice', 'RedfinEstimate','BuyerAgentCommission', 'EstMoPayment', 'PriceSqFt']
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.out.objectkey=''
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        scraper = ZenScraper()
        scraper.get('https://www.redfin.com/CA/Long-Beach/3307-Daisy-Ave-90806/home/7569199', sleep_seconds=1)
        self.out.address = scraper.find_element(By.XPATH, "//h1[@class='full-address']").get_attribute('innerText')
        self.out.listingprice = scraper.find_element(By.XPATH, "//div[@class='statsValue']").get_attribute('innerText')
        try:
            self.out.buywithredfin = scraper.find_element(By.XPATH, "//span[contains(text(), 'Buy with Redfin')]/parent::node()").get_attribute('innerText', inner_text_filter=['Buy With Redfin:'])
        except Exception as e:
            self.out.buywithredfin = ''
        vendor = scraper.find_element(By.XPATH, "//div[contains(text(),'3D Walkthrough')]/parent::node()/parent::node()/script").get_attribute('innerText')
        self.out.vendor = vendor[vendor.find("[")+1:vendor.find("]")].replace('data-buttonenum','').replace('"', '')
        self.out.status = scraper.find_element(By.XPATH, "//span[contains(text(), 'Status')]/parent::node()/span[2]/div").get_attribute('innerText')
        self.out.propertytype = self.get_span_data(scraper, 'Property Type')
        self.out.style = self.get_span_data(scraper, 'Style')
        self.out.lotsize = self.get_span_data(scraper, 'Lot Size')
        self.out.timeonredfin = self.get_span_data(scraper, 'Time on Redfin')
        self.out.yearbuilt = self.get_span_data(scraper, 'Year Built')
        self.out.community = self.get_span_data(scraper, 'Community')
        self.out.mlsno = self.get_span_data(scraper, 'MLS#')
        self.out.listprice = self.get_span_data(scraper, 'List Price')
        try:
            self.out.redfinestimate = scraper.find_element(By.XPATH, "//span[contains(text(), 'Redfin Estimate')]/parent::node()/parent::node()/parent::node()/span[2]").get_attribute('innerText')
        except Exception as e:
            self.out.redfinestimate = ''
        try:
            self.out.buyeragentcommission = scraper.find_element(By.XPATH,"//span[contains(text(), 'Agent Commission')]/parent::node()/parent::node()/parent::node()/parent::node()/span[2]").get_attribute('innerText')
        except Exception as e:
            self.out.buyeragentcommission = ''
        self.out.estmopayment = self.get_span_data(scraper, 'Est. Mo. Payment')
        self.out.pricesqft = self.get_span_data(scraper, 'Price/Sq.Ft.')
        print(self.out.values())
        return self.fetch_out

    @staticmethod
    def get_span_data(scraper, to_find=''):
        try:
            data = scraper.find_element(By.XPATH,f"//span[contains(text(), '{to_find}')]/parent::node()/span[2]").get_attribute('innerText')
            return data
        except Exception as e:
            return ''


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

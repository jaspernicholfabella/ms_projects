""" Robot creation for Usell Website  """
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
import inspect


sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW
import pyersq.utils as squ

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper, By

class Usell(Runner):
    """Collect data from website"""

    def __init__(self, argv):
        super().__init__(argv, output_prefix='usell', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": 'https://www.usell.com',
            "out": ['FetchDate', 'Website', 'URL', 'Device', 'Model',
                    'Carrier', 'Capacity', 'Condition', 'Capacity',
                    'PriceType', 'Price', 'Description', 'SKU'],
        }

        self.parser = squ.get_parser()
        self.phone_list = []
        self.phone_list_carrier = []
        self.phone_list_final = []
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        self.crawl_links()

        self.phone_list_final = ZenScraper().check

        for url in self.phone_list_final:
            self.get_phone_details(url)
        return self.fetch_out

    def crawl_links(self):
        """
        crawl links to get all phone data
        :return:
        """
        self.get_phone_list('https://www.usell.com/sell/iphone')
        self.phone_list.append('https://www.usell.com/sell/cell-phone/samsung')
        self.get_phone_list('https://www.usell.com/sell/ipad/')

        for url in self.phone_list:
            self.get_list_data(self.phone_list_carrier, url, "//a[@class='slide']")

        for url in self.phone_list_carrier:
            self.get_list_data(self.phone_list_final, url, "//a[@class='choose_btn']")
        print(self.phone_list_final)

    def get_phone_list(self, url):
        """get phone list url"""
        print('get_phone_list -->', url)
        phone_list = []
        scraper = ZenScraper()

        while len(phone_list) == 0:
            scraper.get(url)
            elements = scraper.find_elements(By.XPATH, "//a[@class='slide']")
            for element in elements:
                phone_url = element.get_attribute('href')
                if 'iphone' in phone_url:
                    if '4' not in phone_url:
                        if '3' not in phone_url:
                            if '2' not in phone_url:
                                phone_list.append(self.datapoints['base_url'] + phone_url)
                else:
                    phone_list.append(self.datapoints['base_url'] + phone_url)
            if len(phone_list) > 0:
                break
            time.sleep(10)

        phone_list = list(set(phone_list))
        for url in phone_list:
            self.phone_list.append(url)

    def get_list_data(self, list_to_append, url, xpath, while_counter=5):
        """
        :param list_to_append: list that you want to append values to
        :param url: url of the page
        :param xpath: xpath to grab url from
        :param while_counter: while retry maximum count
        :return:
        """
        print("get_list_data -->", xpath, '--->' , url)
        phone_list = []
        scraper = ZenScraper()

        while len(phone_list) == 0:
            scraper.get(url)
            elements = scraper.find_elements(By.XPATH, xpath)
            for element in elements:
                phone_url = element.get_attribute('href')
                phone_list.append(self.datapoints['base_url'] + phone_url)

            if len(phone_list) > 0:
                break
            if while_counter > 10:
                break
            time.sleep(10)

        phone_list = list(set(phone_list))
        for url in phone_list:
            list_to_append.append(url)

    def get_phone_details(self, url):
        """get phone details from url"""
        print('get_phone_details --->', url)

        with SW.get_driver() as driver:
            SW.get_url(driver, url)
            time.sleep(10)
            self.out.fetchdate = self.fetch_date
            self.out.website = 'USell'
            self.out.url = url
            if 'iphone' in url:
                self.out.device = 'Iphone'
            if 'samsung' in url:
                self.out.device = 'Samsung'
            if 'ipad' in url:
                self.out.device = 'Ipad'

            self.out.sku = url.split('/')[-1].replace('.htm', '').replace('.html', '')
            if 'unlocked' in url:
                self.out.pricetype = 'Unlocked'
            else:
                self.out.pricetype = 'Base'

            title = driver.find_element(SeleniumBy.XPATH, "//div[@id='page_title']//span").get_attribute('innerText')
            self.out.description = title
            model = ''

            for word in title.strip().split(' '):
                if 'GB' in word:
                    self.out.capacity = word
                elif '(' in word and ')' in word:
                    self.out.carrier = word.replace('(', '').replace(')', '')
                else:
                    model += f' {word}'
            self.out.model = model

            conditions = ['Damaged', 'Good', 'Flawless']

            for condition in conditions:
                self.out.objectkey = self.out.compute_key()
                self.out.condition = condition
                driver.find_element(SeleniumBy.XPATH, f"//div[@data-condition-name='{condition}']").click()
                time.sleep(10)
                self.out.price = driver.find_element(SeleniumBy.XPATH, "//div[@class='offer-value']").text.replace('$','')[:-2]
                self.fetch_out.append(self.out.values())

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header())
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return data_frame


def main(argv):
    """Main entry"""
    web = Usell(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)

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
from selenium.webdriver.common.action_chains import ActionChains
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
            "base_url": 'https://domainnamestat.com/statistics/registrar/others',
            "out": ['Page', 'Website', 'Link'],
        }

        self.out = Row(self.datapoints['out'])
        self.fetch_out = []

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        with SW.get_driver() as driver:
            SW.get_url(driver, self.datapoints['base_url'])
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return jQuery.active == 0'))
            time.sleep(3)
            #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='bottom-cookie-message-block']/div/i")))
            driver.find_element(By.XPATH, "//div[@id='bottom-cookie-message-block']/div/i").click()
            index = 1
            while True:
                time.sleep(2)
                pagination_element_xpath = f"//a[text() = '{index}']"
                if driver.find_element(By.XPATH, pagination_element_xpath):
                    #clicking pagination from '1'
                    action = ActionChains(driver)
                    pagination_element = driver.find_element(By.XPATH, pagination_element_xpath)
                    action.move_to_element(pagination_element).perform()
                    action.click(pagination_element).perform()
                    #scraping table
                    table = driver.find_element(By.XPATH, "//table")
                    links = table.find_elements(By.XPATH, "..//td/a")
                    for link in links:
                        print(index, link.get_attribute('href'), link.get_attribute('innerText').strip())
                        self.fetch_out.append([index, link.get_attribute('href'), link.get_attribute('innerText').strip()])
                    index += 1
                    continue
                break
        return self.fetch_out

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        return data_frame

def main(argv):
    """Main entry"""
    web = Tsa(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)


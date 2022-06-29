""" Robot creation for US Matterpoint  """
import sys
import json
import os
import time
import re
from datetime import datetime
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
import pyersq.utils as squ
from pyersq.selenium_wrapper import SeleniumWrapper as SW

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper

class Redfin(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, name='redfin_screenshot', headers=['FetchDate', 'State', 'County', 'PropertyLink', 'VendorLink'])
        self.datapoints = {
            "search_api": "https://www.redfin.com/stingray/do/location-autocomplete?location={}",
            "web_search": "https://www.redfin.com/county/{}",
            "web_search_for_rent": "https://www.redfin.com/county/{}/apartments-for-rent",
        }
        self.fetch_out

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        input_dict = self.scraper.utils.files.get_input_file(
            input_path=f'{self.outdir}/input/County_List.xlsx',
            header='County_NAME',
            to_dict_val='State_NAME'
        )
        for count, (key, value) in enumerate(input_dict.items()):
            state_code, county_code = self.get_county_code(value, key)
            self.out.fetchdate = self.fetch_date
            self.out.state = state_code
            self.out.county = key

            if self.scraper.utils.parse.is_partial_run(self.parser):
                if count > 2:
                    self.fetch_out = self.scraper.utils.parse.end_partial_run(self.fetch_out)
                    break
            with SW.get_driver() as driver:
                if county_code != '':
                    house_listings = self.browse_web(driver, county_code)
                    self.browse_house(driver, house_listings)

        return self.fetch_out

    def browse_web(self, driver, county_code, is_for_rent=False):
        """Browe website to gather data"""
        try:
            if is_for_rent:
                url = self.datapoints['web_search_for_rent'].format(f"{county_code}/{self.state_code}/{self.search_for.replace(' ', '-')}")
                print(url)
                SW.get_url(driver, url, sleep_seconds=1)
            else:
                SW.get_url(driver, self.datapoints['web_search'].format(county_code), sleep_seconds=1)

            driver.find_element(By.XPATH, "//span[@data-content='All filters'").click()
            time.sleep(2)
            try:
                action = ActionChains(driver)
                walk_score = driver.find_element(By.XPATH, "//span[contains(text(), 'Walk Score')]")
                open_house_el = driver.find_element(By.XPATH, "//span[contains(text(), 'Open House & Tour')]")
                action.click(open_house_el).perform()
                time.sleep(3)
                driver.find_element(By.XPATH, "//input[@name='virtualTour']").click()
                time.sleep(5)
                home_with_tour = driver.find_element(By.XPATH, "//div")
        except:
            pass


def main(argv):
    """Main entry"""
    web = Redfin(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)



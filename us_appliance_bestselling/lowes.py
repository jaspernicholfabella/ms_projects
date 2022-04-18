""" Scraping data from lowes.com"""
import sys
import os
import random
import pandas as pd
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW

class Lowes(Runner):
    """Scraping playtoearn.net Estimated Website Refresh : 1pm PHTime"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='lowes', output_subdir="raw")
        self.datapoints = {
            'summ': ["FetchDate", "Country", "Website", "Category", "URL", "PageNum", "ItemsOnSite", "ItemsFetched", ],
            'out': ['FetchDate', "Country", "Website", "Category", "Subcategory", "Name", "Model", "SKU", "Brand", "Rank",
                     'Currency', 'OrigPrice', 'DiscPrice', 'Rating', 'Reviews', 'URL', 'PageNum', 'Position', 'Capacity'],
            'to_find': {
                'Washers & Dryers': 'https://www.lowes.com/pl/Top-load-washers-Washing-machines-Washers-dryers-Appliances/4294857976?sortMethod=sortBy_bestSeller&refinement=5007197,5005561',
                'Air Conditioner': 'https://www.lowes.com/pl/Window-air-conditioners-Room-air-conditioners-Air-conditioners-fans-Heating-cooling/3788568798?sortMethod=sortBy_bestSellers&refinement=500197,505561'
            },
            'link_ext':'https://lowes.com',
            'xpath': {
                'next_page': "//a[contains(@aria-label, 'arrow right')]"
            }
        }
        self.out = Row(self.datapoints['out'])
        self.data_list = []


    def get_raw(self, **kwargs):
        """ Get Raw Files from the Websites"""
        with SW.get_driver(headless=True) as driver:
            for category, to_find in self.datapoints['to_find'].items():
                SW.get_url(driver, to_find, sleep_seconds=1)
                for cookies in driver.get_cookies():
                    print(cookies)
                    driver.add_cookie(cookies)


                print(to_find)
                self.get_table_data(driver, to_find)
                offset = 24
                while True:
                    link = f"{to_find.split('?')[0]}?offset={offset}&{to_find.split('?')[1]}"
                    self.get_table_data(driver, link)
                    # if self.check_url_exists(link, cookies):
                    #     self.get_table_data(driver, link)
                    #     offset += 24
                    # else:
                    #     break

        return self.out

    def get_table_data(self, driver, link):
        """ Get Data from the Table on the Website """
        sleep_seconds=random.randint(1,3)
        SW.get_url(driver, link, sleep_seconds=sleep_seconds)

    def normalize(self,raw):
        """Save raw data to file"""
        return pd.DataFrame(raw, columns=self.out.header()[:-1])

    @staticmethod
    def check_url_exists(url, cookies):
        """
        Checks if a url exists
        :param url: url to check
        :return: True if the url exists, false otherwise.
        """
        print(requests.head(url, allow_redirects=True, cookies=cookies).status_code)
        return requests.head(url, allow_redirects=True, cookies=cookies).status_code == 200


def main(argv):
    """Main entry"""
    web = Lowes(argv)
    web.run()


# Script starts
if __name__ == "__main__":
    main(sys.argv)

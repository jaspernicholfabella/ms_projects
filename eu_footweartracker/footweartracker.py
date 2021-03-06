""" Robot creation for EU FootwearTracker JDSports UK  """
import sys
import os
import glob
import time
import random
import re
import html
from datetime import datetime
import pandas as pd
from selenium.webdriver.common.by import By

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW
import pyersq.utils as squ

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper
import ms_projects.utility_scripts.zenscraper_0_4.utils.files as zfiles

class Footweartracker(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='footweartracker', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "out": ['FetchDate', 'Category', 'ProductCode', 'Brand',
                    'ProductName', 'OriginalPrice', 'FinalPrice', 'DiscountRate',
                    'Image', 'JDExclusive'],
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        input_dict = zfiles.get_input_file(
            f"{self.outdir}/input/eu_footweartracker_input.csv",
            header='FootwearLink',
            to_dict_val='Brands'
        )

        for url, brands in input_dict.items():
            self.scrape_page_data(url, brands)
        return self.fetch_out


    def scrape_page_data(self, url, brands):
        with SW.get_driver(headless=False) as driver:
            SW.get_url(driver, url)
            time.sleep(5)
            self.out.fetchdate = self.fetch_date
            self.out.catetgory = 'Men'
            ZenScraper().selenium_utils.actions.move_to_and_click("//button[contains(text(), 'Accept All Cookies')]")
            time.sleep(3)

            while True:
                try:
                    product_list_elements = driver.find_elements(By. XPATH, "//li[@class='productListItem']/a")
                    for product_list_item in product_list_elements:
                        title_element = product_list_item.find_element(By.XPATH, ".//span[@class='itemTitle']/a")
                        self.out.productcode = str(title_element.get_attribute('href')).split('/')[-2]
                    self.out.brand = brands
                    self.out.productname = title_element.get_attribute('innerText')

                    try:
                        self.out.originalprice = html.unescape(product_list_item.find_element(
                            By.XPATH, ".//span[@class='was']/span"
                        ).get_attribute('innerText'))
                        self.out.finalprice = html.unescape(product_list_item.find_element(
                            By.XPATH, ".//span[@class='now']/span"
                        ).get_attribute('innerText'))
                        self.out.discountrate = html.unescape(product_list_item.find_element(
                            By.XPATH, ".//span[@class='sav']/span"
                        ).get_attribute('innerText'))
                    except Exception as e:
                        self.out.originalprice = html.unescape(product_list_item.find_element(
                            By.XPATH, ".//span[@class='pri']"
                        ).get_attribute('innerText'))
                        self.out.finalprice = ''
                        self.out.discountrate = ''

                    try:
                        self.out.image = html.unescape(product_list_item.find_element(
                            By.XPATH, ".//picture/source"
                        ).get_attribute('data-srcset').split(',')[1])
                    except Exception as e:
                        self.out.image = html.unescape(product_list_item.find_element(
                            By.XPATH, ".//picture/source"
                        ).get_attribute('data-srcset').split(',')[0])
                        self.out.objectkey = self.out.compute_key()
                        self.fetch_out.append(self.out.values())
                    driver.find_element(By.XPATH, "//a[@rel='next' and contains(@class, 'pageNav')]").click()
                    time.sleep(5)
                except Exception as e:
                    break



    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.set_index("ObjectKey", inplace=True)
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Footweartracker(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)




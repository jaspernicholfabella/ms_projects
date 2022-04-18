"""website builder tracker on us_appliance_bestselling"""
import sys
import os
import glob
import time
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
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

import pyersq.robot_utils as ru

class ApplianceBestSelling(Runner):
    """ Base Class for Appliance Best Selling """
    def __init__(self, argv, name, html_folder):
        super().__init__(argv, output_prefix=name, output_subdir='raw', output_type='csv')
        self.htmldir = self.outdir/ "raw" / "htmls" / datetime.now().strftime('%Y_%m_%d') / html_folder
        self.datapoints = {
            "summ" : ["FetchDate", "Country", "Website", "Category", "URL", "PageNum", "ItemsOnSite", "ItemsFetched", ],
            "out" : ['FetchDate', "Country", "Website", "Category", "Subcategory", "Name", "Model", "SKU", "Brand", "Rank",
                     'Currency', 'OrigPrice', 'DiscPrice', 'Rating', 'Reviews', 'URL', 'PageNum', 'Position', 'Capacity']
        }
        self.summ = Row(self.datapoints['summ'])
        self.summ.fetchdate = datetime.datetime.now()
        self.fetch_summ = []
        self.fetch_out = []
        self.driver = None
        self.rank = 0
        self.raw = {}
        self.available_brands = {}

    @staticmethod
    def set_options(opts):
        """ Set additional Chrome Options """
        opts.add_argument("--disable-blink-features-AutomationControlled")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--dns-prefetch-disable")
        opts.add_argument("--disable-gpu")
        opts.add_argument("disable-infobars")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--headless")
        opts.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])

        if os.environ.get('headless', None):
            opts.add_argument('--headless')

    def __create_folder(self):
        """ Create Folder for each Website """
        if not self.htmldir.exists():
            Path(self.htmldir).mkdir(parents=True, exists_ok = True)

    def save_raw(self, raw, **kwargs):
        """ Override save_raw() """
        self.__create_folder()

        for key, html in self.raw.items():
            page = self.htmldir/ f'{key}.html'
            page.write_text(html, encoding='utf-8')

    def write_df(self, name, records, old_prefix):
        """ Write dataframe to output file. """
        df = pd.DataFrame(records, columns=self.datapoints['name'])
        df.set_index("ObjectKey", inplace=True)
        self.prefix = self.prefix.replace(old_prefix, name)
        super().save_output(df, index=True)
        return df

    def normalize(self, raw, **kwargs):
        """Override Normalize"""
        df = pd.DataFrame(self.fetch_out, columns=self.datapoints["out"]).set_index("ObjectKey")
        return df

    def save_output(self, data, **kwargs):
        """ Override save_output() """
        super().save_output(data, index=True)
        df = self.write_df("summ", self.fetch_summ, old_prefix="out")
        self.create_index(df)

    def create_index(self, df):
        """ create index.html """
        df = df.reset_index().replace("\"", "", regex=True)
        ru.create_index(df, f"{self.htmldir}/", cat1="Category")


def main(argv):
    """Main entry"""
    web = ApplianceBestSelling(argv)
    web.run()




# Script starts
if __name__ == "__main__":
    main(sys.argv)

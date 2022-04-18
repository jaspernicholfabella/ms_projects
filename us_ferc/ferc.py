"""website builder tracker on https://trends.builtwith.com/cms/simple-website-builder"""
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


class Ferc(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='ferc', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": 'https://elibrary.ferc.gov/eLibrary/searc',
            "out": ['FetchDate', 'Company', 'Status',  'Category', 'Accession', 'Filed',
                    'Document', 'Description', 'Class/Type', 'Security Level', 'Operating Revenue',
                    'Operating Expenses', 'Depreciation', 'Amortization'],
            ":summ": ['Status', 'Value'],
            "xpath_for_mining": {
                'operating_revenues': "//div[contains(text(), 'Operating Revenues')]"
                                      "/parent::node()/parent::node()/parent::tr/td",
                'operating_expenses': "//div[contains(text(), 'Operating Expenses')]"
                                      "/parent::node()/parent::node()/parent::tr/td",
                'depreciation': "//div[text()='Depreciation']"
                                "/parent::node()/parent::node()/parent::tr/td",
                'amortization': "//div[text()='Amortization']"
                                "/parent::node()/parent::node()/parent::tr/td"
            }
        }

        input_path = f'{self.outdir}/input/FERC_input.xlsx'
        to_find_data = pd.read_excel(os.path.abspath(input_path), sheet_name=1)
        self.to_find = to_find_data['Company Name'].drop_duplicates().to_list()

        self.out = Row(self.datapoints["out"])
        self.out_data = []
        self.status = 'complete'


    def get_raw(self):
        """ Get raw data from source"""
        fetchdate = datetime.now().strftime('%m/%d/%Y')
        self.out.fetchdate = fetchdate

        retry = 0
        for to_find in self.to_find:
            file_name = self.string_filter(to_find, remove_spaces=False).replace(" ", "_")
            download_dir = os.path.abspath(f'{self.outdir}/input/'
                                           f'{datetime.now().strftime("%Y_%m_%d")}/ferc/{file_name}')
            Path(download_dir).mkdir(parents=True, exist_ok=True)
            download_dir = ''
            while True:
                is_file_downloaded = self.download_source_file(download_dir, to_find)
                if is_file_downloaded:
                    break
                if retry >= 3:
                    break
                retry += 1
        return self.out_data

    def normalize(self,raw):
        """Save raw data to file"""
        df = pd.DataFrame(raw, columns=self.out.header()[:-1])
        df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return df

    def download_source_file(self,download_dir, to_find):
        """
        web navigation to download html file from FERC website

        :param download_dir: directory where the file should be downloaded
        :param to_find: string that specify which company to find
        :return: bool, if not success repeat the download process
        """
        with SW.get_driver(download_dir=download_dir, desired_capabilities=SW.enable_log()) as driver:
            self.navigate_form(driver, to_find)
            row_element, row_data = self.mining_details(driver, to_find)
            if row_data == ['', '', '', '', '', '', '']:
                self.out_data.append([self.out.fetchdate, to_find, self.status, *row_data, '', '', '', ''])
                return True
            else:
                try:
                    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'html')]/parent::a")))
                    row_element.find_element(By.XPATH, ".//span[contains(text(), 'html')]/parent::a").click()
                    time.sleep(30)
                except NoSuchElementException:
                    self.status = 'nohtml - pdf is the only output'
                    self.out_data.append([self.out.fetchdate, to_find, self.status, *row_data, '', '', '', ''])
                    return True
                try:
                    list_of_files = glob.glob(f'{download_dir}/*.html')  # * means all if need specific format then *.csv
                    latest_file = max(list_of_files, key=os.path.getctime)
                except ValueError:
                    return False

                with open(latest_file, 'r', encoding="utf8") as file:
                    soup = BeautifulSoup(file, "lxml")
                dom = etree.HTML(str(soup))

                self.status = 'complete'
                self.out_data.append([self.out.fetchdate, to_find, self.status, *row_data,
                                       self.search_downloaded_html(dom, 5, self.datapoints['xpath_for_mining']['operating_revenues']),
                                       self.search_downloaded_html(dom, 5, self.datapoints['xpath_for_mining']['operating_expenses']),
                                       self.search_downloaded_html(dom, 2, self.datapoints['xpath_for_mining']['depreciation']),
                                       self.search_downloaded_html(dom, 2, self.datapoints['xpath_for_mining']['amortization'])])

                self.complete = self.complete + 1
                return True

    def navigate_form(self, driver, to_find):
        """navigation on the html form"""
        url = self.datapoints['base_url']
        sleep_seconds = random.randint(1, 3)
        SW.get_url(driver, url, sleep_seconds=sleep_seconds)
        driver.find_element(By.XPATH, "//input[@name='textsearch']").send_keys(to_find)
        element_date_start = driver.find_element(By.XPATH, "//input[@name='dFROM']")
        date = datetime.now() - relativedelta(months=+12)
        element_date_start.send_keys(Keys.CONTROL, 'a')
        element_date_start.send_keys(date.strftime('%m/%d/%Y'))
        driver.find_element(By.XPATH, "//button[contains(@class, 'toggle')]").click()
        element_filter = driver.find_element(By.XPATH, "//input[@placeholder='Filter']")
        element_filter.clear()
        element_filter.send_keys('Form 6')
        driver.find_element(By.XPATH, "//label[contains(text(),'Form 6')]/parent::node()/input").click()
        driver.find_element(By.XPATH, "//label[contains(text(),'Form 6-Q')]/parent::node()/input").click()
        driver.find_element(By.ID, "submit").click()

    def mining_details(self, driver, to_find):
        """mining table result from navigation"""
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//div[@id='main-content']")))
        rows = driver.find_element(By.ID, "tblRslt").find_element(By.XPATH, ".//tbody").find_elements(By.XPATH, ".//tr")
        is_name_matched = False
        row_data = []
        row_element = None
        for row in rows:
            for data in row.find_elements(By.XPATH, ".//td"):
                if self.string_filter(to_find) in self.string_filter(data.get_attribute("innerText")):
                    is_name_matched = True
                    row_element = row
                    break


        if is_name_matched:
            for count, row in enumerate(row_element.find_elements(By.XPATH, ".//td")):
                if count in (4, 8):
                    continue
                row_data.append(row.get_attribute("innerText"))
                if len(row_data) == 7:
                    break
        else:
            self.status = 'nohtml - name does not match description'
            print(self.status)
            row_data = ['', '', '', '', '', '', '']

        return row_element, row_data


    @staticmethod
    def string_filter(text, remove_spaces=True):
        """Remove symbols and spaces"""
        text = re.sub(r'[^\w]', ' ', text)
        if remove_spaces:
            text = text.replace(' ','')
        return text.lower()

    @staticmethod
    def search_downloaded_html(dom, delimiter, xpath):
        """ Search element from the downloaded file """
        elements = dom.xpath(xpath)
        for count, element in enumerate(elements):
            if count == delimiter:
                text = str(etree.tostring(element)).replace('b\'', '')[:-1]
                strip_html = re.compile(r'<.*?>|=')
                return strip_html.sub('', text)
        return ''


def main(argv):
    """Main entry"""
    web = Ferc(argv)
    web.run()


# Script starts
if __name__ == "__main__":
    main(sys.argv)

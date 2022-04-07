"""website builder tracker on https://trends.builtwith.com/cms/simple-website-builder"""
import sys
import os
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.relativedelta import relativedelta

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW

class BWTracker(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='ferc', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": 'https://elibrary.ferc.gov/eLibrary/searc',
            "to_find": ['Permian Express Partners LLC', 'Seaway Crude Pipeline Company LLC', 'Dakota Access, LLC'],
            "data_table": ['FetchDate', 'Company', 'Category', 'Accession', 'Filed',
                           'Document', 'Description', 'Class/Type', 'Security Level', 'Operating Revenue', 'Operating Expenses',
                           'Depreciation', 'Amortization'],
            "xpath_for_mining": {
                'operating_revenues': "//div[contains(text(), 'Operating Revenues')]/parent::node()/parent::node()/parent::tr/td",
                'operating_expenses': "//div[contains(text(), 'Operating Expenses')]/parent::node()/parent::node()/parent::tr/td",
                'depreciation': "//div[text()='Depreciation']/parent::node()/parent::node()/parent::tr/td",
                'amortization': "//div[text()='Amortization']/parent::node()/parent::node()/parent::tr/td"
            }

        }
        self.data_table = Row(self.datapoints["data_table"])
        self.data_list = []


    def get_raw(self):
        """ Get raw data from source"""
        fetchdate = datetime.now().strftime('%m/%d/%Y')
        self.data_table.fetchdate = fetchdate
        download_dir = os.path.abspath(f'{self.outdir}/raw/downloads')
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        retry = 0
        for to_find in self.datapoints["to_find"]:
            while True:
                is_file_downloaded = self.download_source_file(download_dir, to_find)
                if is_file_downloaded:
                    break
                if retry >= 3:
                    break
                retry += 1

        return self.data_list

    def download_source_file(self,download_dir, to_find):
        """
        web navigation to download html file from FERC website

        :param download_dir: directory where the file should be downloaded
        :param to_find: string that specify which company to find
        :return: bool, if not success repeat the download process
        """
        with SW.get_driver(download_dir=download_dir, desired_capabilities=SW.enable_log()) as driver:
            url = self.datapoints['base_url']
            SW.get_url(driver, url)
            driver.find_element(By.XPATH, "//input[@name='textsearch']").send_keys(to_find)
            element_date_start = driver.find_element(By.XPATH, "//input[@name='dFROM']")
            date = datetime.now() - relativedelta(months=+6)
            element_date_start.send_keys(Keys.CONTROL, 'a')
            element_date_start.send_keys(date.strftime('%m/%d/%Y'))
            driver.find_element(By.XPATH, "//button[contains(@class, 'toggle')]").click()
            element_filter = driver.find_element(By.XPATH, "//input[@placeholder='Filter']")
            element_filter.clear()
            element_filter.send_keys('Form 6')
            driver.find_element(By.XPATH, "//label[contains(text(),'Form 6')]/parent::node()/input").click()
            driver.find_element(By.XPATH, "//label[contains(text(),'Form 6-Q')]/parent::node()/input").click()
            driver.find_element(By.ID, "submit").click()
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'html')]/parent::a")))

            table_row = driver.find_elements(By.XPATH, "//span[contains(text(), 'html')]/parent::a/parent::node()/parent::node()/parent::tr/td")
            row_data = []
            for count, row in enumerate(table_row):
                if count in (4, 8):
                    continue
                row_data.append(row.get_attribute("innerText"))
                if len(row_data) == 7:
                    break

            driver.find_element(By.XPATH, "//span[contains(text(), 'html')]/parent::a").click()

            filename = self.wait_file_complete(300, driver)
            new_file_path = f'{download_dir}/{to_find.lower().strip().replace(" ","_")}.html'
            old_file_path = f'{download_dir}/{filename}'
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            try:
                os.rename(old_file_path, new_file_path)
            except FileNotFoundError:
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                return False

            self.delete_all_tab(driver)

            driver.get(new_file_path)
            self.data_list.append([self.data_table.fetchdate, to_find, *row_data,
                                   self.search_downloaded_html(driver, 5, self.datapoints['xpath_for_mining']['operating_revenues']),
                                   self.search_downloaded_html(driver, 5, self.datapoints['xpath_for_mining']['operating_expenses']),
                                   self.search_downloaded_html(driver, 2, self.datapoints['xpath_for_mining']['depreciation']),
                                   self.search_downloaded_html(driver, 2, self.datapoints['xpath_for_mining']['amortization'])])

            return True
            # SW.get_url(driver, new_file_path)
            # time.sleep(100)

    @staticmethod
    def search_downloaded_html(driver, delimiter, xpath):
        """ Search element from the downloaded file """
        elements = driver.find_elements(By.XPATH, xpath)
        for count, element in enumerate(elements):
            if count == delimiter:
                return element.get_attribute('innerText').strip()
        return ''

    @staticmethod
    def delete_all_tab(driver):
        """ Delete all tab except for the current opened tab """
        curr = driver.current_window_handle
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if handle != curr:
                driver.close()

    @staticmethod
    def wait_file_complete(wait_time, driver):
        """Check if file is 100% downloaded on chrome://downloads tab"""
        driver.execute_script("window.open()")
        # switch to new tab
        driver.switch_to.window(driver.window_handles[-1])
        # navigate to chrome downloads
        driver.get('chrome://downloads')
        # define the endTime
        end_time = time.time() + wait_time
        while True:
            try:
                # get downloaded percentage
                download_percentage = driver.execute_script(
                    "return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('#progress').value")
                # check if downloadPercentage is 100 (otherwise the script will keep waiting)
                if download_percentage == 100:
                    # return the file name once the download is completed
                    return driver.execute_script(
                        "return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
            except:
                pass
            time.sleep(1)
            if time.time() > end_time:
                break

    def normalize(self,raw):
        """Save raw data to file"""
        return pd.DataFrame(raw, columns=self.data_table.header()[:-1])

def main(argv):
    """Main entry"""
    web = BWTracker(argv)
    web.run()


# Script starts
if __name__ == "__main__":
    main(sys.argv)

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
        super().__init__(
            argv, output_prefix="ferc", output_subdir="raw", output_type="csv"
        )
        self.datapoints = {
            "base_url": "https://elibrary.ferc.gov/eLibrary/searc",
            "out": [
                "FetchDate",
                "Company",
                "Status",
                "Category",
                "Accession",
                "Filed",
                "Document",
                "Description",
                "Class/Type",
                "Security Level",
                "Operating Revenue",
                "Operating Expenses",
                "Depreciation",
                "Amortization",
                "Download File Location",
            ],
            "summ": ["FetchDate", "Status", "Value"],
            "xpath_for_mining": {
                "operating_revenues": "//div[contains(text(), 'Operating Revenues')]"
                "/parent::node()/parent::node()/parent::tr/td",
                "operating_expenses": "//div[contains(text(), 'Operating Expenses')]"
                "/parent::node()/parent::node()/parent::tr/td",
                "depreciation": "//div[text()='Depreciation']"
                "/parent::node()/parent::node()/parent::tr/td",
                "amortization": "//div[text()='Amortization']"
                "/parent::node()/parent::node()/parent::tr/td",
            },
        }

        self.out = Row(self.datapoints["out"])
        self.summ = Row(self.datapoints["summ"])
        self.form_6_out_data = self.form_6_summ_data = []
        self.form_6Q_out_data = self.form_6Q_summ_data = []
        self.row_data = []
        self.form = ""
        self.form_6_status_count = {
            "complete": 0,
            "nodata": 0,
            "nohtml": 0,
            "failed": 0,
        }
        self.form_6Q_status_count = {
            "complete": 0,
            "nodata": 0,
            "nohtml": 0,
            "failed": 0,
        }

    def get_raw(self):
        """ Get raw data from source"""
        input_path = f"{self.outdir}/input/FERC_input_2.xlsx"
        to_find_data = pd.read_excel(os.path.abspath(input_path), sheet_name=1)
        company_to_find = to_find_data["Company Name"].drop_duplicates().to_list()

        fetchdate = datetime.now().strftime("%m/%d/%Y")
        self.out.fetchdate = self.summ.fetchdate = fetchdate

        for to_find in company_to_find:
            self.start_scraping_process(
                "form6", to_find, self.form_6_status_count, self.form_6_out_data
            )
            self.start_scraping_process(
                "form6Q", to_find, self.form_6Q_status_count, self.form_6Q_out_data
            )

    def start_scraping_process(self, form, to_find, status_count, out_data):
        """Function to Start the Scraping Process with 3 retries"""
        retry = 0
        self.form = form
        download_dir = self.generate_download_dir(to_find)
        while True:
            is_file_downloaded = self.download_source_file(
                download_dir, to_find, status_count, out_data
            )
            if is_file_downloaded:
                break
            if retry >= 3:
                self.status = "failed - download failed. (Time Out on 3 Retries)"
                status_count["failed"] += 1
                out_data.append(
                    [self.out.fetchdate, to_find, self.status, *self.row_data]
                )
                break
            retry += 1

    def generate_download_dir(self, to_find):
        """ Generating Download Directory"""
        file_name = self.string_filter(
            f"{to_find}_{self.form}", remove_spaces=False
        ).replace(" ", "_")
        download_dir = os.path.abspath(
            f"{self.outdir}/input/"
            f'{datetime.now().strftime("%Y_%m_%d")}/ferc/{file_name}'
        )
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        return download_dir

    def download_source_file(self, download_dir, to_find, status_count, out_data):
        """
        web navigation to download html file from FERC website

        :param download_dir: directory where the file should be downloaded
        :param to_find: string that specify which company to find
        :return: bool, if not success repeat the download process
        """
        print(f"process for {to_find}")
        with SW.get_driver(download_dir=download_dir, headless=True) as driver:
            self.navigate_form(driver, to_find)
            row_element = self.mining_details(driver, to_find, status_count)
            if row_element is None:
                out_data.append(
                    [self.out.fetchdate, to_find, self.status, *self.row_data]
                )
                return True

            row_element.find_element(
                By.XPATH, ".//span[contains(text(), 'html')]/parent::a"
            ).click()
            time.sleep(60)

            try:
                list_of_files = glob.glob(
                    f"{download_dir}/*.html"
                )  # * means all if need specific format then *.csv
                latest_file = max(list_of_files, key=os.path.getctime)
            except ValueError:
                return False

            with open(latest_file, "r", encoding="utf8") as file:
                soup = BeautifulSoup(file, "lxml")
            dom = etree.HTML(str(soup))
            self.status = "complete"
            status_count["complete"] += 1
            if self.form == "form6":
                income_statement_delimeter = 5
            elif self.form == "form6Q":
                income_statement_delimeter = 3
            out_data.append(
                [
                    self.out.fetchdate,
                    to_find,
                    self.status,
                    *self.row_data,
                    self.search_downloaded_html(
                        dom,
                        income_statement_delimeter,
                        self.datapoints["xpath_for_mining"]["operating_revenues"],
                    ),
                    self.search_downloaded_html(
                        dom,
                        income_statement_delimeter,
                        self.datapoints["xpath_for_mining"]["operating_expenses"],
                    ),
                    self.search_downloaded_html(
                        dom, 2, self.datapoints["xpath_for_mining"]["depreciation"]
                    ),
                    self.search_downloaded_html(
                        dom, 2, self.datapoints["xpath_for_mining"]["amortization"]
                    ),
                    str(download_dir),
                ]
            )
            return True

    def navigate_form(self, driver, to_find):
        """navigation on the html form"""
        url = self.datapoints["base_url"]
        sleep_seconds = random.randint(1, 5)
        SW.get_url(driver, url, sleep_seconds=sleep_seconds)
        driver.find_element(By.XPATH, "//input[@name='textsearch']").send_keys(to_find)
        element_date_start = driver.find_element(By.XPATH, "//input[@name='dFROM']")
        date = datetime.now() - relativedelta(months=+12)
        element_date_start.send_keys(Keys.CONTROL, "a")
        element_date_start.send_keys(date.strftime("%m/%d/%Y"))
        driver.find_element(By.XPATH, "//button[contains(@class, 'toggle')]").click()
        element_filter = driver.find_element(By.XPATH, "//input[@placeholder='Filter']")
        element_filter.clear()
        element_filter.send_keys("Form 6")
        if self.form == "form6":
            driver.find_element(
                By.XPATH, "//label[contains(text(),'Form 6')]/parent::node()/input"
            ).click()
        elif self.form == "form6Q":
            driver.find_element(
                By.XPATH, "//label[contains(text(),'Form 6-Q')]/parent::node()/input"
            ).click()
        driver.find_element(By.ID, "submit").click()

    def mining_details(self, driver, to_find, status_count):
        """mining table result from navigation"""
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='main-content']"))
        )
        rows = (
            driver.find_element(By.ID, "tblRslt")
            .find_element(By.XPATH, ".//tbody")
            .find_elements(By.XPATH, ".//tr")
        )
        is_name_matched = False
        self.row_data = []
        row_elements = []
        for row in rows:
            for data in row.find_elements(By.XPATH, ".//td"):
                if self.string_filter(to_find) in self.string_filter(
                    data.get_attribute("innerText")
                ):
                    is_name_matched = True
                    row_elements.append(row)

        data_element = None
        if is_name_matched:
            for row_element in row_elements:
                try:
                    row_element.find_element(
                        By.XPATH, ".//span[contains(text(), 'html')]/parent::a"
                    )
                    data_element = row_element
                    break
                except NoSuchElementException:
                    pass

            if data_element is not None:
                self.gather_row_data(data_element)
            else:
                self.status = "nohtml"
                status_count["nohtml"] += 1
                self.gather_row_data(row_elements[0])
        else:
            self.status = "nodata - name not on description"
            status_count["nodata"] += 1
            self.row_data = ["" for _ in range(0, 12)]

        return data_element

    def gather_row_data(self, element):
        """ Gathering Row Data from the Table """
        for count, row in enumerate(element.find_elements(By.XPATH, ".//td")):
            if count in (4, 8):
                continue
            self.row_data.append(row.get_attribute("innerText"))
            if len(self.row_data) == 7:
                break

    def save_output(self, data, **kwargs):
        """Override Save output Function"""
        form_6_df = self.get_out_df(self.form_6_out_data)
        form_6Q_df = self.get_out_df(self.form_6Q_out_data)
        form_6_summ_df = self.get_summarry_df(self.form_6_status_count)
        form_6Q_summ_df = self.get_summarry_df(self.form_6Q_status_count)

        temp_prefix = self.prefix
        self.save_final_output(form_6_df, temp_prefix.replace("ferc", "ferc_form_6"))
        self.save_final_output(form_6Q_df, temp_prefix.replace("ferc", "ferc_form_6Q"))
        self.save_final_output(
            form_6_summ_df, temp_prefix.replace("ferc", "ferc_form_6_summ")
        )
        self.save_final_output(
            form_6Q_summ_df, temp_prefix.replace("ferc", "ferc_form_6Q_summ")
        )

    def save_final_output(self, dataframe, filename):
        """Save final output"""
        Path(f"{self.outdir}/{self.output_subdir}").mkdir(parents=True, exist_ok=True)
        self.prefix = filename
        super().save_output(dataframe, encoding="utf-8")

    def get_out_df(self, out_data):
        """ Get Output Data Frame"""
        dataframe = pd.DataFrame(out_data, columns=self.out.header()[:-1])
        dataframe.replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
            value=["", ""],
            regex=True,
            inplace=True,
        )
        return dataframe

    def get_summarry_df(self, status_count):
        """ Get Summary Data Frame"""
        summ_data = []
        summ_data.append([self.summ.fetchdate, "complete", status_count["complete"]])
        summ_data.append([self.summ.fetchdate, "nodata", status_count["nodata"]])
        summ_data.append([self.summ.fetchdate, "nohtml", status_count["nohtml"]])
        summ_data.append([self.summ.fetchdate, "failed", status_count["failed"]])
        summ_df = pd.DataFrame(summ_data, columns=self.summ.header()[:-1])
        return summ_df

    @staticmethod
    def string_filter(text, remove_spaces=True):
        """Remove symbols and spaces"""
        text = re.sub(r"[^\w]", " ", text)
        if remove_spaces:
            text = text.replace(" ", "")
        return text.lower()

    @staticmethod
    def search_downloaded_html(dom, delimiter, xpath):
        """ Search element from the downloaded file """
        elements = dom.xpath(xpath)
        for count, element in enumerate(elements):
            if count == delimiter:
                text = str(etree.tostring(element)).replace("b'", "")[:-1]
                strip_html = re.compile(r"<.*?>|=")
                return strip_html.sub("", text)
        return ""


def main(argv):
    """Main entry"""
    web = Ferc(argv)
    web.run()


# Script starts
if __name__ == "__main__":
    main(sys.argv)
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

sys.path.append("../../../scripts")
from pyersq.web_runner import Runner
from pyersq.selenium_wrapper import SeleniumWrapper as SW


class ORMType:
    """ Unique type class to decipher between attributes """

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __index__(self):
        return int(self.key)


class ORM:
    """Basic ORM Class"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, ORMType(key, value))

    @staticmethod
    def attr_1():
        """ Adding this for Pylint issues """
        print("attr_1")

    @staticmethod
    def attr_2():
        """ Adding this for Pylint issues """
        print("attr_2")


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
                "Period",
                "Operating Revenue",
                "Operating Expenses",
                "Depreciation",
                "Amortization",
                "Grand Total",
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
                "period": "//div[contains(text(), 'Year/Period of Report')]"
                "/parent::node()/parent::node()/td",
                "grand_total": "//td[contains(text(), 'GRAND TOTAL')]/parent::node()/td",
            },
        }
        self.form6 = ORM()
        self.form6Q = ORM()
        self.form6.out_data = []
        self.form6Q.out_data = []
        self.form6.status_count = {
            "complete": 0,
            "nodata": 0,
            "nohtml": 0,
            "failed": 0,
        }
        self.form6Q.status_count = {
            "complete": 0,
            "nodata": 0,
            "nohtml": 0,
            "failed": 0,
        }
        self.row_data = []
        self.block = ORM()
        self.block.form = ""
        self.block.status = ""

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        input_path = f"{self.outdir}/input/FERC_input_new.xlsx"
        to_find_data = pd.read_excel(os.path.abspath(input_path), sheet_name=2)
        company_to_find = (
            to_find_data["Company Name (Cleaned)"].drop_duplicates().to_list()
        )

        for to_find in company_to_find:
            try:
                self.start_scraping_process(
                    "form6", to_find, self.form6.status_count, self.form6.out_data
                )
                self.start_scraping_process(
                    "form6Q", to_find, self.form6Q.status_count, self.form6Q.out_data
                )
            except TypeError as e:
                print(f"Exception Encountered: {e}")

    def start_scraping_process(self, form, to_find, status_count, out_data):
        """Function to Start the Scraping Process with 3 retries"""
        retry = 0
        self.block.form = form
        download_dir = self.generate_download_dir(to_find)
        while True:
            is_file_downloaded = self.download_source_file(
                download_dir, to_find, status_count, out_data
            )
            if is_file_downloaded:
                break
            if retry >= 3:
                self.block.status = "failed - download failed. (Time Out on 3 Retries)"
                status_count["failed"] += 1
                out_data.append(
                    [
                        datetime.now().strftime("%m/%d/%Y"),
                        to_find,
                        self.block.status,
                        *self.row_data,
                    ]
                )
                break
            retry += 1

    def generate_download_dir(self, to_find):
        """ Generating Download Directory"""
        file_name = self.string_filter(
            f"{to_find}_{self.block.form }", remove_spaces=False
        ).replace(" ", "_")
        download_dir = os.path.abspath(
            f"{self.outdir}/raw/downloaded_html/"
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
        with SW.get_driver(download_dir=download_dir) as driver:
            self.navigate_form(driver, to_find)
            row_element = self.mining_details(driver, to_find, status_count)
            if row_element is None:
                out_data.append(
                    [
                        datetime.now().strftime("%m/%d/%Y"),
                        to_find,
                        self.block.status,
                        *self.row_data,
                    ]
                )
                return True

            download_link = row_element.find_element(
                By.XPATH, ".//span[contains(text(), 'html')]/parent::a"
            ).get_attribute("href")
            print(f"download link at: {download_link}")
            SW.get_url(driver, download_link, sleep_seconds=random.randint(1, 5))

            time.sleep(30)

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
            self.block.status = "complete"
            status_count["complete"] += 1
            if self.block.form == "form6":
                income_statement_delimeter = 3
            elif self.block.form == "form6Q":
                income_statement_delimeter = 5

            # formatted_download_dir = "\\" + str(download_dir).replace('/', '\\')
            out_data.append(
                [
                    datetime.now().strftime("%m/%d/%Y"),
                    to_find,
                    self.block.status,
                    *self.row_data,
                    self.search_downloaded_html(
                        dom,
                        1,
                        self.datapoints["xpath_for_mining"]["period"],
                    ),
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
                    self.search_downloaded_html(
                        dom, 10, self.datapoints["xpath_for_mining"]["grand_total"]
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
        if self.block.form == "form6":
            driver.find_element(
                By.XPATH, "//label[contains(text(),'Form 6')]/parent::node()/input"
            ).click()
        elif self.block.form == "form6Q":
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
                if self.string_filter(data.get_attribute("innerText")).startswith(
                    self.string_filter(to_find)
                ):
                    is_name_matched = True
                    row_elements.append(row)

        row_elements = self.sort_row_elements_by_date(row_elements)

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
                self.block.status = "nohtml"
                status_count["nohtml"] += 1
                self.gather_row_data(row_elements[0])
        else:
            self.block.status = "nodata - name not on description"
            status_count["nodata"] += 1
            self.row_data = ["" for _ in range(0, 12)]

        return data_element

    @staticmethod
    def sort_row_elements_by_date(row_elements):
        """Sort Row Elemnts based """
        row_element_dict = {}
        date_arr = []
        final_arr = []
        for row_element in row_elements:
            data_elements = row_element.find_elements(By.XPATH, ".//td")
            date = str(data_elements[1].get_attribute("innerText")).strip()
            date_arr.append(date)
            row_element_dict.update({date: row_element})

        # date_arr.sort(key=lambda date: datetime.strptime(date, "%m/%d/%Y"), reverse=True)
        date_arr = sorted(date_arr, reverse=True)

        for date in date_arr:
            final_arr.append(row_element_dict[date])

        return final_arr

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
        form_6_df = self.get_out_df(self.form6.out_data)
        form_6Q_df = self.get_out_df(self.form6Q.out_data)
        form_6_summ_df = self.get_summarry_df(self.form6.status_count)
        form_6Q_summ_df = self.get_summarry_df(self.form6Q.status_count)

        temp_prefix = str(self.prefix)
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
        dataframe = pd.DataFrame(out_data, columns=self.datapoints["out"])
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
        summ_data.append(
            [datetime.now().strftime("%m/%d/%Y"), "complete", status_count["complete"]]
        )
        summ_data.append(
            [datetime.now().strftime("%m/%d/%Y"), "nodata", status_count["nodata"]]
        )
        summ_data.append(
            [datetime.now().strftime("%m/%d/%Y"), "nohtml", status_count["nohtml"]]
        )
        summ_data.append(
            [datetime.now().strftime("%m/%d/%Y"), "failed", status_count["failed"]]
        )
        summ_df = pd.DataFrame(summ_data, columns=self.datapoints["summ"])
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
                return " ".join(str(strip_html.sub("", text)).split())
        return ""


def main(argv):
    """Main entry"""
    web = Ferc(argv)
    web.run()


# Script starts
if __name__ == "__main__":
    main(sys.argv)

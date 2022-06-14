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

from ms_projects.utility_scripts.zenscraper import ZenScraper, DataObject, UtilFunctions

class Redfin(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='redfin', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "search_api": "https://www.redfin.com/stingray/do/location-autocomplete?location={}",
            "web_search": "https://www.redfin.com/county/{}",
            "web_search_for_rent": "https://www.redfin.com/county/{}/apartments-for-rent",
            "out": ['FetchDate', 'Website', 'Type', 'State', 'County', 'Total Properties', 'With 3D Tours'],
        }
        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')
        self.search_for = ''
        self.state_code = ''

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        input_path = f'{self.outdir}/input/County_List.xlsx'
        to_find_data = pd.read_excel(os.path.abspath(input_path), sheet_name=0)
        state_name_list = to_find_data['State_NAME'].to_list()
        county_name_list = to_find_data['County_NAME'].to_list()

        for count,val in enumerate(county_name_list):

            if UtilFunctions().is_partial_run(self.parser):
                if count > 2:
                    self.fetch_out = UtilFunctions().end_partial_run(self.fetch_out, self.out.header())
                    break

            state_name = state_name_list[count]
            self.search_for = val

            self.state_code, county_code = self.get_county_code(state_name)

            with SW.get_driver() as driver:
                if county_code != '':
                    self.out.objectkey = self.out.compute_key()

                    all_homes, home_with_tour = self.browse_web(driver, county_code)
                    self.fetch_out.append([self.fetch_date, 'Redfin', 'Buy',
                                          self.state_code, self.search_for, self.filter_result(all_homes),
                                          self.filter_result(home_with_tour), self.out.values()[-1]])

                    all_homes, home_with_tour = self.browse_web(driver, county_code, is_for_rent=True)
                    self.fetch_out.append([self.fetch_date, 'Redfin', 'Rent',
                                          self.state_code, self.search_for, self.filter_result(all_homes),
                                          self.filter_result(home_with_tour), self.out.values()[-1]])
        return self.fetch_out


    @staticmethod
    def filter_result(result):
        result = result.lower().replace('see', '')\
            .replace('homes', '')\
            .replace('no results', '0').strip()
        return result

    def browse_web(self, driver, county_code, is_for_rent=False):
        try:
            all_homes, home_with_tour = '', ''

            if is_for_rent:
                url = self.datapoints['web_search_for_rent'].format(f"{county_code}/{self.state_code}/{self.search_for.replace(' ', '-')}")
                print(url)
                SW.get_url(driver, url, sleep_seconds=1)
            else:
                SW.get_url(driver, self.datapoints['web_search'].format(county_code), sleep_seconds=1)

            self.wait_for_page_load(driver, wait_time=300)

            try:
                self.wait_for_element(driver, wait_time=30, xpath="//div[@class='homes summary']")
                all_homes_full = driver.find_element(By.XPATH, "//div[@class='homes summary']").get_attribute("innerText")
                all_homes_full = all_homes_full.split('of')[1]
                numeric_filter = filter(str.isdigit, all_homes_full)
                all_homes_full = "".join(numeric_filter).strip()
            except: #pylint: disable=broad-except
                all_homes_full = ''
            driver.find_element(By.XPATH, "//span[@data-content='All filters']").click()
            time.sleep(2)
            all_homes = driver.find_element(By.XPATH,
                                            "//div[@class='applyButtonContainer']/button/span").get_attribute('innerText')
            try:
                action = ActionChains(driver)
                self.wait_for_element(driver, wait_time=30, xpath="//span[contains(text(), 'Walk Score')]")
                walk_score = driver.find_element(By.XPATH, "//span[contains(text(), 'Walk Score')]")
                open_house_el = driver.find_element(By.XPATH,
                                                    "//span[contains(text(), 'Open House & Tour')]")
                action.move_to_element(walk_score).perform()
                action.click(open_house_el).perform()
                time.sleep(3)
                driver.find_element(By.XPATH, "//input[@name='virtualTour']").click()
                time.sleep(5)
                home_with_tour = driver.find_element(By.XPATH,
                                                     "//div[@class='applyButtonContainer']/button/span").get_attribute('innerText')
            except Exception as e:
                print(e)

            if '+' in all_homes:
                all_homes = all_homes_full
            return all_homes, home_with_tour
        except Exception as e:
            print(e)
            return all_homes, home_with_tour


    def wait_for_page_load(self, driver, wait_time):
        while not self._page_is_loading(driver, wait_time=wait_time):
            continue

    @staticmethod
    def wait_for_element(driver, wait_time, xpath):
        try:
            WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except Exception as e:
            print(e)

    @staticmethod
    def _page_is_loading(driver, wait_time=30):
        for _ in wait_time:
            x = driver.execute_script("return document.readyState")
            if x == "complete":
                return True
            else:
                time.sleep(1)
                yield False
        return True

    def get_county_code(self, state_name):
        try:
            state_code = ''
            with open(f'{self.outdir}/input/states_hash.json', encoding='utf-8') as f:
                for k, v in json.load(f).items():
                    if v.lower().strip() == state_name.lower():
                        state_code = k

            if state_code != '':
                api_search_for = self.search_for.lower().replace(' ','%20')
                response = ZenScraper().get(self.datapoints['search_api'].format(api_search_for))
                response_text = response.content.decode('utf-8')
                print(f'/{state_code}/{self.search_for.replace(" ", "-")}')
                if f'/{state_code}/{self.search_for.replace(" ", "-")}' in response_text:
                    suffix = f'/{state_code}/{self.search_for.replace(" ", "-")}'
                    county_code = re.search(f'/county/(.*?){suffix}', response_text).group(1)
                    county_code = county_code.split('/')[-1]
                    return state_code, county_code
        except Exception as e:
            print(e)
        return '', ''

    def save_output(self, data, **kwargs):
        """Save final data to output file"""
        self.save_output_csv(data, index=True)

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header())
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        data_frame.set_index("ObjectKey", inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Redfin(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)



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

sys.path.append('../../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
import pyersq.utils as squ
from pyersq.selenium_wrapper import SeleniumWrapper as SW

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper

class Matterport(Runner):
    """Collect data from website"""
    def __init__(self, argv, name, headers):
        super().__init__(argv, output_prefix=name, output_subdir="raw", output_type='csv')
        self.datapoints = {
            "search_api": "https://www.redfin.com/stingray/do/location-autocomplete?location={}",
            "web_search": "https://www.redfin.com/county/{}",
            "web_search_for_rent": "https://www.redfin.com/county/{}/apartments-for-rent",
            "out": ['FetchDate', 'Website', 'Type', 'State', 'County', 'Total Properties', 'With 3D Tours'],
        }
        self.parser = squ.get_parser()
        self.out = Row(headers)
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')
        self.scraper = ZenScraper()


    @staticmethod
    def filter_result(result):
        result = result.lower().replace('see', '')\
            .replace('homes', '')\
            .replace('home', '')\
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

            self.zs.selenium_utils.wait_for_page_load(driver, wait_time=600)

            try:
                self.zs.selenium_utils.wait_for_element(driver, "//div[@class='homes summary']", wait_time=100)
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
                self.wait_for_element(driver, "//span[contains(text(), 'Walk Score')]", wait_time=100)
                walk_score = driver.find_element(By.XPATH, "//span[contains(text(), 'Walk Score')]")
                open_house_el = driver.find_element(By.XPATH,
                                                    "//span[contains(text(), 'Open House & Tour')]")
                action.move_to_element(walk_score).perform()
                action.click(open_house_el).perform()
                time.sleep(3)
                driver.find_element(By.XPATH, "//input[@name='virtualTour']").click()
                time.sleep(5)
                home_with_tour = driver.find_element(By.XPATH, "//div[@class='applyButtonContainer']/button/span").get_attribute('innerText')
            except Exception as e:
                print(e)

            if '+' in all_homes:
                all_homes = all_homes_full
            return all_homes, home_with_tour
        except Exception as e:
            print(e)
            return all_homes, home_with_tour


    def wait_for_page_load(self, driver, wait_time=30):
        while not self._page_is_loading(driver, wait_time=wait_time):
            continue


    def get_county_code(self, state_name, search_for):
        try:
            state_code = ''
            with open(f'{self.outdir}/input/states_hash.json', encoding='utf-8') as f:
                for k, v in json.load(f).items():
                    if v.lower().strip() == state_name.lower():
                        state_code = k

            if state_code != '':
                api_search_for = search_for.lower().replace(' ','%20')
                response = ZenScraper().get(self.datapoints['search_api'].format(api_search_for))
                response_text = response.content.decode('utf-8')
                print(f'/{state_code}/{search_for.replace(" ", "-")}')
                if f'/{state_code}/{search_for.replace(" ", "-")}' in response_text:
                    suffix = f'/{state_code}/{search_for.replace(" ", "-")}'
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
    web = Matterport(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)



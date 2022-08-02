""" Robot creation for US Matterpoint  """
import sys
import json
import os
import time
import re
from datetime import datetime
import pandas as pd
from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
import pyersq.utils as squ
from bs4 import BeautifulSoup
from pyersq.selenium_wrapper import SeleniumWrapper as SW
from matterport import Matterport
from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper, By

class Redfin(Matterport):
    """Collect data from website"""
    def __init__(self, argv):
        headers = ['FetchDate', 'State', 'County', 'PropertyLink', 'Address', 'ListingPrice', 'BuyWithRedfin', 'Vendor',
                   'Status', 'PropertyType', 'Style', 'LotSize', 'TimeOnRedfin', 'YearBuilt', 'Community', 'MlsNo',
                   'ListPrice', 'RedfinEstimate','BuyerAgentCommission', 'EstMoPayment', 'PriceSqFt']
        super().__init__(argv, name='redfin_screenshot', headers=headers)
        self.datapoints = {
            "search_api": "https://www.redfin.com/stingray/do/location-autocomplete?location={}",
            "web_search": "https://www.redfin.com/county/{}",
            "web_search_for_rent": "https://www.redfin.com/county/{}/apartments-for-rent",
        }
        self.fetch_out = []



    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        input_dict = self.scraper.utils.files.get_input_file(
            input_path=f'{self.outdir}/input/redfin_input.csv',
            header='County',
            to_dict_val='State'
        )
        amount_to_scrape = self.scraper.utils.files.get_input_file(
            input_path=f'{self.outdir}/input/redfin_input.csv',
            header='County',
            to_dict_val='Amount'
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
            house_listings = None
            retry_count = 0
            while house_listings is None:
                with SW.get_driver(option_callback=ZenScraper().selenium_utils.options.set_options) as driver:
                    ZenScraper().selenium_utils.options.override_useragent(driver)
                    if county_code != '':
                        house_listings = self.browse_web(driver, county_code, amount_to_scrape=int(amount_to_scrape[key]))
                if retry_count == 3:
                    break
                retry_count += 1
            try:
                for house_url in house_listings:
                    self.out.propertylink = house_url
                    self.out.address = ''
                    self.out.listingprice = ''
                    self.out.buywithredfin = ''
                    self.out.vendor = ''
                    self.out.status = ''
                    self.out.propertytype = ''
                    self.out.style = ''
                    self.out.lotsize = ''
                    self.out.timeonredfin = ''
                    self.out.yearbuilt = ''
                    self.out.community = ''
                    self.out.mlsno = ''
                    self.out.listprice = ''
                    self.out.redfinestimate = ''
                    self.out.buyeragentcommission = ''
                    self.out.estmopayment = ''
                    self.out.pricesqft = ''
                    self.browse_house(house_url)
            except Exception as e:
                print(e)


        return self.fetch_out

    def browse_web(self, driver, county_code, is_for_rent=False, amount_to_scrape=0):
        """Browe website to gather data"""
        print(driver.page_source)
        try:
            if is_for_rent:
                url = self.datapoints['web_search_for_rent'].format(f"{county_code}/{self.state_code}/{self.search_for.replace(' ', '-')}")
                print(url)
                SW.get_url(driver, url, sleep_seconds=1)
            else:
                SW.get_url(driver, self.datapoints['web_search'].format(county_code), sleep_seconds=1)

            driver.find_element(SeleniumBy.XPATH, "//span[@data-content='All filters']").click()
            time.sleep(2)
            try:
                action = ActionChains(driver)
                walk_score = driver.find_element(SeleniumBy.XPATH, "//span[contains(text(), 'Walk Score')]")
                open_house_el = driver.find_element(SeleniumBy.XPATH, "//span[contains(text(), 'Open House & Tour')]")
                action.move_to_element(walk_score).perform()
                action.click(open_house_el).perform()
                time.sleep(3)
                driver.find_element(SeleniumBy.XPATH, "//input[@name='virtualTour']").click()
                time.sleep(5)
                driver.find_element(SeleniumBy.XPATH, "//div[@class='applyButtonContainer']/button/span").click()
                time.sleep(3)

                house_listings = []
                loop_count = 0
                while loop_count < 11:
                    elements = driver.find_elements(SeleniumBy.XPATH, "//div[contains(text(),'3D')]/parent::node()/parent::node()/parent::node()//a")

                    print(f'Gathering url ({len(house_listings)}/{amount_to_scrape})')
                    for element in elements:
                        try:
                            # json_data = json.loads(element.get_attribute('innerText'))
                            url = element.get_attribute('href')
                            house_listings.append(url)

                            if len(house_listings) >= amount_to_scrape:
                                break
                        except:
                            pass
                    house_listings = list(set(house_listings))
                    loop_count += 1
                    if len(house_listings) >= amount_to_scrape:
                        print(f'URL Gathered Successfully ({len(house_listings)}/{amount_to_scrape})')
                        break

                    action = ActionChains(driver)
                    next_button = driver.find_element(SeleniumBy.XPATH, "//button[@data-rf-test-id='react-data-paginate-next']")
                    action.move_to_element(next_button).perform()
                    action.click(next_button).perform()
                    time.sleep(3)
                return house_listings

            except Exception as e:
                print(e)
        except:
            pass



    def browse_house(self, url):
        try:
            scraper = ZenScraper()
            scraper.logger.warning('Scraping data from: %s', url)
            scraper.get(url, sleep_seconds=1)
            self.out.address = scraper.find_element(By.XPATH, "//h1[@class='full-address']").get_attribute('innerText')
            self.out.listingprice = scraper.find_element(By.XPATH, "//div[@class='statsValue']").get_attribute('innerText')
            try:
                self.out.buywithredfin = scraper.find_element(By.XPATH, "//span[contains(text(), 'Buy with Redfin')]/parent::node()").get_attribute('innerText', inner_text_filter=['Buy With Redfin:'])
            except Exception as e:
                self.out.buywithredfin = ''
            try:
                vendor = scraper.find_element(By.XPATH, "//div[contains(text(),'3D Walkthrough')]/parent::node()/parent::node()/script").get_attribute('innerText')
                self.out.vendor = vendor[vendor.find("[")+1:vendor.find("]")].replace('data-buttonenum','').replace('"', '')
            except Exception as e:
                try:
                    vendor = scraper.find_element(By.XPATH,
                                                  "//span[contains(text(), 'Virtual Tour URL Branded')]/span/a").get_attribute(
                        'href')
                    self.out.vendor = vendor
                except Exception as e:
                    self.out.vendor = ''
                self.out.vendor = ''



            self.out.status = scraper.find_element(By.XPATH, "//span[contains(text(), 'Status')]/parent::node()/span[2]/div").get_attribute('innerText')
            self.out.propertytype = self.get_span_data(scraper, 'Property Type')
            self.out.style = self.get_span_data(scraper, 'Style')
            self.out.lotsize = self.get_span_data(scraper, 'Lot Size')
            self.out.timeonredfin = self.get_span_data(scraper, 'Time on Redfin')
            self.out.yearbuilt = self.get_span_data(scraper, 'Year Built')
            self.out.community = self.get_span_data(scraper, 'Community')
            self.out.mlsno = self.get_span_data(scraper, 'MLS#')
            self.out.listprice = self.get_span_data(scraper, 'List Price')
            try:
                self.out.redfinestimate = scraper.find_element(By.XPATH, "//span[contains(text(), 'Redfin Estimate')]/parent::node()/parent::node()/parent::node()/span[2]").get_attribute('innerText')
            except Exception as e:
                self.out.redfinestimate = ''
            try:
                self.out.buyeragentcommission = scraper.find_element(By.XPATH,"//span[contains(text(), 'Agent Commission')]/parent::node()/parent::node()/parent::node()/parent::node()/span[2]").get_attribute('innerText')
            except Exception as e:
                self.out.buyeragentcommission = ''
            self.out.estmopayment = self.get_span_data(scraper, 'Est. Mo. Payment')
            self.out.pricesqft = self.get_span_data(scraper, 'Price/Sq.Ft.')
            self.out.objectkey = self.out.compute_key()
            self.fetch_out.append(self.out.values())
        except Exception as e:
            print(url)

    @staticmethod
    def get_span_data(scraper, to_find=''):
        try:
            data = scraper.find_element(By.XPATH,f"//span[contains(text(), '{to_find}')]/parent::node()/span[2]").get_attribute('innerText')
            return data
        except Exception as e:
            return ''


def main(argv):
    """Main entry"""
    web = Redfin(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)



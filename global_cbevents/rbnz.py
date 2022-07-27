""" Robot creation for RBNZ website  """
import sys
import time
from datetime import datetime
import pandas as pd
from selenium.webdriver.common.by import By as SeleniumBy
sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW
import pyersq.utils as squ

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper, By

class Rbnz(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='rbnz', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": 'https://www.rbnz.govt.nz/news-and-events/events',
            "out": ['FetchDate', 'Bank', 'EventDate', 'EventTime', 'Timezone', 'EventVenue',
                    'Topic', 'Description', 'LNDate', 'LNTime'],
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')
        self.event_urls = []
        self.scraper = ZenScraper()


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        with SW.get_driver(option_callback=self.scraper.selenium_utils.options.set_options) as driver:
            self.scraper.selenium_utils.options.override_useragent(driver)
            SW.get_url(driver, self.datapoints['base_url'])

            while True:
                try:
                    time.sleep(5)
                    self.get_links(driver)
                    driver.find_element(SeleniumBy.XPATH, "//span[@title='Next']").click()
                except Exception as e:
                    break

        self.event_urls = list(set(self.event_urls))
        self.get_events_data()


        return self.fetch_out

    def get_links(self, driver):
        self.out.fetchdate = self.fetch_date
        self.out.bank = 'RBNZ'
        self.out.timezone = 'NZST'
        url_elements = driver.find_elements(
            SeleniumBy.XPATH, "//a[contains(@class, 'CoveoResultLink' )]"
        )
        for url_element in url_elements:
            self.event_urls.append(url_element.get_attribute('href'))

    def get_events_data(self):
        for event_url in self.event_urls:
            with SW.get_driver(option_callback=self.scraper.selenium_utils.options.set_options) as driver:
                self.scraper.selenium_utils.options.override_useragent(driver)
                SW.get_url(driver, event_url)
            time.sleep(5)
            event_datetime = driver.find_element(
                By.XPATH, "//node()[@class='hero__event-card-date']"
            ).get_attribute('innerText')
            print(event_datetime)


    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Rbnz(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)
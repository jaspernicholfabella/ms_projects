""" Robot creation for US Matterport 3D Listings  """
import sys

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

from ms_projects.utility_scripts.zenscraper import ZenScraper, By, DataObject, UtilFunctions

class Zillow(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='zillow', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "out": ['FetchDate'],
        }

        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

    def get_raw(self, **kwargs):
        url = 'https://www.zillow.com/homes/CA_rb/'
        with SW.get_driver(desired_capabilities=SW.enable_log()) as driver:
            SW.get_url(driver, url, sleep_seconds=0)
            logs = self.get_networklogs(driver)

    def get_networklogs(self, driver):
        try:
            logs = list(SW.get_log_msg(driver, self.network_msg))
        except Exception as e: #pylint: disable:broad-except
            pass
        return None

    @staticmethod
    def network_msg(log):
        if (log['method'] == 'Network.responseRecieved' and "params" in log.keys()):
            url = log['params']['response']['url']
            print(url)

        # return False

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame

def main(argv):
    """Main entry"""
    web = Zillow(argv)
    web.run2()

if __name__ == "__main__":
    main(sys.argv)

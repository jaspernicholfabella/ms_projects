""" Robot creation for US Opendoor Homes  """
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
import pyersq.utils as squ
import json

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper, By as zBy

class Opendoor(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='opendoor', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url" : "https://www.opendoor.com/homes",
            "out": ['Collection Date', 'Home ID', 'Street', 'City', 'State', 'Postal Code'
                    'Listing Status', 'Bedrooms', 'Bathrooms', 'Sqft', 'Lot Sqft', 'Location Breadcrumb',
                    'Description', 'Listed By', 'List Price', 'Buy w/ OD Price', 'For Sale Date', 'Year Built',
                    'Price per Sqft', 'Home Type', 'OpenDoor owned home', 'Monthly cost', 'Pay when you close',
                    'Estimated closing credit'],
        }

        self.parser = squ.get_parser()
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        scraper = ZenScraper()
        scraper.get("https://www.opendoor.com/homes/95-riverstone-dr-riverstone-estates-covington-ga-30014")
        elements = scraper.find_elements(zBy.XPATH, '//script')

        for element in elements:
            if 'window.initialJson' in element.get_attribute('innerText'):
                json_string = str(element.get_attribute('innerText')).replace('window.initialJson', '').strip()
                print(json_string)

        # location_list = scraper.utils.files.get_input_file(
        #     f'{self.outdir}/input/opendoor_input.csv',
        #     header='Location'
        # )
        # for location in location_list:
        #     print(f'{self.datapoints["base_url"]}/{location}')

        # location_json = scraper.utils.json.get_json(
        #     "https://buy.opendoor.com/zones/from_breadcrumb.json?breadcrumb_path=/atlanta"
        # )
        #
        # location = location_json['center']
        # location_dict = {
        #     'north': location_json['bounds'][0][0],
        #     'east' : location_json['bounds'][1][1],
        #     'south' : location_json['bounds'][1][0],
        #     'west' : location_json['bounds'][0][1],
        #     'loc_1': location_json['center'][1],
        #     'loc_2': location_json['center'][0]
        # }
        #
        # listing_json = self.get_listing_json(scraper, location_dict, page_size=1)
        # const_max_page = int(listing_json['cnt'])
        # max_page_count = int(listing_json['cnt'])
        # page_count = 1
        # while max_page_count > 0:
        #     print(f'getting thousands value on page-{page_count}')
        #     print(f'current page_count_left: {max_page_count}')
        #     temp_listings = self.get_listing_json(scraper, location_dict, page_num=page_count, page_size=100)
        #     print(temp_listings)
        #     max_page_count -= 1000
        #     page_count += 1
        #
        # properties=temp_listings['properties']
        # [self.fetch_date, properties[0]['id'], properties[0]['address_line_1'], properties[0]['city'], properties[0]['address_line_1'], properties[0]['zip'],
        #  properties[0]['properties_type'], properties['bedrooms'],
        #  'Bathrooms', 'Sqft', 'Lot Sqft', 'Location Breadcrumb',
        #  'Description', 'Listed By', 'List Price', 'Buy w/ OD Price', 'For Sale Date', 'Year Built',
        #  'Price per Sqft', 'Home Type', 'OpenDoor owned home', 'Monthly cost', 'Pay when you close',
        #  'Estimated closing credit']


        # if max_page_count >= 100:
        #     while max_page_count >= 100:
        #         print(f'getting hundreds value on loop-{count}')
        #         print(f'current page_count_left: {max_page_count}')
        #         temp_listings = self.get_listing_json(scraper, location_dict, page_size=100)
        #         max_page_count -= 100

        # print(f'current page_count_left: {max_page_count}')
        # temp_listings = self.get_listing_json(scraper, location_dict, page_size=max_page_count)


        # print(listing_json['cnt'])
        return self.fetch_out

    def get_listing_json(self, scraper, location_dict, page_num=1, page_size=10):

        listings_url = f"""
            https://buy.opendoor.com/zones/null/list_properties.json?
            page={page_num}
            &page_size={page_size}
            &sort=newest
            &properties_filter[include_homebuilder]=true
            &include_markers=1000
            &bounds[north]={location_dict['north']}
            &bounds[east]={location_dict['east']}
            &bounds[south]={location_dict['south']}
            &bounds[west]={location_dict['west']}
            &location[]={location_dict['loc_1']}
            &location[]={location_dict['loc_2']}
        """

        return scraper.utils.json.get_json(listings_url)


    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Opendoor(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)

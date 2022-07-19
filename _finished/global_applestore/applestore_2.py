""" Robot creation for Global Apple Retail Location  """
import json.decoder
import sys
import calendar
import re
from os.path import abspath
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from html import unescape
import pandas as pd
import html
import numpy as np

sys.path.append('../../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
import pyersq.utils as squ
from bs4 import BeautifulSoup

from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper, By

class Applestore(Runner):
    """Collect data from website"""

    def __init__(self, argv):
        super().__init__(argv, output_prefix='applestore', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": "https://www.apple.com/retail/storelist/",
            "locale_json_url": 'https://www.apple.com/rsp-web/autocomplete?locale=en_US',
            "store_json_url": 'https://www.apple.com/rsp-web/store-search?locale={}&sc=false',
            "out": ['country', 'state', 'city', 'store_name', 'address_line_1',
                    'address_line_2', 'phone', 'url', 'id', 'updated', 'lang', 'store_name',
                    'address_line_1_local', 'address_line_2_local', 'state_local', 'city_local',
                    'postal_code', 'message_local', 'latitude', 'longitude', 'dates', 'days',
                    'times_local', 'special_hours', 'closed', 'time_created'],
        }

        self.sleep_seconds = 0
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%Y.%m.%dD%H:%M:%S.%f000')
        self.locale_to_countries = {}
        self.root_map = {}
        self.failed_fetch = []

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        scraper = ZenScraper()
        scraper.get(self.datapoints['base_url'])
        self.get_locale(scraper)
        return self.fetch_out

    def get_locale(self, scraper):
        countries_element = scraper.find_elements(By.XPATH, "//select/option")
        for element in countries_element:
            locale = element.get_attribute('value')
            if locale is not None:
                country = element.get_attribute('innerText')
                self.locale_to_countries.update({locale: country})

        store_list_object = scraper.utils.json.get_json_from_html_script_tag(doc=scraper.doc,
                                                                             id='__NEXT_DATA__')

        for locale, locale_value in store_list_object['props']['locale']['allGeoConfigs'].items():
            self.root_map.update({locale: locale_value['rootPath']})

        store_list_object_array = store_list_object['props']['pageProps']['storeList']

        for store_data in store_list_object_array:
            self.out.country = self.locale_to_countries[store_data['calledLocale']]
            self.out.lang = store_data['locale'].replace('_', '-')
            if 'kr' in store_data['locale'].lower():
                if store_data['hasStates'] is False:
                    self.out.state = self.out.country
                    for store in store_data['store']:
                        self.get_store_data(scraper, store, store_data)
                else:
                    for state in store_data['state']:
                        self.out.state = state['name']
                        for store in state['store']:
                            self.get_store_data(scraper, store, store_data)

    def get_store_data(self, scraper, store, store_data, has_state=True):
        self.out.city = html.unescape(store['address']['city'])
        self.out.store_name = html.unescape(store['name'])
        self.out.address_line_1 = html.unescape(store['address']['address1'])
        self.out.address_line_2 = html.unescape(store['address']['address2'])
        self.out.phone = store['telephone']
        self.out.url = self.__util_url_from_slug(store_data['locale'],
                                                 self.root_map[store_data['locale']],
                                                 store['slug'])
        self.out.id = (self.out.country + self.out.url.split('/')[-2]).lower().replace(' ', '-')
        self.out.updated = 'TRUE'
        self.out.lang = store_data['locale'].replace('_', '-')

        try:
            for _ in range(5):
                new_scraper = ZenScraper()
                new_scraper.get(self.out.url, sleep_seconds=self.sleep_seconds)
                print('scraping data from ', self.out.url)
                individual_store_json = new_scraper.utils.json.get_json_from_html_script_tag(
                    doc=new_scraper.doc, id='__NEXT_DATA__')
                if individual_store_json is not None:
                    local_store = individual_store_json['props']['pageProps']['storeDetails']
                    self.scrape_from_local_store(local_store, has_state)
                    break
                self.failed_fetch.append(self.out.url)
        except Exception as e:
            self.failed_fetch.append(self.out.url)
            print(f'ERROR: failed at {self.out.url} {e}')

    def scrape_from_local_store(self, local_store, has_state):
        if not has_state:
            self.out.state_local = self.out.state
        else:
            self.out.state_local = html.unescape(local_store['address']['stateName'])

        self.out.store_name_local = html.unescape(local_store['name'])
        self.out.address_line_1_local = html.unescape(local_store['address']['address1'])
        self.out.address_line_2_local = html.unescape(local_store['address']['address2'])
        self.out.city_local = html.unescape(local_store['address']['city'])
        self.out.postal_code = local_store['address']['postal']
        try:
            self.out.message_local = html.unescape(local_store['message'])
        except:
            self.out.message_local = ''
        self.out.latitude = local_store['geolocation']['latitude']
        self.out.longitude = local_store['geolocation']['longitude']
        local_store_hours = local_store['hours']
        # self.out.closed = local_store_hours['closed']
        self.out.objectkey = self.out.compute_key()

        past_day = 0
        for local_days in local_store_hours['days']:
            formatted_day = ZenScraper().utils.strings.remove_non_digits(
                self.__remove_unwanted_char(
                    html.unescape(local_days['formattedDayDateA11y'])
                )
            )
            formatted_day = formatted_day.strip()
            if len(str(formatted_day)) > 1:
                if (len(str(formatted_day)) != len(str(datetime.now().day))) or (int(formatted_day) > (datetime.now().day + 7)):
                    formatted_day = formatted_day[1:]
            cur_day = int(formatted_day)
            temp_year = datetime.now().year
            temp_month = datetime.now().month
            temp_date = datetime.strptime(f'{temp_year} {temp_month} {cur_day}', '%Y %m %d')

            if cur_day < past_day:
                temp_date = temp_date + relativedelta(months=1)
            past_day = cur_day

            self.out.dates = temp_date.strftime('%Y%m%d')
            self.out.days = calendar.day_name[temp_date.weekday()]
            self.out.times_local = html.unescape(local_days['formattedTime'])
            if ZenScraper().utils.strings.contains_number(
                    html.unescape(local_days['formattedTime'])):
                self.out.closed = False
            else:
                self.out.closed = True
            self.out.special_hours = local_days['specialHours']
            self.out.time_created = self.fetch_date
            self.fetch_out.append(self.out.values())

    def __remove_unwanted_char(self, str):
        clean = re.sub('&[^;]+;', ' ', str)
        # &#26376;
        return clean

    def __util_url_from_slug(self, locale, root_path, slug):
        """get util from slug"""
        if locale == 'zh_CN':
            url = 'https://www.apple.com.cn/retail/' + slug + '/'
        else:
            if root_path == '/':
                url = 'https://www.apple.com/retail/' + slug + '/'
            else:
                url = 'https://www.apple.com' + root_path + '/retail/' + slug + '/'
        return url

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header())
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                           value=["", ""], regex=True, inplace=True)
        data_frame.set_index("ObjectKey", inplace=True)
        return data_frame

    def cleanup(self):
        """Cleanup File"""
        for data in set(self.failed_fetch):
            print(data)
        # self.generate_map_data()


    def generate_map_data(self):
        """generate world_map_data.csv"""
        output_csv_data = pd.read_csv(
            abspath(f"{self.outdir}/raw/applestore_{datetime.now().strftime('%Y%m%d')}.csv"))

        row_to_delete = self.datapoints['out']
        row_to_delete.append('store_name.1')

        new_csv_data = ZenScraper().utils.data.df_delete_col_except(
            output_csv_data, row_to_delete,
            exception_list=['id', 'latitude', 'longitude', 'closed']
        )
        map_df = new_csv_data.drop_duplicates(subset=['id'], keep='first')
        map_df['closed'] = np.where(map_df['closed'] == False, 'Open', 'Closed')
        map_df.rename(columns={'id': 'store', 'closed': 'status'})
        map_df = ZenScraper().utils.data.df_col_pop(map_df, 'status')
        map_df = ZenScraper().utils.data.df_col_pop(map_df, 'store')
        map_df.to_csv(f"{self.outdir}/raw/world_map_data_{datetime.now().strftime('%Y%m%d')}.csv",
                      index=False)


def main(argv):
    """Main entry"""
    web = Applestore(argv)
    web.run()


if __name__ == "__main__":
    main(sys.argv)

""" Robot creation for US VSAT Distributors | Viasat Data  """
import sys
from datetime import datetime
import pandas as pd

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row

from ms_projects.utility_scripts.zenscraper import ZenScraper, UtilFunctions

class Vsatdist(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='vsatdist', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url" : 'https://www.viasat.com/content/viasat/us/en/satellite-internet/'
                         'contact-sales/retailer-results.findRetailers.json?range=50&resultCount=6'
                         '&zip={}&countryCode=us&lat={}&lng={}',
            "ex_loc_url": 'https://api.promaptools.com/service/us/zip-lat-lng/get/'
                          '?zip={0:0=5d}&key=17o8dysaCDrgv1c',
            "test_url" : 'https://www.viasat.com/satellite-internet/contact-sales/'
                         'retailer-results/?zip={0:0=5d}',
            "out": ['FetchDate', 'ZipCode', 'Dealer', 'Address',
                    'City', 'States', 'Zip',
                    'Type', 'Latitude', 'Longitude', 'Distance',
                    'Elite', 'MapURL', 'MapImage',
                    'DealerSiteURL', 'Phone', 'Email'],
        }
        self.zip_codes = [
            1, 2, 3, 1031, 1039, 1056, 1072, 1083, 99, 231
        ]

        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        for zip_code in self.zip_codes:

            ex_loc_url = self.datapoints['ex_loc_url'].format(zip_code)
            ex_loc_json = ZenScraper().get_json(ex_loc_url)
            if ex_loc_json['status'] == 1:

                lat = ex_loc_json['output'][0]['latitude']
                lng = ex_loc_json['output'][0]['longitude']
                print(f'Data on {zip_code} {lat} {lng}')
                url = self.datapoints['base_url'].format('{0:0=5d}'.format(zip_code), lat, lng) # pylint: disable=consider-using-f-string
                json_data = ZenScraper().get_json(url)
                self.save_json_file(url, f'data_for_{zip_code}')
                for data in json_data:
                    self.fetch_out.append(
                        [self.fetch_date, '{0:0=5d}'.format(zip_code), data['dealer'], # pylint: disable=consider-using-f-string
                         data['address'],
                         data['city'], data['state'], data['zip'], data['type'],
                         data['latitue'], data['longitude'], data['distance'],
                         data['elite'], data['mapUrl'], data['mapImage'],
                         '', data['phone'], data['email']]
                    )

        return self.fetch_out

    def save_json_file(self, url, file_name):
        '''
        :param url: json_file url
        :param file_name: json file name
        :return:
        '''
        jsondir = f'{self.outdir}/{self.output_subdir}/json/' \
                  f'{datetime.now().strftime("%Y_%m_%d")}/vsatdist'
        UtilFunctions().save_json(url, jsondir, f'data_for_{file_name}')


    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        # data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame

def main(argv):
    """Main entry"""
    web = Vsatdist(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)

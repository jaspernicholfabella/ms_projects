""" Robot creation for BR eCommerce Sites  """
import sys
import json
from io import StringIO
from datetime import datetime
import pandas as pd
sys.path.append('../../scripts')
from pyersq.web_runner import Runner
import pyersq.utils as squ
from ms_projects.utility_scripts.zenscraper_0_3 import ZenScraper

class Ecomsite(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='ecomsite', output_subdir="raw", output_type='excel')

        self.parser = squ.get_parser()
        self.header = ['FetchDate', 'Category', 'Geography']
        self.is_header_added = False
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        input_data = ZenScraper().utils.files.get_input_file(
            input_path=f'{self.outdir}/input/ecomsite_input.csv',
            header='Links',
            to_dict_val='Geography'
        )
        for links, geog in input_data.items():
            fetch_logs = ZenScraper().selenium_utils.get_fetch_logs(links)
            for fetch_log in fetch_logs:
                if 'wix-visual-data' in fetch_log['url']:
                    json_data = json.loads(fetch_log['body']['body'])
                    csv_string = StringIO(json_data['csvData'])
                    df = pd.read_csv(csv_string, sep=",", header=None)

                    if not self.is_header_added:
                        table_header = df.iloc[0, :].values
                        for header in table_header:
                            self.header.append(header)
                        self.is_header_added = True

                    for i in range(1, len(df)):
                        table_values = df.iloc[i, :].values
                        self.fetch_out.append([self.fetch_date, self.get_sales_index(links), geog, *table_values])

        return self.fetch_out


    @staticmethod
    def get_sales_index(url):
        if 'de-faturamento' in url:
            return 'Sales Index'
        elif 'de-vendas' in url:
            return 'Orders Index'
        elif 'de-tiquete' in url:
            return 'Average Ticket Index'

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.header)
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        return data_frame

def main(argv):
    """Main entry"""
    web = Ecomsite(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)

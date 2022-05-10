"""website builder tracker on https://trends.builtwith.com/cms/simple-website-builder"""
import sys
from datetime import datetime
import pandas as pd

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row

from ms_projects.utility_scripts.zenscraper import ZenScraper
from ms_projects.utility_scripts.zenscraper import DataObject

class HandM(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='h_and_m', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "data_json" : 'https://hmgroup.com/wp-content/uploads/spur/data.json',
            "production_units_json": 'https://hmgroup.com/wp-content/uploads/'
                                     'spur/productionUnits.json',
            "out": [
                'FetchDate', 'Website', 'Country', 'FactoryName', 'Address', 'City',
                'State', 'Zip', 'FactoryType',
                'SupplierGroup', 'SupplierGrading', 'Relation',
                'ProductCategory', 'WorkersCnt', 'MaleCnt',
                'WomenCnt', 'MalePct', 'WomenPct', 'LineWorkers', 'Brand', 'MigrantWorkers',
                'Subcons', 'WorkerGroup', 'UpdateDate'
            ],
        }

        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

        self.web_data = DataObject()
        self.web_data.countries = {}
        self.web_data.factory_types = {}
        self.web_data.product_category = {}
        self.web_data.supplier_group = {}

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        data_json = ZenScraper().get_json(self.datapoints['data_json'])
        production_units_json = ZenScraper().get_json(self.datapoints['production_units_json'])

        self.web_data.factory_types = data_json['productionTypes']

        for key, val in {'productionGroups': self.web_data.product_category,
                     'countries': self.web_data.countries,
                     'suppliers': self.web_data.supplier_group}.items():
            self.update_web_data_values(data_json[key], val)


        for data in production_units_json['productionUnits']:
            supplier_group, relation = '', ''
            for supplier in data['suppliers']:
                try:
                    supplier_group = self.web_data.supplier_group[
                        int(supplier['supplierId'])]
                    relation = supplier['relation']
                except KeyError:
                    pass
                try:
                    product_category = [
                        self.web_data.product_category[int(x)] for x in data['productionGroups']
                    ]
                except (TypeError, KeyError):
                    product_category = []

                self.fetch_out.append([
                    self.fetch_date, 'H&M', self.web_data.countries[int(data['countryId'])],
                    data['name'], data['shortAddress'], *['' for _ in range(3)],
                    self.join_data_array(data['productionUnitTypes'],'id',
                                         self.web_data.factory_types, is_str=True),
                    supplier_group, '',
                    relation, '; '.join(product_category), data['numberOfWorkers'],
                    *['' for _ in range(10)]
                ]
                )

        return self.fetch_out


    @staticmethod
    def join_data_array(data_json, val_key, key_dict, is_str=False, is_int=False):
        """Join data array from json data"""
        try:
            temp_list = []
            for val in data_json:
                if is_str:
                    temp_list.append(key_dict[str(val[val_key])])
                if is_int:
                    temp_list.append(key_dict[int(val[val_key])])

            return '; '.join(temp_list)
        except KeyError:
            return ''

    @staticmethod
    def update_web_data_values(json_data, web_data_val):
        """Update web_data values"""
        try:
            for data in json_data:
                web_data_val.update({
                    data['id']:data['name']
                })
        except KeyError:
            pass



    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame


def main(argv):
    """Main entry"""
    web = HandM(argv)
    web.run()

# Script starts
if __name__ == "__main__":
    main(sys.argv)

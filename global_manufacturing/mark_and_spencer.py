"""website builder tracker on https://trends.builtwith.com/cms/simple-website-builder"""
import sys
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.requests_wrapper import RequestsWrapper
from lxml import etree
import lxml.html

class ORMType:
    """ Unique type class to decipher between attributes """

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __index__(self):
        return int(self.key)

class ORM:
    """Basic ORM Class"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, ORMType(key, value))

    @staticmethod
    def attr_1():
        """ Adding this for Pylint issues """
        print("attr_1")

    @staticmethod
    def attr_2():
        """ Adding this for Pylint issues """
        print("attr_2")

class MarkAndSpencer(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='mark_and_spencer', output_subdir="raw", output_type='excel')
        self.datapoints = {
            "base_url": "https://interactivemap.marksandspencer.com/ajax/AjaxHandler.ashx?event=reloadMapMarkers&sectionPID=56c359428b0c1e3d3ccdf022&regionPID=626ab5b92a4455ef18207c54&subregionPID=&tagsPIDs=5aa6a3d0c6fe1dab103dd1a9&markerPID=&orderBy=datedesc&take=100000000&skip=0&reloadInfoArea=value&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=",
            "map_url": "https://interactivemap.marksandspencer.com/?regionPID={}&tagsPIDs={}&markerPID={}",
            "out": [
                'FetchDate', 'Website', 'Country', 'FactoryName', 'Address', 'City', 'State', 'Zip', 'FactoryType',
                'SupplierGroup', 'SupplierGrading', 'Relation', 'ProductCategory', 'WorkersCnt', 'MaleCnt',
                'WomenCnt', 'MalePct', 'WomenPct', 'LineWorkers', 'Brand', 'MigrantWorkers',
                'Subcons', 'WorkerGroup', 'UpdateDate'
            ],
            "xpath": {},
        }

        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

        self.web_data = ORM()
        self.web_data.region = {}
        self.web_data.factory_name = {}
        self.web_data.marker = []
        self.tag = ORM()
        self.tag.factory_type = {}
        self.tag.product_category = {}

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        req = RequestsWrapper()
        res = req.get(self.datapoints['base_url'])
        data = res.json()

        for regions in data['Regions']:
            self.web_data.region.update({regions['Pid']: regions['Title']})

        for tags in data['Tags']:
            if tags['Title'] == 'Food':
                self.tag.factory_type.update({tags['Pid']: 'Food'})
            if tags['Title'] == 'Clothing & Home':
                self.tag.factory_type.update({tags['Pid']: 'Clothing & Home'})

        for tags in data['Tags']:
            if tags['ParentPID'] in self.tag.factory_type.keys():
                if tags['Title'] != 'All':
                    self.tag.product_category.update({tags['Pid']: {
                        'factory_type': self.tag.factory_type[tags['ParentPID']],
                        'product_category': tags['Title']}})


        for marker in data['Markers']:
            for x in marker['Tags']:
                if x in self.tag.product_category.keys():
                    self.web_data.marker.append({
                        'id': marker['Pid'],
                        'tag': x,
                        'title': marker['Title'],
                        'region': marker['RegionId'],
                        'address': marker['Address'],
                        'num_worker': marker['numWorker'],
                    })

        self.get_individual_data(req)


        return self.fetch_out



    def get_individual_data(self, req):
        for k, dat in enumerate(self.web_data.marker):
            try:
                print(k, dat)
                if k == 20:
                    break
                res = req.get(self.datapoints['map_url'].format(dat['region'],dat['tag'],dat['id']))
                doc = lxml.html.fromstring(res.content)
                female_worker = self.get_inner_text(
                    doc.xpath("//div[contains(@class, 'map-info-bottom')]//p[contains(text(), 'Female')]")[0]
                )
                male_worker = self.get_inner_text(
                    doc.xpath("//div[contains(@class, 'map-info-bottom')]//p[contains(text(), 'Male')]")[0]
                )

                elements = doc.xpath("//div[contains(@class, 'factory-type-inner')]/span")

                try:
                    worker_group_arr = []
                    for el in elements:
                        worker_group_arr.append(self.get_inner_text(el))
                    worker_group = ';'.join(worker_group_arr)
                    if worker_group == '':
                        worker_group = ''
                except:
                    worker_group = ''

                date_element = doc.xpath("//small[contains(text(), 'FOOD')]")[0]
                split_on_as_of = self.get_inner_text(date_element).split('AS OF')
                food_date = f"{split_on_as_of[1].split('20')[0].strip().title()}, " \
                            f"20{split_on_as_of[1].split('20')[1].strip()[:2]}"
                clothing_home_date = f"{split_on_as_of[2].split('20')[0].strip().title()}, " \
                                     f"20{split_on_as_of[2].split('20')[1].strip()[:2]}"


                if self.tag.product_category[dat['tag']]['factory_type'] == 'Food':
                    update_date = food_date
                else:
                    update_date = clothing_home_date

                self.fetch_out.append(
                    [self.fetch_date, 'M&S', self.web_data.region[dat['region']], dat['title'], dat['address'], '', '', '',
                     self.tag.product_category[dat['tag']]['factory_type'], '', '', '',
                     self.tag.product_category[dat['tag']]['product_category'], dat['num_worker'], '', '',
                     male_worker, female_worker, '', '', '', '', worker_group, update_date])

            except Exception as e:
                print(e)


    def normalize(self, raw):
        """Save raw data to file"""
        df = pd.DataFrame(raw, columns=self.out.header()[:-1])
        df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        df = df.sort_values(by='Country', key=lambda col: col.str.lower())
        return df


    def get_inner_text(self, element):
        return self.strip_html(str(etree.tostring(element)))


    @staticmethod
    def strip_html(data):
        p = re.compile(r'<.*?>|=')
        stripped = p.sub('', data)
        for rep in ['&#160;', '&#13;', '\\n', 'Female', 'Male', "b'"]:
            stripped = stripped.replace(rep, '')
        stripped = stripped.strip()
        return stripped

def main(argv):
    """Main entry"""
    web = MarkAndSpencer(argv)
    web.run()

# Script starts
if __name__ == "__main__":
    main(sys.argv)

"""website builder tracker on https://trends.builtwith.com/cms/simple-website-builder"""
import sys
from datetime import datetime
import lxml.html
import lxml

import pandas as pd
sys.path.append('../../../scripts')
from pyersq.row import Row
from pyersq.web_runner import Runner

from ms_projects.utility_scripts.zenscraper import ZenScraper, By, DataObject

class MarkAndSpencer(Runner):
    """Collect data from website"""

    def __init__(self, argv):
        super().__init__(
            argv,
            output_prefix='mark_and_spencer',
            output_subdir="raw",
            output_type='excel')
        self.datapoints = {
            "base_url": "https://interactivemap.marksandspencer.com/ajax/"
                        "AjaxHandler.ashx?event=reloadMapMarkers&"
                        "sectionPID=56c359428b0c1e3d3ccdf022&"
                        "regionPID=626ab5b92a4455ef18207c54&subregionPID=&"
                        "tagsPIDs=5aa6a3d0c6fe1dab103dd1a9&"
                        "markerPID=&orderBy=datedesc&take=100000000&skip=0&"
                        "reloadInfoArea=value&tagsPIDs=&"
                        "tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&"
                        "tagsPIDs=&tagsPIDs=&tagsPIDs=&"
                        "tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&"
                        "tagsPIDs=&tagsPIDs=",
            "map_url": "https://interactivemap.marksandspencer.com/?"
                       "regionPID={}&tagsPIDs={}&markerPID={}",
            "out": [
                'FetchDate',
                'Website',
                'Country',
                'FactoryName',
                'Address',
                'City',
                'State',
                'Zip',
                'FactoryType',
                'SupplierGroup',
                'SupplierGrading',
                'Relation',
                'ProductCategory',
                'WorkersCnt',
                'MaleCnt',
                'WomenCnt',
                'MalePct',
                'WomenPct',
                'LineWorkers',
                'Brands',
                'MigrantWorkersPct',
                'Subcons',
                'WorkerGroup',
                'UpdateDate'],
            "xpath": {
                'female_worker': "//div[contains(@class, 'map-info-bottom')]//"
                                 "p[contains(text(), 'Female')]",
                'male_worker': "//div[contains(@class, 'map-info-bottom')]//"
                               "p[contains(text(), 'Male')]"},
        }

        self.out = Row(self.datapoints['out'])
        self.fetch_out = []
        self.fetch_date = datetime.now().strftime('%m/%d/%Y')

        self.web_data = DataObject()
        self.web_data.region = {}
        self.web_data.factory_name = {}
        self.web_data.marker = []
        self.tag = DataObject()
        self.tag.factory_type = {}
        self.tag.product_category = {}

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        data = ZenScraper().get_json(self.datapoints['base_url'])

        for regions in data['Regions']:
            self.web_data.region.update({regions['Pid']: regions['Title']})

        for tags in data['Tags']:
            if tags['Title'] == 'Food':
                self.tag.factory_type.update({tags['Pid']: 'Food'})
            if tags['Title'] == 'Clothing & Home':
                self.tag.factory_type.update({tags['Pid']: 'Clothing & Home'})

        for tags in data['Tags']:
            if tags['ParentPID'] in self.tag.factory_type:
                if tags['Title'] != 'All':
                    self.tag.product_category.update({tags['Pid']: {
                        'factory_type': self.tag.factory_type[tags['ParentPID']],
                        'product_category': tags['Title']}})

        for marker in data['Markers']:
            for marker_tag in marker['Tags']:
                if marker_tag in self.tag.product_category:
                    self.web_data.marker.append({
                        'id': marker['Pid'],
                        'tag': marker_tag,
                        'title': marker['Title'],
                        'region': marker['RegionId'],
                        'address': marker['Address'],
                        'num_worker': marker['numWorker'],
                    })

        self.get_individual_data()

        return self.fetch_out

    def get_individual_data(self):
        """Get Individual data for each link"""
        for k, dat in enumerate(self.web_data.marker):
            try:
                print(k, dat)
                # if k == 20:
                #     break
                inner_text_filter = ['&#160;', '&#13;',
                                     '\\n', 'Female', 'Male', "b'", "'", "|"]
                z_scraper = ZenScraper()
                z_scraper.get(
                    self.datapoints['map_url'].format(
                        dat['region'], dat['tag'], dat['id']))
                worker = []
                for worker_data in ['male_worker', 'female_worker']:
                    worker.append(z_scraper.find_element(
                        By.XPATH, self.datapoints['xpath'][worker_data]).get_attribute(
                        'innerText', inner_text_filter=inner_text_filter))

                elements = z_scraper.find_elements(
                    By.XPATH, "//div[contains(@class, 'factory-type-inner')]/span")

                worker_group = self.get_worker_group(elements, inner_text_filter)

                date_element = z_scraper.find_element(
                    By.XPATH, "//small[contains(text(), 'FOOD')]").get_attribute('innerText', inner_text_filter=inner_text_filter)

                self.fetch_out.append([self.fetch_date, 'M&S', self.web_data.region[dat['region']],
                                       dat['title'], dat['address'], *['' for _ in range(3)],
                                       self.tag.product_category[dat['tag']]['product_category'],
                                       *['' for _ in range(3)],
                                       self.tag.product_category[dat['tag']]['product_category'],
                                       dat['num_worker'], *['' for _ in range(2)],
                                       worker[0], worker[1],
                                       *['' for _ in range(4)], worker_group, date_element
                                      .replace('&amp', '&')
                                      .replace('|', '')
                                      .replace('DATA AS OF', '')
                                      .replace('  ', ' ')
                                      .replace(';', '')])
            except lxml.etree.Error as err:
                print(err)

    @staticmethod
    def get_worker_group(elements, inner_text_filter):
        """ Get worker group from the element """
        try:
            worker_group_arr = []
            for element in elements:
                worker_group_arr.append(
                    element.get_attribute(
                        'innerText', inner_text_filter=inner_text_filter)
                )
            worker_group = ';'.join(worker_group_arr)
            if worker_group == '':
                worker_group = ''
        except (lxml.etree.XPathEvalError, lxml.etree.XPathError, lxml.etree.Error, AttributeError):
            worker_group = ''
        return worker_group

    def normalize(self, raw):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.out.header()[:-1])
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame


def main(argv):
    """Main entry"""
    web = MarkAndSpencer(argv)
    web.run()


# Script starts
if __name__ == "__main__":
    main(sys.argv)

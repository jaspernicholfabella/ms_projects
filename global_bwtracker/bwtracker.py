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
from pyersq.selenium_wrapper import SeleniumWrapper as SW

class BWTracker(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='bwtracker', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "base_url": 'https://trends.builtwith.com/cms/simple-website-builder',
            "tofind": ['1m', '100k', '10k', 'Entire Internet'],
            "xpath": {
                'link_locations': "//a[contains(text(),'{}')]",
                'total_sites_by_traffic': "//a[contains(text(),'{}')]/parent::node()/following-sibling::dd[1]",
                'pie_chart': '//div[contains(@class,"ct-pie")]/*[name()="svg"]/*[name()="g"][last()]/*',
                'detections': "//div/h2[contains(text(),'Detections')]",
                'last_updated': "//p[contains(text(), 'Last updated')]"
            },
            "simple_web_table": ['FetchDate', 'LastUpdated', 'Category', 'Technology', 'Weight in Simple Websites'],
            "top_in_web_table": ['FetchDate', 'LastUpdated', 'Category', 'Technology', 'Websites', 'Weight in All Websites'],
            "detections_table": ['FetchDate', 'LastUpdated', 'Category', 'Detections', 'Total'],
        }
        self.simple_web = Row(self.datapoints["simple_web_table"])
        self.top_in_web = Row(self.datapoints["top_in_web_table"])
        self.detections = Row(self.datapoints["detections_table"])
        self.data_simple_web, self.data_top_in_web, self.data_detections = [], [], []

    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        fetchdate = datetime.now().strftime('%m/%d/%Y')
        self.simple_web.fetchdate = self.top_in_web.fetchdate = self.detections.fetchdate = fetchdate

        with SW.get_driver() as driver:
            url = self.datapoints['base_url']
            SW.get_url(driver, url)
            web_links = []
            for tofind in self.datapoints['tofind']:
                element = driver.find_element(By.XPATH, self.datapoints["xpath"]["link_locations"].format(tofind))
                element_total = driver.find_element(By.XPATH,self.datapoints["xpath"]["total_sites_by_traffic"].format(tofind))
                web_links.append({'title': element.text, 'total': element_total.text, 'link': element.get_attribute('href')})

            for pages in web_links:
                self.save_html(driver,pages['title'])
                self.get_data_simple_web(driver, pages)
                self.get_data_top_in_web(driver, pages)
                self.get_data_detections(driver, pages)

    def save_html(self, driver, title):
        """Save html file"""
        html_dir = f'{self.outdir}/{self.output_subdir}/html/{datetime.now().strftime("%Y_%m_%d")}/bwtracker'
        Path(html_dir).mkdir(parents=True, exist_ok=True)
        with open(f'{html_dir}/{title}.html', 'w') as f:
            f.write(driver.page_source)

    def save_output(self,data, **kwargs):
        """Override Save output Function"""
        simple_web_df = pd.DataFrame(self.data_simple_web, columns=self.simple_web.header()[:-1])
        top_in_web_df = pd.DataFrame(self.data_top_in_web, columns=self.top_in_web.header()[:-1])
        top_in_web_df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
        detections_df = pd.DataFrame(self.data_detections, columns=self.detections.header()[:-1])
        temp_prefix = self.prefix
        self.save_final_output(simple_web_df, temp_prefix.replace('bwtracker', 'bwtracker_simple_web'))
        self.save_final_output(top_in_web_df, temp_prefix.replace('bwtracker', 'bwtracker_top_in_web'))
        self.save_final_output(detections_df, temp_prefix.replace('bwtracker', 'bwtracker_detections'))

    def save_final_output(self, df, filename):
        """Save final output"""
        Path(f'{self.outdir}/{self.output_subdir}').mkdir(parents=True, exist_ok=True)
        self.prefix = filename
        super().save_output(df, encoding='utf-8')

    def get_data_simple_web(self, driver, pages):
        """Get data from the chart in the website"""
        SW.get_url(driver, pages['link'])
        elements = driver.find_elements(By.XPATH, self.datapoints['xpath']['pie_chart'])
        for element in elements:
            data = element.text
            website_name = ' '.join((data.split(' ')[:-1]))
            percentage = data.split(' ')[-1].replace('%', '')
            self.data_simple_web.append([self.simple_web.fetchdate, self.get_latest_date_updated(driver), pages['title'], website_name, percentage])

    def get_data_top_in_web(self, driver, pages):
        """Get data from table in the website"""
        soup = BeautifulSoup(driver.page_source, 'lxml')
        table = soup.find('table')
        table_rows = table.find_all('tr')
        for table_row in table_rows:
            table_data = table_row.find_all('td')
            row = [table_row.text for table_row in table_data]
            if len(row) == 3:
                self.data_top_in_web.append([self.top_in_web.fetchdate, self.get_latest_date_updated(driver), pages['title'], *row])

    def get_data_detections(self, driver, pages):
        """Get number of detected websites"""
        detection_element = driver.find_element(By.XPATH, self.datapoints['xpath']['detections'])
        detection_value = re.sub("[^0-9]", "", detection_element.text)
        self.data_detections.append([self.detections.fetchdate, self.get_latest_date_updated(driver), pages['title'], detection_value, pages['total']])

    def get_latest_date_updated(self, driver):
        last_update_string = driver.find_element(By.XPATH, self.datapoints['xpath']['last_updated']).get_attribute("innerText")
        last_update_string = str(last_update_string).lower().split('updated')[1].strip()
        day = last_update_string.split(' ')[0][:2]
        month = last_update_string.split(' ')[1][:3]
        year = last_update_string.split(' ')[2][:4]
        return datetime.strptime(f'{day}-{month}-{year}', '%d-%b-%Y').strftime('%m/%d/%Y')

def main(argv):
    """Main entry"""
    web = BWTracker(argv)
    web.run()


# Script starts
if __name__ == "__main__":
    main(sys.argv)

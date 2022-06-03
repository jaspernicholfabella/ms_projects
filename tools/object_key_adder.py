""" Robot creation for Tools  """
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
from pprint import pprint

sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW
import pyersq.utils as squ

from ms_projects.utility_scripts.zenscraper import ZenScraper, By, DataObject, UtilFunctions

class Object_Key_Adder(Runner):
    """Collect data from website"""
    def __init__(self, argv):
        super().__init__(argv, output_prefix='object_key_adder', output_subdir="raw", output_type='csv')
        self.datapoints = {
            "out": ['FetchDate'],
        }

        self.parser = squ.get_parser()
        self.header = ['ObjectKey']
        self.out = Row(self.datapoints['out'])
        self.fetch_out = []


    def get_raw(self, **kwargs):
        """ Get raw data from source"""
        data_frame = pd.read_csv('tsa_20220531.csv')
        val_list = []
        for key, value in data_frame.to_dict().items():
            if key != 'ObjectKey':
                self.header.append(key)
                temp = []
                for k,v in value.items():
                    temp.append(v)
                val_list.append(temp)

        val_len = 0
        for key, value in data_frame.to_dict().items():
            for _ in value:
                val_len += 1
            break

        object_key_list = []
        for _ in range(val_len):
            self.out.objectkey = self.out.compute_key()
            object_key_list.append(self.out.values()[-1])

        print(object_key_list)

        return zip(object_key_list, *val_list)

    def normalize(self, raw, **kwargs):
        """Save raw data to file"""
        data_frame = pd.DataFrame(raw, columns=self.header)
        data_frame.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"],
                   value=["", ""], regex=True, inplace=True)
        # data_frame = data_frame.sort_values(by='Country', key=lambda col: col.str.lower())
        return data_frame

def main(argv):
    """Main entry"""
    web = Object_Key_Adder(argv)
    web.run()

if __name__ == "__main__":
    main(sys.argv)




import sys
import collections
from ms_projects.utility_scripts.zenscraper import ZenScraper, By


scraper = ZenScraper()
scraper.get('https://pylint.pycqa.org/en/v2.13.7/messages/warning/unspecified-encoding.html')
scraper.find_element(By.XPATH, '//node()::a;')

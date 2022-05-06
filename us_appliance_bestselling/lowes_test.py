import requests
import sys
import Path
import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW



def save_html(self, driver, title):
    """Save html file"""
    html_dir = f''
    Path(html_dir).mkdir(parents=True, exist_ok=True)
    with open(f'{html_dir}/{title}.html', 'w') as f:
        f.write(driver.page_source)

if __name__ == '__main__':
    driver = SW.get_driver(headless=False)
    URL_2 = "https://www.redfin.com/"
    SW.get_url(driver, URL_2, sleep_seconds=1)

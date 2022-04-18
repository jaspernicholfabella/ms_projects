import requests
import sys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
sys.path.append('../../scripts')
from pyersq.web_runner import Runner
from pyersq.row import Row
from pyersq.selenium_wrapper import SeleniumWrapper as SW

driver = SW.get_driver(headless=True)

URL_2 = "https://www.lowes.com/pl/Top-load-washers-Washing-machines-Washers-dryers-Appliances/4294857976?offset=24&sortMethod=sortBy_bestSeller&refinement=5007197,5005561"

SW.get_url(driver, URL_2, sleep_seconds=1)

"""
from pyersq.selenium_wrapper import SeleniumWrapper as SW
from selenium.webdriver.common.by import By
with SW.get_driver() as deriver:
    SW.get_url(driver, 'https://httbin.org/headers')
    res = driver.find_element(By.XPATH,'/html/body/pre')
    print(f"Result:{res.text}")
"""

import os
import logging
import time
import random
import subprocess
import json
from pathlib import Path
import selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from sys import platform

class SeleniumWrapper:
    """Wrapper around selenium"""
    web_hit_count = 0

    @staticmethod
    def get_driver(download_dir=None,option_callback=None,headless=True,**kwargs):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--proxy-server=webproxy-research-bot-inet.ms.com:8080')
        chrome_options.add_argument("--window-size=1600,800")
        if download_dir:
            chrome_options.add_experimental_option("prefs",{
                'download.default_directory': download_dir,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True
            })

        if headless: #Linux
            chrome_options.add_argument('--headless')
            chrome_options.add_argument("--crash-dumps-dir=/tmp")

        if option_callback:
            logging.info("Set customized option: option_callback=%s", option_callback)
            option_callback(chrome_options)
        # try:
        #     chromedriver = os.path.abspath('/home/jaspernf/.wdm/driver/chromedriver')
        #     #windows
        #     # chromedriver = os.path.abspath('G:\My Drive\Projects\Python\Xenide\scripts\pyersq\chromedriver\chromedriver.exe')
        #     driver = webdriver.Chrome(executable_path=chromedriver, options=chrome_options, **kwargs)
        # except:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

        logging.info('Launched Chrome driver successfully: %s',driver.capabilities)
        return driver

    @staticmethod
    def get_driver_with_manager(driver_version=None, download_dir=None, option_callback=None, **kwargs):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=webproxy-research-bot-inet.ms.com:8080')
        chrome_options.add_argument("--window-size=1600,800")
        # chrome_options.add_argument("disable-web-security")
        if download_dir:
            chrome_options.add_experimental_option("prefs",{
                'download.default_directory': download_dir,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True
            })

        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')

        if os.name == 'posix':  # Linux
            chrome_options.add_argument('--headless')

        if option_callback:
            logging.info("Set customized option: option_callback=%s", option_callback)
            option_callback(chrome_options)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logging.info('Launched Chrome driver successfully: %s', driver.capabilities)
        return driver

    @staticmethod
    def get_url(driver,url,sleep_seconds=None,retry=1, ua_override=True):
        """
        :param driver: Webdriver instance
        :param url: Web URL to navigate to
        :param sleep_seconds: Seconds to wait before navigate to the URL.format
        :param retry: # of retries on exception
        :param ua_override: Override UserAgent, default True for override
        :return:
        """
        ua = SeleniumWrapper._AGENTS

        logging.info("Get URL: %s",url)
        for i in range(retry):
            if ua_override:
                driver.execute_cdp_cmd('Network.setUserAgentOverride',{"userAgent": ua[random.randrange(0,len(ua) -1)]})
                time.sleep(sleep_seconds or random.randrange(8,13)) # default 8,13
            try:
                SeleniumWrapper.add_hit_count()
                driver.get(url)
                break
            except selenium.common.exceptions.TimeoutException as e:
                logging.warning("Retry #%s on this exception : %s, %s",i ,type(e), e)

            logging.info("Page Title: %s", driver.title)
            logging.info("User agent: %s", driver.execute_script("return navigator.userAgent"))

    @staticmethod
    def add_hit_count(hits=1):
        """
        Record a web hit besides using get_url()
        :param hits: #of hits to record
        :return:
        """
        SeleniumWrapper.web_hit_count += hits
        logging.info('web_hit_count =%d',SeleniumWrapper.web_hit_count)

    @staticmethod
    def get_hit_count():
        """Return the current web hit count"""
        return SeleniumWrapper.web_hit_count

    @staticmethod
    def enable_log(capabilities=None):
        """Enable all Chrome Logs by adding Desired Capabilities"""
        if capabilities is None:
            capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {'performance': "ALL"}
        return capabilities

    @staticmethod
    def get_log_msg(driver, filter_=None):
        """ Get Chrome Logs with filter """
        logs = driver.get_log('performance')
        for log in logs:
            msg = json.load(log["message"])["message"]
            if filter_(msg):
                request_id = msg['params']['requestID']
                try:
                    body=driver.execute_cdp_cmd('Network.getResponseBody',{'requestID': request_id})
                except Exception:
                    logging.info('log=%s',log)
                    raise
                yield msg, body


    #Randomly switch to different user agent
    _AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    ]

class ElementNotEmpty:
    """An expectation for checking that an element is not empty.

    locator - used to find the elements
    returns the WebElement once it is rendered with text
    """
    def __init__(self,locator):
        self.locator = locator

    def __call__(self,driver):
        element = driver.find_element(*self.locator)
        if element.text > '':
            return element.text
        self.redraw(driver)
        return False

    def redraw(self,driver):
        """Make Chromium draw the element"""
        logging.info('Text is empty, switch the window to draw')
        driver.switch_to.window(driver.window_handles[0])
        driver.execute_script("window.scrollTo(600,2000)")
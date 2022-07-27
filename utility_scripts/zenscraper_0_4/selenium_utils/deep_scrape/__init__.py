""" selenium_utils.deep_scrape v0_1 using deep scraping techniques """
from os.path import abspath, join, dirname
import sys
import time
import json

from selenium.webdriver import DesiredCapabilities

sys.path.insert(0, abspath(join(dirname(__file__), "../../..")))
from pyersq.selenium_wrapper import SeleniumWrapper as SW


def get_fetch_logs(url, sleep_seconds=5):
    """
    :param url: url
    :param sleep_seconds: wait time for getting logs
    :return: return Fetch/XHR as json file , list of dictionaries
    """
    fetch_logs = []
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    with SW.get_driver(desired_capabilities=capabilities) as driver:
        SW.get_url(driver, url)
        time.sleep(sleep_seconds)
        logs_raw = driver.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

        def log_filter(log_):
            """ filter network responses """
            return (
                    log_["method"] == "Network.responseReceived"
                    and "json" in log_["params"]["response"]["mimeType"]
            )

        for log in filter(log_filter, logs):
            try:
                request_id = log["params"]["requestId"]
                resp_url = log["params"]["response"]["url"]
                fetch_logs.append({
                    'url': resp_url,
                    'body': driver.execute_cdp_cmd("Network.getResponseBody",
                                                   {"requestId": request_id})
                })
            except Exception as err: #pylint: disable=broad-except
                print(err)

    return fetch_logs
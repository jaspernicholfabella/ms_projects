import time
import logging
from ._actions import Actions
from ._options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

actions = Actions(logger)
options = Options(logger)


def wait_for_page_load(self, driver, wait_time=30):
    """
    :param driver:
    :param wait_time:
    :return:
    """
    while not self._page_is_loading(driver, wait_time=wait_time):
        continue


@staticmethod
def _page_is_loading(driver, wait_time=30):
    """
    :param driver:
    :param wait_time:
    :return:
    """
    for _ in wait_time:
        loading = driver.execute_script("return document.readyState")
        if loading == "complete":
            return True

        time.sleep(0.5)
        yield False
    return True


def wait_for_element(self, driver, xpath, wait_time=30):
    """
    :param driver: Selenium webdriver
    :param wait_time: wait time in seconds
    :param xpath: xpath expression to wait
    :return:
    """
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((self.SeleniumBy.XPATH, xpath)))
    except Exception as e:
        print(e)


@staticmethod
def take_screenshot(driver, save_fn='test.png'):
    """
    get screenshot of website
    :param driver: selenium webdriver
    :param save_fn: save file location
    :return:
    """
    driver.execute_script("""
        (function () {
            var y = 0;
            var step = 100;
            window.scroll(0, 0)

            function f() {
                if(y < document.body.scrollHeight){
                    y += step;
                    window.scroll(0, y);
                    setTimeout(f, 100);
                } else {
                    window.scroll(0, 0);
                    document.title += "scroll-done";
                }
            }

            setTimeout(f, 1000);
        })();
        """)

    for i in range(30):
        if 'scroll-done' in driver.title:
            break
        time.sleep(10)
        print(i)

    driver.save_screenshshot(save_fn)

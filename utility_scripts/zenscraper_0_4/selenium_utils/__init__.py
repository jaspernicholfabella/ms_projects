<<<<<<< HEAD
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By as SeleniumBy



def wait_for_page_load(driver, wait_time=30):
    """
    :param driver:
    :param wait_time:
    :return:
    """
    while not _page_is_loading(driver, wait_time=wait_time):
        continue


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


def wait_for_element(driver, xpath, wait_time=30):
    """
    :param driver: Selenium webdriver
    :param wait_time: wait time in seconds
    :param xpath: xpath expression to wait
    :return:
    """
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((SeleniumBy.XPATH, xpath)))
    except Exception as e:
        print(e)

    return driver.find_element(SeleniumBy.XPATH, xpath)


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
=======
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By as SeleniumBy



def wait_for_page_load(driver, wait_time=30):
    """
    :param driver:
    :param wait_time:
    :return:
    """
    while not _page_is_loading(driver, wait_time=wait_time):
        continue


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


def wait_for_element(driver, xpath, wait_time=30):
    """
    :param driver: Selenium webdriver
    :param wait_time: wait time in seconds
    :param xpath: xpath expression to wait
    :return:
    """
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((SeleniumBy.XPATH, xpath)))
    except Exception as e:
        print(e)

    return driver.find_element(SeleniumBy.XPATH, xpath)


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
>>>>>>> 9c7a2ecb38c8c26c66a48d4e0105990ca3cfbfd4

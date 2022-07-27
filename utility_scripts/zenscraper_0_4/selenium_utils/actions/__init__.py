from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.common.action_chains import ActionChains
from ..logger import logger


def move_to_and_click(driver, move_to='', click=''):
    """
    :param driver: selenium web driver
    :param move_to: type:xpath: move_to a specified location,
    :param click: type:xpath: click the specified location , if blank click the same element as the move_to
    """
    try:
        action = ActionChains(driver)
        element_move_to = driver.find_element(SeleniumBy.XPATH. move_to)
        if click != '':
            element_click = driver.find_element(SeleniumBy.XPATH, click)
        else:
            element_click = element_move_to

        action.move_to_element(element_move_to).perform()
        action.click(element_click).perform()
    except Exception as err:
        logger.error(err)
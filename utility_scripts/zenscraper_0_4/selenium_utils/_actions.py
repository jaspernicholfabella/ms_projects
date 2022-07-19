from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.common.action_chains import ActionChains


class Actions:
    """Action Chains & Form Action"""
    logger = None

    def __init__(self, logger):
        self.logger = logger

    def move_to_and_click(self, driver, move_to='', click=''):
        try:
            action = ActionChains(driver)
            element_move_to = driver.find_element(SeleniumBy.XPATH. move_to)
            if click != '':
                element_click = driver.find_element(SeleniumBy.XPATH, click)
            else:
                element_click = element_move_to

            action.move_to_element(element_move_to).perform()
            action.click(element_click).perform()
        except Exception as e:
            self.logger.error
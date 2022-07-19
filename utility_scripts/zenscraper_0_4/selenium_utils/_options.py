class Options:
    user_agent = 'Mozzilla/5.0 (Windows NT 10.0; WOW64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'

    @staticmethod
    def set_options(opts, *args):
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--lang=en_US")
        opts.add_argument("--disable-gpu")

        if len(args) != 0:
            for val in args:
                opts.add_argument(val)

    @staticmethod
    def override_useragent(driver):
        driver.execute_cdp_cmd('Network.setUserAgentOverride')
"""
Wrap around 'requests'
Code example:
import pyersq.requests_wrapper as RW
with RW.RequestWrapper() as req:
    resp = req.get('https://httpbin.org/get)
    resp.request.headers['User-Agent']
"""
import time
import random
import logging
import requests

class RequestsWrapper:
    """wrap around requests lib"""
    web_hit_count = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    #     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'en-US,en;q=0.9',
    #     'Upgrade-Insecure-Requests': '1',
    #     'Connection':'close'
    # }

    def __init__(self, **kwargs:str):
        self.session = requests.Session()
        self.session.headers.update(kwargs)

    def request(self,method:str, url:str, **kwargs: str):
        """
        Wrap requests.request(),

        :param method: GET or POST
        :param url: URL, e.g. https://ms.com
        :param kwargs: Optional arguments that ''request'' takes
        :return: Response = <Response> object
        """

        logging.info("%s from: url=%s, kwargs=%s", method,url,kwargs)
        sleep_seconds = kwargs.get("sleep_seconds", random.randrange(1,2))
        kwargs.pop("sleep_seconds",None)
        time.sleep(sleep_seconds)

        #if the user defined a custom header then update the following header
        headers = self.headers.copy()
        headers.update(kwargs.get("headers",{}))
        kwargs.pop("headers",None)

        self.web_hit_count += 1
        resp = self.session.request(method, url,headers=headers, **kwargs)
        logging.info("Response: status_code=%i",resp.status_code)
        logging.info("headers=%s",resp.request.headers)
        logging.info("web_hit_count=%s",self.web_hit_count)
        resp.raise_for_status()
        return resp


    def get(self,url,**kwargs):
        """
        Send a "Get" request to the specified url
        :param url: URL to send request to
        :param kwargs: Other arguments to be sent with the request
        :return:
        """
        response = self.request("GET",url,**kwargs)
        return response


    def get_hit_count(self):
        """Return the current web hit count"""
        return self.web_hit_count

    def print_test(self):
        print('success')

    def __enter__(self):
        logging.debug('__enter__')

    def __exit__(self, *exc):
        logging.debug('__exit__: %s',exc)
        self.session.close()
import sys
import collections
from ms_projects.utility_scripts.zenscraper import ZenScraper, By, UtilFunctions


url = "https://www3.hkexnews.hk/sdw/search/stocklist.aspx?sortby=stockcode&shareholdingdate=20220517"
json_data = ZenScraper.get_json(url)

stocks = []
for data in json_data:
    stocks.append([data['c'], data['n']])

print(stocks)

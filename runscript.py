import os
stream = os.popen('black utility_scripts/zenscraper.py')
output = stream.read()
output
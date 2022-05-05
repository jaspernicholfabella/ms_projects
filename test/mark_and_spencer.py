import sys
import collections
sys.path.append('../../scripts')
from pyersq.requests_wrapper import RequestsWrapper

req = RequestsWrapper()
res = req.get("https://interactivemap.marksandspencer.com/ajax/AjaxHandler.ashx?event=reloadMapMarkers&sectionPID=56c359428b0c1e3d3ccdf022&regionPID=626ab5b92a4455ef18207c54&subregionPID=&tagsPIDs=5aa6a3d0c6fe1dab103dd1a9&markerPID=&orderBy=datedesc&take=100000000&skip=0&reloadInfoArea=value&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=&tagsPIDs=")
data = res.json()

class ORMType:
    """ Unique type class to decipher between attributes """

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __index__(self):
        return int(self.key)

class ORM:
    """Basic ORM Class"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, ORMType(key, value))

    @staticmethod
    def attr_1():
        """ Adding this for Pylint issues """
        print("attr_1")

    @staticmethod
    def attr_2():
        """ Adding this for Pylint issues """
        print("attr_2")


web_data = ORM()
web_data.region = {}
web_data.factory_name = {}
web_data.marker = []
drink_tag = ''

for regions in data['Regions']:
    web_data.region.update({regions['Pid'] : regions['Title']})

for tags in data['Tags']:
    if tags['Title'] == 'drinks':
        drink_tag = tags['Pid']

for marker in data['Markers']:
    if drink_tag in marker['Tags']:
        web_data.marker.append({
                'id' : marker['Pid'],
                'title' : marker['Title'],
                'region' : marker['RegionId'],
                'address' : marker['Address'],
                'num_worker' : marker['numWorker'],
            })

for dat in web_data.marker:
    print(dat['id'])




from dolt import Dolt
import httplib2
from xml.dom import minidom

class StatsMixHttp(object):
    def __init__(self, api_key=None, http=None, *args, **kwargs):
        self.api_key = api_key
        self.http = http or httplib2.Http()

    def request(self, *args, **kwargs):
        if not 'headers' in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['X-StatsMix-Token'] = self.api_key
        return self.http.request(*args, **kwargs)

class StatsMix(Dolt):
    def __init__(self, api_key, *args, **kwargs):
        http = StatsMixHttp(api_key, *args, **kwargs)
        kwargs['http'] = http
        super(StatsMix, self).__init__(*args, **kwargs)
        self._api_url = "http://statsmix.com/api/v1"

    def _handle_response(self, response, data):
        return minidom.parseString(data)

import getpass
import os, sys
sys.path[0:0] = os.path.join(os.path.dirname(__file__), "..")

from dolt import Dolt
from httplib2 import Http

class Readernaut(Dolt):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._api_url = "http://readernaut.com"
        self._url_template = '%(domain)s/api/v1/json/%(generated_url)s'


if __name__ == "__main__":
    http = Http()
    username = raw_input("Readernaut Username: ")
    password = getpass.getpass("Readernaut Password: ")
    http.add_credentials(username, password)
    readernaut = Readernaut(http=http)
    books = readernaut.webology.books()
    print "Total books for webology: %d" % len(books)

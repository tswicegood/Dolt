import getpass
import os, sys
sys.path[0:0] = os.path.join(os.path.dirname(__file__), "..")

from dolt import Dolt
from httplib2 import Http

class Brightkite(Dolt):
    _api_url = "http://brightkite.com"
    _url_template = '%(domain)s/%(generated_url)s.json'


if __name__ == "__main__":
    http = Http()
    username = raw_input("Brightkite Username: ")
    password = getpass.getpass("Brightkite Password: ")
    http.add_credentials(username, password)
    bk = Brightkite(http=http)
    user = bk.me()
    print "Screen Name: %s" % user['login']

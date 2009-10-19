import os, sys
sys.path[0:0] = os.path.join(os.path.dirname(__file__), "..")

from dolt import Dolt
from httplib2 import Http

class Twitter(Dolt):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._api_url = "http://twitter.com"
        self._url_template = '%(domain)s/%(generated_url)s.json'

if __name__ == "__main__":
    http = Http()
    username = raw_input("Twitter Username: ")
    password = raw_input("Twitter Password: ")
    http.add_credentials(username, password)
    twitter = Twitter(http=http)
    user = twitter.users.show("tswicegood")
    print "Screen Name: %s" % user['screen_name']
    print "Real Name:   %s" % user['name']

    tweet = raw_input("Tweet something (blank to exit): ")
    if len(tweet) > 0:
        twitter.statuses.update.POST(status=tweet)


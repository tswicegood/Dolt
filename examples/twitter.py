import getpass
import os, sys
sys.path[0:0] = os.path.join(os.path.dirname(__file__), "..")

from dolt.apis import Twitter
from httplib2 import Http

if __name__ == "__main__":
    http = Http()
    username = raw_input("Twitter Username: ")
    password = getpass.getpass("Twitter Password: ")
    http.add_credentials(username, password)
    twitter = Twitter(http=http)
    user = twitter.users.show("tswicegood")
    print "Screen Name: %s" % user['screen_name']
    print "Real Name:   %s" % user['name']

    tweet = raw_input("Tweet something (blank to exit): ")
    if len(tweet) > 0:
        twitter.statuses.update.POST(status=tweet)


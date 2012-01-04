import os, sys
sys.path[0:0] = os.path.join(os.path.dirname(__file__), ".."),

from dolt import Api

class Flickr(Api):
    def __init__(self, api_key, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._api_key = api_key
        self._api_url = "http://api.flickr.com"
        self._url_template = "%(domain)s/services/rest/?format=json&method=flickr.%(generated_url)s"
        self._stack_collapser = '.'.join
        self._params_template = "&%s"
        self._params['api_key'] = self._api_key
        self._params['nojsoncallback'] = 1

if __name__ == "__main__":
    api_key = raw_input("Flickr API key: ")
    flickr = Flickr(api_key)
    response = flickr.people.getPublicPhotos(user_id="18843927@N00")
    for photo in response["photos"]["photo"]:
        print "id [%s] title [%s]" % (photo['id'], photo['title'])


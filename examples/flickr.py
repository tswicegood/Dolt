import os, sys
sys.path[0:0] = os.path.join(os.path.dirname(__file__), ".."),

from dolt import Dolt

class Flickr(Dolt):
    def __init__(self, api_key, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._api_key = api_key
        self._api_url = "http://api.flickr.com"
        self._url_template = "%(domain)s/services/rest/?format=json&method=%(generated_url)s"
        self._stack_collapser = self._collapse_stack
        self._params_template = "&%s"

    def _collapse_stack(self, *args, **kwargs):
        self._attribute_stack[0:0] = "flickr",
        return ".".join(self._attribute_stack)

    def get_url(self):
        url = super(self.__class__, self).get_url()
        return url + "&api_key=%s" % self._api_key

    def _handle_response(self, response, data):
        return super(self.__class__, self)._handle_response(response, data[14:-1])

if __name__ == "__main__":
    api_key = raw_input("Flickr API key: ")
    flickr = Flickr(api_key)
    response = flickr.people.getPublicPhotos(user_id="18843927@N00")
    for photo in response["photos"]["photo"]:
        print "id [%s] title [%s]" % (photo['id'], photo['title'])


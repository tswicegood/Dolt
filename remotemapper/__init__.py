import urllib

class RemoteMapper(object):
    def __init__(self, http=None):
        self._attribute_stack = []
        self._method = "GET"
        self._posts = []
        self._http = http
        self._params = {}
        self._api_url = ""
        self._url_template = '%(domain)s/%(generated_url)s'

    def __call__(self, *args, **kwargs):
        self._attribute_stack += [str(a) for a in args]
        self._params = kwargs
        self._http.request(self.get_url(), self._method)
        self._attribute_stack = []

    def __getattr__(self, name):
        if name.lower() == "post":
            self._method = "POST"
        else:
            self._attribute_stack.append(name)
        return self

    def get_url(self):
        url = self._url_template % {
            "domain": self._api_url,
            "generated_url" : "/".join(self._attribute_stack)
        }
        if len(self._params):
            url += '?%s' % urllib.urlencode(self._params)
        return url


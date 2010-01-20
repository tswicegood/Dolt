import httplib2
import simplejson
import urllib

class Dolt(object):

    def __init__(self, http=None):
        self._supported_methods = ("GET", "POST", "PUT", "HEAD", "DELETE",)
        self._attribute_stack = []
        self._method = "GET"
        self._posts = []
        self._http = http or httplib2.Http()
        self._params = {}
        self._api_url = ""
        self._url_template = '%(domain)s/%(generated_url)s'
        self._stack_collapser = "/".join
        self._params_template = '?%s'

    def __call__(self, *args, **kwargs):
        self._attribute_stack += [str(a) for a in args]
        self._params = kwargs
        body = None
        if self._method == 'POST':
            body = (self._params_template % urllib.urlencode(self._params))[1:]

        response, data = self._http.request(self.get_url(), self._method, body=body)
        self._attribute_stack = []
        return self._handle_response(response, data)

    def _handle_response(self, response, data):
        return simplejson.loads(data)

    def __getattr__(self, name):
        if name in self._supported_methods:
            self._method = name
        else:
            self._attribute_stack.append(name)
        return self

    def get_url(self):
        url = self._url_template % {
            "domain": self._api_url,
            "generated_url" : self._stack_collapser(self._attribute_stack),
        }
        if len(self._params) and self._method != 'POST':
            url += self._params_template % urllib.urlencode(self._params)
        return url

    try:
        __IPYTHON__
        def __dir__(self):
            return [ 
                '_supported_methods',
                '_attribute_stack',
                '_method',
                '_posts',
                '_http',
                '_params',
                '_api_url',
                '_url_template',
                '_stack_collapser',
                '_params_template',
                '__init__',
                '__call__',
                '_handle_response',
                '__getattr__',
                'get_url',
                '__dir__', 
        ]
        _getAttributeNames = trait_names = __dir__
    except NameError:
        pass

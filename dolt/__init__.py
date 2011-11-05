import httplib2
import urllib

try:
    import json
except ImportError:
    import simplejson as json

try:
    from decorator import decorator
except ImportError:
    # No decorator package available. Create a no-op "decorator".
    def decorator(f):
        def decorate(_func):
            def inner(*args, **kwargs):
                return f(_func, *args, **kwargs)
            return inner
        return decorate    


@decorator
def _makes_clone(_func, *args, **kw):
    """
    A decorator that returns a clone of the current object so that
    we can re-use the object for similar requests.
    """
    self = args[0]._clone()
    _func(self, *args[1:], **kw)
    return self

class Dolt(object):

    def __init__(self, http=None):
        self._supported_methods = ("GET", "POST", "PUT", "HEAD", "DELETE", "OPTIONS")
        self._attribute_stack = []
        self._method = "GET"
        self._body = None
        self._http = http or httplib2.Http()
        self._params = {}
        self._headers = {}
        self._api_url = ""
        self._url_template = '%(domain)s/%(generated_url)s'
        self._stack_collapser = "/".join
        self._params_template = '?%s'

    def __call__(self, *args, **kwargs):
        url = self.get_url(*[str(a) for a in args], **kwargs) 

        response, data = self._http.request(url, self._method, body=self._body, headers=self._headers)
        return self._handle_response(response, data)

    def _generate_params(self, params):
        return self._params_template % urllib.urlencode(params)

    def _handle_response(self, response, data):
        """
        Deserializes JSON if the content-type matches, otherwise returns the response
        body as is.
        """
        if data and response.get('content-type') in (
            'application/json', 
            'application/x-javascript',
            'text/javascript',
            'text/x-javascript',
            'text/x-json'
        ):
            return json.loads(data)
        else:
            return data

    @_makes_clone
    def __getitem__(self, name):
        """
        Adds `name` to the URL path.
        """
        self._attribute_stack.append(name)
        return self

    @_makes_clone
    def __getattr__(self, name):
        """
        Sets the HTTP method for the request or adds `name` to the URL path.

        ::
            
            >>> dolt.GET._method == 'GET'
            True
            >>> dolt.foo.bar.get_url()
            '/foo/bar'

        """
        if name in self._supported_methods:
            self._method = name
        elif not name.endswith(')'):
            self._attribute_stack.append(name)
        return self

    @_makes_clone
    def with_params(self, **params):
        """
        Add URL query parameters to the request.
        """
        self._params.update(params)
        return self

    @_makes_clone
    def with_body(self, body=None, **params):
        """
        Add a body to the request.

        When `body` is a:
            - string, it will be used as is. 
            - dict or list of (key, value) pairs, it will be form encoded
            - None, remove request body
            - anything else, a TypeError will be raised 
            
        If `body` is a dict or None you can also pass in keyword
        arguments to add to the body.

        ::
            >>> dolt.with_body(dict(key='val'), foo='bar')._body
            'foo=bar&key=val'
        """

        if isinstance(body, (tuple, list)):
            body = dict(body)

        if params:
            # Body must be None or able to be a dict
            if isinstance(body, dict):
                body.update(params)
            elif body is None:
                body = params
            else:
                raise ValueError('Body must be None or a dict if used with params, got: %r' % body)

        if isinstance(body, basestring):
            self._body = body
        elif isinstance(body, dict):
            self._body = urllib.urlencode(body)
        elif body is None:
            self._body = None
        else:
            raise TypeError('Invalid body type %r' % body)        
        

        return self

    def with_json(self, data=None, **params):
        """
        Add a json body to the request.   
        
        :param data: A json string, a dict, or a list of key, value pairs
        :param params: A dict of key value pairs to JSON encode     
        """
        if isinstance(data, (tuple, list)):
            data = dict(data)

        if params:
            # data must be None or able to be a dict
            if isinstance(data, dict):
                data.update(params)
            elif data is None:
                data = params
            else:
                raise ValueError('Data must be None or a dict if used with params, got: %r' % data)

        req = self.with_headers({'Content-Type': 'application/json', 'Accept': 'application/json'})
        if isinstance(data, basestring):
            # Looks like it's already been encoded
            return req.with_body(data)
        else:
            return req.with_body(json.dumps(data))

    @_makes_clone
    def with_headers(self, headers=None, **params):
        """
        Add headers to the request.   
        
        :param headers: A dict, or a list of key, value pairs
        :param params: A dict of key value pairs   
        """        
        if isinstance(headers, (tuple, list)):
            headers = dict(headers)

        if params:
            if isinstance(headers, dict):
                headers.update(params)
            elif headers is None:
                headers = params

        self._headers.update(headers)
        return self

    def get_url(self, *paths, **params):
        """
        Returns the URL for this request.

        :param paths: Additional URL path parts to add to the request
        :param params: Additional query parameters to add to the request
        """
        path_stack = self._attribute_stack[:]
        if paths:
            path_stack.extend(paths)

        u = self._stack_collapser(path_stack)
        url = self._url_template % {
            "domain": self._api_url,
            "generated_url" : u,
        }

        if self._params or params:
            internal_params = self._params.copy()
            internal_params.update(params)
            url += self._generate_params(internal_params)

        return url

    def _clone(self):
        """
        Clones the state of the current operation.

        The state is cloned so that you can freeze the state at a certain point for re-use.

        ::

            >>> cat = dolt.cat
            >>> cat.get_url()
            '/cat'
            >>> o = cat.foo
            >>> o.get_url()
            '/cat/foo'
            >>> cat.get_url()
            '/cat'

        """
        cls = self.__class__
        q = cls.__new__(cls)
        q.__dict__ = self.__dict__.copy()
        q._params = self._params.copy()
        q._headers = self._headers.copy()
        q._attribute_stack = self._attribute_stack[:]

        return q

    try:
        __IPYTHON__
        def __dir__(self):
            return [
                '_supported_methods',
                '_attribute_stack',
                '_method',
                '_body',
                '_http',
                '_params',
                '_headers',
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
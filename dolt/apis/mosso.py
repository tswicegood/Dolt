from dolt import Dolt
import datetime
import httplib2
try:
    import json as simplejson
except ImportError:
    import simplejson

MOSSO_AUTH_URL = "https://auth.api.rackspacecloud.com"

class MossoHttp(object):
    def __init__(self, username=None, api_key=None, version="1.0", http=None, *args, **kwargs):
        self.http = http or httplib2.Http()
        self.username = username
        self.api_key = api_key
        self.version = "1.0"
        self.auth_token = None

    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        if not self.auth_token:
            self.initialize_auth_token()
        if not headers:
            headers = {}
        headers['X-Auth-Token'] = self.auth_token
        return self.http.request(uri, method, body, headers, redirections, connection_type)

    def initialize_auth_token(self):
        if self.auth_token:
            return
        url = "%s/v%s?cache=%s" % (MOSSO_AUTH_URL, self.version, datetime.datetime.now().microsecond)
        response, _body = self.http.request(url, headers = {
            'X-Auth-User': self.username,
            'X-Auth-Key': self.api_key,
        })
        # TODO: handle non-204 requests
        self.server_url = response['x-server-management-url']
        self.auth_token = response['x-auth-token']


class MossoServers(Dolt):
    def __init__(self, username, api_key, **kwargs):
        http = MossoHttp(username=username, api_key=api_key)
        self._last_url = None
        super(MossoServers, self).__init__(http=http)

    def get_url(self):
        self._http.initialize_auth_token()
        self._api_url = self._http.server_url
        self._last_url = super(MossoServers, self).get_url()
        return self._last_url

    def _generate_body(self):
        def should_contain_values():
            if self._attribute_stack[-1] == 'servers':
                return True
            elif self._attribute_stack[0] == 'servers' and len(self._attribute_stack) == 2:
                try:
                    int(self._attribute_stack[-1])
                    return True
                except ValueError:
                    pass
            return False
        if self._method in ('POST', 'PUT'):
            values = {}
            if should_contain_values():
                values = {'server': self._params}
            elif self._params:
                values = self._params
            return simplejson.dumps(values)

    def _handle_response(self, response, data):
        if self._method in ('DELETE', 'PUT'):
            return {
                "202": "Completed",
                "204": "Successful",
                "400": "Bad Request",
                "401": "Unauthorized",
                "404": "Item Not Found",
                "409": "Build In-Progress",
                "413": "Over Limit",
                "500": "Cloud Servers Fault",
                "503": "Service Unavailable",
            }[response['status']]
        return super(MossoServers, self)._handle_response(response, data)

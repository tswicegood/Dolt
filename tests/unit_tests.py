import sys, os, random, urllib

try:
    import json
except ImportError:
    import simplejson as json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest, mox
from dolt import Dolt, Api
from dolt.helpers import add_basic_auth
from dolt.apis.couchdb import CouchDB
from dolt.apis.twitter import Twitter
from httplib2 import Http

JSON_HEADERS = {
    'content-type': 'application/json'
}

def random_attribute():
    return "some_random_" + str(random.randint(1, 10))

def testable_dolt():
    http = mox.MockObject(Http)
    dolt = Dolt('', http=http)
    return dolt

def dolt_request(dolt, url, method='GET', body=None, headers={}, response_headers=JSON_HEADERS, response_body='{}'):
    return dolt._http.request(url, method, body=body, headers=headers).AndReturn((response_headers, response_body))

def verify_all(*args):
    [mox.Verify(arg) for arg in args]

def replay_all(*args):
    [mox.Replay(arg) for arg in args]

class TestOfTwitterAPI(unittest.TestCase):
    def test_subclasses_dolt(self):
        twitter = Twitter()
        self.assert_(isinstance(twitter, Api))

    def test_contains_proper_api_url(self):
        twitter = Twitter()
        self.assertEqual(twitter._api_url, "https://twitter.com")

    def test_contains_proper_url_template(self):
        twitter = Twitter()
        self.assertEqual(twitter._url_template, '%(domain)s/%(generated_url)s.json')

    def test_http_can_be_passed_in(self):
        http = "http-%s" % random.randint(1, 10)
        twitter = Twitter(http=http)
        self.assertEqual(twitter._http, http)

class TestOfCouchDBApi(unittest.TestCase):
    def test_does_not_change_full_url(self):
        url = "http://%d.example.com:5984/" % random.randint(100, 200)
        couchdb = CouchDB(url)
        self.assertEqual(url, couchdb._api_url)

    def test_converts_to_localhost(self):
        url = "example"
        couchdb = CouchDB(url)
        self.assertEqual("http://localhost:5984/example", couchdb._api_url)

    def test_handles_json_in_get_params(self):
        http = mox.MockObject(Http)
        http.request(
            'http://localhost:5984/example/foo?' \
            'startkey=["foo",0]&endkey=["foo",{}]',
            'GET', body=None, headers={}
        ).AndReturn((JSON_HEADERS, "{}"))
        url = "example"
        couchdb = CouchDB(url, http=http)

        replay_all(http)

        couchdb.foo(startkey='["foo",0]', endkey='["foo",{}]')
        verify_all(http)

    def test_handles_integers_as_well_as_strings(self):
        http = mox.MockObject(Http)
        r = random.randint(1, 10)
        http.request(
            'http://localhost:5984/example/foo?' \
            'startkey=["foo",0]&endkey=["foo",{}]&group_level=%d' % r,
            'GET', body=None, headers={}
        ).AndReturn((JSON_HEADERS, "{}"))
        url = "example"
        couchdb = CouchDB(url, http=http)

        replay_all(http)

        couchdb.foo(startkey='["foo",0]', endkey='["foo",{}]', group_level=r)
        verify_all(http)

class TestOfDolt(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def test_attributes_return_main_object_clone(self):
        dolt = testable_dolt()

        attr = random_attribute()
        self.assertNotEqual(dolt, getattr(dolt, attr))
        self.assertEqual(dolt.__class__, getattr(dolt, attr).__class__)

    def test_get_url_returns_current_attrs(self):
        dolt = testable_dolt()
        attr = random_attribute()
        expected_url = "/%s/%s" % (attr, attr)
        dolt_request(dolt, expected_url, "GET")
        replay_all(dolt._http)

        getattr(getattr(dolt, attr), attr)()
        verify_all(dolt._http)

    def test_prepends_api_url_to_url(self):
        random_url = "http://api.%s.com" % random_attribute()
        dolt = testable_dolt()
        dolt._api_url = random_url
        dolt_request(dolt, "%s/foo" % random_url, "GET")
        replay_all(dolt._http)
        dolt.foo()
        verify_all(dolt._http)

    def test_uses_template_for_formatting_url(self):
        random_protocol = "http-%d" % random.randint(1, 10)
        dolt = testable_dolt()
        dolt_request(dolt, "%s://example.com/foo" % random_protocol, "GET")

        dolt._url_template = "%s://example.com/%%(generated_url)s" % random_protocol
        replay_all(dolt._http)

        dolt.foo()

        verify_all(dolt._http)

    def test_turns_arg_values_into_url(self):
        random_value = random.randint(1, 10)
        random_value2 = random.randint(1, 10)
        dolt = testable_dolt()
        dolt_request(dolt, "/foo/%d/%d" % (random_value, random_value2), "GET")
        replay_all(dolt._http)

        dolt.foo(random_value, random_value2)

        verify_all(dolt._http)

    def test_turns_kwargs_into_get_params(self):
        random_value = random.randint(1, 10)
        random_value2 = random.randint(1, 10)
        dolt = testable_dolt()
        dolt_request(dolt, "/foo?a=%d&b=%d" % (random_value, random_value2), "GET")
        replay_all(dolt._http)

        dolt.foo(a=random_value, b=random_value2)
        verify_all(dolt._http)

    def test_urls_reset_after_final_call(self):
        dolt = testable_dolt()
        dolt_request(dolt, "/foo", "GET")
        dolt_request(dolt, "/bar", "GET")
        replay_all(dolt._http)

        dolt.foo()
        dolt.bar()

        verify_all(dolt._http)

    def test_params_donot_carry_over_between_executions(self):
        one = random.randint(1, 10)
        two = random.randint(11, 20)
        three = random.randint(21, 30)

        dolt = testable_dolt()
        dolt_request(dolt, "/foo?a=%d&c=%d&b=%d" % (one, three, two), "GET")
        dolt_request(dolt, "/foo?a=%d&b=%d" % (two, one), "GET")

        replay_all(dolt._http)

        dolt.foo(a=one, b=two, c=three)
        dolt.foo(a=two, b=one)

        verify_all(dolt._http)

    def test_request_method_based_on_call(self):
        random_url = "posted-call-%d" % random.randint(1, 10)
        dolt = testable_dolt()
        dolt_request(dolt, "/%s" % random_url, "POST", body='')
        replay_all(dolt._http)

        getattr(dolt, random_url).with_body('').POST()

        verify_all(dolt._http)

    def test_request_methods_are_all_uppercase(self):
        dolt = testable_dolt()
        dolt_request(dolt, "/foo/post", "GET")
        replay_all(dolt._http)

        dolt.foo.post()
        verify_all(dolt._http)

    def test_supports_all_methods(self):
        dolt = testable_dolt()

        methods = ("GET", "POST", "PUT", "HEAD", "DELETE", "OPTIONS")
        for method in methods:
            dolt_request(dolt, "/foo", method)

        replay_all(dolt._http)

        for method in methods:
            getattr(dolt.foo, method)()

        verify_all(dolt._http)

    def test_supports_various_methods_as_attributes_as_well(self):
        dolt = testable_dolt()

        methods = (("GET", {"body": None}),
                   ("POST", {"body": ''}),
                   ("PUT", {"body": None}),
                   ("DELETE", {"body": None}),
                   ("HEAD", {"body": None}),)
        for args in methods:
            dolt_request(dolt, "/foo", args[0], **args[1] )
        replay_all(dolt._http)

        for method, args in methods:
            getattr(dolt, method).with_body(args['body']).foo()

        verify_all(dolt._http)

    def test_instanciates_httplib2_object_if_not_provided(self):
        dolt = Dolt('')
        self.assert_(isinstance(dolt._http, Http))

    def test_returns_parsed_json_response_from_request(self):
        dolt = testable_dolt()
        random_return = {"random": random.randint(1, 10)}
        dolt_request(dolt, "/foo", "GET", response_body=json.dumps(random_return))
        replay_all(dolt._http)

        self.assertEqual(dolt.foo(), random_return)

        verify_all(dolt._http)

    def test_takes_an_http_keyword_arg_and_sets_http_to_it(self):
        random_http = "http-%s" % random.randint(1, 10)
        dolt = Api(http=random_http)
        self.assertEqual(dolt._http, random_http)

    def test_uses_collapse_stack_to_join_string_for_request(self):
        random_separator = "-%d-" % random.randint(1, 10)
        def custom_collapser(stack):
            return random_separator.join(stack)

        expected_url = "/foo%sbar" % random_separator

        dolt = testable_dolt()
        dolt._stack_collapser = custom_collapser

        self.assertEqual(dolt.foo.bar.get_url(), expected_url)

    def test_returns_selfs_handle_response_after_call(self):
        dolt = testable_dolt()
        self.mox.StubOutWithMock(dolt, "_handle_response")
        dolt._handle_response(JSON_HEADERS, json.dumps({"foo":"bar"}))

        dolt_request(dolt, "/foo", "GET", response_body=json.dumps({"foo":"bar"}))
        replay_all(dolt._http, dolt._handle_response)

        dolt.foo()

        verify_all(dolt._http, dolt._handle_response)

    def test_has_a_template_for_params(self):
        dolt = testable_dolt()
        dolt_request(dolt, "/foo\\foo=bar", "GET", response_body=json.dumps({"foo": "bar"}))
        replay_all(dolt._http)

        dolt._params_template = "\\%s"
        dolt.foo(foo="bar")

        verify_all(dolt._http)

    def test_can_handle_get_params_on_post(self):
        dolt = testable_dolt()
        dolt_request(dolt, '/foo?foo=bar', 'POST', body='', response_body=json.dumps({"foo":"bar"}))
        replay_all(dolt._http)

        dolt.foo.with_body('').POST(foo="bar")
        verify_all(dolt._http)

    def test_can_use_getitem_for_path_parts(self):
        dolt = testable_dolt()
        dolt_request(dolt, "/foo/bar.html", 'GET')
        dolt_request(dolt, "/foo/bar.html", 'GET')
        replay_all(dolt._http)

        dolt.foo['bar.html']()
        dolt['foo/bar.html']()
        verify_all(dolt._http)

    def test_handle_getitem_exceptions(self):
        dolt = testable_dolt()
        dolt_request(dolt, "/foo", "GET", response_body=json.dumps({"foo":"bar"}))
        replay_all(dolt._http)

        try:
            dolt.foo[123]()
            raise AssertionError("Exception is not raised")
        except TypeError:
            pass

        # second call shouldn't raise an exception
        self.assertEqual(dolt.foo()['foo'], 'bar')

    def test_can_reuse_dolt(self):
        """
        Ensure that repeated calls to dolt does not stack up the URL paths
        """
        dolt = testable_dolt()
        self.assertEqual(dolt.test.get_url(), '/test')
        self.assertEqual(dolt.foo.get_url(), '/foo')
        self.assertEqual(dolt.foo.bar.get_url(), '/foo/bar')

    def test_with_body_on_post(self):
        dolt = testable_dolt()

        body_data = {"foo":"bar"}
        body = urllib.urlencode(body_data)

        dolt_request(dolt, '/foo', 'POST', body=body, response_body='')
        dolt_request(dolt, '/foo', 'POST', body=body, response_body='')
        dolt_request(dolt, '/foo', 'POST', body=body, response_body='')
        replay_all(dolt._http)

        dolt.foo.with_body(body_data).POST()
        dolt.foo.with_body(body).POST()
        dolt.foo.with_body(body_data.items()).POST()

        verify_all(dolt._http)

    def test_with_json_on_post(self):
        dolt = testable_dolt()

        body_data = {"foo":"bar"}
        body = json.dumps(body_data)
        body2 = json.dumps(dict(foo='bar', baz='123'))
        
        json_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        dolt_request(dolt, '/foo', 'POST', body=body,  headers=json_headers, response_body='')
        dolt_request(dolt, '/foo', 'POST', body=body,  headers=json_headers, response_body='')
        dolt_request(dolt, '/foo', 'POST', body=body2, headers=json_headers, response_body='')
        replay_all(dolt._http)

        dolt.foo.with_json(body_data).POST()
        dolt.foo.with_json(body).POST()
        dolt.foo.with_json(body_data, baz='123').POST()

        verify_all(dolt._http)        

    def test_get_url_with_args(self):
        dolt = testable_dolt()

        tests = [
            (dolt.foo.get_url(), '/foo'),
            (dolt.foo.get_url(foo=1), '/foo?foo=1'),
            (dolt.foo.get_url('bar', foo=2, baz='x'), '/foo/bar?foo=2&baz=x'),
            (dolt.foo.bam.get_url('bar', 'bingo', foo=2, baz='x'), '/foo/bam/bar/bingo?foo=2&baz=x'),
        ]

        for test, expected in tests:
            self.assertEqual(test, expected)

    def test_with_body_with_params(self):
        dolt = testable_dolt()        
        self.assertEqual(dolt.with_body(dict(key='val'))._body, 'key=val')
        self.assertEqual(dolt.with_body(foo='bar')._body, 'foo=bar')
        self.assertEqual(dolt.with_body(dict(key='val'), foo='bar')._body, 'foo=bar&key=val')

        try:
            dolt.with_body('str', foo='bar')
            raise AssertionError("Exception is not raised")
        except ValueError:
            pass

    def test_with_headers(self):
        dolt = testable_dolt()

        headers = {
            'Content-Type': 'text/plain',
            'Accept': 'foo/bar'
        }

        dolt_request(dolt, "/foo/bar", 'GET', body=None, headers=headers)
        dolt_request(dolt, "/foo/bar", 'GET', body=None, headers=headers)
        replay_all(dolt._http)

        dolt.foo.bar.with_headers(headers).GET()
        dolt.foo.bar.with_headers(**headers).GET()
        
        verify_all(dolt._http)
        
    def test_basic_auth_mixin(self):
        dolt = testable_dolt()
        dolt = add_basic_auth(dolt, 'myname', 'mypass')

        self.assertTrue('Authorization' in dolt._headers)
        self.assertTrue(dolt._headers['Authorization'].startswith('Basic '))

    def test_returns_parsed_json_with_content_type_params(self):
        dolt = testable_dolt()
        response_return = {"foo": 1}
        response_headers = {'content-type': 'application/json; param=bar'}
        dolt_request(dolt, "/foo", "GET", response_headers=response_headers,
                     response_body=json.dumps(response_return))
        replay_all(dolt._http)

        self.assertEqual(dolt.foo(), response_return)

        verify_all(dolt._http)

class TestOfSimpleDolt(unittest.TestCase):
    def test_base_url(self):
        dolt = Dolt('http://example.com')
        self.assertEquals(dolt._api_url, 'http://example.com')

if __name__ == '__main__':
    unittest.main()


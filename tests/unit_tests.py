import sys, os, random, simplejson
sys.path[0:0] = os.path.join(os.path.dirname(__file__), '..')
import unittest, mox
from dolt import Dolt
from dolt.apis.twitter import Twitter
from httplib2 import Http

def random_attribute():
    return "some_random_" + str(random.randint(1, 10))

def testable_dolt():
    http = mox.MockObject(Http)
    dolt = Dolt(http=http)
    return dolt

def verify_all(*args):
    [mox.Verify(arg) for arg in args]

def replay_all(*args):
    [mox.Replay(arg) for arg in args]
    
class TestOfTwitterAPI(unittest.TestCase):
    def test_subclasses_dolt(self):
        twitter = Twitter()
        self.assert_(isinstance(twitter, Dolt))
    
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

class TestOfDolt(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def test_attributes_return_main_object(self):
        dolt = testable_dolt()

        attr = random_attribute()
        self.assertEqual(dolt, getattr(dolt, attr))

    def test_get_url_returns_current_attrs(self):
        dolt = testable_dolt()
        attr = random_attribute()
        expected_url = "/%s/%s" % (attr, attr)
        dolt._http.request(expected_url, "GET", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        getattr(getattr(dolt, attr), attr)()
        verify_all(dolt._http)

    def test_prepends_api_url_to_url(self):
        random_url = "http://api.%s.com" % random_attribute()
        dolt = testable_dolt()
        dolt._api_url = random_url
        dolt._http.request("%s/foo" % random_url, "GET", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)
        dolt.foo()
        verify_all(dolt._http)

    def test_uses_template_for_formatting_url(self):
        random_protocol = "http-%d" % random.randint(1, 10)
        dolt = testable_dolt()
        dolt._http.request("%s://example.com/foo" % random_protocol, "GET", body=None).AndReturn(({}, "{}"))

        dolt._url_template = "%s://example.com/%%(generated_url)s" % random_protocol
        replay_all(dolt._http)

        dolt.foo()

        verify_all(dolt._http)

    def test_turns_arg_values_into_url(self):
        random_value = random.randint(1, 10)
        random_value2 = random.randint(1, 10)
        dolt = testable_dolt()
        dolt._http.request("/foo/%d/%d" % (random_value, random_value2), "GET", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo(random_value, random_value2)

        verify_all(dolt._http)

    def test_turns_kwargs_into_get_params(self):
        random_value = random.randint(1, 10)
        random_value2 = random.randint(1, 10)
        dolt = testable_dolt()
        dolt._http.request("/foo?a=%d&b=%d" % (random_value, random_value2), "GET", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo(a=random_value, b=random_value2)
        verify_all(dolt._http)

    def test_urls_reset_after_final_call(self):
        dolt = testable_dolt()
        dolt._http.request("/foo", "GET", body=None).AndReturn(({}, "{}"))
        dolt._http.request("/bar", "GET", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo()
        dolt.bar()

        verify_all(dolt._http)

    def test_params_donot_carry_over_between_executions(self):
        one = random.randint(1, 10)
        two = random.randint(11, 20)

        dolt = testable_dolt()
        dolt._http.request("/foo?a=%d&b=%d" % (one, two), "GET", body=None).AndReturn(({}, "{}"))
        dolt._http.request("/foo?a=%d&b=%d" % (two, one), "GET", body=None).AndReturn(({}, "{}"))

        replay_all(dolt._http)

        dolt.foo(a=one, b=two)
        dolt.foo(a=two, b=one)

        verify_all(dolt._http)

    def test_request_method_based_on_call(self):
        random_url = "posted-call-%d" % random.randint(1, 10)
        dolt = testable_dolt()
        dolt._http.request("/%s" % random_url, "POST", body='').AndReturn(({}, "{}"))
        replay_all(dolt._http)

        getattr(dolt, random_url).POST()

        verify_all(dolt._http)

    def test_request_methods_are_all_uppercase(self):
        dolt = testable_dolt()
        dolt._http.request("/foo/post", "GET", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo.post()
        verify_all(dolt._http)

    def test_supports_put_method(self):
        dolt = testable_dolt()
        dolt._http.request("/foo", "PUT", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo.PUT()
        verify_all(dolt._http)

    def test_supports_head_method(self):
        dolt = testable_dolt()
        dolt._http.request("/foo", "HEAD", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo.HEAD()
        verify_all(dolt._http)

    def test_supports_delete_method(self):
        dolt = testable_dolt()
        dolt._http.request("/foo", "DELETE", body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo.DELETE()
        verify_all(dolt._http)

    def test_supports_various_methods_as_attributes_as_well(self):
        dolt = testable_dolt()

        methods = (("GET", {"body": None}),
                   ("POST", {"body": ''}),
                   ("PUT", {"body": None}),
                   ("DELETE", {"body": None}),
                   ("HEAD", {"body": None}),)
        for args in methods:
            dolt._http.request("/foo", args[0], **args[1] ).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        for args in methods:
            getattr(dolt, args[0]).foo()

        verify_all(dolt._http)

    def test_instanciates_httplib2_object_if_not_provided(self):
        dolt = Dolt()
        self.assert_(isinstance(dolt._http, Http))

    def test_returns_parsed_json_response_from_request(self):
        dolt = testable_dolt()
        random_return = {"random": random.randint(1, 10)}
        dolt._http.request("/foo", "GET", body=None).AndReturn(({}, simplejson.dumps(random_return)))
        replay_all(dolt._http)

        self.assertEqual(dolt.foo(), random_return)

        verify_all(dolt._http)

    def test_takes_an_http_keyword_arg_and_sets_http_to_it(self):
        random_http = "http-%s" % random.randint(1, 10)
        dolt = Dolt(http=random_http)
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
        dolt._handle_response({}, simplejson.dumps({"foo":"bar"}))

        dolt._http.request("/foo", "GET", body=None).AndReturn(({}, simplejson.dumps({"foo":"bar"})))
        replay_all(dolt._http, dolt._handle_response)

        dolt.foo()

        verify_all(dolt._http, dolt._handle_response)

    def test_has_a_template_for_params(self):
        dolt = testable_dolt()
        dolt._http.request("/foo\\foo=bar", "GET", body=None).AndReturn(({}, simplejson.dumps({"foo": "bar"})))
        replay_all(dolt._http)

        dolt._params_template = "\\%s"
        dolt.foo(foo="bar")

        verify_all(dolt._http)

    def test_can_handle_get_params_on_post(self):
        dolt = testable_dolt()
        dolt._http.request('/foo?foo=bar', 'POST', body='').AndReturn(({}, simplejson.dumps({"foo":"bar"})))
        replay_all(dolt._http)

        dolt.foo.POST(GET={"foo": "bar"})
        verify_all(dolt._http)

    def test_can_use_getitem_for_path_parts(self):
        dolt = testable_dolt()
        dolt._http.request("/foo/bar.html", 'GET', body=None).AndReturn(({}, "{}"))
        dolt._http.request("/foo/bar.html", 'GET', body=None).AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo['bar.html']()
        dolt['foo/bar.html']()
        verify_all(dolt._http)


if __name__ == '__main__':
    unittest.main()


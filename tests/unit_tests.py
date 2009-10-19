import sys, os, random, simplejson
sys.path[0:0] = os.path.join(os.path.dirname(__file__), '..')
import unittest, mox
from dolt import Dolt
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

class TestOfDolt(unittest.TestCase):
    def test_attributes_return_main_object(self):
        dolt = testable_dolt()

        attr = random_attribute()
        self.assertEqual(dolt, getattr(dolt, attr))

    def test_get_url_returns_current_attrs(self):
        dolt = testable_dolt()
        attr = random_attribute()
        expected_url = "/%s/%s" % (attr, attr)
        dolt._http.request(expected_url, "GET").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        getattr(getattr(dolt, attr), attr)()
        verify_all(dolt._http)

    def test_prepends_api_url_to_url(self):
        random_url = "http://api.%s.com" % random_attribute()
        dolt = testable_dolt()
        dolt._api_url = random_url
        dolt._http.request("%s/foo" % random_url, "GET").AndReturn(({}, "{}"))
        replay_all(dolt._http)
        dolt.foo()
        verify_all(dolt._http)

    def test_uses_template_for_formatting_url(self):
        random_protocol = "http-%d" % random.randint(1, 10)
        dolt = testable_dolt()
        dolt._http.request("%s://example.com/foo" % random_protocol, "GET").AndReturn(({}, "{}"))

        dolt._url_template = "%s://example.com/%%(generated_url)s" % random_protocol
        replay_all(dolt._http)

        dolt.foo()

        verify_all(dolt._http)

    def test_turns_arg_values_into_url(self):
        random_value = random.randint(1, 10)
        random_value2 = random.randint(1, 10)
        dolt = testable_dolt()
        dolt._http.request("/foo/%d/%d" % (random_value, random_value2), "GET").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo(random_value, random_value2)

        verify_all(dolt._http)

    def test_turns_kwargs_into_get_params(self):
        random_value = random.randint(1, 10)
        random_value2 = random.randint(1, 10)
        dolt = testable_dolt()
        dolt._http.request("/foo?a=%d&b=%d" % (random_value, random_value2), "GET").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo(a=random_value, b=random_value2)
        verify_all(dolt._http)

    def test_urls_reset_after_final_call(self):
        dolt = testable_dolt()
        dolt._http.request("/foo", "GET").AndReturn(({}, "{}"))
        dolt._http.request("/bar", "GET").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo()
        dolt.bar()

        verify_all(dolt._http)

    def test_params_donot_carry_over_between_executions(self):
        one = random.randint(1, 10)
        two = random.randint(11, 20)

        dolt = testable_dolt()
        dolt._http.request("/foo?a=%d&b=%d" % (one, two), "GET").AndReturn(({}, "{}"))
        dolt._http.request("/foo?a=%d&b=%d" % (two, one), "GET").AndReturn(({}, "{}"))

        replay_all(dolt._http)

        dolt.foo(a=one, b=two)
        dolt.foo(a=two, b=one)

        verify_all(dolt._http)

    def test_request_method_based_on_call(self):
        random_url = "posted-call-%d" % random.randint(1, 10)
        dolt = testable_dolt()
        dolt._http.request("/%s" % random_url, "POST").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        getattr(dolt, random_url).POST()

        verify_all(dolt._http)

    def test_request_methods_are_all_uppercase(self):
        dolt = testable_dolt()
        dolt._http.request("/foo/post", "GET").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo.post()
        verify_all(dolt._http)

    def test_supports_put_method(self):
        dolt = testable_dolt()
        dolt._http.request("/foo", "PUT").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo.PUT()
        verify_all(dolt._http)

    def test_supports_head_method(self):
        dolt = testable_dolt()
        dolt._http.request("/foo", "HEAD").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo.HEAD()
        verify_all(dolt._http)

    def test_supports_delete_method(self):
        dolt = testable_dolt()
        dolt._http.request("/foo", "DELETE").AndReturn(({}, "{}"))
        replay_all(dolt._http)

        dolt.foo.DELETE()
        verify_all(dolt._http)

    def test_instanciates_httplib2_object_if_not_provided(self):
        dolt = Dolt()
        self.assert_(isinstance(dolt._http, Http))

    def test_returns_parsed_json_response_from_request(self):
        dolt = testable_dolt()
        random_return = {"random": random.randint(1, 10)}
        dolt._http.request("/foo", "GET").AndReturn(({}, simplejson.dumps(random_return)))
        replay_all(dolt._http)

        self.assertEqual(dolt.foo(), random_return)

        verify_all(dolt._http)

    def test_takes_an_http_keyword_arg_and_sets_http_to_it(self):
        random_http = "http-%s" % random.randint(1, 10)
        dolt = Dolt(http=random_http)
        self.assertEqual(dolt._http, random_http)


if __name__ == '__main__':
    unittest.main()


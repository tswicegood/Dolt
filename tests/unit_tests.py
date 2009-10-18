import sys, os, random
sys.path[0:0] = os.path.join(os.path.dirname(__file__), '..')
import unittest, mox
from remotemapper import RemoteMapper
from httplib2 import Http

def random_attribute():
    return "some_random_" + str(random.randint(1, 10))

def testable_remote_mapper():
    http = mox.MockObject(Http)
    rm = RemoteMapper(http=http)
    return rm

def verify_all(*args):
    [mox.Verify(arg) for arg in args]

def replay_all(*args):
    [mox.Replay(arg) for arg in args]

class TestOfRemoteMapper(unittest.TestCase):
    def test_attributes_return_main_object(self):
        rm = testable_remote_mapper()

        attr = random_attribute()
        self.assertEqual(rm, getattr(rm, attr))

    def test_get_url_returns_current_attrs(self):
        rm = testable_remote_mapper()
        attr = random_attribute()
        expected_url = "/%s/%s" % (attr, attr)
        rm._http.request(expected_url, "GET")
        replay_all(rm._http)

        getattr(getattr(rm, attr), attr)()
        verify_all(rm._http)

    def test_prepends_api_url_to_url(self):
        random_url = "http://api.%s.com" % random_attribute()
        rm = testable_remote_mapper()
        rm._api_url = random_url
        rm._http.request("%s/foo" % random_url, "GET")
        replay_all(rm._http)
        rm.foo()
        verify_all(rm._http)

    def test_uses_template_for_formatting_url(self):
        random_protocol = "http-%d" % random.randint(1, 10)
        rm = testable_remote_mapper()
        rm._http.request("%s://example.com/foo" % random_protocol, "GET")

        rm._url_template = "%s://example.com/%%(generated_url)s" % random_protocol
        replay_all(rm._http)

        rm.foo()

        verify_all(rm._http)

    def test_turns_arg_values_into_url(self):
        random_value = random.randint(1, 10)
        random_value2 = random.randint(1, 10)
        rm = testable_remote_mapper()
        rm._http.request("/foo/%d/%d" % (random_value, random_value2), "GET")
        replay_all(rm._http)

        rm.foo(random_value, random_value2)

        verify_all(rm._http)

    def test_turns_kwargs_into_get_params(self):
        random_value = random.randint(1, 10)
        random_value2 = random.randint(1, 10)
        rm = testable_remote_mapper()
        rm._http.request("/foo?a=%d&b=%d" % (random_value, random_value2), "GET")
        replay_all(rm._http)

        rm.foo(a=random_value, b=random_value2)
        verify_all(rm._http)

    def test_urls_reset_after_final_call(self):
        rm = testable_remote_mapper()
        rm._http.request("/foo", "GET")
        rm._http.request("/bar", "GET")
        replay_all(rm._http)

        rm.foo()
        rm.bar()

        verify_all(rm._http)

    def test_params_donot_carry_over_between_executions(self):
        one = random.randint(1, 10)
        two = random.randint(11, 20)

        rm = testable_remote_mapper()
        rm._http.request("/foo?a=%d&b=%d" % (one, two), "GET")
        rm._http.request("/foo?a=%d&b=%d" % (two, one), "GET")

        replay_all(rm._http)

        rm.foo(a=one, b=two)
        rm.foo(a=two, b=one)

        verify_all(rm._http)

    def test_request_method_based_on_call(self):
        random_url = "posted-call-%d" % random.randint(1, 10)
        rm = testable_remote_mapper()
        rm._http.request("/%s" % random_url, "POST")
        replay_all(rm._http)

        getattr(rm, random_url).POST()

        verify_all(rm._http)

    def test_request_methods_are_all_uppercase(self):
        rm = testable_remote_mapper()
        rm._http.request("/foo/post", "GET")
        replay_all(rm._http)

        rm.foo.post()
        verify_all(rm._http)

    def test_supports_put_method(self):
        rm = testable_remote_mapper()
        rm._http.request("/foo", "PUT")
        replay_all(rm._http)

        rm.foo.PUT()
        verify_all(rm._http)

    def test_supports_head_method(self):
        rm = testable_remote_mapper()
        rm._http.request("/foo", "HEAD")
        replay_all(rm._http)

        rm.foo.HEAD()
        verify_all(rm._http)

    def test_supports_delete_method(self):
        rm = testable_remote_mapper()
        rm._http.request("/foo", "DELETE")
        replay_all(rm._http)

        rm.foo.DELETE()
        verify_all(rm._http)

    def test_instanciates_httplib2_object_if_not_provided(self):
        rm = RemoteMapper()
        self.assert_(isinstance(rm._http, Http))

if __name__ == '__main__':
    unittest.main()


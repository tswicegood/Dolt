import base64

def add_basic_auth(dolt, username, password):
    """
    Send basic auth username and password.

    Normally you can use httplib2.Http.add_credentials() to add username and password.
    However this has two disadvantages.

    1. Some poorly implemented APIs require basic auth but don't send a
       "401 Authorization Required". Httplib2 won't send basic auth unless the server
       responds this way (see http://code.google.com/p/httplib2/issues/detail?id=130)
    2. Doing a request just to get a "401 Authorization Required" header is a waste
       of time and bandwidth. If you know you need basic auth, you might as well
       send it right up front.

    By using `with_basic_auth`, the username and password will be sent proactively
    without waiting for a 401 header.
    """
    return dolt.with_headers(
        Authorization='Basic %s' % base64.b64encode('%s:%s' % (username, password)).strip()
    )
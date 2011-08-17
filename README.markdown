Dolt
====
A dumb little wrapper around RESTful interfaces

What is Dolt?
-------------
Dolt is a minimalist wrapper around RESTful interfaces, specifically, JSON
RESTful interfaces.  Instead of adding another layer on top of the calls, this
uses Httplib2 and some Python magic to allow truly simple wrappers on top of
already well thought out (at least sometimes) REST APIs.

For example, let's look at the Twitter API call for grabbing a user.  We'll
use my user, [tswicegood][1]

    http://twitter.com/users/show.json?screen_name=tswicegood

[python-twitter][python-twitter] maps that to:

    twitter = twitter.Api()
    twitter.GetUser("tswicegood")

So where'd this come from?  The creators of python-twitter.  You have to read
their documentation to figure out what call to make, because the [api
docs][api-docs] don't mention `GetUser` anywhere.

Here's what that same call in the Twitter Dolt object as shown in the examples/
directory:

    twitter = Twitter()
    twitter.users.show(screen_name="tswicegood")

Notice the similarities?  This way, you can use the official API docs to figure
out how your'e supposed to interact with the object that represents it.  No extra
documentation needed.


How to handle non-GET methods
-----------------------------
Dolt can handle all sorts of methods in its requests, not just GET method
requests.  To do that, you have to muddy up the API call just a bit.

Here's an example making a post to update the status.  First, the Twitter
API:

    http://twitter.com/statuses/update.json

Now the Dolt version:

    twitter = Twitter()
    twitter.statuses.update.POST(status="Hello from Dolt!")

Notice that all you need to add to it is the method you want to call.  If
you're feeling very Pythonic and want to be explicit in every call, you can add
`.GET` as the final method call, though that's always assumed.

Sometimes having that `POST` or `PUT` at the end seems weird.  You can stick
the method wherever you want in the call string of properties, it just has to
be in all uppercase.  For example, this works just the same as the previous
code:

    twitter = Twitter()
    twitter.POST.statuses.update(status="Hello from Dolt!")

This works for other HTTP methods as well, such as `PUT`, `DELETE`, and `HEAD`.


Handling authentication
-----------------------
Dolt relies on the [httplib2][httplib2] project for its underlying HTTP
requests.  Httplib2 has an `add_credentials` method that allows you to add
credentials to it.  Dolt takes an `http` parameter in its `__init__` method
which allows you to pass in an Http object with credentials.  For example:

    http = Http()
    http.add_credentials("some_user", "secret")
    some_api = Dolt(http=http)


Using dictionary-style lookups
------------------------------
Not all sections of a path can be represented directly as part of a string.
You can use a dict-like syntax to add segments to the URL.  For example, you
can use the following:

    from dolt.apis.couchdb import CouchDB
    couch = CouchDB("awesome")
    couch["_design/posts"]["_list/all"]()

That is equivalent to:

    couch._design.posts._list.all()


Included APIs
-------------
Dolt's primary purpose is to make it easy to wrap other APIs, but there are a
few extras that are included as part of the distribution.

In alphabetical order:

* bit.ly
* CouchDB
* Disqus
* GitHub
* Mosso/Rackspace Cloud
* Statsmix
* Twitter


Contributing
------------
All development happens on [GitHub][main].  Follow these simple steps to get
your code added:

* Create something awesome -- make the code better, add a new API, whatever
  (this is the hardest part).
* [Fork][] Dolt
* Create a topic branch to house your changes
* Get all of your commits in the new topic branch
* Submit a [pull request][].

### Optional Steps
* Offer to buy me a beer. :-)
* *Or* Make sure your pull request contains all of the relevant unit tests to
  verify your code with.

### Running the test suite

* install mox (`pip install mox`);
* run the tests:

      cd Dolt/tests
      python unit_tests.py

License
-------
As of v0.3, this work is licensed under the [BSD][].

Of course, I'm not a lawyer, so if you have questions about the licensing and
how it effects your use, please consult a professional lawyer, not some random
README file.



[1]: http://twitter.com/tswicegood
[python-twitter]: http://code.google.com/p/python-twitter/
[api-docs]: http://apiwiki.twitter.com/Twitter-API-Documentation
[httplib2]: http://code.google.com/p/httplib2/
[BSD]: http://opensource.org/licenses/bsd-license.php
[main]: http://github.com/tswicegood/Dolt/
[Fork]: http://help.github.com/forking/
[pull request]: http://help.github.com/pull-requests/

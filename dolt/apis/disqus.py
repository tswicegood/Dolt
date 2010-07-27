from dolt import Dolt

class Disqus(Dolt):
    def __init__(self, user_api_key, version="1.1", *args, **kwargs):
        super(Disqus, self).__init__(*args, **kwargs)
        self._api_url = "http://disqus.com"
        self._url_template = "%(domain)s/api/%(generated_url)s/?user_api_key=" + user_api_key + "&version=" + version
        self._params_template = "&%s"



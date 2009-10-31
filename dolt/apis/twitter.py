from dolt import Dolt

class Twitter(Dolt):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._api_url = "https://twitter.com"
        self._url_template = '%(domain)s/%(generated_url)s.json'
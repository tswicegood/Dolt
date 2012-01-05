from dolt import Dolt

class GitHub(Dolt):
    def __init__(self, api_version="v2", *args, **kwargs):
        super(GitHub, self).__init__(*args, **kwargs)
        self._api_url = "https://github.com/api/%s/json" % api_version
        self._url_template = "%(domain)s/%(generated_url)s"


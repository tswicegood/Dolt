from dolt import Dolt

class Bitly(Dolt):
    def __init__(self, *args, **kwargs):
        super(Bitly, self).__init__(*args, **kwargs)
        self._defaults = {
            'login':None,
            'apiKey':None,
            'apiVersion':'2.0.1',
            'format':'json',
        }
        self._defaults.update(kwargs)
        self._api_url = 'http://api.bit.ly'
        self._url_template = '%(domain)s/%(generated_url)s.json'

    def __call__(self, *args, **kwargs):
        updated_kwargs = kwargs.update(self._defaults)
        super(Bitly, self).__call__(*args, **updated_kwargs)

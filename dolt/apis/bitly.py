from dolt import Dolt

class Bitly(Dolt):
    _api_url = 'http://api.bit.ly'

    def __init__(self, http=None, **kwargs):
        super(Bitly, self).__init__(http)
        self._defaults = {
            'login':None,
            'apiKey':None,
            'version':'2.0.1',
            'format':'json',
        }
        self._defaults.update(kwargs)

    def __call__(self, *args, **kwargs):
        updated_kwargs = kwargs
        updated_kwargs.update(self._defaults)
        return super(Bitly, self).__call__(*args, **updated_kwargs)

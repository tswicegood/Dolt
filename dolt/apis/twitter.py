from dolt import Dolt

class Twitter(Dolt):
    _api_url = "https://twitter.com"
    _url_template = '%(domain)s/%(generated_url)s.json'
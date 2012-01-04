from dolt import Api

class Twitter(Api):
    _api_url = "https://twitter.com"
    _url_template = '%(domain)s/%(generated_url)s.json'
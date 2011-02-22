from dolt import Dolt

class CouchDB(Dolt):
    def __init__(self, couch_db, *args, **kwargs):
        super(CouchDB, self).__init__(*args, **kwargs)
        if couch_db.find("/") is -1:
            couch_db = "http://localhost:5984/%s" % couch_db
        self._api_url = couch_db


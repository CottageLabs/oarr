import esprit
from portality.core import app

class AccountDAO(esprit.dao.DomainObject):
    __type__ = "account"
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    
    def save(self, conn=None, created=True, updated=True):
        # just a shim in case we want to do any tasks before doing the actual save
        super(AccountDAO, self).save(conn=conn, created=created, updated=updated)

class RegisterDAO(esprit.dao.DomainObject):
    __type__ = "register"
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    
    def save(self, conn=None, created=True, updated=True):
        # just a shim in case we want to do any tasks before doing the actual save
        super(RegisterDAO, self).save(conn=conn, created=created, updated=updated)

class StatisticsDAO(esprit.dao.DomainObject):
    __type__ = "statistics"
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    
    def save(self, conn=None, created=False, updated=False): # Note that we don't care about last_updated or created_date for stats
        # just a shim in case we want to do any tasks before doing the actual save
        super(StatisticsDAO, self).save(conn=conn, created=created, updated=updated)

class HistoryDAO(esprit.dao.DomainObject):
    __type__ = "history"
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    
    def save(self, conn=None, created=True, updated=True):
        # just a shim in case we want to do any tasks before doing the actual save
        super(HistoryDAO, self).save(conn=conn, created=created, updated=updated)

class SearchQuery(object):
    def __init__(self, full_query=None, query_string=None, fields=None, from_number=None, size=None, from_date=None, until_date=None):
        self.full_query = full_query
        self.query_string = query_string
        self.fields = fields
        self.from_number = from_number
        self.size = size
        self.from_date = from_date
        self.until_date = until_date
    
    def query(self):
        q = None
        
        # full_query overrides query_string, and if neither are set, then match all
        if self.full_query is not None:
            q = self.full_query
        elif self.query_string is not None:
            q = {"query" : {"query_string" : {"query" : self.query_string}}}
        else:
            if self.from_date is not None or self.until_date is not None:
                rq = {"range" : {"last_updated" : {}}}
                if self.from_date:
                    rq["range"]["last_updated"]["gte"] = self.from_date
                if self.until_date:
                    rq["range"]["last_updated"]["lte"] = self.until_date
                q = {"query" : rq}
            else:
                q = {"query" : {"match_all" : {}}}
        
        if self.fields is not None:
            q["fields"] = self.fields
        
        if self.from_number is not None:
            q["from"] = self.from_number
        
        if self.size is not None:
            q["size"] = self.size
        
        return q






























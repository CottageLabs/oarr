import esprit
from portality.core import app

class AccountDAO(esprit.dao.DomainObject):
    __type__ = "account"
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    
    @classmethod
    def pull_by_auth_token(cls, auth_token):
        q = AccountQuery(auth_token=auth_token)
        res = cls.query(q=q.query())
        accs = esprit.raw.unpack_json_result(res)
        if len(accs) == 0 or accs is None:
            return None
        if len(accs) > 1:
            raise AccountDAOException("more than one account with that auth_token")
        return cls(accs[0])
    
    @classmethod
    def pull_by_name(cls, name):
        q = AccountQuery(name=name)
        res = cls.query(q=q.query())
        accs = esprit.raw.unpack_json_result(res)
        if len(accs) == 0 or accs is None:
            return None
        if len(accs) > 1:
            raise AccountDAOException("more than one account with that name")
        return cls(accs[0])
    
    def save(self, conn=None, created=True, updated=True):
        # just a shim in case we want to do any tasks before doing the actual save
        super(AccountDAO, self).save(conn=conn, created=created, updated=updated)

class AccountQuery(object):
    def __init__(self, auth_token=None):
        self.auth_token = auth_token
    def query(self):
        q = {
            "query" : {
                "term" : {"auth_token.exact" : self.auth_token}
            }
        }
        return q

class AccountDAOException(Exception):
    pass



class RegisterDAO(esprit.dao.DomainObject):
    __type__ = "register"
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    
    def save(self, conn=None, created=True, updated=True):
        # just a shim in case we want to do any tasks before doing the actual save
        super(RegisterDAO, self).save(conn=conn, created=created, updated=updated)



class StatisticsDAO(esprit.dao.DomainObject):
    __type__ = "statistics"
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    
    @classmethod
    def list_statistics(cls, record_id, from_date=None, until_date=None, provider=None, stat_type=None):
        stats_query = StatsQuery(record_id, from_date, until_date, provider, stat_type)
        es_results = cls.query(q=stats_query.query())
        stats = esprit.raw.unpack_json_result(es_results)
        return stats
    
    def save(self, conn=None, created=False, updated=False): # Note that we don't care about last_updated or created_date for stats
        # just a shim in case we want to do any tasks before doing the actual save
        super(StatisticsDAO, self).save(conn=conn, created=created, updated=updated)

class StatsQuery(object):
    def __init__(self, record_id=None, from_date=None, until_date=None, provider=None, stat_type=None):
        self.record_id = record_id
        self.from_date = from_date
        self.until_date = until_date
        self.provider = provider
        self.stat_type = stat_type
    
    def query(self):
        q = {"query" : {"bool" : {"must" : []}}}
        
        if self.record_id is not None:
            iq = {"term" : {"about.exact" : self.record_id}}
            q["query"]["bool"]["must"].append(iq)
        
        if self.from_date is not None or self.until_date is not None:
            rq = {"range" : {"date" : {}}}
            if self.from_date:
                rq["range"]["date"]["gte"] = self.from_date
            if self.until_date:
                rq["range"]["date"]["lte"] = self.until_date
            q["query"]["bool"]["must"].append(rq)
        
        if self.provider is not None:
            pq = {"term" : {"third_party.exact" : self.provider}}
            q["query"]["bool"]["must"].append(pq)
        
        if self.stat_type is not None:
            sq = {"term" : {"type.exact" : self.stat_type}}
            q["query"]["bool"]["must"].append(sq)
        
        q["size"] = 10000
        q["sort"] = {"date" : {"order" : "desc"}}
        
        return q



class HistoryDAO(esprit.dao.DomainObject):
    __type__ = "history"
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    
    @classmethod
    def list_history(cls, about, from_date=None, until_date=None):
        hist_query = HistoryQuery(about, from_date, until_date)
        es_results = cls.query(q=hist_query.query())
        h = esprit.raw.unpack_json_result(es_results)
        return h
    
    def save(self, conn=None, created=True, updated=True):
        # just a shim in case we want to do any tasks before doing the actual save
        super(HistoryDAO, self).save(conn=conn, created=created, updated=updated)

class HistoryQuery(object):
    def __init__(self, about, from_date=None, until_date=None):
        self.about = about
        self.from_date = from_date
        self.until_date = until_date
    
    def query(self):
        q = {"query" : {"bool" : {"must" : []}}}
        
        if self.about is not None:
            aq = {"term" : {"about.exact" : self.about}}
            q["query"]["bool"]["must"].append(aq)
        
        if self.from_date is not None or self.until_date is not None:
            rq = {"range" : {"last_updated" : {}}}
            if self.from_date:
                rq["range"]["last_updated"]["gte"] = self.from_date
            if self.until_date:
                rq["range"]["last_updated"]["lte"] = self.until_date
            q["query"]["bool"]["must"].append(rq)
        
        q["sort"] = {"last_updated" : {"order" : "desc"}}
        
        return q




class SearchQuery(object):
    def __init__(self, full_query=None, query_string=None, fields=None, 
                    from_number=None, size=None, 
                    from_date=None, until_date=None,
                    order=None):
        self.full_query = full_query
        self.query_string = query_string
        self.fields = fields
        self.from_number = from_number
        self.size = size
        self.from_date = from_date
        self.until_date = until_date
        self.order = order if isinstance(order, tuple) and len(order) == 2 else None
    
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
        
        if self.order is not None:
            sort_by, direction = self.order
            q["sort"] = {sort_by : {"order" : direction}}
        
        return q






























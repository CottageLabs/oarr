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

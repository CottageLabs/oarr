from portality import models, dao

class RegistryAPI(object):
    @classmethod
    def get_registry_entry(cls, record_id):
        register = models.Register.pull(record_id)
        return register
    
    @classmethod
    def search(cls, es=None, q=None, fields=None, from_number=None, size=None):
        search_query = dao.SearchQuery(es, q, fields, from_number, size)
        es_results = models.Register.query(q=search_query.query())
        return es_results
    
    @classmethod
    def change_list(cls, from_date=None, until_date=None):
        range_query = dao.SearchQuery(from_date=from_date, until_date=until_date)
        # TODO: work out how best to represent a Change List

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
    def change_list(cls, from_date=None, until_date=None, from_number=None, size=None):
        range_query = dao.SearchQuery(from_number=from_number, size=size, 
                        from_date=from_date, until_date=until_date, order=("last_updated", "asc"))
        es_results = models.Register.query(q=range_query.query())
        return es_results
    
    @classmethod
    def get_statistics(cls, record_id, from_date=None, until_date=None, provider=None, stat_type=None):
        return models.Statistics.list_statistics(record_id, from_date=from_date, until_date=until_date, provider=provider, stat_type=stat_type)
    
    @classmethod
    def create_register(cls, new_register):
        # mint the object and save
        record = models.Register(new_register)
        record.save()
        return record.id
    
    @classmethod
    def update_register(cls, record, new_register):
        if "register" in new_register:
            new_register = new_register["register"]
        record.merge_register(new_register)
        record.save()
    
    @classmethod
    def replace_register(cls, record, new_register):
        if "register" in new_register:
            new_register = new_register["register"]
        record.replace_register(new_register)
        record.save()

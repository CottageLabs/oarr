from portality import models, dao

class AuthorisationException(Exception):
    pass

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
    def create_register(cls, account, new_register):
        # check permissions on the account
        if not account.registry_access:
            raise AuthorisationException("This user account does not have permission to create objects in the registry")
        
        # ensure the register object has the right structure
        if "register" not in new_register:
            new_register = {"register" : new_register}
        
        # prune the third party account data if necessary
        cls._prune_third_party(account, new_register)
        
        # mint the object and save
        record = models.Register(new_register)
        record.save()
        
        # return the identifier of the newly created item
        return record.id
    
    @classmethod
    def update_register(cls, account, record, new_register):
        # check permissions on the account
        if not account.registry_access:
            raise AuthorisationException("This user account does not have permission to modify objects in the registry")
        
        # ensure the register object has the right structure
        if "register" not in new_register:
            new_register = {"register" : new_register}
        
        # prune the third party account data if necessary
        cls._prune_third_party(account, new_register)
        
        # snapshot, then merge the new register into the record and save
        record.snapshot()
        record.merge_register(new_register)
        record.save()
    
    @classmethod
    def replace_register(cls, account, record, new_register):
        # check permissions on the account
        if not account.registry_access:
            raise AuthorisationException("This user account does not have permission to overwrite objects in the registry")
            
        # ensure the register object has the right structure
        if "register" not in new_register:
            new_register = {"register" : new_register}
        
        # prune the third party account data if necessary
        cls._prune_third_party(account, new_register)
        
        # snapshot, then replace the register and save
        record.snapshot()
        record.replace_register(new_register)
        record.save()
    
    @classmethod
    def delete_register(cls, account, record):
        # check permissions on the account
        if not account.registry_access:
            raise AuthorisationException("This user account does not have permission to delete objects from the registry")
        
        # snapshot and then delete the registry object
        record.snapshot()
        record.soft_delete()
        record.save()
    
    @classmethod
    def _prune_third_party(cls, account, register):
        if "admin" not in register:
            return
        if len(register["admin"].keys()) == 0:
            return
        remove_keys = []
        for key in register["admin"].keys():
            if key != account.name:
                remove_keys.append(key)
        for k in remove_keys:
            del register["admin"][k]
        
        

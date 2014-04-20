from portality import models, dao
from datetime import datetime

class AuthorisationException(Exception):
    pass

class APIException(Exception):
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
    def get_history(cls, record_id, from_date=None, until_date=None):
        return models.History.list_history(record_id, from_date=from_date, until_date=until_date)
    
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
        record.snapshot(account=account)
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
        record.snapshot(account=account)
        record.replace_register(new_register)
        record.save()
    
    @classmethod
    def delete_register(cls, account, record):
        # check permissions on the account
        if not account.registry_access:
            raise AuthorisationException("This user account does not have permission to delete objects from the registry")
        
        # snapshot and then delete the registry object
        record.snapshot(account=account)
        record.soft_delete()
        record.save()
    
    @classmethod
    def add_statistic(cls, account, record, raw_stat):
        # check permissions on the account
        if not account.statistics_access:
            raise AuthorisationException("This user account does not have permission to add statistics to the registry")
        
        value = raw_stat.get("value")
        type = raw_stat.get("type")
        date = raw_stat.get("date")
        
        # dates must be of the right format
        if date is None:
            date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            date = cls._normalise_date(date)
        
        # values must be a float
        value = cls._numberise(value)
        
        # create, populate and save the statistic
        stat = models.Statistics()
        stat.about = record.id
        stat.value = value
        stat.type = type
        stat.date = date
        stat.third_party = account.name
        stat.save()
        
        return stat.id
        
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
    
    @classmethod
    def _normalise_date(cls, date):
        try:
            ts = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            return date
        except:
            pass
        try:
            ts = datetime.strptime(date, "%Y-%m-%d")
            return date + "T00:00:00Z"
        except:
            pass
        raise APIException(str(date) + " is not of an acceptable format")

    @classmethod
    def _numberise(self, s):
        try:
            return float(s)
        except:
            raise APIException(str(s) + " cannot be coerced to float")
















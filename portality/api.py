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

        # clear the created date and last updated date -> the client can't set these, only the system.
        # they will be allocated at save for new records
        cls._clear_admin_dates(new_register)
        
        # we may be getting admin data too
        if "admin" in new_register:
            if not account.admin_access:
                raise AuthorisationException("This user account does not have permission to set admin data on the registry")
        
        # mint the object and save
        try:
            record = models.Register(new_register)
        except models.ModelException:
            raise APIException("unable to create register object from supplied data")
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

        # clear the created date and last updated date -> the client can't set these, only the system.
        # they will be merged in from the old version of the record
        cls._clear_admin_dates(new_register)
        
        # we may be getting admin data too
        if "admin" in new_register:
            if not account.admin_access:
                raise AuthorisationException("This user account does not have permission to set admin data on the registry")
        
        # snapshot, then merge the new register into the record and save
        record.snapshot(account=account)
        try:
            record.merge_register(new_register)
        except models.ModelException:
            raise APIException("unable to create register object from supplied data")
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

        # clear the created date and last updated date -> the client can't set these, only the system.
        # they will be merged in from the old version of the record
        cls._clear_admin_dates(new_register)
        
        # we may be getting admin data too
        if "admin" in new_register:
            if not account.admin_access:
                raise AuthorisationException("This user account does not have permission to set admin data on the registry")
        
        # snapshot, then replace the register and save
        record.snapshot(account=account)
        try:
            record.replace_register(new_register)
        except models.ModelException:
            raise APIException("unable to create register object from supplied data")
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
    def set_admin(cls, account, record, admin):
        # check permissions on the account
        if not account.admin_access:
            raise AuthorisationException("This user account does not have permission to set admin data on the registry")
        
        # set the admin record
        record.set_admin(account.name, admin)
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
    def delete_statistic(cls, account, stat, force=False):
        # check permissions on the account
        if not account.statistics_access:
            raise AuthorisationException("This user account does not have permission to delete statistics from the registry")
        
        if account.name != stat.third_party and not force:
            raise AuthorisationException("This user does not own the statistic so cannot delete it")
        
        # delete the stat from the index
        stat.delete()
    
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
    def _clear_admin_dates(cls, register):
        if "created_date" in register:
            del register["created_date"]
        if "last_updated" in register:
            del register["last_updated"]

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
















from portality import dao, schema
from flask.ext.login import UserMixin
from copy import deepcopy

class ModelException(Exception):
    pass

class Account(dao.AccountDAO, UserMixin):
    """
    {
        "id" : "<opaque identifier for this third party>",
        "name" : "<human readable name for this third party>",
        "contact" : [
            {
                "name" : "<contact name>",
                "email" : "<contact email>"
            }
        ],
        "access" : {
            "registry" : true|false,
            "statistics" : true|false,
            "admin" : true|false
        },
        "auth_token" : "<account's API authentication token>",
    }
    """
    __type__ = 'account'
    
    @property
    def name(self):
        return self.data.get("name")
    
    def set_name(self, name):
        self.data["name"] = name
    
    def set_auth_token(self, token):
        self.data['auth_token'] = token

    def check_auth_token(self, token):
        return token is not None and token == self.data.get("auth_token")
    
    def add_contact(self, name, email):
        if "contact" not in self.data:
            self.data["contact"] = []
        self.data["contact"].append({"name" : name, "email" : email})
    
    def set_contact(self, name, email):
        self.data["contact"] = [{"name" : name, "email" : email}]
    
    @property
    def contact(self):
        return self.data.get("contact", [])
    
    @property
    def registry_access(self):
        return self.data.get("access", {}).get("registry", False)
    
    def allow_registry_access(self, val):
        if "access" not in self.data:
            self.data["access"] = {}
        self.data["access"]["registry"] = val
    
    @property
    def statistics_access(self):
        return self.data.get("access", {}).get("statistics", False)
    
    def allow_statistics_access(self, val):
        if "access" not in self.data:
            self.data["access"] = {}
        self.data["access"]["statistics"] = val
    
    @property
    def admin_access(self):
        return self.data.get("access", {}).get("admin", False)
    
    def allow_admin_access(self, val):
        if "access" not in self.data:
            self.data["access"] = {}
        self.data["access"]["admin"] = val
    
    @property
    def is_super(self):
        return not self.is_anonymous() and self.id in app.config['SUPER_USER']
        

class Statistics(dao.StatisticsDAO):
    """
    {
        "id" : "<opaque identifier for this statistical record>",
        "about" : "<opaque identifier for the repository>",
        "value" : <the numerical statistic, whatever it is>,
        "type" : "<the name of the type of statistic>",
        "date" : "<date the statistic was generated>",
        "third_party" : "<system id that provided the statistic>"
    }
    """
    
    @property
    def about(self): return self.data.get("about")
    @about.setter
    def about(self, repo_id): self.data["about"] = repo_id
    
    @property
    def value(self): return self.data.get("value")
    @value.setter
    def value(self, val): self.data["value"] = val
    
    @property
    def type(self): return self.data.get("type")
    @type.setter
    def type(self, t): self.data["type"] = t
    
    @property
    def date(self): return self.data.get("date")
    @date.setter
    def date(self, date): self.data["date"] = date # should probably do some validation
    
    @property
    def third_party(self): return self.data.get("third_party")
    @third_party.setter
    def third_party(self, tp): self.data["third_party"] = third_party

class Register(dao.RegisterDAO):
    _register_schema = {
        "fields" : ["replaces", "isreplacedby", "operational_status"],
        "lists" : ["metadata", "software", "contact", "organisation", "policy", "api", "integration"],
        "list_entries" : {
            "metadata" : {
                "bools" : ["default"],
                "fields" : ["lang"],
                "objects" : ["record"],
                "object_entries" : {
                    "record" : {
                        "fields" : ["country", "continent", "twitter", "acronym", "description", "established_date", "name", "url"],
                        "lists" : ["language", "subject", "repository_type", "certification", "content_type"],
                        "list_entries" : {
                            "subject" : {
                                "fields" : ["scheme", "term", "code"]
                            }
                        }
                    }
                }
            },
            "software" : {
                "fields" : ["name", "version", "url"]
            },
            "contact" : {
                "lists" : ["role"],
                "objects" : ["details"],
                "object_entries" : {
                    "details" : {
                        "fields" : ["name", "email", "address", "fax", "phone", "lat", "lon", "job_title"]
                    }
                }
            },
            "organisation" : {
                "lists" : ["role"],
                "objects" : ["details"],
                "object_entries" : {
                    "details" : {
                        "fields" : ["name", "acronym", "url", "unit", "unit_acronym", "unit_url", "country", "lat", "lon"]
                    }
                }
            },
            "policy" : {
                "fields" : ["policy_type", "policy_grade", "description"],
                "lists" : ["terms"]
            },
            "api" : {
                "fields" : ["api_type", "version", "base_url"],
                "lists" : ["metadata_prefixes", "accepts", "accept_packaging"]
            },
            "integration" : {
                "fields" : ["integrated_with", "nature", "url", "software", "version"]
            }
        }
    }
    
    """
    {
        "id" : "<opaque identifier for this repository>",
        "last_updated" : "<datestamp of last record modification>",
        "created_date" : "<datestamp of record creation time>",
        
        "register" : {
            "replaces" : "<oarr uri of repository this one replaces>",
            "isreplacedby" : "<oarr uri of repository this one is replaced by>",
            "operational_status" : "<status flag for this repository>",
            
            "metadata" : [
                {
                    "lang" : "en",
                    "default" : true|false
                    "record" : {
                        "country" : "<country repository resides in>",
                        "continent" : "<continent repository resides in>",
                        "twitter" : "<repository's twitter handle>",
                        "acronym" : "<repository name acronym>",
                        "description" : "<free text description of repository>",
                        "established_date" : "<date established!>",
                        "language" : [<languages of content found in repo (iso-639-1)>],
                        "name" : "<name of repository>",
                        "url" : "<url for repository home page>",
                        "subject" : [
                            { 
                                "scheme" : "<classification scheme>",
                                "term" : "<classification term>",
                                "code" : "<classification code>"
                            }
                        ],
                        "repository_type" : [<list of vocabulary terms for the repository>],
                        "certification" : [<list of certifications held by this repository>],
                        "content_type" : [<list of vocabulary terms for the content in this repository>]
                    }
                }
            ],
            "software" : [
                {
                    "name" : "<name of software used to provide this repository>",
                    "verson" : "<version of software used to provide this repository>",
                    "url" : "<url for the software/this version of the software>"
                }
            ],
            "contact" : [
                {
                    "role" : ["<contact role with regard to this repository>"]
                    "details": {
                        "name" : "<contact name>",
                        "email" : "<contact email>",
                        "address" : "<postal address for contact>",
                        "fax": "<fax number of contact>",
                        "phone": "<phone number of contact>",
                        "lat" : "<latitude of contact location>",
                        "lon" : "<longitude of contact location>",
                        "job_title" : "<contact job title>"
                    }
                }
            ],
            "organisation" : [
                {
                    "role" : [<organisation roles with regard to this repository>],
                    "details" : {
                        "name" : "<name of organisation>",
                        "acronym" : "<acronym of organisation>",
                        "url" : "<organisation url>",
                        
                        "unit" : "<name of organisation's unit responsible>"
                        "unit_acronym" : "<acronym of unit responsible>",
                        "unit_url" : "<url of responsible unit>",
                        
                        "country" : "<country repository resides in>",
                        "lat" : "<latitude of organisation/unit>",
                        "lon" : "<longitude of organisation/unit>"
                    }
                }
            ]
            "policy" : [
                {
                    "policy_type" : "<vocabulary term for policy>",
                    "policy_grade" : "<vocabulary term for quality of policy>",
                    "description" : "<description of policy terms, human readable>",
                    "terms" : [<list of vocabulary terms describing the policy>]
                }
            ],
            "api" : [
                {
                    "api_type" : "<api type from known list or free text>",
                    "version" : "<version of the API>",
                    "base_url" : "<base url of API>",
                    
                    "metadata_prefixes" : [<list of supported prefixes>], # oai-pmh
                    "accepts" : [<list of accepted mimetypes>], # sword
                    "accept_packaging" : [<list of accepted package formats>], #sword
                }
            ],
            "integration": [
                {
                    "integrated_with" : "<type of system integrated with>",
                    "nature" : "<nature of integration>",
                    "url" : "<url of system integrated with, if available>",
                    "software" : "<name of software integrated with>",
                    "version": "<version of software integrated with>"
                }
            ]
        },
        
        "admin" : {
            "<third_party name>" : {
                "date_added" : "<date 3rd party approved record for inclusion>",
                "in_opendoar" : true|false
            }
        }
    }
    """
    # FIXME: this object is very complex, and there isn't an immediately obvious
    # way in which it will be used server-side, so we should just flesh this out
    # as the functions become necessary.
    #
    # Probably the most important thing will be making sure that users aren't just
    # dumping junk into it.  So some kind of schema validation, maybe.
    
    def __init__(self, raw):
        super(Register, self).__init__(raw)
        valid = self._validate_register(self.data.get("register", {}))
        if not valid:
            raise ModelException("Raw data provided to Register is not schema valid")
    
    @property
    def register(self):
        return self.data.get("register")
    
    @register.setter
    def register(self, reg):
        self.data["register"] = reg
    
    def set_admin(self, third_party, record):
        if "admin" not in self.data:
            self.data["admin"] = {}
        self.data["admin"][third_party] = record
    
    def get_admin(self, third_party):
        if "register" not in self.data:
            self.data["register"] = {}
        return self.data.get("admin", {}).get(third_party)
    
    def merge_register(self, new_reg):
        if not self._validate_register(new_reg):
            raise ModelException("Update to register is not schema valid")
        for k, v in new_reg.iteritems():
            self.data["register"][k] = deepcopy(v)
    
    def replace_register(self, new_reg):
        if not self._validate_register(new_reg):
            raise ModelException("Replacement register is not schema valid")
        self.register = deepcopy(new_reg)
        
    def _validate_register(self, reg):
        try:
            schema.validate(reg, self._register_schema)
            return True
        except schema.ObjectSchemaValidationError as e:
            print e.message
        return False
    

class History(dao.HistoryDAO, Register):
    """
    {
        "ver" : "<version number for the record>",
        "about" : "<opaque id of the repository record it is about>"
    }
    
    This inherits from Register.
    
    Left-to-right search of multiple parents means the HistoryDAO must be left-most to ensure that
    the correct DAO methods are called.
    """
    
    @property
    def ver(self): return self.data.get("ver")
    @ver.setter
    def ver(self, ver): self.data["ver"] = ver
    
    @property
    def about(self): return self.data.get("about")
    @about.setter
    def about(self, repo_id): self.data["about"] = repo_id
    
    def set_register(self, register):
        v = self.ver
        a = self.about
        self.data.clear()
        self.data.update(register)
        self.ver = v
        self.about = a
    

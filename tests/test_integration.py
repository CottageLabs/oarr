# TODO: this is where we actively fire stuff at the API, and check that it works

from unittest import TestCase
import requests, json, time
from portality import models

BASE_URL = "http://localhost:5001/"
AUTH_TOKEN_1 = "feaf5347e4e94fe2b45cc51976879648"
AUTH_TOKEN_2 = "69013a52e8e14221b09b122b489ee87c"
AUTH_TOKEN_3 = "135ac0e2af78475eb8a915fbbe64dff9"

class TestIntegration(TestCase):

    def setUp(self):
        self._make_account("test1", True, False, False, AUTH_TOKEN_1)
        self._make_account("test2", False, False, False, AUTH_TOKEN_2)
        self._make_account("test3", True, False, False, AUTH_TOKEN_3)
        models.Account.refresh()
        
    def tearDown(self):
        self._delete_account(AUTH_TOKEN_1)
        self._delete_account(AUTH_TOKEN_2)
        self._delete_account(AUTH_TOKEN_3)
        models.Account.refresh()
    
    def _make_account(self, name, register, stats, admin, token):
        acc = models.Account()
        acc.set_name(name)
        acc.allow_registry_access(register)
        acc.allow_statistics_access(stats)
        acc.allow_admin_access(admin)
        acc.set_auth_token(token)
        acc.save()
    
    def _delete_account(self, token):
        acc = models.Account.pull_by_auth_token(token)
        acc.delete()
    
    #########################################################
    ## Test for creating a register object
    #########################################################
    
    def test_01_01_create_register(self):
        # first, without an admin record, the most simple case
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            }
        }
        
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        
        # aggressively test the response object
        j = resp.json()
        loc = resp.headers["location"]
        
        assert "id" in j
        assert "success" in j
        assert "location" in j
        
        assert resp.status_code == 201, resp.status_code # HTTP Created
        assert loc is not None # Location header should be set
        assert loc.endswith(j["location"]) # location may be relative
        assert j["location"].endswith(j["id"]) # id is in the path
        assert j["success"] == "true"
    
    def test_01_02_create_admin_register(self):
        # now with an admin record which is correct for the account
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "some_key" : "some_value"
                }
            }
        }
        
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        
        # aggressively test the response object
        j = resp.json()
        loc = resp.headers["location"]
        
        assert "id" in j
        assert "success" in j
        assert "location" in j
        
        assert resp.status_code == 201, resp.status_code # HTTP Created
        assert loc is not None # Location header should be set
        assert loc.endswith(j["location"]) # location may be relative
        assert j["location"].endswith(j["id"]) # id is in the path
        assert j["success"] == "true"
    
    def test_01_03_unauthorised(self):
        # first, without an admin record, the most simple case
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            }
        }
        
        resp = requests.post(BASE_URL + "record?api_key=1234", json.dumps(reg))
        assert resp.status_code == 401
    
    def test_01_04_no_permission(self):
        # first, without an admin record, the most simple case
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            }
        }
        
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_2, json.dumps(reg))
        assert resp.status_code == 401
        
    def test_01_05_malformed(self):
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, "akdhfoiaeiq;{}")
        assert resp.status_code == 400
    
    def test_01_06_invalid_schema(self):
        # first, without an admin record, the most simple case
        reg = {
            "something" : "invalid"
        }
        
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        assert resp.status_code == 400
    
    ##########################################################
    # Tests for retrieving register objects
    ##########################################################
    
    def test_02_01_retrieve_register(self):
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 2",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "some_key" : "some_value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        
        loc = resp.headers["location"]
        ret = requests.get(loc)
        j = ret.json()
        
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 2"
        assert j.get("admin", {}).get("test1", {}).get("some_key") == "some_value"
    
    ##########################################################
    ## Tests for updating/patching a register object
    ##########################################################

    def test_03_01_update_register(self):
        # create the base version
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 3",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ],
                "api" : [
                    {
                        "api_type" : "oai-pmh",
                        "version" : "2.0"
                    }
                ],
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # now send the replacement
        reg2 = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 4",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ],
                "software" : [
                    {
                        "name" : "DSpace",
                        "version" : "2.0",
                        "url" : "http://www.dspace.org/2.0"
                    }
                ]
            }
        }
        resp = requests.post(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(reg2))
        
        # allow the index time to refresh
        time.sleep(2)
        
        # request the object
        ret = requests.get(loc)
        j = ret.json()
        
        # look to see that the resulting object is a merge of the two
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 4"
        assert j.get("register", {}).get("api", [{}])[0].get("api_type") == "oai-pmh"
        assert j.get("register", {}).get("software", [{}])[0].get("name") == "DSpace"
    
    def test_03_02_update_admin(self):
        # create the base version
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 3",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # now send the replacement
        reg2 = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 4",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "mykey" : "other value"
                }
            }
        }
        resp = requests.post(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(reg2))
        
        # allow the index time to refresh
        time.sleep(2)
        
        # request the object
        ret = requests.get(loc)
        j = ret.json()
        
        # check that the admin object has been fully overwritten
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 4"
        assert j.get("admin", {}).get("test1", {}).get("mykey") == "other value"
        assert "otherkey" not in j.get("admin", {}).get("test1", {})
    
    def test_03_03_other_admin(self):
        # create the base version
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 3",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # now send the replacement as a different user
        reg2 = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 4",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "mykey" : "other value"
                },
                "test3" : {
                    "myadmin" : "hereitis"
                }
            }
        }
        resp = requests.post(loc + "?api_key=" + AUTH_TOKEN_3, json.dumps(reg2))
        
        # allow the index time to refresh
        time.sleep(2)
        
        # request the object
        ret = requests.get(loc)
        j = ret.json()
        
        # check that the foreign admin object has been ignored but your new one has been imported
        assert j.get("admin", {}).get("test1", {}).get("mykey") == "my value", j
        assert j.get("admin", {}).get("test1", {}).get("otherkey") == "some value"
        assert j.get("admin", {}).get("test3", {}).get("myadmin") == "hereitis"
    
    ##########################################################
    ## Tests for overwriting a register object
    ##########################################################
    
    def test_04_01_replace_register(self):
        # create the base version
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 3",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ],
                "api" : [
                    {
                        "api_type" : "oai-pmh",
                        "version" : "2.0"
                    }
                ],
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # now send the replacement
        reg2 = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 4",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ],
                "software" : [
                    {
                        "name" : "DSpace",
                        "version" : "2.0",
                        "url" : "http://www.dspace.org/2.0"
                    }
                ]
            }
        }
        resp = requests.put(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(reg2))
        
        # allow the index time to refresh
        time.sleep(2)
        
        # request the object
        ret = requests.get(loc)
        j = ret.json()
        
        # look to see that the resulting object has overwritten the original object
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 4"
        assert "api" not in j.get("register", {}), j
        assert j.get("register", {}).get("software", [{}])[0].get("name") == "DSpace"
    
    def test_04_02_replace_admin(self):
        # create the base version
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 3",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # now send the replacement
        reg2 = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 4",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "mykey" : "other value"
                }
            }
        }
        resp = requests.put(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(reg2))
        
        # allow the index time to refresh
        time.sleep(2)
        
        # request the object
        ret = requests.get(loc)
        j = ret.json()
        
        # check that the admin object has been fully overwritten
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 4"
        assert j.get("admin", {}).get("test1", {}).get("mykey") == "other value"
        assert "otherkey" not in j.get("admin", {}).get("test1", {})
    
    def test_04_03_other_admin(self):
        # create the base version
        reg = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 3",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # now send the replacement as a different user
        reg2 = {
            "register" : {
                "metadata" : [
                    {
                        "lang" : "en",
                        "default" : True,
                        "record" : {
                            "name" : "My Repo 4",
                            "url" : "http://myrepo",
                            "repository_type" : ["Institutional"]
                        }
                    }
                ]
            },
            "admin" : {
                "test1" : {
                    "mykey" : "other value"
                },
                "test3" : {
                    "myadmin" : "hereitis"
                }
            }
        }
        resp = requests.put(loc + "?api_key=" + AUTH_TOKEN_3, json.dumps(reg2))
        
        # allow the index time to refresh
        time.sleep(2)
        
        # request the object
        ret = requests.get(loc)
        j = ret.json()
        
        # check that the foreign admin object has been ignored but your new one has been imported
        assert j.get("admin", {}).get("test1", {}).get("mykey") == "my value", j
        assert j.get("admin", {}).get("test1", {}).get("otherkey") == "some value"
        assert j.get("admin", {}).get("test3", {}).get("myadmin") == "hereitis"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

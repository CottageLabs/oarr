from unittest import TestCase
import requests, json, time
from portality import models
from datetime import datetime

BASE_URL = "http://localhost:5001/"
AUTH_TOKEN_1 = "feaf5347e4e94fe2b45cc51976879648"
AUTH_TOKEN_2 = "69013a52e8e14221b09b122b489ee87c"
AUTH_TOKEN_3 = "135ac0e2af78475eb8a915fbbe64dff9"
AUTH_TOKEN_4 = "b831f34f96d641ed8a8d517063b659af"
AUTH_TOKEN_5 = "34eb22acfc9d4eea8e18a9a28f896426"

class TestIntegration(TestCase):

    def setUp(self):
        self._make_account("test1", True, False, False, AUTH_TOKEN_1)
        self._make_account("test2", False, False, False, AUTH_TOKEN_2)
        self._make_account("test3", True, False, True, AUTH_TOKEN_3)
        self._make_account("test4", True, True, False, AUTH_TOKEN_4)
        self._make_account("test5", True, False, True, AUTH_TOKEN_5)
        models.Account.refresh()
        
    def tearDown(self):
        self._delete_account(AUTH_TOKEN_1)
        self._delete_account(AUTH_TOKEN_2)
        self._delete_account(AUTH_TOKEN_3)
        self._delete_account(AUTH_TOKEN_4)
        self._delete_account(AUTH_TOKEN_5)
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
        
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
        
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
        # now a couple of ways.  First, without any register access
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
        
        # next with register access but no admin access
        reg["admin"] = {
            "test1" : {
                "one" : "two"
            }
        }
        resp2 = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
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
        assert resp.status_code == 400, resp.status_code

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
                "test5" : {
                    "some_key" : "some_value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
        
        loc = resp.headers["location"]
        ret = requests.get(loc)
        j = ret.json()
        
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 2"
        assert j.get("admin", {}).get("test5", {}).get("some_key") == "some_value"
    
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
                "test5" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
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
                "test5" : {
                    "mykey" : "other value"
                }
            }
        }
        resp = requests.post(loc + "?api_key=" + AUTH_TOKEN_5, json.dumps(reg2))
        
        # allow the index time to refresh
        time.sleep(2)
        
        # request the object
        ret = requests.get(loc)
        j = ret.json()
        
        # check that the admin object has been fully overwritten
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 4"
        assert j.get("admin", {}).get("test5", {}).get("mykey") == "other value"
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
                "test5" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
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
                "test5" : {
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
        assert j.get("admin", {}).get("test5", {}).get("mykey") == "my value", j
        assert j.get("admin", {}).get("test5", {}).get("otherkey") == "some value"
        assert j.get("admin", {}).get("test3", {}).get("myadmin") == "hereitis"

    def test_03_04_overwrite_dates(self):
        # create an initial register
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

        # retrieve it
        loc = resp.headers["location"]
        ret = requests.get(loc)
        j = ret.json()

        # check that it has some dates
        cd = j.get("created_date")
        lm = j.get("last_updated")
        assert cd is not None
        assert lm is not None

        # try to overwrite these
        date_reg = {
            "created_date" : "2001-01-01T00:00:00Z",
            "last_updated" : "2002-01-01T00:00:00Z",
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

        resp = requests.post(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(date_reg))

        # allow the index time to refresh
        time.sleep(2)

        # request the object
        ret = requests.get(loc)
        j = ret.json()

        # check that it has some dates
        cd2 = j.get("created_date")
        lm2 = j.get("last_updated")
        assert cd is not None
        assert lm is not None

        # and check that the cd is the same as the original and the last modified is current
        assert cd2 == cd
        assert lm2 != "2002-01-01T00:00:00Z"

    def test_03_05_update_empty_admin(self):
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
                "test5" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
        loc = resp.headers["Location"]

        # now send the replacement with an empty admin record
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
                "test5" : {}
            }
        }
        resp = requests.post(loc + "?api_key=" + AUTH_TOKEN_5, json.dumps(reg2))

        # allow the index time to refresh
        time.sleep(2)

        # request the object
        ret = requests.get(loc)
        j = ret.json()

        # check that the admin object has been removed
        assert j.get("admin", {}).get("test5") is None

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
                "test5" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
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
                "test5" : {
                    "mykey" : "other value"
                }
            }
        }
        resp = requests.put(loc + "?api_key=" + AUTH_TOKEN_5, json.dumps(reg2))
        
        # allow the index time to refresh
        time.sleep(2)
        
        # request the object
        ret = requests.get(loc)
        j = ret.json()
        
        # check that the admin object has been fully overwritten
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 4"
        assert j.get("admin", {}).get("test5", {}).get("mykey") == "other value"
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
                "test5" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
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
                "test5" : {
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
        assert j.get("admin", {}).get("test5", {}).get("mykey") == "my value", j
        assert j.get("admin", {}).get("test5", {}).get("otherkey") == "some value"
        assert j.get("admin", {}).get("test3", {}).get("myadmin") == "hereitis"

    def test_04_04_overwrite_dates(self):
        # create an initial register
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

        # retrieve it
        loc = resp.headers["location"]
        ret = requests.get(loc)
        j = ret.json()

        # check that it has some dates
        cd = j.get("created_date")
        lm = j.get("last_updated")
        assert cd is not None
        assert lm is not None

        # try to overwrite these
        date_reg = {
            "created_date" : "2001-01-01T00:00:00Z",
            "last_updated" : "2002-01-01T00:00:00Z",
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
        resp = requests.put(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(date_reg))

        # allow the index time to refresh
        time.sleep(2)

        # request the object
        ret = requests.get(loc)
        j = ret.json()

        # check that it has some dates
        cd2 = j.get("created_date")
        lm2 = j.get("last_updated")
        assert cd is not None
        assert lm is not None

        # and check that the cd is the same as the original and the last modified is current
        assert cd2 == cd
        assert lm2 != "2002-01-01T00:00:00Z"

    def test_04_05_replace_empty(self):
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

        # now send the (empty) replacement
        reg2 = {}
        resp = requests.put(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(reg2))

        assert resp.status_code == 400

    def test_04_06_replace_empty_admin(self):
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
                "test5" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
        loc = resp.headers["Location"]

        # now send the replacement with an empty admin record
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
                "test5" : {}
            }
        }
        resp = requests.put(loc + "?api_key=" + AUTH_TOKEN_5, json.dumps(reg2))

        # allow the index time to refresh
        time.sleep(2)

        # request the object
        ret = requests.get(loc)
        j = ret.json()

        # check that the admin object has been removed
        assert j.get("admin", {}).get("test5") is None

    ##########################################################
    ## Tests for deleting a register object
    ##########################################################
    
    def test_05_01_delete(self):
        n = datetime.now()
        time.sleep(1)
        
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
            },
            "admin" : {
                "test5" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # issue the delete request
        resp2 = requests.delete(loc + "?api_key=" + AUTH_TOKEN_5)
        assert resp2.status_code == 200
        
        j = resp2.json()
        assert j.get("success") == "true"
        
        resp3 = requests.get(loc)
        j = resp3.json()
        assert j.get("register", {}).get("deleted") is not None
        
        d = j.get("register", {}).get("deleted")
        dt = datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ")
        assert dt >= n, (dt, n)
    
    def test_05_02_delete_fail(self):
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
        
        # issue the delete request
        resp2 = requests.delete(loc + "?api_key=" + AUTH_TOKEN_2)
        assert resp2.status_code == 401
    
    ##########################################################
    ## Tests on retrieving histories
    ##########################################################
    
    def test_06_01_no_history(self):
        # create a record
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
        loc = resp.headers["location"]
        
        # there should be no history entry for the record, as it is brand new
        resp2 = requests.get(loc + "/history")
        assert resp2.status_code == 404
    
    def test_06_02_merge_history(self):
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
        j = resp.json()
        id = j.get("id")
        assert id is not None
        
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
        resp2 = requests.post(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(reg2))
        
        # let the index catch up
        time.sleep(2)
        
        # request the history
        resp3 = requests.get(loc + "/history")
        j = resp3.json()
        
        assert len(j) == 1
        assert j[0].get("about") == id
        assert j[0].get("register", {}).get("api", [{}])[0].get("api_type") == "oai-pmh", j[0].get("register", {}).get("api", [{}])[0].get("api_type")
        assert "software" not in j[0].get("register", {"software" : None})
        
    def test_06_03_replace_history(self):
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
        j = resp.json()
        id = j.get("id")
        assert id is not None
        
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
        
        # request the history
        ret = requests.get(loc + "/history")
        j = ret.json()
        
        assert len(j) == 1
        assert j[0].get("about") == id
        assert j[0].get("register", {}).get("api", [{}])[0].get("api_type") == "oai-pmh", j[0].get("register", {}).get("api", [{}])[0].get("api_type")
        assert "software" not in j[0].get("register", {"software" : None})
    
    def test_06_04_delete_history(self):
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
                "test5" : {
                    "mykey" : "my value",
                    "otherkey" : "some value"
                }
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
        loc = resp.headers["Location"]
        j = resp.json()
        id = j.get("id")
        assert id is not None
        
        # issue the delete request
        resp2 = requests.delete(loc + "?api_key=" + AUTH_TOKEN_5)
        
        # give the index a moment to catch up
        time.sleep(2)
        
        # request the history
        ret = requests.get(loc + "/history")
        j = ret.json()
        
        assert len(j) == 1
        assert j[0].get("about") == id
        assert j[0].get("admin", {}).get("test5", {}).get("mykey") == "my value"
        
    def test_06_05_multi_history(self):
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
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_1, json.dumps(reg))
        loc = resp.headers["Location"]
        j = resp.json()
        id = j.get("id")
        
        # so that there's measurable difference in the timestamps
        time.sleep(1)
        
        # now send the replacement
        reg2 = {
            "register" : {
                "software" : [
                    {
                        "name" : "DSpace",
                        "version" : "2.0",
                        "url" : "http://www.dspace.org/2.0"
                    }
                ]
            }
        }
        resp2 = requests.post(loc + "?api_key=" + AUTH_TOKEN_1, json.dumps(reg2))
        
        # so that there's measurable difference in the timestamps
        time.sleep(1)
        
        # issue the delete request
        resp3 = requests.delete(loc + "?api_key=" + AUTH_TOKEN_1)
        
        # let the index catch up
        time.sleep(2)
        
        # request the history
        resp4 = requests.get(loc + "/history")
        j = resp4.json()
        
        # we should have two entries in the history table for this object
        assert len(j) == 2
        
        # check that the objects are date ordered
        newest = j[0]
        oldest = j[1]
        nd = datetime.strptime(newest.get("last_updated"), "%Y-%m-%dT%H:%M:%SZ")
        od = datetime.strptime(oldest.get("last_updated"), "%Y-%m-%dT%H:%M:%SZ")
        assert nd > od, (nd, od)
        
        assert oldest.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 3"
        assert "software" not in oldest.get("register", {"software" : {}})
        
        assert newest.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 3"
        assert newest.get("register", {}).get("software", [{}])[0].get("name") == "DSpace"
        
    ##################################################
    ## Test for creating and retrieving stats
    ##################################################
    
    def test_07_01_create_stat(self):
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
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_4, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # create the statistic
        stat = {
            "value" : "27",
            "type" : "record_count"
        }
        resp = requests.post(loc + "/stats?api_key=" + AUTH_TOKEN_4, json.dumps(stat))
        assert resp.status_code == 201
        sl = resp.headers["Location"]
        j = resp.json()
        assert j["success"] == "true"
        assert sl.endswith(j["id"])
        assert sl.endswith(j["location"])
    
    def test_07_02_create_retrieve_stats(self):
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
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_4, json.dumps(reg))
        loc = resp.headers["Location"]
        j = resp.json()
        record_id = j.get("id")
        
        # create the statistics
        stats = [
            { "value" : "10", "type" : "record_count", "date" : "2014-01-01T12:00:00Z"},
            { "value" : "20", "type" : "record_count", "date" : "2014-02-01"},
            { "value" : "30", "type" : "record_count", "date" : "2014-03-01T12:00:00Z"},
            { "value" : "50", "type" : "record_count", "date" : "2014-04-01"}
        ]
        
        ids = []
        for stat in stats:
            resp = requests.post(loc + "/stats?api_key=" + AUTH_TOKEN_4, json.dumps(stat))
            assert resp.status_code == 201
            j = resp.json()
            ids.append(j["id"])
            time.sleep(1)
        
        # give the index time to catch up
        time.sleep(1)
        
        # retrieve the statistics
        resp2 = requests.get(loc + "/stats")
        j = resp2.json()
        
        # check there are the right number of stats
        assert len(j) == 4
        
        # - are the stats in the right order?
        dates = [datetime.strptime(x.get("date"), "%Y-%m-%dT%H:%M:%SZ") for x in j]
        assert dates[0] > dates[1]
        assert dates[1] > dates[2]
        assert dates[2] > dates[3]
        
        # - do the stats all have the right properties?
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
        id2 = []
        for stat in j:
            id2.append(stat.get("id"))
            assert stat.get("id") in ids
            assert stat.get("about") == record_id
            assert stat.get("value") in [10.0, 20.0, 30.0, 50.0]
            assert stat.get("type") == "record_count"
            assert stat.get("third_party") == "test4"
        
        assert len(list(set(id2))) == 4
    
    def test_07_03_delete_stat(self):
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
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_4, json.dumps(reg))
        loc = resp.headers["Location"]
        
        # create the statistic
        stat = {
            "value" : "27",
            "type" : "record_count"
        }
        resp = requests.post(loc + "/stats?api_key=" + AUTH_TOKEN_4, json.dumps(stat))
        sl = resp.headers["Location"]
        
        # let the index catch up
        time.sleep(2)
        
        # issue a delete request
        resp3 = requests.delete(sl + "?api_key=" + AUTH_TOKEN_4)
        assert resp3.status_code == 200
        j = resp3.json()
        assert j.get("success") == "true"
    
    ##################################################
    ## Test for creating and retrieving admin data
    ##################################################
    
    def test_08_01_create_admin(self):
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
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
        loc = resp.headers["Location"]
        
        admin = {
            "akey" : "a value"
        }
        resp2 = requests.put(loc + "/admin?api_key=" + AUTH_TOKEN_5, json.dumps(admin))
        
        assert resp2.status_code == 200
        j = resp2.json()
        assert j.get("success") == "true"
        
        # give the index time to catch up
        time.sleep(2)
        
        resp3 = requests.get(loc)
        j = resp3.json()
        assert "admin" in j
        assert "test5" in j["admin"]
        assert j["admin"]["test5"]["akey"] == "a value"
    
    def test_08_02_replace_admin(self):
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
            }
        }
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN_5, json.dumps(reg))
        loc = resp.headers["Location"]
        
        admin = {
            "akey" : "a value"
        }
        resp2 = requests.put(loc + "/admin?api_key=" + AUTH_TOKEN_5, json.dumps(admin))
        
        # give the index time to catch up
        time.sleep(2)
        
        resp3 = requests.get(loc)
        j = resp3.json()
        assert "admin" in j
        assert "test5" in j["admin"]
        assert j["admin"]["test5"]["akey"] == "a value"
        
        admin2 = {
            "justthis" : "key"
        }
        resp4 = requests.put(loc + "/admin?api_key=" + AUTH_TOKEN_5, json.dumps(admin2))
        
        assert resp4.status_code == 200
        j = resp4.json()
        assert j.get("success") == "true"
        
        # give the index time to catch up
        time.sleep(2)
        
        resp5 = requests.get(loc)
        j = resp5.json()
        assert "admin" in j
        assert "test5" in j["admin"]
        assert j["admin"]["test5"]["justthis"] == "key"
        assert "akey" not in j["admin"]["test5"]
        
    
    
    
    
    

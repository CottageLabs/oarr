# TODO: this is where we actively fire stuff at the API, and check that it works

from unittest import TestCase
import requests, json, time

BASE_URL = "http://localhost:5001/"
AUTH_TOKEN = "05b70de7132545e5830dd3c8a8bfa25d"

class TestIntegration(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_01_create_register(self):
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
        
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN, json.dumps(reg))
        #print resp.headers["location"]
        #print resp.json()
        #print resp.status_code
        
        j = resp.json()
        loc = resp.headers["location"]
        assert resp.status_code == 201
        assert loc is not None
    
    def test_02_retrieve_register(self):
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
            }
        }
        
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN, json.dumps(reg))
        loc = resp.headers["location"]
        
        ret = requests.get(loc)
        j = ret.json()
        
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 2"
        
        
    def test_03_update_register(self):
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
        
        resp = requests.post(BASE_URL + "record?api_key=" + AUTH_TOKEN, json.dumps(reg))
        assert resp.status_code == 201
        
        loc = resp.headers["Location"]
        
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
        
        resp = requests.post(loc + "?api_key=" + AUTH_TOKEN, json.dumps(reg2))
        
        # allow the index time to catch up
        time.sleep(2)
        
        ret = requests.get(loc)
        j = ret.json()
        
        assert j.get("register", {}).get("metadata", [{}])[0].get("record", {}).get("name") == "My Repo 4"
        assert j.get("register", {}).get("api", [{}])[0].get("api_type") == "oai-pmh"
        assert j.get("register", {}).get("software", [{}])[0].get("name") == "DSpace"
        

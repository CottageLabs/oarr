from unittest import TestCase
from portality import models
from copy import deepcopy
from datetime import datetime
import time

_example1 = {
    "id" : "1234",
    "register": {
        "organisation": [
            {
                "details": {
                    "url": "http://denison.edu/",
                    "lat": 43.4079,
                    "lon": -73.2596,
                    "name": "Denison University"
                }
            }
        ],
        "operational_status": "Operational",
        "metadata": [
            {
                "lang": "en",
                "default": True,
                "record": {
                    "name": "DENISON Digital Resource Commons: Denison Virtual Earth Material Gallery",
                    "language": ["en"],
                    "url": "http://cdm15963.contentdm.oclc.org/cdm/landingpage/collection/p15963coll37",
                    "description": "This virtual gallery is a sampling of the upward of 9,000 specimens from the Denison Geosciences Earth materials collection",
                    "content_type": ["Multimedia and audio-visual materials"],
                    "repository_type": ["Institutional"],
                    "subject": [
                        {
                            "term": "Earth and Planetary Sciences",
                            "code": "Cam"
                        }
                    ]
                }
            }
        ]
    }
}

_example2 = {
    "register": {
        "api": [
            {
                "base_url": "http://epubs.rcsi.ie/do/oai/",
                "api_type": "oai-pmh"
            }
        ],
        "organisation": [
            {
                "details": {
                    "acronym": "RCSI",
                    "url": "http://www.rcsi.ie/",
                    "lat": 53.3389,
                    "name": "Royal College of Surgeons in Ireland",
                    "lon": -6.2619
                }
            }
        ],
        "operational_status": "Operational",
        "contact": [
            {
                "details": {
                    "email": "jbyrne@rcsi.ie",
                    "address": "Dublin 2",
                    "name": "Jenny Byrne",
                    "job_title": "Administrator"
                }
            }
        ],
        "policy": [
            {
                "policy_grade": "Content policies defined",
                "terms": [
                    "This is an institutional or departmental repository.",
                    "The repository is restricted to: ",
                    "Deposited items may include: ",
                    "Principal Languages: English",
                    "For more information, please see webpage: "
                ],
                "policy_type": "Content"
            },
            {
                "policy_grade": "Metadata re-use policy explicitly undefined",
                "terms": [
                    "No policy registered in OpenDOAR."
                ],
                "policy_type": "Metadata"
            }
        ],
        "metadata": [
            {
                "lang": "en",
                "default": True,
                "record": {
                    "name": "e-publications@RCSI",
                    "language": ["en"],
                    "url": "http://epubs.rcsi.ie/",
                    "description": "This repository is an open access repository of research and scholarly output from the Royal College of Surgeons",
                    "content_type": [
                        "Journal articles",
                        "Theses and dissertations"
                    ],
                    "repository_type": ["Institutional"],
                    "subject": [
                        {
                            "term": "Health and Medicine",
                            "code": "Ce"
                        }
                    ]
                }
            }
        ],
        "software": [
            {
                "name": "Digital Commons"
            }
        ]
    }
}

_example3 = {
    "id" : "1234",
    "register": {
        "metadata": [
            {
                "lang": "en",
                "default": True,
                "record": {
                    "name": "DENISON Digital Resource Commons: Denison Virtual Earth Material Gallery",
                    "language": ["en"],
                    "url": "http://cdm15963.contentdm.oclc.org/cdm/landingpage/collection/p15963coll37",
                }
            }
        ]
    },
    "admin" : {
        "tp" : {
            "some_key" : "some value"
        }
    }
}

class TestSchema(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_01_create_valid(self):
        reg = models.Register(_example1)
        
        # a few spot-checks just to make sure everything is ok
        register = reg.register
        assert register.get("operational_status") == "Operational"
        
        md = register.get("metadata")
        assert len(md) == 1
        
        en = md[0]
        rec = en.get("record")
        
        assert rec.get("name") == "DENISON Digital Resource Commons: Denison Virtual Earth Material Gallery"
    
    def test_02_replace(self):
        reg = models.Register(deepcopy(_example2))
        
        register = reg.register
        assert "api" in register
        assert register.get("metadata", [{}])[0].get("record", {}).get("name") == "e-publications@RCSI"
        
        reg.replace_register(deepcopy(_example1))
        
        register = reg.register
        assert "api" not in register
        assert register.get("metadata", [{}])[0].get("record", {}).get("name") == "DENISON Digital Resource Commons: Denison Virtual Earth Material Gallery"
    
    def test_03_overlay(self):
        reg = models.Register(deepcopy(_example2))
        
        register = reg.register
        assert "api" in register
        assert register.get("metadata", [{}])[0].get("record", {}).get("name") == "e-publications@RCSI"
        
        reg.merge_register(deepcopy(_example1))
        
        register = reg.register
        assert "api" in register
        assert register.get("metadata", [{}])[0].get("record", {}).get("name") == "DENISON Digital Resource Commons: Denison Virtual Earth Material Gallery"
    
    def test_04_snapshot(self):
        reg = models.Register(_example1)
        hist = reg.snapshot(write=False)
        
        assert "id" not in hist.data # we haven't saved it yet
        assert hist.data.get("about") == "1234" # the original id
        assert hist.data.get("register") is not None
        rec = hist.data.get("register")
        assert rec.get("metadata", [{}])[0].get("record", {}).get("name") == "DENISON Digital Resource Commons: Denison Virtual Earth Material Gallery"
    
    def test_05_soft_delete(self):
        n = datetime.now()
        time.sleep(1)
        
        reg = models.Register(_example3)
        reg.soft_delete()
        rec = reg.register
        
        assert rec.get("deleted") is not None # record marked as deleted
        assert "metadata" not in rec # metadata has gone
        assert reg.data.get("admin", {}).get("tp", {}).get("some_key") == "some value" # admin data remains
        
        d = rec.get("deleted")
        dt = datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ")
        
        assert dt >= n, (dt, n)
        
        


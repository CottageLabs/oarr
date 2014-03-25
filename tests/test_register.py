from unittest import TestCase
from portality import models
from copy import deepcopy

_example1 = {
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
        
        reg.replace_register(deepcopy(_example1.get("register")))
        
        register = reg.register
        assert "api" not in register
        assert register.get("metadata", [{}])[0].get("record", {}).get("name") == "DENISON Digital Resource Commons: Denison Virtual Earth Material Gallery"
    
    def test_03_overlay(self):
        reg = models.Register(deepcopy(_example2))
        
        register = reg.register
        assert "api" in register
        assert register.get("metadata", [{}])[0].get("record", {}).get("name") == "e-publications@RCSI"
        
        reg.merge_register(deepcopy(_example1.get("register")))
        
        register = reg.register
        assert "api" in register
        assert register.get("metadata", [{}])[0].get("record", {}).get("name") == "DENISON Digital Resource Commons: Denison Virtual Earth Material Gallery"


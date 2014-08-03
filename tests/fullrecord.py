"""
make a record which employs all of the fields in the register data model
and save it so we can do things like build interfaces on top of it
"""

record = {
    "last_updated" : "2014-05-11T17:12:45Z",
    "created_date" : "2014-03-01T19:43:08Z",

    "register" : {
        "replaces" : "info:oarr:123456789",
        "isreplacedby" : "info:oarr:987654321",
        "operational_status" : "Operational",

        "metadata" : [
            {
                "lang" : "en",
                "default" : True,
                "record" : {
                    "country" : "United Kingdom",
                    "country_code" : "GB",
                    "continent" : "Europe",
                    "continent_code" : "eu",
                    "twitter" : "@repotwit",
                    "acronym" : "MR@CL",
                    "description" : "The Cottage Labs repository full of all sorts of interesting things",
                    "established_date" : "2010",
                    "language" : ["English", "Norwegian"],
                    "language_code" : ["en", "no"],
                    "name" : "My Repository @ Cottage Labs",
                    "url" : "http://cottagelabs.com/news",
                    "subject" : [
                        {
                            "scheme" : "lcsh",
                            "term" : "Medicine",
                            "code" : "M23"
                        }
                    ],
                    "repository_type" : ["Institutional"],
                    "certification" : ["DINI", "RIOXX"],
                    "content_type" : ["Journal articles", "Reports"]
                }
            }
        ],
        "software" : [
            {
                "name" : "Portality",
                "version" : "0.8.1",
                "url" : "http://github.com/CottageLabs/portality"
            }
        ],
        "contact" : [
            {
                "role" : ["Administrator"],
                "details": {
                    "name" : "Richard Jones",
                    "email" : "richard@cottagelabs.com",
                    "address" : "123 The Cottage",
                    "fax": "01234 5678",
                    "phone": "09877 345762",
                    "lat" : 50.0,
                    "lon" : -4.0,
                    "job_title" : "Senior Partner"
                }
            },
            {
                "role" : ["Developer"],
                "details": {
                    "name" : "Mark MacGillivray",
                    "email" : "mark@cottagelabs.com",
                    "address" : "124 The Cottage",
                    "fax": "01234 5678",
                    "phone": "09877 345762",
                    "lat" : 50.0,
                    "lon" : -4.0,
                    "job_title" : "Senior Partner"
                }
            }
        ],
        "organisation" : [
            {
                "role" : ["developer"],
                "details" : {
                    "name" : "Cottage Labs",
                    "acronym" : "CL",
                    "url" : "http://cottagelabs.com",

                    "unit" : "Repo Unit",
                    "unit_acronym" : "RU",
                    "unit_url" : "http://cottagelabs.com/repounit",

                    "country" : "United Kingdom",
                    "country_code" : "GB",
                    "lat" : 50.0,
                    "lon" : -4.0
                }
            },
            {
                "role" : ["host"],
                "details" : {
                    "name" : "University of Nottingham",
                    "acronym" : "UoN",
                    "url" : "http://www.nottingham.ac.uk/",

                    "unit" : "Centre for Research Communication",
                    "unit_acronym" : "CRC",
                    "unit_url" : "http://www.sherpa.ac.uk",

                    "country" : "United Kingdom",
                    "country_code" : "GB",
                    "lat" : 50.0,
                    "lon" : -4.0
                }
            }
        ],
        "policy" : [
            {
                "terms": [
                    "This is an institutional or departmental repository.",
                    "The repository is restricted to: ",
                    "Principal Languages: Spanish; English",
                    "For more information, please see webpage: "
                ],
                "policy_type": "Content",
                "description" : "We'll do good stuff with the content"
            },
            {
                "terms": [
                    "Anyone may access the metadata free of charge.",
                    "The metadata may be re-used in any medium without prior permission for not-for-profit purposes",
                    "The metadata must not be re-used in any medium for commercial purposes without formal permission.",
                    "For more information, please see webpage: "
                ],
                "policy_type": "Metadata",
                "description" : "You can look at our metadata"
            },
            {
                "terms": [
                    "Anyone may access full items free of charge.",
                    "Single copies of full items can be: ",
                    "For more information see webpage: "
                ],
                "policy_type": "Data",
                "description" : "We like to give our data away"
            },
            {
                "terms": [
                    "No policy registered in OpenDOAR."
                ],
                "policy_type": "Submission",
                "description": "No policy yet, sorry"
            },
            {
                "terms": [
                    "No policy registered in OpenDOAR."
                ],
                "policy_type": "Preserve",
                "description" : "no policy yet, sorry"
            }
        ],
        "api" : [
            {
                "api_type" : "oai-pmh",
                "version" : "2.0",
                "base_url" : "http://cottagelabs.com/pmh",
                "metadata_formats" : [
                    {"prefix" : "oai_dc", "namespace" : "http://www.openarchives.org/OAI/2.0/oai_dc/", "schema" : "http://www.openarchives.org/OAI/2.0/oai_dc.xsd"},
                    {"prefix" : "marc", "namespace" : "http://www.loc.gov/MARC21/slim", "schema" : "http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd"}
                ]
            },
            {
                "api_type" : "sword",
                "version" : "2.0",
                "base_url" : "http://cottagelabs.com/swordv2",
                "authenticated" : True,
                "accepts" : ["application/zip"],
                "accept_packaging" : ["http://purl.net/sword/packaging/SimpleZip"],
            }
        ],
        "integration": [
            {
                "integrated_with" : "blog",
                "nature" : "blog is fed from repoisitory",
                "url" : "http://wordpress.com",
                "software" : "Wordpress",
                "version": "3.8"
            }
        ]
    },

    "admin" : {
        "opendoar" : {
            "date_added" : "2014-03-17T09:47:55Z",
            "in_opendoar" : True
        }
    }
}

from portality.models import Register
r = Register(record)
r.save()
print r.id
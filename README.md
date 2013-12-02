# Open Access Repository Registry

## Core Data Model

This represents the full dataset required to be captured for the registry.  It is not yet optimised for storage or searching, it's just a list of all the things that we need to know, and roughly how they relate to eachother.

    {
        "id" : "<opaque identifier for this repository>",
        "repository_type" : [<list of vocabulary terms for the repository>],
        "certification" : [<list of certifications held by this repository>],
        "status" : "<status flag for this record>",
        "metadata" : [
            {
                "lang" : "en",
                "default" : true|false
                "record" : {
                    "lat" : "<latitude of repository>",
                    "long" : "<logitude of repository>",
                    "country" : "<country repository resides in>",
                    "continent" : "<continent repository resides in>",
                    "twitter" : "<repository's twitter handle>",
                    "acronym" : "<repository name acronym>",
                    "description" : "<free text description of repository>",
                    "established_date" : "<date established!>",
                    "languages" : [<languages of content found in repo>],
                    "name" : "<name of repository>",
                    "url" : "<url for repository home page>",
                    "subjects" : ["<subject classifications for repository>"]
                }
            }
        ],
        "software" : [
            {
                "name" : "<name of software used to provide this repository>",
                "verson" : "<version of software used to provide this repository>"
            }
        ]
        "contact" : [
            {
                "role" : ["<contact role with regard to this repository>"]
                "details": {
                    "id" : "<unique id for this contact across all records>",
                    "name" : "<contact name>",
                    "email" : "<contact email>",
                    "address" : {
                        <details of address>
                    },
                    "fax": "<fax number of contact>",
                    "phone": "<phone number of contact>",
                    "lat" : "<latitude of contact location>",
                    "long" : "<longitude of contact location>"
                }
            }
        ],
        "organisation" : [
            {
                "role" : [<organisation roles with regard to this repository>],
                "details" : {
                    "id" : "<unique id for this organisation across all records>",
                    "name" : "<name of organisation>",
                    "address" : {
                        <details of address>
                    },
                    "acronym" : "<acronym of organisation>",
                    "lat" : "<latitude of organisation>",
                    "long" : "<longitude of organisation>"
                }
            }
        ]
        "policy" : [
            {
                "policy_type" : "<vocabulary term for policy>",
                "description" : "<description of policy terms, human readable>",
                "tags" : [<list of tags/vocabulary terms describing the policy>]
            }
        ],
        "api" : [
            {
                "api_type" : "<api type from known list or free text>",
                "version" : "<version of the API>",
                "base_url" : "<base url of API>",
                
                "metadata_prefixes" : [<list of supported prefixes>], # oai-pmh
                "accepts" : [<list of accepted mimetypes>], # sword
                "acceptPackaging" : [<list of accepted package formats>], #sword
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
        ],
        "statistics": [
            {
                "value" : "<the numerical statistic, whatever it is>",
                "type" : "<the type of statistic>",
                "date" : "<date the statistic was generated>",
                "provider" : "<system id that provided the statistic>"
            }
        ],
        "admin" : [
            {
                "third_party" : "<name of third party (e.g. opendoar)>",
                "note" : [
                    {
                        "date" : "<date of note>",
                        "message" : "<content of note>",
                        "by" : "<name of agent in third party posting the note>"
                    }
                ],
                "date_added" : "<date 3rd party approved record for inclusion>",
            }
        ]
        "history" : [
            "date" : "<date this history record was created>",
            "record" : {<historic version of the record>}
        ],
        "last_updated" : "<datestamp of last record modification>",
        "created_date" : "<datestamp of record creation time>"
    }

## Questions

* Where does the policy tool come in?

## Required Vocabularies

* Repository Types
* Contact Roles on Repository
* Policy Types
    * archiving, oa mandate, preservation, content, data, metadata, submission
* Policy Tags for each policy type
* Certifications
    * DINI
* API Type:
    * OAI-PMH, SWORD, ResourceSync, RSS, Atom
* Integration system:
    * CRIS
* Nature of integration:
    * deposit, upstream, downstream, authentication, dissemination, ...
* Types of statistic
    * all, fulltext, metadata only, preprint, postprint, data
* Organisation Roles on Repository
* Repository Subject classifications
    * LCC
* Status flags
    * suggested, malfunctioning, deleted, ...

# Open Access Repository Registry

## Usage of the Core Registry

The Core Repository has two distinct ways that it is used by client systems:

1. As a read-only source of data
2. As a read-write system for data retrieval and storage

### Read-Only

Read-only operations provide the following functions to the client:

* An endpoint for analytical queries against the dataset
* To access a full data dump
* To enable the client to filter by some administrative/workflow criteria (e.g. find only records which have been approved for inclusion in OpenDOAR)
* To enable the client to filter out fields that it is not interested in, to reduce the overall document size

As a read-only interface to data that is free to access, the following will be true of the use of the API:

1. There will be no authentication or authorisation requirements
2. No calls to the API will be able to change the data in any way
3. All administrative data from any third party system held by the registry will be available to any client

### Read-Write

The Read-Write operations are a super-set which subsume the Read-Only operations described above.  In addition to the Read-Only queries, the Read-Write operations provide the following functions to clients:

* An endpoint to add/update/delete metadata associated with a record in the registry
* An endpoint to add/delete statistical data associated with a record in the registry
* An endpoint to store client-specific information (such as whether a record is "approved" by that client; e.g. is a record in OpenDOAR)

As a read-write interface, the following will be true of the API:

1. Authentication is required - clients will need to be approved in advance to access these parts of the API
2. Authorisation is required - clients will be limited to specific pre-approved actions, which may differ per client
3. Calls to the API will be able to change the data, and this will change what all clients who use the API see

## Core Data Model

This represents the full dataset required to be captured for the registry.  It is not yet optimised for storage or searching, it's just a list of all the things that we need to know, and roughly how they relate to eachother.

    {
        "id" : "<opaque identifier for this repository>",
        "last_updated" : "<datestamp of last record modification>",
        "created_date" : "<datestamp of record creation time>",
        "version_created" : "<datestampe of when the current version of the object was created>",
        
        "replaces" : "<id of repository this one replaces>",
        "isreplacedby" : "<id of repository this one is replaced by>",
        
        "register" : {
            "operational_status" : "<status flag for this repository>",
            "repository_type" : [<list of vocabulary terms for the repository>],
            "certification" : [<list of certifications held by this repository>],
            "content_type" : [<list of vocabulary terms for the content in this repository>]
            
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
                    "verson" : "<version of software used to provide this repository>",
                    "url" : "<url for the software/this version of the software>"
                }
            ],
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
                    },
                    "created_date" : "<date this contact record was created>",
                    "last_modified" : "<date this contact record was last modified>"
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
                    },
                    "created_date" : "<date this contact record was created>",
                    "last_modified" : "<date this contact record was last modified>"
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
            ]
        },
        
        "statistics": [
            {
                "id" : "<opaque identifier for this statistical record>",
                "value" : "<the numerical statistic, whatever it is>",
                "type" : "<the type of statistic>",
                "date" : "<date the statistic was generated>",
                "third_party" : "<system id that provided the statistic>"
            }
        ],
        
        "admin" : [
            {
                "third_party" : "<name/id of third party (e.g. opendoar)>",
                "note" : [
                    {
                        "date" : "<date of note>",
                        "message" : "<content of note>",
                        "by" : "<name of agent in third party posting the note>",
                        "to" : "<contact details of user email composed to>"
                    }
                ],
                "date_added" : "<date 3rd party approved record for inclusion>",
                "in_opendoar" : true|false,
                "workflow" : "<pending|eligible|etc>"
            }
        ],
        
        "history" : [
            "date" : "<date this history record was created>",
            "record" : {<historic version of the record>}
        ]
    }

### Notes on the Core Data Model

* replaces/isreplacedby is not for versioning the record, it is for when another repository actually replaces the current one in the real world
* Everything in "register" is the metadata associated with a repository in the registry.  Everything outside that is either administrator or in some way otherwise related to third party supplied information
* The metadata field can hold multiple objects, and each object can be used to represent a different language of the metadata.  The record marked as "default" should be taken as the primary record, and if the record is requested in some other language, the record for that other language should be overlaid onto the default one.  In this way, fields which do not have translations fall back to the default language.
* Contacts may need to be stored separately, so that we can refer to them independently via their identifier, and list the repositories associated with them.  As such they have created and last modified dates associated with them.
* Organisations may need to be stored separately, so that we can refer to them independently via their identifier, and list the repositories associated with them.  As such they have created and last modified dates associated with them.
* Entries in the API field will always take the first three fields: api_type, version, base_url, but then depending on the specific API, extra details may also be provided
* The values in "admin" are examples which are relevant to OpenDOAR.  This part of the model will be extensible, and third parties may store whatever they need in here (within reason)
* "history" indicates that we will need to store some previous versions of the record.  They may be embedded in the main record, or stored separately or in another type in the index.  Note that we will only need to revision the part of the record in "registry" - the rest of the record is under control by external parties, and it is their responsibility to manage the content in the most appropriate way.

#### Questions

* Does the registry object itself require a "status" (which is different from "operational___status" which is to do with the repository itself, and different from a third party's approval of a registry entry as being correct)?  The reason for this might be that the registry itself has an administrator interface (i.e. _not_ OpenDOAR), which deals with operational concerns such as spam entries.  OTOH, perhaps OpenDOAR _is_ the administrator interface (and there could be others), and spam is dealt with by an aggregate of their considerations.

### A thought on data storage

It may be that we want to separate completely the core data of the registry (i.e. everything in "registry"), and the data managed by third parties.  We may even want to make third parties totally responsible for their workflows, although some of this information (such as statistics, or whether a record is "approved" by some third party such as OpenDOAR) could be relevant to _other_ third parties.


## Third Party Account Model

The third party account model describes the information we need to know about any client which has read-write access to the core registry.

    {
        "id" : "<opaque identifier for this third party>",
        "name" : "<human readable name for this third party>",
        "contact" : [
            {
                "name" : "<contact name>",
                "email" : "<contact email>"
            }
        ]
        "access" : {
            "registry" : true|false,
            "statistics" : true|false,
            "admin" : true|false
        }
        "admin_schema" : {<the admin schema used by this third party>},
        "auth_token" : "<account's API authentication token>",
    }

### Notes on the Third Party Account Model

* The third party has both an opaque identifier (assigned by the registry) and a human-readable name (assigned by the third party)
* Third parties may have multiple contacts
* The "access" object provides coarse-grained control over the rights the third party has
    * "registry" - the third party may create/modify/delete elements in the registry portion of the data model.  The registry will apply a schema to the data model which third parties must comply with
    * "statistics" - the third party may create/modify/delete statistics (it may only modify and delete statistics which it created).
    * "admin" - the third party may store administrative data in the registry.  It will only be able to write data to its own admin portion of the model
* "admin_schema" allows the third party to specify in advance the data it will store in the admin area of the registry.  Not sure yet how this will work, but it is to allow us to review whether the client is storing too much data, and will allow us to also reject any objects they supply us which do not meet these criteria

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
* Content Types
    * fulltext, metadata only, research archive, data archive, etc.

## API

All interactions with the registry should be via the API, and as many of the registry's features should be implemented as third parties which consume the API.  The API will be natively JSON, with other formats made available if necessary and time permitting.

API usage should be logged for statistical analysis at a later date.

### Record Access (Read-Only)

    GET /record/<id>

Get the whole record for the registry entry with the given ID.

### Discovery (Read-Only)

    GET /query?<params>

allowed params:

    es=<elasticsearch query object>
    q=<free text search>
    fields=<list of top level fields required>
    from=<start result number>
    size=<page size>

If there are no params provided, then the query endpoint will return everything with sensible defaults for page sizes

### Change List (Read-Only)

    GET /change?<params>

allowed params:

    from=<date to provide changes from>
    until=<date to provide changes until>
    
This lists all the records which have changed in the supplied time period.

There are a number of pre-existing options for this API endpoint, including ResourceSync, OAI-PMH and Atom.  These are all XML formats, which would place this endpoint at some odds with the rest of the API which will be JSON.

### Record Update (Read-Write)

    POST /record/<id> [registry object]

Send a full or partial registry object to the registry.  This will have the following effects:

* If the third party does not have the right to access the registry, the request will be rejected
* If the object violates the registry schema, the request will be rejected
* any fields that are provided will be overwritten on the target object
* any new fields will be added to the target object
* Any fields which are not mentioned will be left as-is
* The old version of the record will be stored

.

    PUT /record/<id> [registry object]

Send a replacement registry object to the registry.  This will have the following effects:

* If the third party does not have the right to access the registry, the request will be rejected
* All fields in the object which are considered to be part of the registry will be completely replaced.  This will not affect third-party specific aspects of the record, or statistics
* The old version of the record will be stored

The third party may use this method to remove data from the object, by sending a replacement object with fewer fields to replace the existing one.

.

    DELETE /record/<id> 

Send a request to remove the registry object.  This will have the following effects:

* If the third party does not have the right to access the registry, the request will be rejected
* The registry object will have all of its fields removed, but this will not affect third party data or statistics data
* The registry object will be marked as "withdrawn" until such time as new fields are added.  This provides a tombstone for deleted records.
* The old version of the record will be stored

.


### Provide Statistics (Read-Write)

    POST /record/<id>/stat [statistic record]

Send a new statistic to the registry from a third party which is calculating them.  This will have the following effects:

* If the third party does not have the right to access statistics, this request will be rejected
* The statistic will be added to the registry object, attributed to the third party
* The statistic will receive an ID which will be returned to the client in the response

.

    DELETE /record/<id>/stat/<stat_id>
    
Remove any statistic which was created by the third party with the given statistic identifier.  This will have the following effects:

* If the third party does not have the right to access statistics, this request will be rejected
* Any statistic attributed to the third party which has the given id will be removed from the registry object
* No record of the statistic will be kept


### Provide Third Party-Specific Data (Read-Write)

    PUT /record/<id>/admin [full admin record]

Provide a complete new admin record for the authenticating third party.  This will have the following effects:

* If the third party does not have the right to access admin, this request will be rejected
* If the third party attempts to add fields which are not registered as being allowed by their schema, this request will be rejected as a whole
* The existing admin record for the third party will be completely replaced with the new record.  All previous values will be lost.
* No new version of the item will be created - third parties must maintain their own revision history if they desire

## Index Structure

FIXME: Use this section to work out what the index in the core actually looks like, and what bits of data are dependent on other bits during update/delete/etc.

## Discovery Interface

The registry will provide a Discovery Interface as a third party read-only module.  This interface needs to provide the following features:

### Faceted Search/Browse

This should provide any advanced search functionality, as well as appropriately chosen facets.  Facets will include:

* Any field in the registry record which is represented by a term from a controlled vocabulary
* by continent
* by country
* by software
* by repository type
* by operational status
* by content type
* by language
* by subjects
* by any of the policy types (e.g. metadata, content, preservation, etc)

It should also be possible to view the search results both as a textual/tabular list of results, or plotted onto a map.

### Graphical Views

The graphical views on the content will provide statistical analysis of the content in the registry.  We will want to be able to provide statistics in all of the above facets as graphs.


## Native Third Party Modules

There are a number of third party modules that we could consider developing during the course of this project.  They are

### The Harvest Module

This would query repositories for known endpoints and useful locations of information (such as known OAI-PMH url patterns), and look for the registry file that this project will propose repositories be able to supply.

It would primarily know how to query DSpace and EPrints, and the following approaches could be used

#### DSpace

* Look for dspace-* webapps, and other url patters such as oai, sword2, sword2/service-document, etc
* Extract administrator data from oai Identify requests and sword service document requests
* Look for the registry file in a known location

#### EPrints

* Look for known url patterns
* Extract adminsitrator data from oai Identify requests and sword service document requests
* Look for the registry file in a known location
* Look at EPrints CGI file for details about the repository

### The ROAR Sync Module

This would periodically query ROAR and attempt to locate repositories which are new or which have changed since the last request

### The Suggest Module

A User Interface which allows end-users to suggest a repository for inclusion into the registry.  This may be deployed closely aligned with the Discovery Interface, although could still be a stand-alone third party module.

### Link-Checker Module

A bot which scans the entire contents of the registry periodically, attempts to resolve links, and reports back if failures are found.

## Questions

* Where does the policy tool come in?
* There is significant complexity in the auth model.  An alternative is to much more tighly control who the 3rd parties allowed to interact are, although this would limit us from reaching all of the requirements.
* There is a lot to think about wrt the Read-Write API - since the records are hierarchical, it will be difficult to devise an update/patch operation which works properly and as intended.  May be the case that we re-think how updates are actually carried out
* What exactly is DINI/Repository Certification?  Is this to do with metadata profiles the repository supports?  (e.g. RIOXX)


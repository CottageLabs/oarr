from esprit import mappings

# ========================
# MAIN SETTINGS

# make this something secret in your overriding app.cfg
SECRET_KEY = "default-key"

# contact info
ADMIN_NAME = "Cottage Labs LLP"
ADMIN_EMAIL = "us@cottagelabs.com"

# service info
SERVICE_NAME = "OARR"
SERVICE_TAGLINE = "Open Access Repository Registry"
HOST = "0.0.0.0"
DEBUG = True
PORT = 5001

# elasticsearch settings
ELASTIC_SEARCH_HOST = "http://127.0.0.1:9200" # remember the http:// or https://
ELASTIC_SEARCH_DB = "oarr"
INITIALISE_INDEX = True # whether or not to try creating the index and required index types on startup

# list of superuser account names
# FIXME: port role-based authorisations when necessary
SUPER_USER = []

# Can people register publicly? If false, only the superuser can create new accounts
PUBLIC_REGISTER = False

# can anonymous users get raw JSON records via the query endpoint?
PUBLIC_ACCESSIBLE_JSON = True 


# ========================
# MAPPING SETTINGS

# a dict of the ES mappings. identify by name, and include name as first object name
# and identifier for how non-analyzed fields for faceting are differentiated in the mappings
FACET_FIELD = ".exact"

MAPPINGS = {
    "account" : mappings.for_type("account", mappings.dynamic_templates([mappings.EXACT])),
    "register" : mappings.for_type("register", mappings.dynamic_templates([mappings.EXACT])),
    "statistics" : mappings.for_type("statistics", mappings.dynamic_templates([mappings.EXACT])),
    "history" : mappings.for_type("history", mappings.dynamic_templates([mappings.EXACT]))
}

# ========================
# QUERY SETTINGS

# list index types that should not be queryable via the query endpoint
NO_QUERY = ['account']

# list additional terms to impose on anonymous users of query endpoint
# for each index type that you wish to have some
# must be a list of objects that can be appended to an ES query.bool.must
# for example [{'term':{'visible':True}},{'term':{'accessible':True}}]
ANONYMOUS_SEARCH_TERMS = {
#    "pages": [{'term':{'visible':True}},{'term':{'accessible':True}}]
}

# a default sort to apply to query endpoint searches
# for each index type that you wish to have one
# for example {'created_date' + FACET_FIELD : {"order":"desc"}}
DEFAULT_SORT = {
#    "pages": {'created_date' + FACET_FIELD : {"order":"desc"}}
}


# ========================
# MEDIA SETTINGS

# location of media storage folder
MEDIA_FOLDER = "media"


# ========================
# PAGEMANAGER SETTINGS

# folder name for storing page content
# will be added under the templates/pagemanager route
CONTENT_FOLDER = "content"

# etherpad endpoint if available for collaborative editing
COLLABORATIVE = 'http://localhost:9001'

# when a page is deleted from the index should it also be removed from 
# filesystem and etherpad (if they are available in the first place)
DELETE_REMOVES_FS = False # True / False
DELETE_REMOVES_EP = False # MUST BE THE ETHERPAD API-KEY OR DELETES WILL FAIL

# disqus account shortname if available for page comments
COMMENTS = ''


# ========================
# HOOK SETTINGS

REPOS = {
    "portality": {
        "path": "/opt/portality/src/portality"
    },
    "content": {
        "path": "/opt/portality/src/portality/portality/templates/pagemanager/content"
    }
}

# ========================
# FEED SETTINGS

BASE_URL = "http://portality.com"

# Maximum number of feed entries to be given in a single response.  If this is omitted, it will
# default to 20
MAX_FEED_ENTRIES = 20

# Maximum age of feed entries (in seconds) (default value here is 3 months).  If this is omitted
# then we will always supply up to the MAX_FEED_ENTRIES above
MAX_FEED_ENTRY_AGE = 7776000

# Which index to run feeds from
FEED_INDEX = "Pages"

# Licensing terms for feed content
FEED_LICENCE = "(c) Cottage Labs LLP 2012.  All content Copyheart: http://copyheart.org"

# name of the feed generator (goes in the atom:generator element)
FEED_GENERATOR = "CottageLabs feed generator"

# Larger image to use as the logo for all of the feeds
FEED_LOGO = "http://cottagelabs.com/media/cottage_hill_bubble_small.jpg"


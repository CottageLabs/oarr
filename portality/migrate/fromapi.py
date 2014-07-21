import requests, HTMLParser, csv, json, os
from lxml import etree
import StringIO
from portality import models
from incf.countryutils import transformations # need this for continents data
import pycountry

BASE_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

h = HTMLParser.HTMLParser()

policy_map_path = os.path.join(BASE_FILE_PATH, "..", "..", "policy_terms_normalised.csv")
reader = csv.reader(open(policy_map_path))
policy_map = {}
instruction_map = {}
first = True
for row in reader:
    if first:
        first = False
        continue

    # see if there's a mapping from an old to new, if so record it
    old = row[0]
    new = row[3]
    if new is not None and new.strip() != "":
        policy_map[old.strip()] = new.strip()
        continue

    # see if there's a special instruction
    instruction = row[1]
    if instruction is not None and instruction.strip() != "":
        instruction_map[old.strip()] = instruction.strip()
        parts = instruction.split(":")
        continue

    # see if we should just keep the existing thing
    keep = row[2]
    if keep.lower() == "keep":
        policy_map[old.strip()] = old.strip()

"""
resp = requests.get("http://opendoar.org/api13.php?all=y&show=max")
# do something to convert the request into a stream reader, like use StringIO
f = StringIO.StringIO(resp.text)
"""

path = os.path.join(BASE_FILE_PATH, "..", "..", "opendoar.xml")
f = open(path)
xml = etree.parse(f)
root = xml.getroot()
repos = root.find("repositories")

def _extract(repo, field, target_dict, target_field, unescape=False, lower=False, cast=None, aslist=False, append=False, prepend=None):
    el = repo.find(field)
    if el is not None:
        val = el.text
        if val is not None:
            if prepend is not None:
                val = prepend + val
            if unescape:
                val = h.unescape(val)
            if lower:
                val = val.lower()
            if cast is not None:
                val = cast(val)
            if aslist:
                val = [val]

            if append:
                target_dict[target_field] += val
            else:
                target_dict[target_field] = val

def _apply(obj, stack, cursor, value):
    field = stack[cursor]
    if isinstance(obj, list):
        for o in obj:
            _apply(o, stack, cursor, value)
        return
    elif isinstance(obj, dict):
        if cursor + 1 > len(stack) - 1:
            obj[field] = value
        else:
            o = obj.get(field)
            _apply(o, stack, cursor + 1, value)
        return
    else:
        return

def migrate_repo(repo):
    # the various components we need to assemble
    opendoar = {}
    metadata = {}
    organisation = {}
    contacts = []
    apis = []
    statistics = {}
    register = {}
    software = {}
    policies = []

    # a record of the patches to be applied to the data (mostly come from the policy data)
    patches = []
    
    # original opendoar id
    odid = repo.get("rID")
    if odid is not None:
        opendoar["rid"] = odid
    
    # repository name
    _extract(repo, "rName", metadata, "name", unescape=True)
    
    # repository acronym
    _extract(repo, "rAcronym", metadata, "acronym", unescape=True)
    
    # repository url
    _extract(repo, "rUrl", metadata, "url")
    
    # oai base url
    oai = {"api_type" : "oai-pmh"}
    _extract(repo, "rOaiBaseUrl", oai, "base_url")
    if "base_url" in oai:
        apis.append(oai)
    
    # organisational details
    _extract(repo, "uName", organisation, "unit", unescape=True)
    _extract(repo, "uAcronym", organisation, "unit_acronym", unescape=True)
    _extract(repo, "uUrl", organisation, "unit_url")
    _extract(repo, "oName", organisation, "name", unescape=True)
    _extract(repo, "oAcronym", organisation, "acronym", unescape=True)
    _extract(repo, "oUrl", organisation, "url")
    _extract(repo, "paLatitude", organisation, "lat", cast=float)
    _extract(repo, "paLongitude", organisation, "lon", cast=float)
    
    cel = repo.find("country")
    _extract(cel, "cIsoCode", metadata, "country_code", lower=True)
    _extract(cel, "cIsoCode", organisation, "country_code", lower=True)

    isocode = cel.find("cIsoCode")
    if isocode is not None:
        code = isocode.text
        if code is not None and code != "":
            try:
                # specify the continent in the metadata
                continent_code = transformations.cca_to_ctca2(code)
                metadata["continent_code"] = continent_code.lower()
                continent = transformations.cca_to_ctn(code)
                metadata["continent"] = continent

                # normalised country name
                country = pycountry.countries.get(alpha2=code.upper()).name
                metadata["country"] = country
                organisation["country"] = country
            except KeyError:
                pass
    
    # repository description
    _extract(repo, "rDescription", metadata, "description", unescape=True)
    
    # remarks
    _extract(repo, "rRemarks", metadata, "description", unescape=True, append=True, prepend="  ")
    
    # statistics
    _extract(repo, "rNumOfItems", statistics, "value", cast=int)
    _extract(repo, "rDateHarvested", statistics, "date")
    
    # established date
    _extract(repo, "rYearEstablished", metadata, "established_date")
    
    # repository type
    _extract(repo, "repositoryType", metadata, "repository_type", aslist=True)
    
    # operational status
    _extract(repo, "operationalStatus", register, "operational_status")
    
    # software
    _extract(repo, "rSoftWareName", software, "name", unescape=True)
    _extract(repo, "rSoftWareVersion", software, "version")
    
    # subject classifications
    classes = repo.find("classes")
    if classes is not None:
        metadata["subject"] = []
        for c in classes:
            subject = {}
            _extract(c, "clCode", subject, "code")
            _extract(c, "clTitle", subject, "term", unescape=True)
            metadata["subject"].append(subject)
    
    # languages
    langs = repo.find("languages")
    if langs is not None:
        metadata["language_code"] = []
        metadata["language"] = []
        for l in langs:
            code = l.find("lIsoCode")
            if code is not None and code.text != "":
                lc = code.text.lower()
                lang = pycountry.languages.get(alpha2=lc).name
                metadata["language_code"].append(lc)
                metadata["language"].append(lang)
    
    # content types
    ctel = repo.find("contentTypes")
    if ctel is not None:
        metadata["content_type"] = []
        for ct in ctel:
            metadata["content_type"].append(ct.text)
    
    # policies
    polel = repo.find("policies")
    for p in polel:
        policy = {}
        _extract(p, "policyType", policy, "policy_type")
        posel = p.find("poStandard")
        if posel is not None:
            policy["terms"] = []
            for item in posel:
                t = item.text.strip()

                # only keep terms which have mappings in the policy map
                mapped = policy_map.get(t)
                if mapped is not None:
                    policy["terms"].append(mapped)

                # look for any special instructions on the term
                patch = instruction_map.get(t)
                if patch is not None:
                    patches.append(patch)

        if len(policy.get("terms", [])) > 0:
            policies.append(policy)
    
    # contacts
    conel = repo.find("contacts")
    for contact in conel:
        cont_details = {}
        _extract(contact, "pName", cont_details, "name", unescape=True)
        _extract(contact, "pJobTitle", cont_details, "job_title", unescape=True)
        _extract(contact, "pEmail", cont_details, "email")
        _extract(contact, "pPhone", cont_details, "phone")
        
        has_phone = contact.find("pPhone") is not None and contact.find("pPhone").text is not None
        
        # add the top level repo data about address and phone
        _extract(repo, "postalAddress", cont_details, "address", unescape=True)
        if not has_phone:
            _extract(repo, "paPhone", cont_details, "phone")
        _extract(repo, "paFax", cont_details, "fax")

        # we also add the top level stuff about lat/lon
        if organisation.get("lat") is not None:
            cont_details["lat"] = organisation.get("lat")
        if organisation.get("lon") is not None:
            cont_details["lon"] = organisation.get("lon")

        # record the job title as the contact role for the time being
        full_record = {"details" : cont_details}
        _extract(contact, "pJobTitle", full_record, "role", unescape=True, aslist=True)
        
        contacts.append(full_record)

    # now assemble the object
    register["metadata"] = [
        {
            "lang" : "en",
            "default" : True,
            "record" : metadata
        }
    ]

    if len(software.keys()) > 0:
        register["software"] = [software]
    if len(contacts) > 0:
        register["contact"] = contacts
    if len(organisation.keys()) > 0:
        register["organisation"] = [{"details" : organisation, "role" : ["host"]}] # add a default role
    if len(policies) > 0:
        register["policy"] = policies
    if len(apis) > 0:
        register["api"] = apis
    
    opendoar["in_opendoar"] = True
    
    record = {
        "register" : register,
        "admin" : {
            "opendoar" : opendoar
        }
    }
    
    statistics["third_party"] = "opendoar"
    statistics["type"] = "item_count"

    # apply any additional field patches
    for patch in patches:
        segments = patch.split("||")
        for s in segments:
            parts = s.split(":", 1)
            field = parts[0]
            try:
                value = json.loads(parts[1])
            except ValueError:
                value = parts[1]
            stack = field.split(".")
            _apply(record, stack, 0, value)

    return record, [statistics]

for repo in repos:
    record, stats = migrate_repo(repo)
    print record
    print stats
    r = models.Register(record)
    r.save()
    about = r.id
    for stat in stats:
        stat["about"] = about
        s = models.Statistics(stat)
        s.save()
    
    
"""
Full record structure

<repository rID="2891">
    <rName>&quot;Ergani - Historical Archive of Aegean&quot; Repository</rName>
    <rAcronym/>
    <rNamePreferred>Y</rNamePreferred>
    <rUrl>http://www.ergani-repository.gr/</rUrl>
    <rOaiBaseUrl>http://www.ergani-repository.gr/ergani-oai/</rOaiBaseUrl>
    <uName/>
    <uAcronym/>
    <uNamePreferred/>
    <uUrl/>
    <oName>Hellenic National Documentation Centre</oName>
    <oAcronym/>
    <oNamePreferred>Y</oNamePreferred>
    <oUrl>http://www.ekt.gr/</oUrl>
    <postalAddress>48 Vassileos, Constantinou Av, GR-11635, Athens</postalAddress>
    <country>
        <cIsoCode>GR</cIsoCode>
        <cCountry>Greece</cCountry>
    </country>
    <paLatitude>37.967000</paLatitude>
    <paLongitude>23.746100</paLongitude>
    <paPhone>+30 210 7273900-3</paPhone>
    <paFax>+30 210 7246824</paFax>
    <rDescription/>
    <rRemarks/>
    <rNumOfItems>1574</rNumOfItems>
    <rDateHarvested>2014-01-30</rDateHarvested>
    <rYearEstablished/>
    <repositoryType>Governmental</repositoryType>
    <operationalStatus>Closed</operationalStatus>
    <rSoftWareName>DSpace</rSoftWareName>
    <rSoftWareVersion/>
    <classes>
        <class>
            <clCode>Cok</clCode>
            <clTitle>History and Archaeology</clTitle>
        </class>
        <class>
            <clCode>Cu</clCode>
            <clTitle>Social Sciences General</clTitle>
        </class>
    </classes>
    <languages>
        <language>
            <lIsoCode>el</lIsoCode>
            <lName>Greek</lName>
        </language>
        <language>
            <lIsoCode>en</lIsoCode>
            <lName>English</lName>
        </language>
    </languages>
    <contentTypes>
        <contentType ctID="7">Unpublished reports and working papers</contentType>
        <contentType ctID="11">Multimedia and audio-visual materials</contentType>
        <contentType ctID="14">Other special item types</contentType>
    </contentTypes>
    <policies>
        <policy>
            <policyType potID="1">Content</policyType>
            <policyGrade pogID="1">Content policies unknown</policyGrade>
            <poStandard>
                <item>No policy registered in OpenDOAR.</item>
            </poStandard>
        </policy>
        <policy>
            <policyType potID="2">Metadata</policyType>
            <policyGrade pogID="6">Metadata policies unknown</policyGrade>
            <poStandard>
                <item>No policy registered in OpenDOAR.</item>
            </poStandard>
        </policy>
        <policy>
            <policyType potID="3">Data</policyType>
            <policyGrade pogID="13">Full data item policies unknown</policyGrade>
            <poStandard>
                <item>No policy registered in OpenDOAR.</item>
            </poStandard>
        </policy>
        <policy>
            <policyType potID="4">Submission</policyType>
            <policyGrade pogID="22">Submission policies unknown</policyGrade>
            <poStandard>
                <item>No policy registered in OpenDOAR.</item>
            </poStandard>
        </policy>
        <policy>
            <policyType potID="5">Preserve</policyType>
            <policyGrade pogID="27">Preservation policies unknown</policyGrade>
            <poStandard>
                <item>No policy registered in OpenDOAR.</item>
            </poStandard>
        </policy>
    </policies>
    <contacts>
        <person>
            <pName>Despina Hardouveli</pName>
            <pJobTitle>Administrator</pJobTitle>
            <pEmail>dxardo@ekt.gr</pEmail>
            <pPhone/>
        </person>
        <person>
            <pName>Nikos Houssos</pName>
            <pJobTitle>Suggester</pJobTitle>
            <pEmail>nhoussos@ekt.gr</pEmail>
            <pPhone/>
        </person>
    </contacts>
</repository>
"""

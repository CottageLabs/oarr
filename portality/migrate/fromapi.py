import requests, HTMLParser
from lxml import etree
import StringIO
from portality import models

h = HTMLParser.HTMLParser()

"""
resp = requests.get("http://opendoar.org/api13.php?all=y&show=max")

# do something to convert the request into a stream reader, like use StringIO

f = StringIO.StringIO(resp.text)
"""

path = "opendoar.xml"
f = open(path)

xml = etree.parse(f)
root = xml.getroot()
repos = root.find("repositories")

def _extract(repo, field, target_dict, target_field, unescape=False, lower=False, cast=None, aslist=False):
    el = repo.find(field)
    if el is not None:
        val = el.text
        if val is not None:
             if unescape:
                val = h.unescape(val)
             if lower:
                val = val.lower()
             if cast is not None:
                val = cast(val)
             if aslist:
                val = [val]
             target_dict[target_field] = val

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
    _extract(repo, "cIsoCode", organisation, "country", lower=True)
    
    # repository description
    _extract(repo, "rDescription", metadata, "description", unescape=True)
    
    # remarks
    _extract(repo, "rRemarks", opendoar, "remarks", unescape=True)
    
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
        metadata["language"] = []
        for l in langs:
            code = l.find("lIsoCode")
            metadata["language"].append(code.text)
    
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
        _extract(p, "policyGrade", policy, "policy_grade")
        posel = p.find("poStandard")
        if posel is not None:
            policy["terms"] = []
            for item in posel:
                policy["terms"].append(item.text)
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
        
        contacts.append(cont_details)

    # now assemble the object
    register["metadata"] = [
        {
            "lang" : "en",
            "default" : True,
            "record" : metadata
        }
    ]
    register["software"] = [software]
    register["contact"] = [{"details" : c} for c in contacts]
    register["organisation"] = [{"details" : organisation}]
    register["policy"] = policies
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

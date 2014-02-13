import requests, HTMLParser
from lxml import etree

h = HTMLParser.HTMLParser()

resp = requests.get("http://opendoar.org/api13.php?all=y&show=max")

# do something to convert the request into a stream reader, like use StringIO

xml = etree.parse(f)
root = xml.getroot()
repos = root.find("repositories")

def _extract(repo, field, target_dict, target_field, unescape=False):
    el = repo.find(field)
    if el is not None:
        val = el.text
        if val is not None:
             if unescape:
                val = h.unescape(val)
             target_dict[target_field] = val

for repo in repos:
    # register for opendoar specific third-party data
    opendoar = {}
    metadata = {}
    organisation = {}
    apis = []
    
    # original opendoar id
    odid = repo.get("rID")
    if odid is not None:
        opendoar["rid"] = odid
    
    # repository name
    _extract(repo, "rName", metadata, "name", True)
    
    # repository acronym
    _extract(repo, "rAcronym", metadata, "acronym", True)
    
    # repository url
    _extract(repo, "rUrl", metadata, "url")
    
    # oai base url
    oai = {"api_type" : "oai-pmh"}
    _extract(repo, "rOaiBaseUrl", oai, "base_url")
    if "base_url" in oai:
        apis.append(oai)
    
    
    
    

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

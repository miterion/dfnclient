from suds.client import Client
from suds import null
from hashlib import sha1

from base64 import b64decode


def submit_request(req, fqdn, altnames, profile, pin, applicant, mail, unit,
                   raid, testserver, onlyreqnumber=False, **kwargs):
    pin_hashed = sha1(str(pin).encode()).hexdigest()
    if testserver:
        cl = Client(
            'https://pki.pca.dfn.de/test-eins-ca/cgi-bin/pub/soap?wsdl=1')
    else:
        cl = Client(
            'https://pki.pca.dfn.de/dfn-ca-global-g2/cgi-bin/pub/soap?wsdl=1')
    alt_type = cl.factory.create('ArrayOfString')
    alt_type._arrayType = "ns0:string[1]"
    req_number = cl.service.newRequest(
        RaID=raid,
        PKCS10=req,  # Certificate Signing Request
        AltNames=alt_type,  # Altnames
        Role=profile,
        Pin=pin_hashed,
        AddName=applicant,
        AddEMail=mail,
        AddOrgUnit=unit,
        Publish=True,  # publish cert
    )
    print('The request number is: {}'.format(req_number))
    if onlyreqnumber:
        return
    pdf = cl.service.getRequestPrintout(
        RaID=raid, Serial=req_number, Format='application/pdf', Pin=pin_hashed)
    with open('{}.pdf'.format(fqdn), 'wb') as f:
        f.write(b64decode(pdf))

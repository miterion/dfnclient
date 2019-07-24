from subprocess import run, CalledProcessError
from sys import exit

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from termcolor import cprint


def gen_csr_with_new_cert(fqdn, subject, password, altnames=None):
    key = rsa.generate_private_key(
        public_exponent=65537, key_size=4096, backend=default_backend())
    with open('{}.key'.format(fqdn), 'wb') as f:
        if password:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.BestAvailableEncryption(
                        password.encode()),
                ))
        else:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                ))

    return generate_csr(key, fqdn, subject, altnames)


def gen_csr_with_existing_cert(key_path,
                               fqdn,
                               subject,
                               additional=None,
                               password=None):
    key = None
    with open(key_path, 'rb') as f:
        key = serialization.load_pem_private_key(f.read(), password,
                                                 default_backend())
    return generate_csr(key, fqdn, subject, additional)


# Helper function


def generate_csr(key, fqdn, subject, altnames=None):
    csr = x509.CertificateSigningRequestBuilder().subject_name(
        x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, subject['country']),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,
                               subject['state']),
            x509.NameAttribute(NameOID.LOCALITY_NAME, subject['city']),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject['org']),
            x509.NameAttribute(NameOID.COMMON_NAME, subject['cn']),
        ]))
    if altnames != None:
        csr = csr.add_extension(
            x509.SubjectAlternativeName(
                [x509.DNSName(domain) for domain in altnames]),
            critical=False,
        )
    csr = csr.sign(key, hashes.SHA256(), default_backend())
    with open('{}.req'.format(fqdn), 'wb') as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
    return csr.public_bytes(serialization.Encoding.PEM).decode()

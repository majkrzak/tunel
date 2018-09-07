from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID


def gen_csr(key: EllipticCurvePrivateKey, domain: str) -> bytes:
	return x509.CertificateSigningRequestBuilder().subject_name(
		x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, domain)])
	).sign(key, SHA256(), default_backend()).public_bytes(Encoding.DER)

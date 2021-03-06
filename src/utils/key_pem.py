from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKeyWithSerialization
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat


def key_pem(key: EllipticCurvePrivateKeyWithSerialization) -> str:
	return key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()).decode()

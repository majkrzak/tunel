from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1, generate_private_key
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption


def gen_ecc() -> str:
	return generate_private_key(
		SECP256R1,
		default_backend()
	).private_bytes(
		Encoding.PEM,
		PrivateFormat.TraditionalOpenSSL,
		NoEncryption()
	).decode()

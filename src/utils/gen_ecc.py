from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import (EllipticCurvePrivateKeyWithSerialization, SECP256R1,
                                                          generate_private_key)


def gen_ecc() -> EllipticCurvePrivateKeyWithSerialization:
	return generate_private_key(
		SECP256R1, default_backend()
	)

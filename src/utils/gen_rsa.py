from OpenSSL.crypto import PKey, TYPE_RSA

KEY_SIZE = 2048


def gen_rsa() -> PKey:
	key = PKey()
	key.generate_key(TYPE_RSA, KEY_SIZE)
	return key

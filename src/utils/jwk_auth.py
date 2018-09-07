from json import dumps as to_json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import Hash, SHA256

from .b64url import b64url


def sha256(data: str):
	sha = Hash(SHA256(), default_backend())
	sha.update(data.encode())
	return sha.finalize()


def jwk_auth(jwk):
	return b64url(sha256(to_json(jwk, sort_keys=True, separators=(',', ':'))))

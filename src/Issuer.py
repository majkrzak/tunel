from asyncio import sleep
from asyncio.locks import Lock
from json import dumps as to_json

from aiohttp import ClientSession
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import (ECDSA, EllipticCurvePrivateKey, EllipticCurvePublicKey,
                                                          EllipticCurvePrivateKeyWithSerialization)
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from utils.b64url import b64url
from utils.gen_csr import gen_csr
from utils.jwk_auth import jwk_auth
from utils.key_pem import key_pem


class Issuer:
	directory: str
	key: EllipticCurvePrivateKey

	lock: Lock

	auth: str
	urls: dict
	acc: str = None

	nonce: str

	def __init__(self, directory: str, key: str):
		self.directory = directory
		self.key = load_pem_private_key(key, None, default_backend())
		self.lock = Lock()
		self.auth = jwk_auth(jwk(self.key.public_key()))
		pass

	async def __aenter__(self):
		if self.acc:
			return

		async with self.lock, ClientSession(raise_for_status=True) as session:
			async with session.get(self.directory) as response:
				data = await response.json()
				self.urls = {
					'account': data['newAccount'],
					'nonce': data['newNonce'],
					'order': data['newOrder'],
				}

			async with session.head(self.urls['nonce']) as response:
				self.nonce = response.headers['Replay-Nonce']

			async with session.post(
					self.urls['account'],
					data=self.msg(self.urls['account'], termsOfServiceAgreed=True),
					headers={'Content-Type': 'application/jose+json'}
			) as response:
				self.nonce = response.headers['Replay-Nonce']
				self.acc = response.headers['Location']

	def __call__(self, key: str, domain: str):
		return Issuance(self, key, domain)

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		print(exc_type, exc_val, exc_tb)
		pass

	def msg(self, url, **kwargs):
		protected = b64url(to_json({
			'alg': 'ES256',
			'kid' if self.acc else 'jwk': self.acc or jwk(self.key.public_key()),
			'nonce': self.nonce,
			'url': url,
		}))
		payload = b64url(to_json(kwargs))
		signature = b64url(self.sig(f'{protected}.{payload}'.encode()))

		return to_json({
			'protected': protected,
			'payload': payload,
			'signature': signature,
		})

	def sig(self, data):
		r, s = decode_dss_signature(self.key.sign(data, ECDSA(SHA256())))
		return r.to_bytes(32, 'big') + s.to_bytes(32, 'big')


class Issuance:
	issuer: Issuer
	key: EllipticCurvePrivateKeyWithSerialization
	domain: str

	finalize: str
	auth: str

	http01: dict

	def __init__(self, issuer: Issuer, key: str, domain: str):
		self.issuer = issuer
		self.key = load_pem_private_key(key, None, default_backend())
		self.domain = domain

	async def __aenter__(self):
		async with self.issuer.lock, ClientSession(raise_for_status=True) as session:
			async with session.head(self.issuer.urls['nonce']) as response:
				self.issuer.nonce = response.headers['Replay-Nonce']

			async with session.post(
					self.issuer.urls['order'],
					data=self.issuer.msg(self.issuer.urls['order'],
					                     identifiers=[{'type': 'dns', 'value': self.domain}]),
					headers={'Content-Type': 'application/jose+json'}
			) as response:
				data = await response.json()
				self.finalize = data['finalize']
				self.issuer.nonce = response.headers['Replay-Nonce']

			async with session.get(data['authorizations'][0]) as response:
				data = await response.json()
				self.http01 = next((challenge for challenge in data['challenges'] if challenge['type'] == 'http-01'))

		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		print(exc_type, exc_val, exc_tb)

	async def __call__(self):
		async with self.issuer.lock, ClientSession(raise_for_status=True) as session:
			async with session.head(self.issuer.urls['nonce']) as response:
				self.issuer.nonce = response.headers['Replay-Nonce']

			async with session.post(
					self.http01['url'],
					data=self.issuer.msg(self.http01['url']),
					headers={'Content-Type': 'application/jose+json'}
			) as response:
				self.issuer.nonce = response.headers['Replay-Nonce']

			while self.http01['status'] == 'pending':
				await sleep(1)
				async with session.get(self.http01['url']) as response:
					self.http01 = await response.json()

			async with session.post(
					self.finalize,
					data=self.issuer.msg(self.finalize, csr=b64url(gen_csr(self.key, self.domain))),
					headers={'Content-Type': 'application/jose+json'}
			) as response:
				data = await response.json()

			while data['status'] == 'processing':
				await sleep(1)
				async with session.get(self.finalize) as response:
					data = await response.json()

			async with session.get(data['certificate']) as response:
				crt = await response.text()
				key = key_pem(self.key)

				return f'{key}\n{crt}\n'

	def __format__(self, format_spec):
		if format_spec == 'token':
			return self.http01['token']
		if format_spec == 'auth':
			return self.issuer.auth
		raise KeyError()


def jwk(key: EllipticCurvePublicKey) -> dict:
	return {
		'kty': 'EC',
		'crv': 'P-256',
		'x': b64url(key.public_numbers().x.to_bytes(32, 'big')),
		'y': b64url(key.public_numbers().y.to_bytes(32, 'big')),
	}

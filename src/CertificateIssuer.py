from acme.client import Client
from acme.challenges import HTTP01
from josepy import JWKRSA
from josepy.util import ComparableX509
from signalslot import Signal
from asyncio import ensure_future, wrap_future
from concurrent.futures import ThreadPoolExecutor

from .utils.gen_rsa import gen_rsa
from .utils.gen_csr import gen_csr


class CertificateIssuer:
	key: JWKRSA
	client: Client
	executor: ThreadPoolExecutor

	challenge_requested: Signal
	challenge_answered: Signal
	certificate_issued: Signal

	def __init__(self, directory: str):
		self.key = JWKRSA(key=gen_rsa().to_cryptography_key())
		self.client = Client(directory, self.key)
		self.executor = ThreadPoolExecutor(1)

		self.challenge_requested = Signal(args=['key', 'value'])
		self.challenge_answered = Signal(args=['key'])
		self.certificate_issued = Signal(args=['domain', 'key', 'crt'])

		self.client.agree_to_tos(self.client.register())

	def _ath(self, fn, *args, **kwargs):
		return wrap_future(self.executor.submit(fn, *args, **kwargs))

	async def issue(self, domain) -> None:
		key = gen_rsa()
		csr = gen_csr(domain, key)

		authzr = await self._ath(self.client.request_domain_challenges, domain)
		challb = next(filter(lambda x: isinstance(x.chall, HTTP01), authzr.body.challenges))

		self.challenge_requested.emit(
			key=challb.chall.path,
			value=challb.chall.validation(self.key).encode()
		)

		await self._ath(self.client.answer_challenge, challb, challb.chall.response(self.key))
		crtr, authzr = await self._ath(self.client.poll_and_request_issuance, ComparableX509(csr), [authzr])

		self.challenge_answered.emit(
			key=challb.chall.path
		)

		self.certificate_issued.emit(
			domain=domain,
			key=key,
			crt=crtr.body.wrapped
		)

	def __call__(self, domain):
		ensure_future(self.issue(domain))

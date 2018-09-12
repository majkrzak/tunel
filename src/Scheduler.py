from asyncio import Queue, sleep
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta

DELTA = timedelta(days=1)
MAX_SLEEP = (2 ** 31 - 1) / 1000


class Scheduler:
	queue: Queue

	def __init__(self):
		self.queue = Queue()

	async def __call__(self, crt: str) -> None:
		certificate = load_pem_x509_certificate(crt.encode(), default_backend())
		domain = next(iter(certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME))).value
		expiration = certificate.not_valid_after
		delay = min((expiration - datetime.utcnow() - DELTA).total_seconds(), MAX_SLEEP)
		await sleep(delay)
		await self.queue.put(domain)

	def __aiter__(self):
		return self

	async def __anext__(self):
		return await self.queue.get()

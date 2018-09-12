from asyncio import Queue, StreamReader, StreamWriter, create_task, start_server
from ssl import ALERT_DESCRIPTION_UNRECOGNIZED_NAME, PROTOCOL_TLSv1_2, SSLContext, SSLObject


class Terminator:
	contexts: dict
	queue: Queue

	def __init__(self, port: int):
		self.contexts = {}
		self.queue = Queue()

		create_task(start_server(self.handler, '', port, ssl=self.ssl()))

	def __setitem__(self, key: str, val: str):
		self.contexts[key] = self.ssl(val)

	def ssl(self, cert: str = None) -> SSLContext:
		ssl = SSLContext(PROTOCOL_TLSv1_2)
		if cert is None:
			ssl.sni_callback = self.sni
		else:
			ssl.load_cert_chain(cert)
		return ssl

	def sni(self, ssl_object: SSLObject, domain: str, _) -> int:
		if domain not in self.contexts:
			return ALERT_DESCRIPTION_UNRECOGNIZED_NAME
		setattr(ssl_object, 'context', self.contexts[domain])
		setattr(ssl_object, 'domain', domain)

	async def handler(self, reader: StreamReader, writer: StreamWriter):
		domain = writer.get_extra_info('ssl_object').domain
		await self.queue.put((domain, reader, writer))

	def __aiter__(self):
		return self

	async def __anext__(self):
		return await self.queue.get()

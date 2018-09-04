from asyncio import ensure_future, start_server, open_connection, gather
from ssl import SSLContext, SSLObject, PROTOCOL_TLSv1_2

from .utils.pipe import pipe


class ProxyServer:
	contexts: dict
	targets: dict

	def __init__(self, port: int):
		self.contexts = {}
		self.targets = {}

		ensure_future(start_server(self.handler, '', port, ssl=self.ssl()))

	def __setitem__(self, key, value):
		self.contexts[key] = value['ssl']
		self.targets[key] = value['target']

	def __delitem__(self, key):
		del self.contexts[key]
		del self.targets[key]

	def ssl(self):
		ssl = SSLContext(PROTOCOL_TLSv1_2)
		ssl.sni_callback = self.sni
		return ssl

	def sni(self, ssl_object: SSLObject, domain: str, _):
		setattr(ssl_object, 'context', self.contexts[domain])
		setattr(ssl_object, 'domain', domain)

	async def handler(self, local_reader, local_writer):
		domain = local_writer.get_extra_info('ssl_object').domain

		try:
			remote_reader, remote_writer = await open_connection(self.targets[domain], 80)
			await gather(
				pipe(local_reader, remote_writer),
				pipe(remote_reader, local_writer)
			)
		finally:
			local_writer.close()

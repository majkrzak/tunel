from asyncio import create_task, start_server, open_connection, gather
from ssl import SSLContext, SSLObject, PROTOCOL_TLSv1_2

from .utils.pipe import pipe


class ProxyServer:
	configs: dict

	def __init__(self, port: int):
		self.configs = {}

		create_task(start_server(self.handler, '', port, ssl=self.ssl()))

	def __getitem__(self, item):
		if item not in self.configs:
			self.configs[item] = Config()

		return self.configs[item]

	def ssl(self):
		ssl = SSLContext(PROTOCOL_TLSv1_2)
		ssl.sni_callback = self.sni
		return ssl

	def sni(self, ssl_object: SSLObject, domain: str, _):
		setattr(ssl_object, 'context', self.configs[domain].context)
		setattr(ssl_object, 'domain', domain)

	async def handler(self, local_reader, local_writer):
		domain = local_writer.get_extra_info('ssl_object').domain

		try:
			remote_reader, remote_writer = await open_connection(self.configs[domain].target, 80)
			await gather(
				pipe(local_reader, remote_writer),
				pipe(remote_reader, local_writer)
			)
		finally:
			local_writer.close()


class Config:

	def __init__(self):
		self._target = None
		self._context = None

	@property
	def target(self):
		return self._target

	@target.setter
	def target(self, value):
		self._target = value

	@property
	def context(self):
		return self._context

	@context.setter
	def context(self, value):
		ctx = SSLContext(PROTOCOL_TLSv1_2)
		ctx.load_cert_chain(value)
		self._context = ctx

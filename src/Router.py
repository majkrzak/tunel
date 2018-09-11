from asyncio import open_connection, gather

CHUNK_SIZE = 2048
PORT = 80


class Router:
	routes: dict

	def __init__(self):
		self.routes = {}

	def __setitem__(self, key, value):
		self.routes[key] = value

	async def __call__(self, domain, local_reader, local_writer):
		try:
			remote_reader, remote_writer = await open_connection(self.routes[domain], PORT)
			await gather(
				self.pipe(local_reader, remote_writer),
				self.pipe(remote_reader, local_writer)
			)
		finally:
			if local_writer:
				local_writer.close()

	@staticmethod
	async def pipe(reader, writer):
		try:
			while not reader.at_eof():
				writer.write(await reader.read(CHUNK_SIZE))
		finally:
			writer.close()

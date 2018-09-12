from asyncio import StreamReader, StreamWriter, gather, open_connection

CHUNK_SIZE = 2048
PORT = 80


class Router:
	routes: dict

	def __init__(self):
		self.routes = {}

	def __setitem__(self, key: str, val: str) -> None:
		self.routes[key] = val

	async def __call__(self, domain: str, local_reader: StreamReader, local_writer: StreamWriter) -> None:
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
	async def pipe(reader: StreamReader, writer: StreamWriter) -> None:
		try:
			while not reader.at_eof():
				writer.write(await reader.read(CHUNK_SIZE))
		finally:
			writer.close()

from asyncio import ensure_future, start_server
from asyncio.streams import StreamWriter, StreamReader

CRLF = '\r\n'


class Challenger:
	challenges: dict = {}

	def __init__(self, port: int):
		ensure_future(start_server(self.handler, '', port))

	def __setitem__(self, key, value):
		self.challenges[key] = value

	def __delitem__(self, key):
		del self.challenges[key]

	async def handler(self, reader: StreamReader, writer: StreamWriter):
		request = self.parse((await reader.readuntil((CRLF + CRLF).encode())).decode())

		if request['method'] == 'GET' and request['path'] in self.challenges:
			writer.write(self.respond(self.challenges[request['path']]).encode())
		else:
			writer.write(self.redirect(request['headers']['Host'], request['path']).encode())

		writer.close()

	@staticmethod
	def parse(data: str) -> dict:
		request_line, *header_lines = data.strip('\r\n').split('\r\n')

		method, path = request_line.split(' ')[:2]
		headers = dict(header_line.split(': ', 1) for header_line in header_lines)

		return {
			'method': method,
			'path': path,
			'headers': headers,
		}

	@staticmethod
	def respond(payload: str) -> str:
		return f'HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(payload)}\r\n\r\n{payload}'

	@staticmethod
	def redirect(host: str, path: str) -> str:
		return f'HTTP/1.1 301 Moved Permanently\r\nLocation: https://{host}{path}'

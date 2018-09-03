from aiohttp.web import Server, Request, Response, HTTPMovedPermanently
from asyncio import ensure_future, get_event_loop

HTTP_PORT = 80


class RedirectServer:
	responses: dict = {}

	def __init__(self):
		ensure_future(get_event_loop().create_server(Server(self.handler), '', HTTP_PORT))

	def __setitem__(self, key, value):
		self.responses[key] = value

	def __delitem__(self, key):
		del self.responses[key]

	async def handler(self, request: Request) -> Response:
		if request.method == 'GET' and request.path in self.responses:
			return Response(body=self.responses[request.path])
		else:
			return HTTPMovedPermanently(f'https://{request.host}{request.path_qs}')

from asyncio import create_task

from aiohttp.web_exceptions import HTTPMovedPermanently, HTTPOk
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from .utils.start_server import start_server


class Challenger:
	challenges: dict = {}

	def __init__(self, port: int):
		self.challenges = {}

		create_task(start_server(self.handler, '', port))

	def __setitem__(self, key: str, val: str) -> None:
		self.challenges[key] = val

	def __delitem__(self, key: str) -> None:
		del self.challenges[key]

	async def handler(self, request: Request) -> Response:
		if request.method == 'GET' and request.path in self.challenges:
			return HTTPOk(body=self.challenges[request.path])
		else:
			return HTTPMovedPermanently(f'https://{request.host}{request.path_qs}')

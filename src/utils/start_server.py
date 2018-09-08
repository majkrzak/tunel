from aiohttp.web_runner import ServerRunner, TCPSite
from aiohttp.web_server import Server


async def start_server(handler, host, port):
	server = Server(handler)
	runner = ServerRunner(server)
	await runner.setup()
	site = TCPSite(runner, host, port)
	await site.start()

from asyncio import get_event_loop, ensure_future
from os import environ
from operator import setitem

from .Context import Context
from .DockerMonitor import DockerMonitor
from .Issuer import Issuer
from .Challenger import Challenger
from .ProxyServer import ProxyServer
from .utils.gen_ecc import gen_ecc

DIRECTORY = environ.get('DIRECTORY', 'https://acme-v02.api.letsencrypt.org/directory')
CONTEXT = environ.get('CONTEXT', '.')
HTTP_PORT = int(environ.get('HTTP_PORT', 80))
HTTPS_PORT = int(environ.get('HTTPS_PORT', 443))


async def main():
	context = Context(CONTEXT)
	docker_monitor = DockerMonitor()

	issuer = Issuer(DIRECTORY, 'key' not in context and setitem(context, 'key', gen_ecc()) or context['key'])
	challenger = Challenger(HTTP_PORT)
	proxy_server = ProxyServer(HTTPS_PORT)

	async for domain, target in docker_monitor:
		if domain not in context:
			async with issuer:
				async with issuer(gen_ecc(), domain) as issuance:
					challenger[f'/.well-known/acme-challenge/{issuance:token}'] = f'{issuance:token}.{issuance:auth}'
					context[domain] = await issuance()

		proxy_server[domain].target = target
		proxy_server[domain].context = context[domain]


ensure_future(main())
get_event_loop().run_forever()

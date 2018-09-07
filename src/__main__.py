from asyncio import get_event_loop
from os import environ

from .DockerMonitor import DockerMonitor
from .Issuer import Issuer
from .Challenger import Challenger
from .ProxyServer import ProxyServer
from .utils.ssl_factory import ssl_factory
from .utils.gen_ecc import gen_ecc

DIRECTORY = environ.get('DIRECTORY', 'https://acme-v02.api.letsencrypt.org/directory')
KEY = gen_ecc()
HTTP_PORT = int(environ.get('HTTP_PORT', 80))
HTTPS_PORT = int(environ.get('HTTPS_PORT', 443))

context = {}
docker_monitor = DockerMonitor()
issuer = Issuer(DIRECTORY, KEY)
challenger = Challenger(HTTP_PORT)
proxy_server = ProxyServer(HTTPS_PORT)


@docker_monitor.domain_attached.connect
async def domain_attached_handler(domain: str, target: str) -> None:
	print(domain, target)

	if domain in context:
		context[domain]['target'] = target
	else:
		async with issuer:
			async with issuer(gen_ecc(), domain) as issuance:
				challenger[f'/.well-known/acme-challenge/{issuance:token}'] = f'{issuance:token}.{issuance:auth}'

				context[domain] = {
					'target': target,
					'ssl': ssl_factory(domain, await issuance())
				}
				proxy_server[domain] = context[domain]


get_event_loop().run_forever()

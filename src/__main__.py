from asyncio import get_event_loop
from os import environ

from .DockerMonitor import DockerMonitor
from .CertificateIssuer import CertificateIssuer
from .Challenger import Challenger
from .ProxyServer import ProxyServer
from .utils.ssl_factory import ssl_factory

DIRECTORY = environ.get('DIRECTORY', 'https://acme-v1.api.letsencrypt.org/directory')
HTTP_PORT = int(environ.get('HTTP_PORT', 80))
HTTPS_PORT = int(environ.get('HTTPS_PORT', 443))

context = {}
docker_monitor = DockerMonitor()
certificate_issuer = CertificateIssuer(DIRECTORY)
challenger = Challenger(HTTP_PORT)
proxy_server = ProxyServer(HTTPS_PORT)


@docker_monitor.domain_attached.connect
async def domain_attached_handler(domain: str, target: str) -> None:
	if domain in context:
		context[domain]['target'] = target
	else:
		context[domain] = {
			'target': target
		}
		key, crt = await certificate_issuer(domain)
		context[domain]['ssl'] = ssl_factory(domain, key, crt)
		proxy_server[domain] = context[domain]


@certificate_issuer.challenge_requested.connect
async def challenge_requested_handler(key: str, value: str) -> None:
	challenger[key] = value


@certificate_issuer.challenge_answered.connect
async def challenge_answered_handler(key: str) -> None:
	del challenger[key]


get_event_loop().run_forever()

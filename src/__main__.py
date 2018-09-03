from asyncio import get_event_loop
from signalslot import Slot

from .DockerMonitor import DockerMonitor
from .CertificateIssuer import CertificateIssuer
from .RedirectServer import RedirectServer
from .ProxyServer import ProxyServer
from .utils.ssl_factory import ssl_factory

DIRECTORY = 'https://acme-v01.api.letsencrypt.org/directory'

context = {}
docker_monitor = DockerMonitor()
certificate_issuer = CertificateIssuer(DIRECTORY)
redirect_server = RedirectServer()
proxy_server = ProxyServer()


@docker_monitor.domain_attached.connect
@Slot
def domain_attached_handler(domain: str, target: str) -> None:
	if domain in context:
		context[domain]['target'] = target
	else:
		context[domain] = {
			'target': target
		}
		certificate_issuer(domain)


@certificate_issuer.challenge_requested.connect
@Slot
def challenge_requested_handler(key: str, value: str) -> None:
	redirect_server[key] = value


@certificate_issuer.challenge_answered.connect
@Slot
def challenge_answered_handler(key: str) -> None:
	del redirect_server[key]


@certificate_issuer.certificate_issued.connect
@Slot
def certificate_issued_handler(domain: str, key, crt):
	context[domain]['ssl'] = ssl_factory(domain, key, crt)
	proxy_server[domain] = context[domain]


get_event_loop().run_forever()

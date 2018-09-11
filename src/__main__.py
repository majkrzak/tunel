from asyncio import get_event_loop, ensure_future, create_task
from os import environ
from operator import setitem

from .Storage import Storage
from .DockerMonitor import DockerMonitor
from .Scheduler import Scheduler
from .Issuer import Issuer
from .Challenger import Challenger
from .ProxyServer import ProxyServer
from .utils.gen_ecc import gen_ecc
from .utils.call import call

DIRECTORY = environ.get('DIRECTORY', 'https://acme-v02.api.letsencrypt.org/directory')
CONTEXT = environ.get('CONTEXT', '.')
HTTP_PORT = int(environ.get('HTTP_PORT', 80))
HTTPS_PORT = int(environ.get('HTTPS_PORT', 443))


@ensure_future
@call
async def main():
	storage = Storage(CONTEXT)
	docker_monitor = DockerMonitor()
	scheduler = Scheduler()
	issuer = Issuer(DIRECTORY, 'key' not in storage and setitem(storage, 'key', gen_ecc()) or storage['key'])
	challenger = Challenger(HTTP_PORT)
	proxy_server = ProxyServer(HTTPS_PORT)

	async for domain, target in docker_monitor:
		if domain not in storage:
			async with issuer:
				async with issuer(gen_ecc(), domain) as issuance:
					challenger[f'/.well-known/acme-challenge/{issuance:token}'] = f'{issuance:token}.{issuance:auth}'
					storage[domain] = await issuance()

		proxy_server[domain].target = target
		proxy_server[domain].context = storage(domain)
		create_task(scheduler(storage[domain]))


get_event_loop().run_forever()

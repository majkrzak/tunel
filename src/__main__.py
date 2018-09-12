from asyncio import get_event_loop, ensure_future, create_task
from os import environ
from operator import setitem

from .Storage import Storage
from .Monitor import Monitor
from .Scheduler import Scheduler
from .Issuer import Issuer
from .Challenger import Challenger
from .Terminator import Terminator
from .Router import Router
from .utils.gen_ecc import gen_ecc
from .utils.call import call


CONTEXT = environ.get('CONTEXT', '.')
DIRECTORY = environ.get('DIRECTORY', 'https://acme-v02.api.letsencrypt.org/directory')
HTTP_PORT = int(environ.get('HTTP_PORT', 80))
HTTPS_PORT = int(environ.get('HTTPS_PORT', 443))


@ensure_future
@call
async def main():
	storage = Storage(CONTEXT)
	docker_monitor = Monitor()
	scheduler = Scheduler()
	issuer = Issuer(DIRECTORY, 'key' not in storage and setitem(storage, 'key', gen_ecc()) or storage['key'])
	challenger = Challenger(HTTP_PORT)
	terminator = Terminator(HTTPS_PORT)
	router = Router()

	async def issue(domain):
		async with issuer:
			async with issuer(gen_ecc(), domain) as issuance:
				challenger[f'/.well-known/acme-challenge/{issuance:token}'] = f'{issuance:token}.{issuance:auth}'
				storage[domain] = await issuance()

	@create_task
	@call
	async def monitor_handler():
		async for domain, target in docker_monitor:
			if domain not in storage:
				await issue(domain)
			terminator[domain] = storage(domain)
			router[domain] = target
			create_task(scheduler(storage[domain]))

	@create_task
	@call
	async def scheduler_handler():
		async for domain in scheduler:
			await issue(domain)
			create_task(scheduler(storage[domain]))

	@create_task
	@call
	async def terminator_handler():
		async for domain, reader, writer in terminator:
			create_task(router(domain, reader, writer))


get_event_loop().run_forever()

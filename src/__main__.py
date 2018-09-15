from asyncio import create_task, ensure_future, get_event_loop
from operator import setitem
from os import environ

from .Challenger import Challenger
from .Issuer import Issuer
from .Monitor import Monitor
from .Router import Router
from .Scheduler import Scheduler
from .Storage import Storage
from .Terminator import Terminator
from .utils.call import call
from .utils.gen_ecc import gen_ecc

CONTEXT = environ.get('CONTEXT', '.')
DIRECTORY = environ.get('DIRECTORY', 'https://acme-v02.api.letsencrypt.org/directory')
HTTP_PORT = int(environ.get('HTTP_PORT', 80))
HTTPS_PORT = int(environ.get('HTTPS_PORT', 443))


@ensure_future
@call
async def main():
	storage = Storage(CONTEXT)
	monitor = Monitor()
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
		async for domain, target in monitor:
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

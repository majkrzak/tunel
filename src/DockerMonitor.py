from aiodocker import Docker
from aiodocker.containers import DockerContainer
from asyncio import ensure_future, sleep

from .utils.AsyncSignal import AsyncSignal


class DockerMonitor:
	docker: Docker

	domain_attached: AsyncSignal

	def __init__(self):
		self.docker = Docker()
		self.domain_attached = AsyncSignal()

		ensure_future(self.query_running())
		ensure_future(self.query_started())

	async def query_running(self) -> None:
		containers = await self.docker.containers.list()
		for container in containers:
			await self.handle(container)

	async def query_started(self) -> None:
		channel = self.docker.events.subscribe()
		while channel:
			event = await channel.get()
			if event['Type'] == 'container' and event['status'] == 'start':
				await sleep(1000)
				container = await self.docker.containers.get(event['id'])
				await self.handle(container)

	async def handle(self, container: DockerContainer) -> None:
		try:
			await self.domain_attached.emit(
				domain=container['Labels']['domain'],
				target=next(iter(container['NetworkSettings']['Networks'].values()))['IPAddress']
			)
		except KeyError:
			pass

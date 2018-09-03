from aiodocker import Docker
from aiodocker.containers import DockerContainer
from asyncio import ensure_future
from signalslot import Signal


class DockerMonitor:
	docker: Docker

	domain_attached: Signal

	def __init__(self):
		self.docker = Docker()
		self.domain_attached = Signal(args=['domain', 'target'])

		ensure_future(self.query_running())
		ensure_future(self.query_started())

	async def query_running(self) -> None:
		containers = await self.docker.containers.list()
		for container in containers:
			self.handle(container)

	async def query_started(self) -> None:
		channel = self.docker.events.subscribe()
		while channel:
			event = await channel.get()
			if event['Type'] == 'container' and event['status'] == 'start':
				container = await self.docker.containers.get(event['id'])
				self.handle(container)

	def handle(self, container: DockerContainer) -> None:
		try:
			self.domain_attached.emit(
				domain=container['Labels']['domain'],
				target=next(iter(container['NetworkSettings']['Networks'].values()))['IPAddress']
			)
		except KeyError:
			pass

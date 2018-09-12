from asyncio import Queue, create_task

from aiodocker import Docker
from aiodocker.containers import DockerContainer


class Monitor:
	docker: Docker
	queue: Queue

	def __init__(self):
		self.docker = Docker()
		self.queue = Queue()

		create_task(self.query_running())
		create_task(self.query_started())

	async def query_running(self) -> None:
		containers = await self.docker.containers.list()
		for container in containers:
			await container.show()
			await self.handle(container)

	async def query_started(self) -> None:
		channel = self.docker.events.subscribe()
		while channel:
			event = await channel.get()
			if event['Type'] == 'container' and event['status'] == 'start':
				container = self.docker.containers.container(event['id'])
				await container.show()
				await self.handle(container)

	async def handle(self, container: DockerContainer) -> None:
		try:
			await self.queue.put((
				container['Config']['Labels']['domain'],
				next(iter(container['NetworkSettings']['Networks'].values()))['IPAddress'],
			))
		except KeyError:
			pass

	def __aiter__(self):
		return self

	async def __anext__(self):
		return await self.queue.get()

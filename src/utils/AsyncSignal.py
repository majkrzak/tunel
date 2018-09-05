class AsyncSignal:
	def __init__(self):
		self.callbacks = []

	async def emit(self, **kwargs):
		for callback in self.callbacks:
			retval = await callback(**kwargs)
			if retval is not None:
				return retval

	def connect(self, callback):
		self.callbacks.append(callback)

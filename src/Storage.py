from os.path import join, isfile


class Storage:
	context: str
	cache: dict

	def __init__(self, base: str):
		self.context = base
		self.cache = {}
		pass

	def __setitem__(self, key: str, val: str) -> None:
		with open(self(key), 'w') as f:
			f.write(val)
			f.flush()
		self.cache[key] = val

	def __getitem__(self, key) -> str:
		if key not in self.cache:
			with open(self(key)) as f:
				self.cache[key] = f.read()
		return self.cache[key]

	def __contains__(self, key) -> bool:
		return key in self.cache or isfile(self(key))

	def __call__(self, key) -> str:
		return join(self.context, key)
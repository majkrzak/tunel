from os.path import join, isfile


class Context:
	base: str

	def __init__(self, base: str):
		self.base = base
		pass

	def __setitem__(self, key: str, val: str) -> str:
		with open(self(key), 'w') as f:
			f.write(val)
			f.flush()
		return val

	def __getitem__(self, key) -> str:
		with open(self(key)) as f:
			return f.read()

	def __contains__(self, key) -> bool:
		return isfile(self(key))

	def __call__(self, key) -> str:
		return join(self.base, key)

import setuptools

NAME = 'tunel'
REPOSITORY = 'https://majkrzak@bitbucket.org/majkrzak/tunel.git'
CORE_DEPENDENCIES = [
	'aiodocker',
	'acme'
]
BUILD_DEPENDECIES = [
	'docker',
	'wheel'
]
DOCKERFILE = f'''
	FROM python:3.7-slim AS build
	COPY . .
	RUN python setup.py bdist_wheel --dist-dir .
	
	FROM python:3.7-slim
	COPY --from=build {NAME}-0.0.0-py3-none-any.whl .
	RUN python3 -m pip install {NAME}-0.0.0-py3-none-any.whl
	
	ENTRYPOINT ["python3", "-m", "{NAME}"]
	CMD []
'''


def cmd(run):
	return type(run.__name__, (setuptools.Command,), {
		'user_options': [],
		'initialize_options': lambda _: None,
		'finalize_options': lambda _: None,
		'run': staticmethod(run),
	})


@cmd
def dockerize():
	from docker import from_env
	from docker.errors import BuildError
	import docker.api.build
	docker.api.build.process_dockerfile = lambda dockerfile, path: ('Dockerfile', dockerfile)

	try:
		img, log = from_env().images.build(
			path='.',
			rm=True,
			tag=NAME,
			dockerfile=DOCKERFILE
		)
		for line in log:
			print(line)
	except BuildError as e:
		for line in e.build_log:
			print(line)


@cmd
def deploy():
	from docker import from_env
	from docker.errors import NotFound

	try:
		from_env().containers.get(NAME).remove(force=True)
	except NotFound:
		pass

	from_env().containers.run(
		image=NAME,
		name=NAME,
		volumes=['/var/run/docker.sock:/var/run/docker.sock'],
		ports={'80': '80', '443': '443'},
		detach=True,
		restart_policy={'Name': 'always'}
	)


setuptools.setup(
	name=NAME,
	description='Instant Docker reverse TLS 1.2 termination proxy',
	author='Piotr Majrzak',
	author_email='petrol.91@gmail.com',
	license='Permission to use, copy, modify, and distribute this software for any '
	        + 'purpose with or without fee is hereby granted, provided that the above '
	        + 'copyright notice and this permission notice appear in all copies.',
	packages=[
		NAME,
		NAME + '.utils'
	],
	package_dir={NAME: './src'},
	install_requires=CORE_DEPENDENCIES,
	setup_requires=BUILD_DEPENDECIES,
	cmdclass={
		'dockerize': dockerize,
		'deploy': deploy,
	}
)

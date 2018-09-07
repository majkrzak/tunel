from ssl import SSLContext, PROTOCOL_TLSv1_2


def ssl_factory(domain: str, pem: str) -> SSLContext:
	with open(f'{domain}', 'w') as crt_file:
		crt_file.write(pem)
	ctx = SSLContext(PROTOCOL_TLSv1_2)
	ctx.load_cert_chain(f'{domain}')
	return ctx

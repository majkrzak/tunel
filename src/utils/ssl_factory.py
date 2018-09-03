from OpenSSL.crypto import PKey, X509, FILETYPE_PEM, dump_privatekey, dump_certificate
from ssl import SSLContext, PROTOCOL_TLSv1_2


def ssl_factory(domain: str, key: PKey, crt: X509) -> SSLContext:
	with open(f'{domain}', 'wb') as crt_file:
		crt_file.write(dump_privatekey(FILETYPE_PEM, key))
		crt_file.write(dump_certificate(FILETYPE_PEM, crt))
	ctx = SSLContext(PROTOCOL_TLSv1_2)
	ctx.load_cert_chain(f'{domain}')
	return ctx

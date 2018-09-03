from OpenSSL.crypto import PKey, X509Req


def gen_csr(domain: str, key: PKey) -> X509Req:
	csr = X509Req()
	csr.set_pubkey(key)
	setattr(csr.get_subject(), 'CN', domain)
	csr.sign(key, 'sha256')
	return csr

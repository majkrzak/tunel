from base64 import urlsafe_b64encode


def b64url(msg):
	return urlsafe_b64encode((msg.encode() if type(msg) is str else msg)).decode().strip('=')

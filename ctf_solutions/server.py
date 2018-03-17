import base64
import signal
import socketserver
from crypt import *
import os

PORT = 3000

def bad_decrypt_gm(c, sk):
	p, q = sk
	m = 0
	for z in c:
		m <<= 1
		if legendre(z % p, p) != 1 or legendre(z % q, q) != 1:
			m += 1
	h = '%x' % m
	l = len(h)
	return hex2bytes(h.zfill(l + l % 2))

def bad_encrypt_aes(m, k):
	iv = os.urandom(16)
	return iv + aes_encrypt(m, k, modes.CFB8(iv))

message = open('message', 'rb').read()

with open('sk') as f:
	p = int(f.readline())
	q = int(f.readline())
	sk = (p, q)

class incoming(socketserver.BaseRequestHandler):
	def handle(self):
		req = self.request

		def receive():
			buf = b''
			while not buf.endswith(b'\n'):
				buf += req.recv(1)
			return buf[:-1]

		signal.alarm(60)

		req.sendall(b'Welcome to the Goldwasser-Micali key exchange!\n')
		req.sendall(b'Please send us an encrypted 128 bit key for us to use.\n')
		req.sendall(b'Each encrypted bit should be sent line by line in integer format.\n')

		enckey = []
		for i in range(128):
			enckey.append(int(receive()))	#get gm-encrypted key from user
		print('len(enckey):', len(enckey))
		key = bad_decrypt_gm(enckey, sk)	#decrypt given key with GM
		encmessage = bad_encrypt_aes(message, key)	#then use it to encrypt the message with AES.

		req.sendall(base64.b64encode(encmessage)+b'\n')	#send the encrypted message to the user in b64
		req.close()

class ReusableTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
	pass

socketserver.TCPServer.allow_reuse_address = True
server = ReusableTCPServer(('0.0.0.0', PORT), incoming)

print('Server listening on port %d' % PORT)
server.serve_forever()

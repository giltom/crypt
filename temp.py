from crypt import *

from pwn import *

import socket

f = open('data/pk')
n = int(f.readline())
x = int(f.readline())
aes_key = b'\0'*16
enc_aes_key = gm_encrypt(aes_key, x, n)

sock = socket.create_connection(('web.angstromctf.com', 3000))


for val in enc_aes_key:
	sock.sendall(str(val).encode('UTF-8'))
print(sock.recv(4098))

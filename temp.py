from crypt import *
from pwn import *
import socket

f = open('data/pk')
n = int(f.readline())
x = int(f.readline())
print(n)
print(x)
print(n > x)
aes_key = b'\xFF'*16
enc_aes_key = gm_encrypt(aes_key, x, n)
print(len(enc_aes_key))

sock = remote('web.angstromctf.com', 3000)

print(sock.recvuntil('format.\n'))
for val in enc_aes_key:
	sock.sendline(str(val))
cipherb64 = sock.recvall()[:-1]
cipher = base642bytes(cipherb64)
print(aes_decrypt(cipher[16:], aes_key, modes.CFB8(cipher[:16])))

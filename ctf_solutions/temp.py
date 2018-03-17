from crypt import *
from pwn import *
import itertools
import sys

DOMAIN = 'web.angstromctf.com'

f = open('data/pk')
n = int(f.readline())
x = int(f.readline())

#aes_key = b'\xC0\x00\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x00'
enc_aes_key = [int(line) for line in open('data/key.enc')]#gm_encrypt(aes_key, x, n)

def send_key(enc_key):
	sock = remote(DOMAIN, 3000)
	sock.recvuntil('format.\n')
	for val in enc_key:
		sock.sendline(str(val))
	cipherb64 = sock.recvall()[:-1]
	sock.close()
	return base642bytes(cipherb64)

def is_empty_response(enc_key):
	sock = remote(DOMAIN, 3000)
	sock.recvuntil('format.\n')
	for val in enc_key:
		sock.sendline(str(val))
	try:
		sock.recvn(1)
		return False
	except EOFError:
		return True
	finally:
		sock.close()

def get_1st_byte():	#it's 26 = 0x1A = 00011010
	for num_ones in range(9):
		for one_indexes in itertools.combinations(range(8), num_ones):
			enc_key_copy = list(enc_aes_key)
			bits = [0]*8
			for i in one_indexes:
				enc_key_copy[i] = 1
				bits[i] = 1
			print('Trying mask', bits)
			if is_empty_response(enc_key_copy):
				print('Success!')
				return bits2bytes(bits)[0]

"""
test_enc_key = [1]*128
keybits = []
for val in [int(line) for line in open('data/key.enc')]:
	test_enc_key[0] = val
	if is_empty_response(test_enc_key):
		keybits.append(0)
		print('got 0')
	else:
		keybits.append(1)
		print('got 1')
key = bits2bytes(keybits)
print(key)
"""
key = b'\x1a\xcc\xff\x17\x9b\xac\xec,\x95g\xdb\xeb\xe4C\xce '
"""
cipher = send_key([int(line) for line in open('data/key.enc')])
message = aes_decrypt(cipher[16:], key, modes.CFB8(cipher[:16]))
print(message)
"""
ciphertext = open('data/flag.enc', 'rb').read()
flag = aes_decrypt(ciphertext[16:], key, modes.CFB8(ciphertext[:16]))
fout = open('data/output', 'wb')
fout.write(flag)
fout.close()

#enc_aes_key =

#print()

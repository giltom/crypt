from crypt import *
import struct

def lcg(m, a, c, x):
	return (a*x + c) % m

def pack(i):
    return struct.pack('>I', i)

def unpack(b):
    return struct.unpack('>I', b)[0]

m = pow(2, 32)

PNG_HEADER = hex2bytes('89 50 4E 47 0D 0A 1A 0A 00 00 00 0D') + b'IHDR'
HEADER_LEN = len(PNG_HEADER)

f = open('data/flag.png.enc', 'rb')
enc_header = f.read(HEADER_LEN)
f.close()

x = [bytes2int_big(block) for block in get_blocks(xor(enc_header, PNG_HEADER), 4)]
print(x)
a = (((x[1] - x[2]) % m) * mod_inverse((x[0] - x[1]) % m, m)) % m
c = (x[1] - a*x[0]) % m
xt = x[0]

ctext = open('data/flag.png.enc', 'rb').read()
outf = open('data/output.png', 'wb')
for block in get_blocks(ctext, 4):
    outf.write(xor(block, pack(xt)))
    xt = lcg(m, a, c, xt)
outf.close()

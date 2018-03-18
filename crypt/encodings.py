import binascii
import base64

#hex string to bytes
def hex2bytes(hexstr):
    return bytes.fromhex(hexstr)

#bytes to hex string
def bytes2hex(b):
    return binascii.hexlify(b).decode('ASCII')

#bytes to base64 string
def bytes2base64(b):
    return base64.b64encode(b).decode('ASCII')

#base64 string to bytes
def base642bytes(s):
    return base64.b64decode(s)

#Bytes to unsigned integer, big endian
def bytes2int_big(b):
    val = 0
    for byte in b:
        val = (val << 8) + byte
    return val

#Bytes to unsigned integer, little endian
def bytes2int_little(b):
    return bytes2int_big(reversed(b))

#Integer to bytes, big endian
def int2bytes_big(i):
    res = b''
    while i != 0:
        res = bytes([i & 0xFF]) + res
        i >>= 8
    return res

#Integer to bytes, little endian
def int2bytes_little(i):
    return bytes(reversed(int2bytes_big(i)))

def bytes2bitstring(b):
    s = ''
    for byte in b:
        s += '{:08b}'.format(byte)
    return s

def bitstring2bytes(s):
    b = []
    for start in range(0, len(s), 8):
        bits = s[start:start+8]
        b.append(int(bits, 2))
    return bytes(b)

#returns list of integer bits
def bytes2bits(b):
    return [int(c) for c in bytes2bitstring(b)]

def bits2bytes(bits):
    return bitstring2bytes(''.join(str(bit) for bit in bits))

def is_base64(b):
    try:
        base64.b64decode(b, validate=True)
        return True
    except binascii.Error:
        return False

#add some bytes to produce valid base64, assuming the string starts at index start
def pad_base64(s, start=0):
    res = 'A'*start + s
    declen = len(res)*6
    pad = ''
    while (declen + 6*len(pad)) % 8 != 0:
        pad += 'A'
    if len(pad) == 1:
        pad = '='
    elif len(pad) >= 2:
        pad = pad[:-2] + '=='
    return res + pad

import binascii
import base64

from crypt import util

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
#If size is given (in bytes), discards bytes over the given size and fills with 0 bytes up to it
def int2bytes_big(i, size=None):
    if size is None and i < 0:
        raise util.CryptoException('Size must be given for negative integers')
    res = b''
    while (size is None and i != 0) or (size is not None and len(res) < size):
        res = bytes([i & 0xFF]) + res
        i >>= 8
    return res

#Integer to bytes, little endian
#if size is given, fills with 0 bytes to the given size
def int2bytes_little(i, size=None):
    return bytes(reversed(int2bytes_big(i, size=size)))

def bytes2bin(b):
    s = ''
    for byte in b:
        s += '{:08b}'.format(byte)
    return s

def bin2bytes(s):
    b = []
    for start in range(0, len(s), 8):
        bits = s[start:start+8]
        b.append(int(bits, 2))
    return bytes(b)

#returns list of integer bits
def bytes2bits(b):
    return [int(c) for c in bytes2bin(b)]

def bits2bytes(bits):
    return bin2bytes(''.join(str(bit) for bit in bits))

def is_base64(s):
    if type(s) is not str:
        return False
    try:
        base64.b64decode(s, validate=True)
        return True
    except binascii.Error:
        return False

def is_hex(s):
    if type(s) is not str:
        return False
    try:
        hex2bytes(s)
        return True
    except ValueError:
        return False

def is_bin(s):
    if type(s) is not str:
        return False
    return all(c == '0' or c == '1' for c in s)

def is_bits(l):
    if type(l) is not list:
        return False
    return all(c == 0 or c == 1 for c in s)


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

#maps an encoding name to a 3-tuple (frombytes, tobytes, identify)
#frombytes - converts from bytes to this
#tobytes - converts from this to bytes
#identify - returns True if a value is of this type. Use None if the type cannot be identified.
ENCODING_MAP = {
    'bytes' : (lambda x: x, lambda x: x, lambda x: type(x) is bytes),                   #bytes object
    'hex' : (bytes2hex, hex2bytes, is_hex),                         #hexadecimal string
    'base64' : (bytes2base64, base642bytes, is_base64),                #base64
    'int_big' : (bytes2int_big, int2bytes_big, None),             #integer, big endian conversion
    'int_little' : (bytes2int_little, int2bytes_little, None),    #integer, little endian conversion
    'int' : (bytes2int_big, int2bytes_big, lambda x: type(x) is int),                 #same as int_big
    'bin' : (bytes2bin, bin2bytes, is_bin),                         #binary string
    'bits' : (bytes2bits, bits2bytes, is_bits)                       #list of bits (the integers 0 and 1)
}

class Converter:
    #create a callable object that converts from encfrom to encto
    def __init__(self, encfrom, encto):
        self.encfrom = encfrom.strip().lower()
        self.encto = encto.strip().lower()
        if self.encfrom not in ENCODING_MAP or self.encto not in ENCODING_MAP:
            raise util.CryptoException("Bad encoding name")
        self.tobytes = ENCODING_MAP[self.encfrom][1]
        self.bytesto = ENCODING_MAP[self.encto][0]

    def __call__(self, val):
        return self.bytesto(self.tobytes(val))

#Returns the name of the encoding of val if it can be guessed, or None otherwise
def id_encoding(val):
    for name in sorted(ENCODING_MAP.keys()):
        checkfunc = ENCODING_MAP[name][2]
        if checkfunc is not None and checkfunc(val):
            return name
    return None

#convert val from the format encfrom to the format encto (as strings).
def convert(val, encfrom, encto):
    return Converter(encfrom, encto)(val)

#tries to determine the encoding of a automatically and convert it to encto.
#integers are converted as big-endian
#be careful of cases of ambiguity (such as hex vs b64) - the result could be either one.
def conv(val, encto):
    encfrom = id_encoding(val)
    if encfrom is None:
        raise util.CryptoException("Could not identify encoding.")
    return convert(val, encfrom, encto)

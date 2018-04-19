from cryptography.hazmat.primitives import hashes

from crypt import const

from crypt import byte
from crypt import encodings as enc
from crypt import numbers as num
from crypt import util

#hash b using the hash algorithm hfunc provided by cryptography
def get_hash(b, hfunc):
    digest = hashes.Hash(hfunc, const.BACKEND)
    digest.update(b)
    return digest.finalize()

def sha1(b):
    return get_hash(b, hashes.SHA1())

def sha256(b):
    return get_hash(b, hashes.SHA256())

def md5(b):
    return get_hash(b, hashes.MD5())

def sha512(b):
    return get_hash(b, hashes.SHA512())

#return the pad for the given message length
def sha1_get_pad(length):
    d = (55 - length) % 64
    lenbytes = byte.nullfill(enc.int2bytes_big(length*8), 8)
    return b'\x80' + d*b'\x00' + lenbytes

#the padding used by sha-1
def sha1_pad(b):
    return b + sha1_get_pad(len(b))

#execute a single round of sha-1, starting with the 20-byte internal state and applying the 64-byte data chunk
#returns the next internal 20-byte state, which is the final hash if this is the last round.
def sha1_round(state, chunk):
    h = [enc.bytes2int_big(block) for block in byte.get_blocks(state, 4)]   #5 4-byte blocks
    w = [enc.bytes2int_big(block) for block in byte.get_blocks(chunk, 4)]   #16 4-byte blocks
    mask = ~-(1<<32)
    for i in range(16, 80):
        w.append(util.lrotate(w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16], 1, 32))
    a, b, c, d, e = h
    for i in range(0, 80):
        if 0 <= i <= 19:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif 20 <= i <= 39:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif 40 <= i <= 59:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6
        temp = (util.lrotate(a, 5, 32) + f + e + k + w[i]) & mask
        e = d
        d = c
        c = util.lrotate(b, 30, 32)
        b = a
        a = temp
    h[0] += a
    h[1] += b
    h[2] += c
    h[3] += d
    h[4] += e
    for i in range(5):
        h[i] &= mask
    return byte.join_blocks(byte.nullfill(enc.int2bytes_big(h[i]), 4) for i in range(5))

#sha1 using my implementation (for testing)
def sha1_alt(b):
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0
    state = byte.join_blocks(byte.nullfill(enc.int2bytes_big(h), 4) for h in [h0, h1, h2, h3, h4])
    for chunk in byte.get_blocks(sha1_pad(b), 64):
        state = sha1_round(state, chunk)
    return state

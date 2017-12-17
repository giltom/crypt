import base64
import binascii
import math
from const import *
import string
import itertools
import os
import heapq

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

#hex string to bytes
def hex2bytes(hexstr):
    return bytes.fromhex(hexstr)

#bytes to hex string
def bytes2hex(b):
    return binascii.hexlify(b).decode('ASCII')

#bytes to base64 string
def bytes2base64(b):
    return base64.b64encode(b).decode('ASCII')

#convert hex string to base64 string
def hex2base64(hexstr):
    return b64encode(bytes.fromhex(hexstr)).decode('ASCII')

#base64 string to bytes
def base642bytes(s):
    return base64.b64decode(s)

#base64 string to hex string
def base642hex(s):
    return bytes2hex(base642bytes(s))

#xor all bytes in bytes objects (result is the length of the shorter input)
def xor(bytes1, bytes2):
    tot = bytearray()
    for b1,b2 in zip(bytes1, bytes2):
        tot.append(b1 ^ b2)
    return bytes(tot)

#xor all bytes, repeating bytes in the second argument.
def xor_repeat(b, repeat):
    tot = bytearray()
    for b1,b2 in zip(b, itertools.cycle(repeat)):
        tot.append(b1 ^ b2)
    return bytes(tot)

#xor the crib with the bytes, starting and the start index and skipping step bytes ahead each time
def xor_crib(b, crib, start, step):
    if len(crib) > step:
        raise Exception('Crib longer than step.')
    res = b[0:start]
    for i in range(start, len(b), step):
        res += xor(crib, b[i:])
        res += b[i+len(crib): i+step]
    return res

#list of crib results
def xor_crib_list(b, crib, start, step):
    res = []
    for i in range(start, len(b), step):
        res.append(xor(crib, b[i:]))
    return res

#xor two hex strings and return hex string
def xor_hex(hex1, hex2):
    return bytes2hex(xor(hex2bytes(hex1), hex2bytes(hex2)))

#number of printable characters
def num_printable(b):
    s = set(string.printable.encode('ASCII'))
    cnt = 0
    for byte in b:
        if byte in s:
            cnt += 1
    return cnt

#return list of length 256 of the count of each byte in the given bytes
def count_bytes(b):
    counts = [0]*256
    for byte in b:
        counts[byte] += 1
    return counts

#Cumulative standard normal distribution
def phi(x):
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

#approximate the probability of getting the byte frequencies of b, counting only some bytes
#assuming each byte is independent and approximating using a normal distribution.
#probs is a dict whose keys are ints in range(0,256) and whose values should be floats that sum to 1
#probs[i] is the probability of a given byte being i
#bytes that are not keys in probs are ignored.
#this is a decent metric if the frequency of each byte is fairly regular (i.e. english text)
def normal_byte_dist(b, probs):
    score = 1
    freqs = count_bytes(b)
    length = 0
    for byte in b:
        if byte in probs:
            length += 1
    for byte in probs:
        #approximate normal distribution
        expect = probs[byte] * length
        dev = math.sqrt(expect * (1 - probs[byte]))
        prob = phi((freqs[byte] + 0.5 - expect) / dev) - phi((freqs[byte] - 0.5 - expect) / dev)
        score *= prob
    return score

def all_printable(b):
    s = set(string.printable.encode('ASCII'))
    return all(byte in s for byte in b)

def all_nonws(b):
    s = set(string.printable.encode('ASCII')) - set(string.whitespace.encode('ASCII'))
    return all(byte in s for byte in b)

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

#count number of non-overlapping substrings in b using the given wordlist, which should be a list of bytes
def count_substrings(b, wordlist):
    count = 0
    for word in wordlist:
        count += b.count(word)
    return count

#count number of whitespace-surrounded words in b that appear in wordlist.
#if lower is given, converts to lowercase.
def count_words(b, wordlist, lower=False):
    count = 0
    for word in b.split():
        w = word.lower() if lower else word
        if w in wordlist:
            count += 1
    return count

#The lower this is, the closer it is to the given distribution
def freq_dist(b, probs):
    counts = count_bytes(b)
    tot = sum(counts[i] for i in probs)
    return math.sqrt(math.fsum((counts[i]/tot - probs[i])**2 for i in probs))

#Return inverse of distance between "frequency vectors"
#This is my best metric for automated frequency analysis
#The higher this is, the closer it is to the given distribution
def inverse_freq_dist(b, probs):
    return 1/freq_dist(b, probs)

#Lower all characters in the string and remove non-letter characters:
def to_alpha(b):
    return bytes(filter(lambda byte: chr(byte) in string.ascii_lowercase, b.lower()))

def alpha_freq_score(b):
    return inverse_freq_dist(to_alpha(b), FREQ_ALPHA)

def nonws_freq_score(b):
    return inverse_freq_dist(b, FREQ_NONWS)

#Return a list of (key,plaintext,score) triples sorted by a score.
#Each key in keys is tried, using decfn(cipher, key)
#Plaintexts are evaluated with scorefn, which must accept a bytes and return a numeric score
#filt can be a function that accepts a plaintext and returns a boolean. Only plaintexts for which it returns True will be checked.
#if maxkeys is None, will only store up to maxkeys keys in memory.
def rank_keys(cipher, keys, decfn, scorefn, filt=None, maxkeys=None):
    res = set()
    for key in keys:
        plain = decfn(cipher, key)
        if filt is None or filt(plain):
            score = scorefn(plain)
            if maxkeys is None or len(res) < maxkeys:
                res.add((key,plain,score))
            else:
                minkey = min(res, key=lambda t: t[2])
                if score > minkey[2]:
                    res.remove(minkey)
                    res.add((key,plain,score))
    res = list(res)
    res.sort(key=lambda t: t[2], reverse=True)
    return res

#return (key,plaintext) with best rank returned by rank_keys
def rank_best(cipher, keys, decfn, scorefn, filt=None):
    res = rank_keys(cipher, keys, decfn, scorefn, filt=filt, maxkeys=1)
    if len(res) == 0:
        return None
    return res[0][0], res[0][1]

#number of ones in binary integer
def count_ones(byte):
    tot = 0
    while byte:
        tot += byte & 1
        byte >>= 1
    return tot

#number of different bits (1s in the xor)
def hamming_distance(b1, b2):
    return sum(count_ones(byte) for byte in xor(b1,b2))

#hamming distance divided by the number of bytes
def normalized_hamming_distance(b1, b2):
    return hamming_distance(b1,b2)/min(len(b1),len(b2))

#partition bytes into blocks of given size
def get_blocks(b, blocksize):
    blocks = []
    for i in range(0, (len(b)//blocksize)*blocksize, blocksize):
        blocks.append(b[i:i+blocksize])
    return blocks

#iterator of blocks
def iter_blocks(b, blocksize):
    for i in range(0, (len(b)//blocksize)*blocksize, blocksize):
        yield b[i:i+blocksize]

#join list of blocks
def join_blocks(blocks):
    b = b''
    for block in blocks:
        b += block
    return b

#average of normalized hamming distance between every two blocks in the bytes object
#This is low when the texts are similar, making it a good metric for the key length in the vigenere cipher
def average_block_hamming(b, bsize):
    blocks = get_blocks(b, bsize)
    if len(blocks) <= 1:
        return 4
    npairs = len(blocks) * (len(blocks) - 1) / 2    #n choose 2
    tot = math.fsum(normalized_hamming_distance(b1,b2) for b1,b2 in itertools.combinations(blocks, r=2))
    return tot / npairs

#return pkcs#7 padded bytes
def pkcs7_pad(b, bsize):
    padder = padding.PKCS7(bsize*8).padder()
    return padder.update(b) + padder.finalize()

def pkcs7_unpad(b, bsize):
    unpadder = padding.PKCS7(bsize*8).unpadder()
    return unpadder.update(b) + unpadder.finalize()

def pkcs7_pad_16(b):
    return pkcs7_pad(b, 16)

def pkcs7_unpad_16(b):
    return pkcs7_unpad(b, 16)

def pkcs7_is_valid(b, bsize):
    try:
        pkcs7_unpad(b, bsize)
        return True
    except ValueError:
        return False

#AES encryption using given mode and padding function or no padding if None (will raise an exception if padding is required by the mode).
def aes_encrypt(plaintext, key, mode, pad=None):
    cipher = Cipher(algorithms.AES(key), mode, backend=BACKEND)
    encryptor = cipher.encryptor()
    padded = plaintext if pad is None else pad(plaintext)
    return encryptor.update(padded) + encryptor.finalize()

def aes_decrypt(ciphertext, key, mode, unpad=None):
    cipher = Cipher(algorithms.AES(key), mode, backend=BACKEND)
    decryptor = cipher.decryptor()
    plain = decryptor.update(ciphertext) + decryptor.finalize()
    return plain if unpad is None else unpad(plain)

def aes_encrypt_ecb(plaintext, key, pad=pkcs7_pad_16):
    return aes_encrypt(plaintext, key, ECB_MODE, pad=pad)

def aes_decrypt_ecb(ciphertext, key, unpad=pkcs7_unpad_16):
    return aes_decrypt(ciphertext, key, ECB_MODE, unpad=unpad)

def aes_encrypt_cbc(plaintext, key, iv, pad=pkcs7_pad_16):
    return aes_encrypt(plaintext, key, modes.CBC(iv), pad=pad)

def aes_decrypt_cbc(ciphertext, key, iv, unpad=pkcs7_unpad_16):
    return aes_decrypt(ciphertext, key, modes.CBC(iv), unpad=unpad)

#check if a block repeats itself
def has_repeated_block(b, bsize):
    blocks = get_blocks(b, bsize)
    return len(set(blocks)) < len(blocks)

def random_aes_key():
    return os.urandom(16)

#performs replacements on byte/string according to given dict
def replace_all(b, d):
    for key in d:
        b = b.replace(key, d[key])
    return b

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

def lfsr_stream(nbits, start, feedback_bit, length):
    reg = start
    out = ''
    for _ in range(length):
        bit = reg & 1
        out += str(bit)
        feedback = 1 if reg & (1 << feedback_bit) else 0
        reg = (reg >> 1) | ((feedback ^ bit) << (nbits - 1))
    return out

#true if square number
def is_square(n):
    start = n - 1
    prev = start
    while True:
        new = (prev + start // prev) >> 1
        if new == prev:
            return False
        if new > prev:
            return True
        prev = new

#integer square root (rounded down)
def isqrt(n):
    x = n
    y = (x + 1) >> 1
    while y < x:
        x = y
        y = (x + n // x) >> 1
    return x

#multiplicative inverse of a mod n
def mult_inverse(a, n):
    n0 = n
    a0 = a
    t0 = 0
    t = 1
    q = n0 // a0
    r = n0 - q*a0
    while r > 0:
        temp = (t0 - q*t) % n
        t0 = t
        t = temp
        n0 = a0
        a0 = r
        q = n0 // a0
        r = n0 - q*a0
    if a0 != 1:
        raise Exception('No inverse!')
    return t

#returns r,s,t such that r = gcd(a,b) and sa + tb = r
def extended_euclidian(a, b):
    t0 = 0
    t = 1
    s0 = 1
    s = 0
    q = a // b
    r = a - q * b
    while r > 0:
        temp = t0 - q * t
        t0 = t
        t = temp
        temp = s0 - q*s
        s0 = s
        s = temp
        a = b
        b = r
        q = a // b
        r = a - q * b
    r = b
    return (r,s,t)

#cubic root of integer
def icbrt(a):
    n = 0
    while (1 << (3*(n+1)) < a):
        n += 1
    res = 1 << n
    for i in range(n-1, -1, -1):
        val = res | (1 << i)
        if val**3 < a:
            res = val
    if (res + 1)**3 == a:
        return res + 1
    return res

#computes x**y mod n. y can be negative, in which case the multiplicative inverse of x will be used.
def pow_neg(x, y, n):
    if y < 0:
        x = mult_inverse(x, n)
        y = -y
    return pow(x, y, n)

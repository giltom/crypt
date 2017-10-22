import base64
import binascii
import math
from const import *
import string
import itertools

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

#xor all bytes in bytes objects (result is the length of the shorted input)
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

#xor two hex strings and return hex string
def xor_hex(hex1, hex2):
    return bytes2hex(xor(hex2bytes(hex1), hex2bytes(hex2)))

#return list of length 256 of the count of each byte in the given bytes
def byte_freq(b):
    counts = [0]*256
    for byte in b:
        counts[byte] += 1
    return counts

#Cumulative standard normal distribution
def phi(x):
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

#approximate the probability of getting the byte frequencies of b, counting only some bytes
#assuming each byte is independent and approximates using a normal distribution.
#probs is a dict whose keys are ints in range(0,256) and whose values should be floats that sum to 1
#probs[i] is the probability of a given byte being i
#bytes that are not keys in probs are ignored.
#this is a decent metric if the frequency of each byte is fairly regular (i.e. english text)
def normal_byte_dist(b, probs):
    score = 1
    freqs = byte_freq(b)
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

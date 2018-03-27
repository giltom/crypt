import string
import math
import itertools

from crypt import util
from crypt import encodings as enc
from crypt import const

#xor all bytes in bytes objects (result is the length of the shorter input)
def xor(bytes1, bytes2):
    length = min(len(bytes1), len(bytes2))
    tot = bytearray(length)
    for i in range(length):
        tot[i] = bytes1[i] ^ bytes2[i]
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
        raise util.CryptoException('Crib longer than step.')
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
    return enc.bytes2hex(xor(enc.hex2bytes(hex1), enc.hex2bytes(hex2)))

#number of printable characters
def num_printable(b):
    cnt = 0
    for byte in b:
        if byte in const.CHARS_PRINTABLE:
            cnt += 1
    return cnt

#return list of length 256 of the count of each byte in the given bytes
def count_bytes(b):
    counts = [0]*256
    for byte in b:
        counts[byte] += 1
    return counts

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
    return all(byte in const.CHARS_PRINTABLE for byte in b)

def all_nonws(b):
    return all(byte in const.CHARS_PRINTABLE_NONWS for byte in b)

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
    return inverse_freq_dist(to_alpha(b), const.FREQ_ALPHA)

def nonws_freq_score(b):
    return inverse_freq_dist(b, const.FREQ_NONWS)

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

#normalized hamming distance between 1st two blocks
def first_blocks_hamming(b, bsize):
    return normalized_hamming_distance(b[0:bsize], b[bsize:2*bsize])

#check if a block repeats itself
def has_repeated_block(b, bsize):
    blocks = get_blocks(b, bsize)
    return len(set(blocks)) < len(blocks)

#iterate bits (1 or 0) of given bytes object, starting at the MSB of the first byte
def bits(b):
    pos = 7
    for byte in b:
        yield (byte >> pos) & 1
        pos = (pos - 1) % 8

#iterate bits (1 or 0) of given bytes object, starting at the LSB of the first byte
def bits_lsb(b):
    pos = 0
    for byte in b:
        yield (byte >> pos) & 1
        pos = (pos + 1) % 8

#performs replacements on byte/string according to given dict
def replace_all(b, d):
    for key in d:
        b = b.replace(key, d[key])
    return b

#adds null bytes to the start of b to that it is n bytes long
def nullfill(b, n):
    if len(b) >= n:
        return b
    return (n - len(b))*b'\0' + b

#same, but add to the end of b
def nullfill_r(b, n):
    if len(b) >= n:
        return b
    return b + (n - len(b))*b'\0'

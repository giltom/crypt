from cryptutil import *
from challenge import *
import random

cipherhex = '6e19223f204b31183e333f005c122d37264a350e3e3c2808672436250b3f3d1b2e2c151c671d553e182b4713262c3f045c1d553e0b3f391c1449385d7309223c20153d022d3c011a673322394822242e0118003a5a1333123b222b361b22353d5110231230222b1f102c28566e03281a2e21240c041e3e2d491337022e313b26181a3a5a532919122a31343e071f2e2d4928531a2e31342607713702673a3963140b1737001c0f5c742d3a172e133a331b4b3d167f090418210b3a31390d0f025933390810023a334e0e2427733c021818081119141c0928552629170c172a230f08373808246a0a113d142645421b357e0853327132013d2439243565000c190514093d3f171b0b6503070a2f001b2e0d140a0e6a7f0a340522442d1a3d17356913500870290b2e31435d0d7a32061e70101f7e2f495d5f6730263a1a4b39042d49055f6d79506d48'

cipher = hex2bytes(cipherhex)

keybytes = list(set(string.printable.encode('ASCII')) - set(string.whitespace.encode('ASCII')))
pbytes = set(string.ascii_letters.encode('ASCII') + string.digits.encode('ASCII') + b'+/')

def is_valid_kbyte(kbyte, pos, keylen, cipher):
    for i in range(pos, len(cipher), keylen):
        pbyte = kbyte ^ cipher[i]
        if i == len(cipher) - 1:
            if pbyte != ord('\n'):
                return False
            continue
        if not (
                pbyte in pbytes or
                (pbyte == ord('=') and (i == len(cipher) - 3 or i == len(cipher) - 2))
            ):
            return False
    return True

def get_options(keylen, cipher):
    key = []
    for i in range(keylen):
        options = []
        for kbyte in keybytes:
            if is_valid_kbyte(kbyte, i, keylen, cipher):
                options.append(kbyte)
        if len(options) == 0:
            return None
        key.append(options)
    return key

def score_text(p):
    #return average_block_hamming(p, 1)
    return freq_dist(p, FREQ_BASE64) + average_block_hamming(p, 1)

for keylen in range(120, 121):
    options = get_options(keylen, cipher)
    if options is None:
        continue
    print('Key length', keylen)
    key = bytearray(keylen)
    for i in range(keylen):
        chars = cipher[i::keylen]
        best = min(options[i], key=lambda b: score_text(xor_repeat(chars, bytes([b]))))
        key[i] = best
    text = base642bytes(xor_repeat(cipher, key))
    print(text)
    #print(b''.join(bytes([x]) for x in text if x in string.printable.encode('ASCII')))

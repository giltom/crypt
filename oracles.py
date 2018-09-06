import random
import os
from collections import OrderedDict

from crypt import byte
from crypt import symmetric as sym
from crypt import padders as pad

#appends a constant prefix and suffix to the plaintext, then encrypts with the given function
#it should accept a plaintext.
#performs replacesments on plaintext before encryption with the replace dict.
def insert_encrypt_oracle(prefix, suffix, encrypt, replace={}):
    return lambda p: encrypt(prefix + byte.replace_all(p, replace) + suffix)

#Returns an encrypting oracle with AES in ECB mode with a random constant key
def aes_ecb_encrypt_oracle():
    key = sym.random_aes_key()
    return lambda p: sym.aes_encrypt_ecb(p, key)

#Returns an encrypting oracle with AES in CBC mode with a random constant key and a random changing IV
def aes_cbc_encrypt_oracle():
    key = sym.random_aes_key()
    return lambda p: sym.aes_encrypt_cbc(p, key, os.urandom(16))

#randomly choose aes or cbc (random iv), and random key.
#also adds a random prefix and suffix
def aes_random_encrypt(plaintext):
    key = sym.random_aes_key()
    prefix = os.urandom(random.randint(0,32))
    suffix = os.urandom(random.randint(0,32))
    text = prefix + plaintext + suffix
    if random.randint(0,1):
        print('Using ecb')
        return sym.aes_encrypt_ecb(text, key)
    else:
        print('Using cbc')
        return sym.aes_encrypt_cbc(text, key, os.urandom(16))



####Profile challenge

#parses bytes such as b'foo=bar&baz=qux&zap=zazzle' into a dict
def parse_cookie(cookie):
    res = OrderedDict()
    for part in cookie.split(b'&'):
        if part.count(b'=') != 1:
            raise Exception('Bad cookie format.')
        key,val = part.split(b'=')
        if key in res:
            raise Exception('Duplicate key.')
        res[key] = val
    return res

#encodes a dict as above
def encode_cookie(d):
    parts = [key + b'=' + d[key] for key in d]
    return b'&'.join(parts)

def profile_for(email):
    od = OrderedDict()
    od[b'email'] = email.replace(b'&',b'').replace(b'=',b'')
    od[b'uid'] = b'10'
    od[b'role'] = b'user'
    return od

cookie_key = sym.random_aes_key()

#generate profile, encode it, then encrypt
def encrypt_cookie_oracle(email):
    cookie = encode_cookie(profile_for(email))
    return sym.aes_encrypt_ecb(cookie, cookie_key)

#decrypt then parse
def decrypt_cookie(ciphertext):
    cookie = sym.aes_decrypt_ecb(ciphertext, cookie_key)
    return parse_cookie(cookie)

#Returns function accepting ciphertext and decrypting with given IV, returning True if PKCS7 padding on plaintext is valid.
#bsize is block size
def pkcs7_padding_oracle(decrypter, bsize):
    return lambda c, iv: pad.pkcs7_is_valid(decrypter(c, iv), bsize)

#Returns decrypter for given key in AES CBC mode, using given padding or no padding if None
def aes_cbc_decrypter(key, unpadder=pad.pkcs7_unpad_16):
    return lambda c, iv: sym.aes_decrypt_cbc(c, key, iv, unpadder=unpadder)

#Returns encrypter for given key in AES CBC mode, using given padding or no padding if None (will throw error if bad size).
def aes_cbc_encrypter(key, padder=pad.pkcs7_pad_16):
    return lambda p, iv: sym.aes_encrypt_cbc(p, key, iv, padder=padder)

#Returns oracle that returns true if given ciphertext and IV decrypt to plaintext with valid PKCS7 padding
def aes_cbc_pkcs7_padding_oracle(key):
    return pkcs7_padding_oracle(aes_cbc_decrypter(key, unpadder=None), 16)

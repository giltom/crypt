import os
import itertools

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from crypt import const
from crypt import padders as pad
from crypt import byte
from crypt import encodings as enc
from crypt import util

def symmetric_encrypt(plaintext, algorithm, mode=None, padder=None):
    cipher = Cipher(algorithm, mode, backend=const.BACKEND)
    encryptor = cipher.encryptor()
    padded = plaintext if padder is None else padder(plaintext)
    return encryptor.update(padded) + encryptor.finalize()

def symmetric_decrypt(ciphertext, algorithm, mode=None, unpadder=None):
    cipher = Cipher(algorithm, mode, backend=const.BACKEND)
    decryptor = cipher.decryptor()
    plain = decryptor.update(ciphertext) + decryptor.finalize()
    return plain if unpadder is None else unpadder(plain)

#AES encryption using given mode and padding function or no padding if None (will raise an exception if padding is required by the mode).
def aes_encrypt(plaintext, key, mode, padder=None):
    return symmetric_encrypt(plaintext, algorithms.AES(key), mode, padder=padder)

def aes_decrypt(ciphertext, key, mode, unpadder=None):
    return symmetric_decrypt(ciphertext, algorithms.AES(key), mode, unpadder=unpadder)

def aes_encrypt_block(plaintext, key):
    if len(plaintext) != 16:
        raise util.CryptoException('Plaintext must be 16 bytes')
    return aes_encrypt(plaintext, key, modes.ECB(), padder=None)

def aes_decrypt_block(ciphertext, key):
    if len(ciphertext) != 16:
        raise util.CryptoException('Ciphertext must be 16 bytes')
    return aes_decrypt(plaintext, key, modes.ECB(), unpadder=None)

def aes_encrypt_ecb(plaintext, key, padder=pad.pkcs7_pad_16):
    return aes_encrypt(plaintext, key, modes.ECB(), padder=padder)

def aes_decrypt_ecb(ciphertext, key, unpadder=pad.pkcs7_unpad_16):
    return aes_decrypt(ciphertext, key, modes.ECB(), unpadder=unpadder)

def aes_encrypt_cbc(plaintext, key, iv, padder=pad.pkcs7_pad_16):
    return aes_encrypt(plaintext, key, modes.CBC(iv), padder=padder)

def aes_decrypt_cbc(ciphertext, key, iv, unpadder=pad.pkcs7_unpad_16):
    return aes_decrypt(ciphertext, key, modes.CBC(iv), unpadder=unpadder)

def aes_encrypt_cfb(plaintext, key, iv):
    return aes_encrypt(plaintext, key, modes.CFB(iv))

def aes_decrypt_cfb(ciphertext, key, iv):
    return aes_decrypt(ciphertext, key, modes.CFB(iv))

def random_aes_key():
    return os.urandom(16)

def blowfish_encrypt(plaintext, key, mode, padder=pad.pkcs7_pad_8):
    return symmetric_encrypt(plaintext, algorithms.Blowfish(key), mode, padder=padder)

def blowfish_decrypt(ciphertext, key, mode, unpadder=pad.pkcs7_unpad_8):
    return symmetric_decrypt(ciphertext, algorithms.Blowfish(key), mode, unpadder=unpadder)

#LFSR with a single feedback bit. Returns bit-list of required length.
def lfsr_1bit(nbits, start, feedback_bit, length):
    reg = start
    out = []
    for _ in range(length):
        bit = reg & 1
        out.append(bit)
        feedback = 1 if reg & (1 << feedback_bit) else 0
        reg = (reg >> 1) | ((feedback ^ bit) << (nbits - 1))
    return out

#An alternative way to generate a CTR keystream.
#nonce must have a length of half of the block size.
#The first len(nonce) bytes of the block are the nonce.
#The last len(nonce) bytes of the block are a running counter, little endian.
def ctr_alt_ptext_stream(nonce):
    ctr = 0
    half_bsize = 1 << len(nonce)
    while True:
        yield nonce + enc.int2bytes_little(ctr, size=len(nonce))
        ctr = (ctr + 1) % half_bsize

def aes_ctr_alt_keystream(key, nonce):
    if len(nonce) != 8:
        raise util.CryptoException('Nonce must be 8 bytes')
    for block in ctr_alt_ptext_stream(nonce):
        cblock = aes_encrypt_block(block, key)
        for b in cblock:
            yield b

#works for both encryption and decryption
def aes_ctr_alt_crypt(text, key, nonce):
    return byte.xor(text, aes_ctr_alt_keystream(key, nonce))

def rc4_stream(key, alphabet=None):
    if alphabet is None:
        alphabet = range(256)
    perm = list(alphabet)
    length = len(perm)
    j = 0
    for i in range(length):
        j = (j + perm[i] + key[i % len(key)]) % length
        perm[i], perm[j] = perm[j], perm[i]
    i = 0
    j = 0
    while True:
        i = (i + 1) % length
        j = (j + perm[i]) % length
        perm[i], perm[j] = perm[j], perm[i]
        yield perm[(perm[i] + perm[j]) % length]

def stream_slice(stream, *args):
    return bytes(itertools.islice(stream, *args))
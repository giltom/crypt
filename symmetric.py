import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from crypt import const
from crypt import padders as pad

#AES encryption using given mode and padding function or no padding if None (will raise an exception if padding is required by the mode).
def aes_encrypt(plaintext, key, mode, padder=None):
    cipher = Cipher(algorithms.AES(key), mode, backend=const.BACKEND)
    encryptor = cipher.encryptor()
    padded = plaintext if padder is None else padder(plaintext)
    return encryptor.update(padded) + encryptor.finalize()

def aes_decrypt(ciphertext, key, mode, unpadder=None):
    cipher = Cipher(algorithms.AES(key), mode, backend=const.BACKEND)
    decryptor = cipher.decryptor()
    plain = decryptor.update(ciphertext) + decryptor.finalize()
    return plain if unpadder is None else unpadder(plain)

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

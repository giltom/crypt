import random

from cryptography.hazmat.primitives import serialization

from crypt import numbers as num
from crypt import encodings as enc
from crypt import const

def rsa_encrypt(p, e, n):
    return pow(p, e, n)

def rsa_decrypt(c, d, n):
    return pow(c, d, n)

#goldwasser-micali encryption. input is bytes and output is a list of integers.
def gm_encrypt(p, x, n):
    rand = random.SystemRandom()
    res = []
    for bit in enc.bytes2bits(p):
        y = rand.randrange(n)
        while gcd(y, n) != 1:
            y = rand.randrange(n)
        res.append((y**2 * x**bit) % n)
    return res

#goldwasser-micali decryption. input is a list of integers and output is bytes.
def gm_decrypt(c, p, q):
    bits = []
    for val in c:
        if num.is_quad_residue(val % p, p) and num.is_quad_residue(val % q, q):
            bits.append(0)
        else:
            bits.append(1)
    return enc.bits2bytes(bits)

#generate goldwasser-micali key as x,n,p,q
def gm_keygen(nbits):
    p = num.gen_random_prime(nbits//2)
    q = num.gen_random_prime(nbits//2)
    n = p*q
    rand = random.SystemRandom()
    x = rand.randrange(n)
    while num.legendre(x, p) != -1 or num.legendre(x, q) != -1:
        x = rand.randrange(n)
    return x, n, p, q

#parse the SSH publice key file given by fname and return n,e
def parse_ssh_rsa_public_key(fname):
    f = open(fname, 'rb')
    key = serialization.load_ssh_public_key(f.read(), const.BACKEND)
    nums = key.public_numbers()
    return nums.n, nums.e

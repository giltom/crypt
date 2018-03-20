import random

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

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
    f.close()
    nums = key.public_numbers()
    return nums.n, nums.e

#Return the prime factors p,q of n. e is the public exponent and d is the private exponent.
def rsa_factor_given_private_key(n, e, d):
    return rsa.rsa_recover_prime_factors(n, e, d)

#Creates a PEM-format RSA private key in the file fname, using the modulus n, public exponent e and private exponent d
def make_pem_rsa_key(fname, n, e, d):
    p, q = rsa_factor_given_private_key(n, e, d)
    dmp1 = d % (p - 1)
    dmq1 = d % (q - 1)
    iqmp = num.mod_inverse(q, p)
    pub_nums = rsa.RSAPublicNumbers(e, n)
    priv_nums = rsa.RSAPrivateNumbers(p, q, d, dmp1, dmq1, iqmp, pub_nums)
    key = priv_nums.private_key(const.BACKEND)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    )
    with open(fname, 'wb') as f:
        f.write(pem)

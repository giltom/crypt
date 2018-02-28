from crypt.cryptutil import *
from crypt.oracles import *
from crypt.const import *
import os
import itertools
import heapq
import string

#returns key,plaintext or None
def break_single_char_xor(b):
    return rank_best(b, keys, lambda c,k: xor_repeat(c, bytes([k])), nonws_freq_score, filt=is_base64)

#break repeating key xor ("vigenere cipher") with frequency analysis
def break_repeating_xor(b, n=1000):
    res = []
    keylens = heapq.nsmallest(n, range(1,len(b)//2), key=lambda i: average_block_hamming(b, i))
    for keylen in keylens:
        print(keylen)
        key = b''
        notfound = False
        for offset in range(keylen):
            s = b[offset::keylen]
            char = break_single_char_xor(s)
            if char is None:
                notfound = True
                break
            byte = char[0]
            key += bytes([byte])
        if notfound:
            continue
        res.append((key, xor_repeat(b, key)))
    return res

#oracle should accept a plaintext and encrypt it however it wants. it can add a prefix and suffix.
#Will determine if uses ECB mode with just one encryption
def is_ecb_mode(bsize, oracle):
    nblocks = random.randint(100,200)
    block = os.urandom(bsize)
    cipher = oracle(block * (nblocks+1))
    blocks = get_blocks(cipher, bsize)
    #check if there is a sequence of N_BLOCKS (+1) consecutive equal blocks
    i = 0
    while i < len(blocks):
        curr = i
        while curr < len(blocks) - 1 and blocks[curr+1] == blocks[curr]:
            curr += 1
        cnt = curr - i + 1
        if cnt == nblocks or cnt == nblocks+1:
            return True
        i = curr + 1
    return False

#Oracle should accept a plaintext, add a prefix and suffix to it, and then encrypt it with ECB
#using a constant key.
#Returns the block size, the start index of the inserted text.
def ecb_identify_block(oracle):
    NCHECKS = 10
    #Find start index of start block of text:
    start = 0
    ciphers = [oracle(os.urandom(1)) for _ in range(NCHECKS)]
    while all(ciphers[i][start] == ciphers[0][start] for i in range(1,NCHECKS)):
        start += 1
    #Find the distance between the start of the text to the start of the next block:
    dist = 0
    while True:
        text = os.urandom(dist)
        check = oracle(text)[start]
        if all(check == oracle(text + os.urandom(1))[start] for _ in range(NCHECKS)):      #try multiple bytes to be certain
            break
        dist += 1
    #Find end index of block (start of next block):
    end = start + 1
    ciphers = [oracle(b'a'*dist + os.urandom(1)) for _ in range(NCHECKS)]
    while all(ciphers[i][end] == ciphers[0][end] for i in range(1,NCHECKS)):
        end += 1
    return end - start, end - dist  #block size, start of string

#Oracle should accept a plaintext, add a prefix and suffix to it, and then encrypt it with ECB using a constant key.
#Decrypts the suffix.
#Determines block size automatically.
def break_ecb_insert(oracle):
    bsize, start = ecb_identify_block(oracle)
    prefix = b'a' * (bsize - start % bsize)     #prefix added to get to start of next block
    res = b''
    for bstart in range((start // bsize + 1) * bsize, len(oracle(prefix)), bsize):  #for each block
        for i in range(bsize):  #find the ith character in the block
            text = prefix + b'a'*(bsize - i - 1)
            actual = oracle(text)[bstart:bstart + bsize]
            for byte in range(256):
                cipher = oracle(text + res + bytes([byte]))[bstart:bstart + bsize]
                if cipher == actual:
                    res += bytes([byte])
                    break
    return res

#Padding oracle attack against CBC encryption with given block size and IV. Decrypts full ciphertext.
#oracle should accept a ciphertext and IV and return True if resulting plaintext has valid PKCS7 padding.
#Can safely assume that the given IV will always be used in oracle queries, so the IV argument of the oracle can be ignored in the oracle implementation.
#However the IV is needed to decrypt the first block (other blocks will be correct even if the IV is wrong).
def pkcs7_padding_oracle_attack(oracle, bsize, ciphertext, iv):
    dblocks = []    #raw decrypted blocks before they are XORed with each other
    cblocks = get_blocks(ciphertext, bsize) #ciphertext blocks
    for cblock in cblocks:   #current ciphertext block being decrypted
        text = bytearray(bsize) + cblock  #two blocks that we control and repeatedly change and send the oracle
        byteind = bsize - 1     #index in block of byte being decrypted
        while byteind >= 0:
            padlen = bsize - byteind - 1   #length of padding achieved up until now
            for i in range(bsize - 1, byteind, -1): #this does nothing on the 1st iteration
                text[i] = text[i] ^ padlen ^ (padlen + 1)   #xor bytes up to current index so we get almost valid padding except for one byte
            while not oracle(bytes(text), iv):  #go through all byte values until we get valid padding
                text[byteind] += 1
            byteind -= 1
            while byteind >= 0:
                text[byteind] ^= 1  #flip a bit to see if the padding gets fucked up
                answer = oracle(bytes(text), iv)
                text[byteind] ^= 1  #flip it back
                if answer:    #stop if padding is good - this means we reached the end of the decrypted bytes
                    break
                byteind -= 1
        for i in range(0, bsize):   #at this point the "plaintext" decrypted by the oracle ends in a full block of bsizes, xor to cancel them out and get the decryption.
            text[i] ^= bsize
        dblocks.append(bytes(text[0:bsize]))
    #We now have the decrypted ciphertext blocks, before they are xored with each other (as if decrypted in ECB mode)
    #all that's left is to simulate CBC mode and get the real plaintext
    plain = xor(dblocks[0], iv)
    for i in range(1, len(dblocks)):
        plain += xor(dblocks[i], cblocks[i-1])
    return plain

#Finds RSA decryption exponent corresponding to the encryption exponent e and modulus n.
#Only works if d < n**(1/4)/3. This is may be the case if the encryption exponent is very is large.
#Returns d,p,q where d is the decryption exponent and p,q are the prime factors of n.
def wieners_algorithm(n, e):
    for t, d in convergents(e, n):
        if t == 0:
            continue
        mult = d * e - 1
        if mult % t == 0:
            phin = mult // t
            b = n - phin + 1
            p = (b - isqrt(b**2 - 4*n)) // 2    #we are solving a quadratic equation
            if n % p == 0:
                return d, p, n // p
    raise Exception('Could not execute wiener\'s algorithm; Could the decryption exponent be too large?')

#Attempt to factor n into two integers p*q. Only viable if p is near q.
def fermat_factor(n):
    a = isqrt(n)
    if a*a == n:
        return a,a
    while True:
        a += 1
        b = a*a - n
        if is_square(b):
            break
    sqrtb = isqrt(b)
    return a - sqrtb, a + sqrtb

#Trial division factoring. Returns a factor of n or None if n is prime.
def trial_factor(n):
    sqn = isqrt(n)

#Breaks textbook elgamal signature when the same random nonce is used twice.
#Arguments:
#p - prime modulus.
#alpha, beta - elgamal public key.
#gamma - 1st part of signature, used twice.
#delta1, delta2 - 2nd parts of the two signatures.
#m1, m2 - the two messages signed.
#Returns (a,k), where a is the private key and k is the nonce used.
def elgamal_break_two_signatures(p, alpha, beta, gamma, m1, delta1, m2, delta2):
    if delta2 > delta1:
        delta1, delta2 = delta2, delta1
        m1, m2 = m2, m1
    d = gcd(delta1 - delta2, p-1)
    mt = (m1 - m2) // d
    deltat = (delta1 - delta2) // d
    pt = (p-1) // d
    kmodpt = (mt * mod_inverse(deltat, pt)) % pt
    for i in range(d):
        k = (kmodpt + i*pt) % (p-1)
        if pow(alpha, k, p) == gamma:
            dt = gcd(gamma, p-1)
            gammat = gamma // dt
            ptt = (p-1) // dt
            righthand = (m1 - k * delta1) // dt
            amodptt = (mod_inverse(gammat, ptt) * righthand) % ptt
            for j in range(dt):
                a = (amodptt + i*ptt) % (p-1)
                if pow(alpha, a, p) == beta:
                    return a,k
    raise Exception('Error: could not calculate elgamal private key.')

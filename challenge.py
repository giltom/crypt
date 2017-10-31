from cryptutil import *
import os
from oracles import *
import itertools

#returns key,plaintext
def break_single_char_xor(b):
    return rank_best(b, range(256), lambda c,k: xor_repeat(c, bytes([k])), nonws_freq_score, filt=all_printable)

#break repeating key xor ("vigenere cipher") with frequency analysis
def break_repeating_xor(b):
    keylen = min(range(2,41), key=lambda i: average_block_hamming(b, i))
    key = b''
    for offset in range(keylen):
        s = b[offset::keylen]
        byte = break_single_char_xor(s)[0]
        key += bytes([byte])
    return key, xor_repeat(b, key)

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

#Oracle should accept a plaintext, add a prefix and suffix to it, and then encrypt it with ECB
#using a constant key.
#Decrypts the suffix.
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

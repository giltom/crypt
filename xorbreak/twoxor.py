from crypt import byte
import heapq
import math

MINF = float('-inf')

#Decypts multiple ciphertexts that were encrypted by XORing with the same unknown key,
#using statistical data from the NGramStats object ngs.
#Prune is the prune level of ther search tree. Higher values are slower but more accurate.
#Returns the key used, *up to the length of the shortest ciphertext*.
#If verbose is true, prints progress messages
def break_multiple_xors(ciphertexts, ngs, prune=100, verbose=False):
    keylen = min(len(c) for c in ciphertexts)
    states = [(0, b'')] #this is a list of tuples, in the form cost, partial key
    for i in range(keylen):
        next_states = (
            (
                cost - math.fsum(
                    ngs.log_prob(pbyte, pprefix)
                    for pbyte, pprefix in guess_terms
                ),
                key
            )
            for cost, keystart in states
            for guess_terms, key in get_prob_terms(ciphertexts, ngs, keystart)
        )
        states = heapq.nsmallest(prune, next_states, key=lambda t: t[0])
        if verbose and (i+1) % 10 == 0:
            print('{:0.2%} Complete.'.format((i+1)/keylen))
    return min(states)[1]

#yields tuples of [list of (pbyte, pprefix)], key
def get_prob_terms(ciphertexts, ngs, keystart):
    i = len(keystart)
    kprefix = keystart[-ngs.maxlen + 1:]    #last maxlen-1 bytes of candidate partial key
    cdata = [
        (
            ctext[i],
            byte.xor(kprefix, ctext[max(0, i-ngs.maxlen+1) : i])
        )
        for ctext in ciphertexts
    ]
    for kbyte in range(256):
        guess_terms = []
        for cbyte, pprefix in cdata:
            pbyte = kbyte ^ cbyte
            if not ngs.is_byte_used(pbyte):
                break
            guess_terms.append((pbyte, pprefix))
        else:   #no break, valid guess
            key = keystart + bytes([kbyte])
            yield guess_terms, key
from crypt import byte
import heapq
import math

#Decypts multiple ciphertexts that were encrypted by XORing with the same unknown key,
#using statistical data from the NGramStats object ngs.
#Prune is the prune level of ther search tree. Higher values are slower but more accurate.
#Returns the key used, *up to the length of the shortest ciphertext*.
#If verbose is true, prints progress messages
def break_multiple_xors(ciphertexts, ngs, prune=100, verbose=False):
    keylen = min(len(c) for c in ciphertexts)
    states = [(0, b'')] #this is a list of tuples, in the form cost, partial key
    for i in range(keylen):
        next_states = []
        for cost, keystart in states:
            kprefix = keystart[-ngs.maxlen + 1:]    #last maxlen-1 bytes of candidate partial key
            for keyguess in range(256):
                prob = 1
                for ctext in ciphertexts:
                    pbyte = keyguess ^ ctext[i]
                    if not ngs.is_byte_used(pbyte):
                        prob = 0
                        break
                    cprefix = ctext[max(0, i - ngs.maxlen + 1) : i]
                    prob *= ngs.prob(pbyte, byte.xor(kprefix, cprefix))
                if prob != 0:
                    next_states.append((cost - math.log(prob), keystart + bytes([keyguess])))
        states = heapq.nsmallest(prune, next_states)
        if verbose and (i+1) % 10 == 0:
            print('{:0.2%} Complete.'.format((i+1)/keylen))
    return min(states)[1]

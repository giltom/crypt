import math
import argparse
import string
import itertools
import sys
import stats

#xor all bytes in bytes objects
def xor_all(bytes1, bytes2):
    tot = []
    for b1,b2 in zip(bytes1, bytes2):
        tot.append(b1 ^ b2)
    return bytes(tot)

#all 2-tuples of bytes p,q such that p ^ q = xor
def all_xor_pairs(xor):
    options = [((0,0),(1,1))]*8
    b = xor
    for i in range(8):
        if b & (0x80 >> i):
            options[i] = ((0,1),(1,0))
    for t in itertools.product(*options):
        p = 0
        q = 0
        for pbit,qbit in t:
            p = (p << 1) | pbit
            q = (q << 1) | qbit
        yield p,q

parser = argparse.ArgumentParser()
parser.add_argument('cipher1', type=argparse.FileType('rb'))
parser.add_argument('cipher2', type=argparse.FileType('rb'))
parser.add_argument('distfile', metavar='distribution')
parser.add_argument('-p', dest='prune', type=int, default=100, help='Prune search graph to given number of vertices after each iteration. Default: 100.')
parser.add_argument('-o1', dest='output1', help='file to write plaintext 1 to', type=argparse.FileType('wb'))
parser.add_argument('-o2', dest='output2', help='file to write plaintext 2 to', type=argparse.FileType('wb'))
parser.add_argument('-oa', dest='outputall', type=argparse.FileType('w'), help='File to write top plaintext-plaintext-key triples to (number given by -p).')
parser.add_argument('-n', dest='number', type=int, help='Number of plaintext-plaintext-key triples to write to output file (no effect if -oa isn\'t used). Can\'t be larger than the value given in -p.')
parser.add_argument('-q', dest='verbose', help='Do not print progress meter', action='store_false')
args = parser.parse_args()

PRUNE = args.prune #number of vertices to keep track of (memory usage and runtime increase too much if it is too large)

if args.number and args.number > PRUNE:
    print('-n can\'t be larger than -p.')
    sys.exit(1)

dist = stats.NGramStats(args.distfile, args.verbose)
cipher1 = args.cipher1.read()
cipher2 = args.cipher2.read()

#Use simplified version of viterbi algorithm to find the highest probability plaintext given a ciphertext and uneven key & plaintext distributions
#We prune the results after each iteration, so it doesn't really guarantee the best probability
#This is in order to avoid about 256^7 bytes of memory usage assuming n=7 (which is totally unrealistic)

if args.verbose:
    print('Attempting decryption...')
#Dictionary containing states of previous step
#Key is tuple of n-grams, value is the "length" of the shortest path to that state
states = {(b'', b''):0} #initial state is empty with 0 "length"
cipherlen = min(len(cipher1), len(cipher2))
for i,t in enumerate(zip(cipher1, cipher2)):
    newstates = {}
    for ostate in states:
        prefix1 = ostate[0][max(len(ostate[0]) - dist.n + 1, 0):]  #n last bytes of text 1
        prefix2 = ostate[1][max(len(ostate[1]) - dist.n + 1, 0):]  #n last bytes of text 2
        for p,q in all_xor_pairs(t[0] ^ t[1]):     #iterate over possible plaintext bytes
            prob = dist.prob(prefix1, p) * dist.prob(prefix2, q)
            length = states[ostate] - math.log(prob)   #maximizing the product of probabilities is equivalent to minimizing the sum of their logs
            #update newstates with new path information
            if len(newstates) < PRUNE:
                nstate = (ostate[0] + bytes([p]), ostate[1] + bytes([q]))
                newstates[nstate] = length
            else:
                maxstate = max(newstates, key=lambda s: newstates[s])
                if length < newstates[maxstate]:
                    del newstates[maxstate]
                    nstate = (ostate[0] + bytes([p]), ostate[1] + bytes([q]))
                    newstates[nstate] = length
    states = newstates
    text1,text2 = min(states, key=lambda s: states[s])
    if args.verbose and i % 10 == 0:
        print('{:.2%} complete.'.format(i/cipherlen))

if args.output1 is not None:
    args.output1.write(text1)
    args.output1.close()
if args.output2 is not None:
    args.output2.write(text2)
    args.output2.close()
if args.outputall is not None:
    i = 0
    for text1,text2 in sorted(states.keys(), key=lambda s: states[s]):
        print('Score:', math.exp(-states[(text1, text2)]), file=args.outputall)
        print('Plaintext 1:', text1, file=args.outputall)
        print('Plaintext 2:', text2, file=args.outputall)
        if len(text1) > len(text2):
            print('Key:', xor_all(cipher1, text1).hex(), file=args.outputall)
        else:
            print('Key:', xor_all(cipher2, text2).hex(), file=args.outputall)
        print(file=args.outputall)
        i += 1
        if args.number and i >= args.number:
            break
    args.outputall.close()

if args.verbose:
    #get "most probable" plaintext
    text1,text2 = min(states, key=lambda s: states[s])
    print('Top Paintext 1: {}\nHex: {}\nCiphertext 1: {}\nHex: {}\n\n'.format(text1, text1.hex(), cipher1, cipher1.hex()))
    print('Top Paintext 2: {}\nHex: {}\nCiphertext 2: {}\nHex: {}\n\n'.format(text2, text2.hex(), cipher2, cipher2.hex()))
    #get key by xoring plaintext with ciphertext
    print('Key (Hex): {}'.format(xor_all(cipher1, text1).hex()))

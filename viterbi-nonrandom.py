import nltk
import math
import pickle
import argparse
import string

parser = argparse.ArgumentParser()
parser.add_argument('ciphertext', type=argparse.FileType('rb'))
parser.add_argument('distfile', metavar='distribution', type=argparse.FileType('rb'))
parser.add_argument('depth', type=int)
parser.add_argument('prob1', metavar='1-probability', type=float)
parser.add_argument('-o', dest='output', help='file to write plaintext to', type=argparse.FileType('wb'))
parser.add_argument('-v', dest='verbose', help='Print progress meter', action='store_true')
args = parser.parse_args()

PRUNE = 100 #number of vertices to keep track of (memory usage and runtime increase too much if it is too large)

key_lookup = [0]*256    #lookup table for probability of the index being the key byte (gotta improve dat performance)

#Fill key lookup table:
for k in range(256):
    numones = 0
    x = k
    while x:
        numones += x & 1
        x >>= 1
    key_lookup[k] = (args.prob1 ** numones) * ((1 - args.prob1)**(8 - numones))

if args.verbose:
    print('Loading distribution data...')
cpdistr = pickle.load(args.distfile)
ciphertext = args.ciphertext.read()

#Use simplified version of viterbi algorithm to find the highest probability plaintext given a ciphertext and uneven key & plaintext distributions
#We prune the results after each iteration, so it doesn't really guarantee the best probability
#This is in order to avoid about 256^7 bytes of memory usage assuming n=7 (which is totally unrealistic)

#Dictionary containing states of previous step
#Key is the state, value is the "length" of the shortest path to that state
states = {b'':0} #initial state is empty with 0 "length"
plain_lookup = [0]*256     #lookup table used in each iteration for probabilities of given plaintext byte
for i,c in enumerate(ciphertext):
    newstates = {}
    for ostate in states:
        prefix = ostate[max(len(ostate) - args.depth + 1, 0):]  #depth last bytes of state
        for p in range(256):     #fill plantext probability lookup
            plain_lookup[p] = cpdistr[prefix].prob(p)
        probsum = math.fsum(key_lookup[k] * plain_lookup[c ^ k] for k in range(256))     #used in baye's formula
        for p in range(256):     #iterate over possible plaintext bytes
            prob = (plain_lookup[p] * key_lookup[p ^ c]) / probsum    #get updated probability with baye's theorem
            dist = states[ostate] - math.log(prob)   #maximizing the product of probabilities is equivalent to minimizing the sum of their logs
            #update newstates with new path information
            if len(newstates) < PRUNE:
                nstate = ostate + bytes([p])
                newstates[nstate] = dist
            else:
                maxstate = max(newstates, key=lambda s: newstates[s])
                if dist < newstates[maxstate]:
                    del newstates[maxstate]
                    nstate = ostate + bytes([p])
                    newstates[nstate] = dist
    states = newstates
    if args.verbose and i % 10 == 0:
        print('{:.2%} complete.'.format(i/len(ciphertext)))

#get "most probable" plaintext
plaintext = min(states, key=lambda s: states[s])
if args.output is not None:
    args.output.write(plaintext)
    args.output.close()
print('Paintext: {}\nHex: {}\n'.format(plaintext, plaintext.hex()))
#get key by xoring plaintext with ciphertext
key = b''
for p,c in zip(plaintext, ciphertext):
    key += bytes([p ^ c])
print('Key (Hex): {}'.format(key.hex()))

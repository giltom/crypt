import sys
import string
from prime_math import *

MIN_GROUP_LEN = 3
MAX_GROUP_LEN = 10
MIN_COUNTS = 3

if len(sys.argv) < 2:
    print('Keylength analysis on vigenere cipher.\nUsage: python3 vigenere_keylen.py FILE FILE FILE...')
    exit()

ciphers = [open(fname).read().replace(' ','') for fname in sys.argv[1:]]
factcounts = {}

for cipher in ciphers:
    print('Analyzing cipher', ciphers.index(cipher))
    groups = {}

    for grouplen in range(MIN_GROUP_LEN, MAX_GROUP_LEN+1):
        for i in range(0, len(cipher) - grouplen + 1):
            group = cipher[i:i+grouplen]
            if group not in groups and cipher.count(group) >= MIN_COUNTS:
                groups[group] = cipher.count(group)

    for group in sorted(list(groups.items()), key=lambda g: len(g[0])*g[1], reverse=True):
        print('Analyzing group \'{}\', length {:d}, appears {:d} times.'.format(group[0], len(group[0]), group[1]))
        distances = []
        i = cipher.find(group[0])
        while True:
            j = cipher.find(group[0], i+len(group[0]))
            if j == -1:
                break
            distances.append(j-i)
            i = j
        for dist in distances:
            facts = get_factors(dist)
            for n in facts:
                if n >= MIN_GROUP_LEN:
                    if n in factcounts:
                        factcounts[n] += 1
                    else:
                        factcounts[n] = 1

    print()

print('Most common factors:')
sortedfacts = sorted(list(factcounts.items()), key=lambda f: f[1], reverse=True)
for factor in sortedfacts[0:min(20, len(factcounts))]:
    print('{:d}: {:d} times'.format(factor[0], factor[1]))

print('Recommended key length (try other common factors if it does not work):', max(sortedfacts, key=lambda f: f[0]**0.5*f[1])[0])

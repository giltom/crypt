import os
import sys
import base64

counts = [0]*256
for fname in os.listdir(sys.argv[1]):
    for line in open(sys.argv[1] + '/' + fname):
        base = base64.b64encode(line.strip().encode('UTF-8'))
        for char in base:
            counts[char] += 1
tot = sum(counts)
freqs = {}
for char in range(256):
    freqs[char] = counts[char] / tot
print(freqs)

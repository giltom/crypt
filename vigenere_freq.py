import sys
import string

if len(sys.argv) < 3:
    print('Frequency analysis on vigenere cipher with a known keylength.\nUsage: python3 vigenere_freq.py KEYLENGTH FILE FILE FILE...')
    exit()

keylen = int(sys.argv[1])

counts = []
for i in range(keylen):
    counts.append({})
    for c in string.ascii_uppercase:
        counts[i][c] = 0

for fname in sys.argv[2:]:
    text = open(fname).read().replace(' ', '')
    i = 0
    for c in text:
        counts[i][c] += 1
        i = (i+1) % keylen

key = ''
for i, result in enumerate(counts):
    print('Position {:d}:'.format(i))
    ordered = sorted(result.items(), key=lambda x: x[1], reverse=True)
    for letter, count in ordered:
        print('{} : {:4d}'.format(letter,count))
    distance = (ord(ordered[0][0]) - ord('E')) % 26
    letter = chr(ord('A') + distance)
    key += letter
    print("Recommended key letter: " + letter)

print('Recommended key: ' + key)

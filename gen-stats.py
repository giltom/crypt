import argparse
import struct
import os
import string
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('dir', help='Directory of text files.')
parser.add_argument('n', type=int, help='Length of n-gram.')
parser.add_argument('out', type=argparse.FileType('wb'), help='output file.')
parser.add_argument('-q', action='store_false', dest='verbose', help='Do not print progress messages.')
parser.add_argument('-c', dest='count', type=argparse.FileType('w'), help='Generate statistics about the frequencies of each byte and write them in Python format to the given file.')
args = parser.parse_args()

def to_lower(byte):
    if byte < ord('a'):
        return byte + 32
    return byte

#groups of characters to generate relative frequencies for
#1st element - name. 2nd element - bytes to count. 3rd element - function to call on each byte (can be None).
#4th element - bytes in output (None for all).
C_GROUPS = [
    ('FREQ_ALL', bytes(range(256)), lambda x: x, None),
    ('FREQ_ALPHA', string.ascii_letters.encode('ASCII'), to_lower, string.ascii_lowercase.encode('ASCII')),
    ('FREQ_NONWS', (string.ascii_letters + string.punctuation + string.digits).encode('ASCII'), lambda x: x, None),
    ('FREQ_PRINTABLE', string.printable.encode('ASCII'), lambda x: x, None)
]

ngram_fmt = '>B{:d}p'.format(args.n)   #1,prefix
char_fmt = '>BBI'   #0, char, count after the last prefix
c_counts = [0]*256
ngrams = {}

if args.verbose:
    print('Processing files...')
nfiles = len(os.listdir(args.dir))
for cnt,fname in enumerate(os.listdir(args.dir)):
    f = open(os.path.join(args.dir,fname), 'rb')
    text = f.read()
    f.close()
    for i in range(args.n - 1, len(text)):  #n-grams and char counts
        pref = text[i - args.n + 1:i]
        byte = text[i]
        c_counts[byte] += 1
        if pref not in ngrams:
            ngrams[pref] = {}
        if byte not in ngrams[pref]:
            ngrams[pref][byte] = 1
        else:
            ngrams[pref][byte] += 1
    for line in text.split(b'\n'):  #<n-grams at the start if each line
        for i in range(min(args.n-1, len(line))):
            pref = line[0:i]
            byte = line[i]
            if pref not in ngrams:
                ngrams[pref] = {}
            if byte not in ngrams[pref]:
                ngrams[pref][byte] = 1
            else:
                ngrams[pref][byte] += 1
    if args.verbose and cnt % 20 == 0:
        print('{:.02%} complete.'.format(cnt/nfiles))

if args.verbose:
    print('Creating output...')
"""
pickle.dump(ngrams, args.out)
args.out.close()
"""
cnt = 0
nkeys = len(ngrams.keys())
for gram in ngrams:
    #tot = sum(ngrams[gram].values())
    args.out.write(struct.pack(ngram_fmt, 1, gram))
    for byte in ngrams[gram]:
        args.out.write(struct.pack(char_fmt, 0, byte, ngrams[gram][byte]))
    if args.verbose:
        cnt += 1
        if cnt % 1000 == 0:
            print('{:.02%} complete.'.format(cnt/nkeys))
args.out.close()

if args.count:
    if args.verbose:
        print('Genereting byte frequencies...')
    for name, cntbytes, func, outbytes in C_GROUPS:
        res = {}
        tot = sum(c_counts[c] for c in cntbytes)
        if outbytes is None:
            b = cntbytes
        else:
            b = outbytes
        for byte in b:
            cnt = sum(c_counts[c] for c in cntbytes if func(c) == byte)
            res[byte] = cnt/tot
        args.count.write('{} = {}\n\n'.format(name, repr(res)))
    args.count.close()

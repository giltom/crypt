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

if args.n > 256:
    print('n-gram length too large.')
    sys.exit(1)

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

###File Format:
#The first byte of the file contains the n-gram size - 1. After that, each ngram is stored as following:
#The first n bytes contain the (n-1)-gram, as a "pascal string" - 1st byte is the length, and after that follows the string itself.
#The byte after that contains the number of character entries for the (n-1)-gram, *minus 1*
#The byte after that contains log2(the number of bytes per character entry) - 0,1,2, or 3 - depending on the amount of storage needed.
#After that, the specified number of entries follow:
##Each entry consists of one byte containing the character,
##And then the specified number of bytes containing the count of that character (big endian, unsigned).

ngram_fmt = '>{:d}pBB'.format(args.n)   #1,prefix
MAX_1_BYTE = 2**8 - 1
MAX_2_BYTES = 2**16 - 1
MAX_4_BYTES = 2**32 - 1

args.out.write(bytes([args.n - 1]))     #write ngram size-1 to first byte
cnt = 0
nkeys = len(ngrams)
for gram in ngrams:
    maxcnt = max(ngrams[gram].values())
    if maxcnt <= MAX_1_BYTE:
        nbytes = 0
        char_fmt = '>BB'
    elif maxcnt <= MAX_2_BYTES:
        nbytes = 1
        char_fmt = '>BH'
    elif maxcnt <= MAX_4_BYTES:
        nbytes = 2
        char_fmt = '>BI'
    else:
        nbytes = 3
        char_fmt = '>BQ'
    args.out.write(struct.pack(ngram_fmt, gram, len(ngrams[gram]) - 1, nbytes))
    for byte in ngrams[gram]:
        args.out.write(struct.pack(char_fmt, byte, ngrams[gram][byte]))
    if args.verbose:
        cnt += 1
        if cnt % 100000 == 0:
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

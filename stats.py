import struct
import os
import math

###File Format:
#The first byte of the file contains the n-gram size - 1. After that, each ngram is stored as following:
#The first n bytes contain the (n-1)-gram, as a "pascal string" - 1st byte is the length, and after that follows the string itself.
#The byte after that contains the number of character entries for the (n-1)-gram, *minus 1*
#The byte after that contains the number of bytes per character entry - 1,2,4 or 8 depending on the amount of storage needed.
#After that, the specified number of entries follow:
##Each entry consists of one byte containing the character,
##And then the specified number of bytes containing the count of that character (big endian, unsigned).

#Index is log2(number of bytes), value 0 is the format, value 2 is the total number of bytes to read
FORMATS = [
    ('>BB', 2),
    ('>BH', 3),
    ('>BI', 5),
    ('>BQ', 9)
]

class NGramStats:
    def __init__(self, fname, verbose=False):
        if verbose:
            print('Loading {}...'.format(fname))
        f = open(fname, 'rb')
        fsize = os.path.getsize(fname)
        self.ngrams = {}
        self.n = f.read(1)[0] + 1 #read ngram size
        ngram_fmt = '>{:d}pBB'.format(self.n)
        ngram_size = struct.calcsize(ngram_fmt)
        cnt = 0
        while True:
            chunk = f.read(ngram_size)
            if len(chunk) == 0:
                break    #done reading
            curr, ncharsm1, entrylen = struct.unpack(ngram_fmt, chunk)   #new ngram
            char_fmt, char_size = FORMATS[entrylen]
            self.ngrams[curr] = {}
            for _ in range(ncharsm1 + 1):   #add all chars in the n-gram
                c, count = struct.unpack(char_fmt, f.read(char_size))
                self.ngrams[curr][c] = count
            if verbose:
                cnt +=1
                if cnt % 500000 == 0:
                    print('{:.02%} complete.'.format(f.tell()/fsize))
        f.close()
        self.p0 = {}
        if verbose:
            print('Processing data...')
        for gram in self.ngrams:
            tot = sum(self.ngrams[gram].values()) + len(self.ngrams[gram])
            for byte in self.ngrams[gram]:
                self.ngrams[gram][byte] /= tot


    def prob(self, pref, char):
        if char < 0 or char >= 256:
            raise KeyError('Char not in range.')
        if len(pref) >= self.n:
            raise KeyError('Prefix too long.')
        if pref not in self.ngrams:
            return 0.00390625   #1/256
        if char not in self.ngrams[pref]:
            if pref not in self.p0:
                self.p0[pref] = (1 - math.fsum(self.ngrams[pref].values())) / (256 - len(self.ngrams[pref]))
            return self.p0[pref]
        return self.ngrams[pref][char]

import struct
import os
import math

###File Format:
#The first byte of the file contains the n-gram size - 1. After that, each ngram is stored as following:
#The first n bytes contain the (n-1)-gram, as a "Pascal String" - the first byte contains the length of the n-1gram, followed by the n-1gram itself, padded with 0s.
#The byte after that contains the number of character entries for the (n-1)-gram, *minus 1*
#The byte after that contains log2(the number of bytes per character entry) - 0,1,2, or 3 - depending on the amount of storage needed.
#After that, the specified number of entries follow:
##Each entry consists of one byte containing the character,
##And then the specified number of bytes containing the count of that character (big endian, unsigned).

#Index is log2(number of bytes), value is the format
FORMATS = [
    struct.Struct('>BB'),
    struct.Struct('>BH'),
    struct.Struct('>BI'),
    struct.Struct('>BQ')
]

class NGramStats:
    def __init__(self, fname, verbose=False):
        if verbose:
            print('Loading {}...'.format(fname))
        f = open(fname, 'rb')
        fsize = os.path.getsize(fname)
        self.ngrams = {}
        self.n = f.read(1)[0] + 1 #read ngram size
        ngram_fmt = struct.Struct('{:d}pBB'.format(self.n))
        ngram_size = ngram_fmt.size
        cnt = 0
        while True:
            chunk = f.read(ngram_size)
            if len(chunk) == 0:
                break    #done reading
            curr, ncharsm1, entrylen = ngram_fmt.unpack(chunk)   #new ngram
            char_fmt = FORMATS[entrylen]
            char_size = char_fmt.size
            self.ngrams[curr] = {}
            block = f.read(char_size * (ncharsm1 + 1))
            for i in range(0, len(block), char_size):   #add all chars in the n-gram
                c, count = char_fmt.unpack_from(block[i:])
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
        if pref not in self.ngrams: #no information about prefix
            return 0.00390625   #1/256
        if char not in self.ngrams[pref]:   #no information about char given prefix
            if pref not in self.p0:
                self.p0[pref] = (1 - math.fsum(self.ngrams[pref].values())) / (256 - len(self.ngrams[pref]))
            return self.p0[pref]
        return self.ngrams[pref][char]

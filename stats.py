import struct
import os
import math

CHAR_FMT = '>BI'
SIZE_CHAR = struct.calcsize(CHAR_FMT)

class NGramStats:
    def __init__(self, fname, verbose=False):
        if verbose:
            print('Loading {}...'.format(fname))
        f = open(fname, 'rb')
        fsize = os.path.getsize(fname)
        self.ngrams = {}
        self.n = f.read(1)[0]
        ngram_fmt = '>{:d}p'.format(self.n)
        size_ngram = struct.calcsize(ngram_fmt)
        cnt = 0
        while True:
            ctrl = f.read(1)
            if len(ctrl) == 0:
                break
            if ctrl[0]:     #new ngram
                chunk = f.read(size_ngram)
                curr = struct.unpack(ngram_fmt, chunk)[0]
                self.ngrams[curr] = {}
            else:   #new char in current ngram
                chunk = f.read(SIZE_CHAR)
                c, count = struct.unpack(CHAR_FMT, chunk)
                self.ngrams[curr][c] = count
            if verbose:
                cnt +=1
                if cnt % 500000 == 0:
                    print('{:.02%} complete.'.format(f.tell()/fsize))
        f.close()
        self.p0 = {}
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

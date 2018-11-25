import pickle
import math
import functools

from crypt import util

def load_ngram_counts(fname):
    f = open(fname, 'rb')
    counts = pickle.load(f)
    f.close()
    return counts

MINF = float('-inf')

class NGramStats:
    def __init__(self, counts=None, fname=None, delta=0.75):
        if (counts is None and fname is None) or (counts is not None and fname is not None):
            raise util.CryptoException('Exactly one of counts and fname should be given')
        if fname is not None:
            self.counts = load_ngram_counts(fname)
        else:
            self.counts = counts
        npairs = 0
        nbefore = [0]*256
        for b1 in range(256):
            for b2 in range(256):
                if bytes([b1, b2]) in self.counts:
                    npairs += 1
                    nbefore[b2] += 1
        self.uniprobs = [nbefore[b] / npairs for b in range(256)]
        self.delta = delta
        self.maxlen = max(len(k) for k in self.counts)
        self.usedbytes = [b for b in range(256) if bytes([b]) in self.counts]

    #probability of b given the prefix
    @functools.lru_cache(maxsize=2**16)
    def prob(self, b, prefix):
        if not prefix:
            return self.uniprobs[b]
        if prefix not in self.counts:
            return self.prob(b, prefix[1:])
        nafter, timesafter = self.get_after_stats(prefix)
        seq = prefix + bytes([b])
        count = self.counts.get(seq)
        if count is not None:
            nseq = count - self.delta
        else:
            nseq = 0
        prob = (nseq + nafter * self.prob(b, prefix[1:])) / timesafter
        return prob
    
    def log_prob(self, b, prefix):
        prob = self.prob(b, prefix)
        if prob == 0:
            return MINF
        return math.log(prob)

    def is_byte_used(self, b):
        return self.uniprobs[b] != 0

    #Return (nafter, timesafter) where:
    #nafter is (the number of unique bytes that appear after prefix) * delta
    #timesafter is the number of times prefix appears not at the end of the text
    @functools.lru_cache(maxsize=256)
    def get_after_stats(self, prefix):
        nafter = 0
        timesafter = 0
        for bt in self.usedbytes:
            ngram = prefix + bytes([bt])
            count = self.counts.get(ngram)
            if count is not None:
                nafter += 1
                timesafter += count
        return nafter * self.delta, timesafter
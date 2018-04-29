import pickle
from crypt import util

def load_ngram_counts(fname):
    f = open(fname, 'rb')
    counts = pickle.load(f)
    f.close()
    return counts

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
        self.uniprobs = []
        for b in range(256):
            self.uniprobs.append(nbefore[b] / npairs)
        self.delta = delta
        self.maxlen = max(len(k) for k in self.counts)
        self.probcache = {}
        self.usedbytes = [b for b in range(256) if bytes([b]) in self.counts]

    #probability of b given the prefix
    def prob(self, b, prefix):
        if len(prefix) == 0:
            return self.uniprobs[b]
        if self.uniprobs[b] == 0:
            return 0.0
        if (b, prefix) in self.probcache:
            return self.probcache[(b, prefix)]
        if prefix not in self.counts:
            return self.prob(b, prefix[1:])
        nafter = 0
        timesafter = 0
        for bt in self.usedbytes:
            ngram = prefix + bytes([bt])
            if ngram in self.counts:
                nafter += 1
                timesafter += self.counts[ngram]
        seq = prefix + bytes([b])
        if seq in self.counts:
            nseq = self.counts[seq] - self.delta
        else:
            nseq = 0
        res = (nseq + self.delta * nafter * self.prob(b, prefix[1:])) / timesafter
        self.probcache[(b, prefix)] = res
        return res

    def is_byte_used(self, b):
        return self.uniprobs[b] != 0

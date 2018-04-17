import math
from contextlib import contextmanager
import signal

class CryptoException(Exception):
    pass

#Cumulative standard normal distribution
def phi(x):
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

#Return a list of (key,plaintext,score) triples sorted by a score.
#Each key in keys is tried, using decfn(cipher, key)
#Plaintexts are evaluated with scorefn, which must accept a bytes and return a numeric score
#filt can be a function that accepts a plaintext and returns a boolean. Only plaintexts for which it returns True will be checked.
#if maxkeys is None, will only store up to maxkeys keys in memory.
def rank_keys(cipher, keys, decfn, scorefn, filt=None, maxkeys=None):
    res = set()
    for key in keys:
        plain = decfn(cipher, key)
        if filt is None or filt(plain):
            score = scorefn(plain)
            if maxkeys is None or len(res) < maxkeys:
                res.add((key,plain,score))
            else:
                minkey = min(res, key=lambda t: t[2])
                if score > minkey[2]:
                    res.remove(minkey)
                    res.add((key,plain,score))
    res = list(res)
    res.sort(key=lambda t: t[2], reverse=True)
    return res

#return (key,plaintext) with best rank returned by rank_keys
def rank_best(cipher, keys, decfn, scorefn, filt=None):
    res = rank_keys(cipher, keys, decfn, scorefn, filt=filt, maxkeys=1)
    if len(res) == 0:
        return None
    return res[0][0], res[0][1]

class TimeoutException(Exception):
    pass

#Context manager that limits the execution time of the statements, raising TimeoutException if time runs out.
#Note that this uses SIGALRM.
@contextmanager
def time_limit(seconds):
    def sigalrm_handler(signum, frame):
        raise TimeoutException('Timed out!')
    old_handler = signal.signal(signal.SIGALRM, sigalrm_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

#rotate the size-bits unsigned integer i amt bits to the left
def lrotate(i, amt, size):
    amt = amt % size
    mask = ~-(1 << size)
    return ((i << amt) + (i >> (size - amt))) & mask

#rotate the size-bits unsigned integer i amt bits to the right
def rrotate(i, amt, size):
    amt = amt % size
    mask = ~-(1 << size)
    return ((i >> amt) + (i << (size - amt))) & mask

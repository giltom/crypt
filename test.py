from lib import *

def dec(c,k):
    return xor_repeat(c,bytes([k]))

def score(p):
    return count_words(p, EN_WORDS, lower=True)

res = []
for line in open('data/xors.txt','r'):
    h = line.strip()
    if h != '':
        b = hex2bytes(h)
        ranks = rank_keys(b, range(256), dec, score, filt=all_printable, maxkeys=3)
        res.extend((h,)+rank for rank in ranks)
res.sort(key=lambda t: t[3], reverse=True)
print(res[0])

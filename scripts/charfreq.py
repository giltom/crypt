import nltk
from nltk import probability as prob
import string

#list of 2-tuples - corpus and list of filenames
#if filename list is empty, reads all files
CORPORA = [
    (nltk.corpus.gutenberg, []),
    (nltk.corpus.abc, []),
    (nltk.corpus.genesis, ['english-web.txt']),
    (nltk.corpus.inaugural, []),
    (nltk.corpus.movie_reviews, []),
    (nltk.corpus.state_union, []),
    (nltk.corpus.udhr, ['English-Latin1']),
    (nltk.corpus.webtext, [])
]

CHARS = set(string.ascii_letters.encode('ASCII'))

def texts():
    for corpus, l in CORPORA:
        if len(l) == 0:
            fnames = corpus.fileids()
        else:
            fnames = l
        for fname in fnames:
            yield corpus.raw(fname).encode('UTF-8')

def lower_byte(byte):
    if byte < 97:   #'a'
        return byte + 32
    return byte

def upper_byte(byte):
    if byte > 90:   #'Z'
        return byte - 32
    return byte

fdist = nltk.FreqDist(lower_byte(b) for t in texts() for b in t if b in CHARS)
probs = {}
for char in string.ascii_lowercase.encode('ASCII'):
    probs[char] = fdist.freq(char)
print(probs)

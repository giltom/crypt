import nltk
from nltk import probability as prob
import pickle
import argparse
import sys

parser = argparse.ArgumentParser(description='Generate statistics from text corpora.')
parser.add_argument('depth', type=int, help='Number of chars before to use in statistics.')
parser.add_argument('output', type=argparse.FileType('wb'), help='File to save results to.')
args = parser.parse_args()

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

def texts():
    for corpus, l in CORPORA:
        if len(l) == 0:
            fnames = corpus.fileids()
        else:
            fnames = l
        for fname in fnames:
            yield corpus.raw(fname).encode('UTF-8')

cfdist = prob.ConditionalFreqDist()
chars = set()
for s in texts():
    for i in range(len(s)):
        condition = s[max(i - args.depth + 1, 0) : i]
        cfdist[condition][s[i]] += 1
    chars |= set(s)
cpdist = prob.ConditionalProbDist(cfdist, prob.WittenBellProbDist, bins=len(chars))
pickle.dump(cpdist, args.output)
args.output.close()

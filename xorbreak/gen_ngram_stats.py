import argparse
import pickle

#counts all ngrams up to maxlen (inclusive) in the given list of open file objects
#returns a dictionary of the results, in the form ngram : count
def count_ngrams(files,  maxlen, verbose=False):
    counts = {}
    for fnum, f in enumerate(files):
        text = f.read()
        f.close()
        for nglen in range(1, args.n + 1):
            for i in range(len(text) - args.n + 1):
                ngram = text[i : i + nglen]
                if ngram in counts:
                    counts[ngram] += 1
                else:
                    counts[ngram] = 1
        if args.verbose and fnum % 20 == 19:
            print('{:.02%} complete'.format((fnum+1) / len(files)))
    return counts

#writes the ngram counts in the dictionary counts to the open file object given by file
def export_ngram_counts(counts, file):
    pickle.dump(counts, args.out)
    args.out.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', type=argparse.FileType('rb'), help='Text files to read.')
    parser.add_argument('n', type=int, help='Maximum length of n-gram.')
    parser.add_argument('out', type=argparse.FileType('wb'), help='output file.')
    parser.add_argument('-q', action='store_false', dest='verbose', help='Do not print progress messages.')
    args = parser.parse_args()

    counts = count_ngrams(args.files, args.n, args.verbose)
    if args.verbose:
        print('Writing to output file...')
    export_ngram_counts(counts, args.out)
    args.out.close()

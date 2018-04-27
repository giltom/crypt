import argparse
import pickle

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', type=argparse.FileType('rb'), help='Text files to read.')
    parser.add_argument('n', type=int, help='Maximum length of n-gram.')
    parser.add_argument('out', type=argparse.FileType('wb'), help='output file.')
    parser.add_argument('-q', action='store_false', dest='verbose', help='Do not print progress messages.')
    args = parser.parse_args()

    res = {}
    for f in args.files:
        text = f.read()
        f.close()
        for nglen in range(1, args.n + 1):
            for i in range(len(text) - args.n + 1):
                ngram = text[i : i + nglen]
                if ngram in res:
                    res[ngram] += 1
                else:
                    res[ngram] = 1

    if args.verbose:
        print('Writing to output file...')
    pickle.dump(res, args.out)
    args.out.close()

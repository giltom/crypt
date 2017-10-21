import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('file1', type=argparse.FileType('rb'))
parser.add_argument('file2', type=argparse.FileType('rb'))
args = parser.parse_args()

file1 = args.file1.read()
file2 = args.file2.read()
if len(file1) != len(file2):
    print('Not same length')
    sys.exit(0)
tot = 0
for p,x in zip(file1, file2):
    if p == x:
        tot += 1
print('Percentage of equal bytes:', round(tot / len(file1),3))

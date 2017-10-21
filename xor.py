import argparse
import sys

parser = argparse.ArgumentParser(description='XORs two files (up to the length of the shorter one).')
parser.add_argument('plaintext', metavar='file1', type=argparse.FileType('rb'))
parser.add_argument('key', metavar='file2', type=argparse.FileType('rb'))
parser.add_argument('output', type=argparse.FileType('wb'))
args = parser.parse_args()

plain = args.plaintext.read()
key = args.key.read()
cipher = b''
for p,k in zip(plain, key):
    cipher += bytes([p ^ k])
args.output.write(cipher)
args.output.close()

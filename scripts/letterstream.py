#!/usr/bin/python3

import argparse
import sys
import string
import itertools

def letter2num(letter, alphabet, base):
    return alphabet.index(letter) + base

def num2letter(num, alphabet, base):
    return alphabet[num - base]

def maxnum(alphabet, base):
    return len(alphabet) + base - 1

def addl(l1, l2, alphabet, base):
    n1 = letter2num(l1, alphabet, base)
    n2 = letter2num(l2, alphabet, base)
    res = n1 + n2
    if res > maxnum(alphabet, base):
        res -= len(alphabet)
    return num2letter(res, alphabet, base)

def subl(l1, l2, alphabet, base):
    n1 = letter2num(l1, alphabet, base)
    n2 = letter2num(l2, alphabet, base)
    res = n1 - n2
    if res < base:
        res += len(alphabet)
    return num2letter(res, alphabet, base)

def letterstreamgen(fp):
    while True:
        c = fp.read(1)
        if c == '':
            break
        yield c

def tryconsumekey(stream, alphabet, ignore):
    while True:
        try:
            c = next(stream)
        except StopIteration:
            print('\nERROR: key ended before input.')
            exit(2)
        if c not in alphabet:
            if ignore:
                continue
            print('\nERROR: invalid character in key stream.')
            exit(2)
        return c


parser = argparse.ArgumentParser(description="Encrypt/Decrypt a message letters with a key stream using modulo addition/subtraction. Reads key from STDIN by default.")
parser.add_argument('input', metavar='INPUT', type=argparse.FileType('r'), help='Ciphertext/Plaintext input. \'-\' for STDIN. When a non-letter character is read, it is written to output as-is, and *a character is not consumed from the key stream* unless -c is added.')
parser.add_argument('-d', dest='decrypt', action='store_true', help='Decrypt (modulo subtraction) instead of encrypt (modulo addition).')
parser.add_argument('-r', dest='repeat', action='store_true', help='Store the key stream values and repeat them indefinitely if the key stream ends.')
parser.add_argument('-b', dest='base', type=int, default=0, help='Numerical value of first letter, i.e. \'A\'. Default 0.')
parser.add_argument('-o', dest='output', type=argparse.FileType('w'), default=sys.stdout, help='Write output to file instead of STDOUT.')
parser.add_argument('-k', dest='key', type=argparse.FileType('r'), default=sys.stdin, help='Read key from file instead of from STDIN.')
parser.add_argument('-l', dest='alphabet', action='store_const', const=string.ascii_lowercase, default=string.ascii_uppercase, help='Use lowercase letters instead of uppercase letters.')
parser.add_argument('-c', dest='consume', action='store_true', help='Consume a character from the key stream even if the corresponding input character isn\'t a letter.')
parser.add_argument('-i', dest='ignore', action='store_true', help='Ignore invalid characters in the key stream.')
args = parser.parse_args()

if args.repeat:
    key = itertools.cycle(letterstreamgen(args.key))
else:
    key = letterstreamgen(args.key)

for c in letterstreamgen(args.input):
    if c not in args.alphabet:
        if args.consume:
            tryconsumekey(key, args.alphabet, args.ignore)
        args.output.write(c)
        continue
    k = tryconsumekey(key, args.alphabet, args.ignore)
    if args.decrypt:
        res = subl(c, k, args.alphabet, args.base)
    else:
        res = addl(c, k, args.alphabet, args.base)
    args.output.write(res)

import sys
import string

if len(sys.argv) < 3:
    print('Decrypts vigenere cipher with a given key.\nUsage: python3 vigenere_decrypt.py KEY FILE')
    exit()

key = sys.argv[1]
cipher = open(sys.argv[2]).read()
plain = ''

i = 0
for c in cipher:
    if c not in string.whitespace:
        plain += chr((ord(c) - ord(key[i])) % 26 + ord('A'))
        i = (i+1) % len(key)
    else:
        plain += c

print(plain)

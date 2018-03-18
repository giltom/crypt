import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('plaintext', type=argparse.FileType('rb'))
parser.add_argument('prob1', metavar='1-probability', type=float)
parser.add_argument('output', type=argparse.FileType('wb'))
parser.add_argument('-k', help='key output', dest='key', type=argparse.FileType('wb'))
args = parser.parse_args()

random.seed()

def gen_byte():
    byte = 0
    for i in range(8):
        if random.random() < args.prob1:
            byte |= 1 << i
    return byte

plaintext = args.plaintext.read()
cipher = b''
key = b''
for p in plaintext:
    byte = gen_byte()
    key += bytes([byte])
    cipher += bytes([p ^ byte])
args.output.write(cipher)
args.output.close()
if args.key is not None:
    args.key.write(key)
    args.key.close()

print('Plaintext (Hex):', plaintext.hex())
print('Key (Hex):', key.hex())
print('Ciphertext (Hex):', cipher.hex())

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input', type=argparse.FileType('rb'))
args = parser.parse_args()

inp = args.input.read()
tot = 0
for byte in inp:
    b = byte
    while b:
        tot += b & 1
        b >>= 1
print('{:.2%} ones.'.format(tot / (8 * len(inp))))

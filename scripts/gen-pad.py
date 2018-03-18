import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('length', type=int)
parser.add_argument('output', type=argparse.FileType('wb'))
parser.add_argument('-s', dest='seed', help='Seed for the RNG.')
args = parser.parse_args()

random.seed(args.seed)
for _ in range(args.length):
    args.output.write(bytes([random.randint(0,255)]))
args.output.close()

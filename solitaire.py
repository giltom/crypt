from cards import *
import sys
import argparse
import string

def solitaire_step(deck):
    deck.move('OA', 1) #step 1
    deck.move('OB', 2) #step 2
    posA = deck.position('OA')
    posB = deck.position('OB')
    if posA < posB:
        deck.triplecut(posA-1, posB+1) #step 3
    else:
        deck.triplecut(posB-1, posA+1) #step 3
    deck.countcut(deck[54].getnumber()) #step 4
    return deck[deck[1].getnumber() + 1] #step 5

parser = argparse.ArgumentParser(description='Generates a keystream using the solitaire cipher.', epilog='CARD CODES: a code can either be an ID, or a designation. For IDs, 1 is Ace of Clubs, 2 is 2 of Clubs (and so on), 13 is King of Clubs, 14 is Ace of Diamonds, 27 is Ace of Hearts, 40 is Ace of Spades, 53 is Joker A, and 54 is Joker B. For designations, OA and OB are Jokers A and B respectively. For other cards, use the card number or the first letter of its name followed by the first letter of the suite. For example, 10H is 10 of Hearts, KS is King of Spades, AC is Ace of Clubs.')
keygroup = parser.add_mutually_exclusive_group(required=True)
keygroup.add_argument('-k', dest='key', help='A key used to generate the initial order of the deck. It should consist only of capital letters (whitespace is ignored).')
keygroup.add_argument('-d', metavar='FILE', dest='deckfile', type=argparse.FileType('r'), help='A file containing the initial order of the deck. It should contain a whitespace-separated list of 54 card codes (see below).')
keygroup.add_argument('-r', action='store_true', dest='random', help='Generate the initial order randomly. It will be written to STDERR unless -w is specified.')
parser.add_argument('-n', type=int, dest='length', help='Length of the generated keystream. If not specified, generates indefinitely.')
parser.add_argument('-w', metavar='FILE', type=argparse.FileType('w'), dest='outdeckfile', help='Write the initial order of the deck to the given file.')
parser.add_argument('-f', dest='format', choices=['numbers', 'letters', '5letters'], default='letters', help='Output keystream format. numbers writes the IDs of output cards, separated by spaces. letters prints a sequence of capital letters. 5letters is the same, but it splits the letters into space-separated groups of 5. Default is letters.')
parser.add_argument('-o', metavar='FILE', dest='outfile', type=argparse.FileType('w'), default=sys.stdout, help='Write key to file instead of to STDOUT. Requires -n.')
parser.add_argument('-g', action='store_true', dest='generate', help='Generate a deck order and exit, without generating a keystream. Should be used with -w or -w - for STDOUT.')
args = parser.parse_args()

if args.outfile != sys.stdout and args.length:
    print('Must specify length if writing to file.', file=sys.stderr)
    exit(2)

#Generate initial order:
if args.key is not None:
    deck = Deck(range(1,55))
    for c in args.key:
        if c in string.ascii_uppercase:
            solitaire_step(deck)
            deck.countcut(ord(c) - ord('A') + 1)
elif args.deckfile:
    try:
        deck = Deck(args.deckfile.read().split())
    except ValueError as e:
        print(e, file=sys.stderr)
        exit(2)
elif args.random:
    deck = Deck()
    if args.outdeckfile is None:
        print('Randomly generated deck:\n' + str(deck), file=sys.stderr)

if args.outdeckfile:
    args.outdeckfile.write(str(deck) + '\n')
if args.generate:
    exit(0)

count = 0
lcount = 0
try:
    while True:
        res = solitaire_step(deck)
        if not res.isjoker():
            if args.format == 'numbers':
                args.outfile.write(str(res.id) + ' ')
            else:
                args.outfile.write(res.getletter())
                lcount += 1
                if args.format == '5letters' and lcount == 5:
                    args.outfile.write(' ')
                    lcount = 0
            count += 1
            if args.length and count == args.length:
                break
except BrokenPipeError:
    exit(0)

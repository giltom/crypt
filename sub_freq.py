import sys
import string

LETTERS = string.ascii_uppercase
LETTERFREQ = 'etaoinshrdlcumwfgypbvkjxqz'

def count_occurences(s, l):
    results = {}
    i = 0
    for i in range(0,len(s)):
        word = s[i:i+l]
        if word in results:
            results[word] += 1
        else:
            results[word] = 1
    return sorted(results.items(), key=lambda x: x[1], reverse=True)

def print_results(l):
    for word, count in l:
        print('{} : {:4d}'.format(word,count))

if len(sys.argv) < 2:
    print('Frequency analysis for substituion ciphers.\nUsage: python3 sub_freq.py FILE FILE FILE...')
    exit()

totstr = ""
for fname in sys.argv[1:]:
    fp = open(fname)
    totstr += fp.read()
    fp.close()
totstr = totstr.replace(' ', '')

print('Single letter counts:')
counts = count_occurences(totstr,1)
tot = sum(x[1] for x in counts)
cnt = 0
for c, count in counts:
    print("{} : {:4d} ({:02.2%}) ({})".format(c, count, count/tot, LETTERFREQ[cnt]))
    cnt+=1

print('Recommended string for sub:')
substr = ''
for i in range(0,len(counts)):
    substr += counts[i][0] + ':' + LETTERFREQ[i] + ' '
print(substr)

print('Digram counts:')
filtered = [x for x in count_occurences(totstr,2) if x[1]>10]
print_results(filtered)

print('Trigram counts:')
filtered = [x for x in count_occurences(totstr,3) if x[1]>10]
print_results(filtered)

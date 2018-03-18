import sys

if len(sys.argv) < 3:
    print('Decrypt substitution cipher with a given table.\nUsage: python3 sub_decrypt.py FILE A:a B:b C:c ...\nIn this example A will be replaced with a, B with b, and so on.')
    exit()

fp = open(sys.argv[1])
contents = fp.read()
fp.close()
for rule in sys.argv[2:]:
    old = rule.split(':')[0]
    new = rule.split(':')[1]
    if len(old)!=1 or len(new)!=1:
        print('Invalid argument!')
        break
    contents = contents.replace(old, new)
print(contents)

from cryptutil import *
import random

cipherhex = '6e19223f204b31183e333f005c122d37264a350e3e3c2808672436250b3f3d1b2e2c151c671d553e182b4713262c3f045c1d553e0b3f391c1449385d7309223c20153d022d3c011a673322394822242e0118003a5a1333123b222b361b22353d5110231230222b1f102c28566e03281a2e21240c041e3e2d491337022e313b26181a3a5a532919122a31343e071f2e2d4928531a2e31342607713702673a3963140b1737001c0f5c742d3a172e133a331b4b3d167f090418210b3a31390d0f025933390810023a334e0e2427733c021818081119141c0928552629170c172a230f08373808246a0a113d142645421b357e0853327132013d2439243565000c190514093d3f171b0b6503070a2f001b2e0d140a0e6a7f0a340522442d1a3d17356913500870290b2e31435d0d7a32061e70101f7e2f495d5f6730263a1a4b39042d49055f6d79506d48'

cipher = hex2bytes(cipherhex)

keybytes = list(set(string.printable.encode('ASCII')) - set(string.whitespace.encode('ASCII')))
pbytes = set(string.ascii_letters.encode('ASCII') + string.digits.encode('ASCII') + b'+/=\n')

hamdists = [(first_blocks_hamming(cipher, keylen), keylen) for keylen in range(1, len(cipher)//2)]
hamdists.sort()

for dist, keylen in hamdists:
    print('Key length {:d}: {}'.format(keylen, str(dist)))

keylen = hamdists[0][1]
print('Selected most likely key length of', keylen)

key_opts = []
for keypos in range(keylen):
    key_opts.append([])
    for kbyte in keybytes:
        if all(cipher[i] ^ kbyte in pbytes for i in range(keypos, len(cipher), keylen)):
            key_opts[keypos].append(kbyte)
print('key options:', key_opts)

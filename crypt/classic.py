import crypt
import string
import itertools

#single character to value mod 26
def char2lval(c, aval=0):
    if c not in string.ascii_letters:
        raise crypt.CryptoException("Character " + c + " is not a letter.")
    return ord(c.lower()) - ord('a') + aval

#value mod 26 to character
def lval2char(val, aval=0, upper=True):
    if val < aval or val >= aval + 26:
        raise crypt.CryptoException("Bad letter value " + val)
    if upper:
        return chr(ord('A') + val - aval)
    else:
        return chr(ord('a') + val - aval)

#string to list of letter values. aval is value of the letter A. ignores case.
def str2lvals(s, aval=0):
    return [char2lval(c, aval) for c in s]

#iterable of letter values to string. aval is value of the letter A. if upper is True, output uppercase, otherwise lowercase.
def lvals2str(lvals, aval=0, upper=True):
    return ''.join(lval2char(val, aval, upper) for val in lvals)

#modular sum of letter values. Output has the length of the shorter list.
def lvals_add(lvals1, lvals2):
    res = []
    for val1, val2 in zip(lvals1, lvals2):
        res.append((val1 + val2) % 26)
    return res

#modular sum of letter values. Output has the length of the shorter list.
def lvals_sub(lvals1, lvals2):
    res = []
    for val1, val2 in zip(lvals1, lvals2):
        res.append((val1 - val2) % 26)
    return res

#repeats the list indefinitely. Useful for vigenere, etc.
def lvals_repeat(lvals):
    copy = list(lvals)
    while True:
        for val in copy:
            yield val

#modular multiply all by a constant
def lvals_mult_const(lvals, const):
    res = []
    for val in lvals:
        res.append((val*const) % 26)
    return res

#modular add a constant
def lvals_add_const(lvals, const):
    res = []
    for val in lvals:
        res.append((val + const) % 26)
    return res

#modular subtract a constant
def lvals_sub_const(lvals, const):
    res = []
    for val in lvals:
        res.append((val - const) % 26)
    return res

#affine cipher encryption
def affine_encrypt(s, a, b):
    lvals = str2lvals(s)
    lvals = lvals_mult_const(lvals, a)
    lvals = lvals_add_const(lvals, b)
    return lvals2str(lvals)

#affine cipher decryption. requires gcd(a, 26) = 1
def affine_decrypt(s, a, b):
    lvals = str2lvals(s)
    lvals = lvals_sub_const(lvals, b)
    lvals = lvals_mult_const(lvals, crypt.mod_inverse(a, 26))
    return lvals2str(lvals)

#rotation cipher, a.k.a shift cipher, caesar cipher
def rot_encrypt(s, k):
    lvals = str2lvals(s)
    lvals = lvals_add_const(lvals, k)
    return lvals2str(lvals)

#rot decryption
def rot_decrypt(s, k):
    lvals = str2lvals(s)
    lvals = lvals_sub_const(lvals, k)
    return lvals2str(lvals)

#Substitution cipher. Subs must be a dict of char:char pairs. Ignores chars not in the dict. Ignores case and switches everything to uppercase.
def sub_encrypt(s, subs):
    s = s.upper()
    for char in subs:
        s = s.replace(char.upper(), subs[char].upper())
    return s

#Sub cipher decryption. subs must be the dict used to encrypt. Ignores case and switches to lowercase.
def sub_decrypt(s, subs):
    s = s.lower()
    for char in subs:
        s = s.replace(subs[char].lower(), char.lower())
    return s

#vigenere cipher
def vigenere_encrypt(s, key):
    lvals = str2lvals(s)
    keyvals = str2lvals(key)
    lvals = lvals_add(lvals, lvals_repeat(keyvals))
    return lvals2str(lvals)

#vigenere cipher
def vigenere_decrypt(s, key):
    lvals = str2lvals(s)
    keyvals = str2lvals(key)
    lvals = lvals_sub(lvals, lvals_repeat(keyvals))
    return lvals2str(lvals)

#returns the key (a,b) for an affine cipher that maps p to c
def break_affine(p, c):
    if len(p) != len(c):
        raise crypt.CryptoException('Cipher and plaintext have different lengths')
    for i,j in itertools.combinations(range(len(p)), 2):
        p1 = char2lval(p[i])
        p2 = char2lval(p[j])
        c1 = char2lval(c[i])
        c2 = char2lval(c[j])
        try:
            inv = crypt.mod_inverse((p1 - p2) % 26, 26)
        except crypt.CryptoException:
            continue
        a = (((c1 - c2) % 26) * inv) % 26
        b = (c1 - a*p1) % 26
        return a, b

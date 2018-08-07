import itertools
import functools

from crypt import util
from crypt import numbers as num

ORD_A = ord('A')
ORD_Z = ord('Z')
ORD_a = ord('a')
ORD_z = ord('z')

KEEP = object()
FAIL = object()
REMOVE = object()
CONVERT = object()
UPPER = object()
LOWER = object()
BOTH = object()

def is_upper(char):
    return ORD_A <= ord(char) <= ORD_Z

def is_lower(char):
    return ORD_a <= ord(char) <= ORD_z

def is_letter(char):
    return is_upper(char) or is_lower(char)

def get_case(char):
    if is_upper(char):
        return UPPER
    if is_lower(char):
        return LOWER
    raise ValueError('Not a letter')

class LetterConverter:
    #by default, othercase gets the value of others
    def __init__(self, start=0, others=KEEP, case=BOTH, othercase=None):
        self.start = start
        if others not in [KEEP, FAIL, REMOVE]:
            raise ValueError('Invalid value for others')
        self.others = others
        if case not in [UPPER, LOWER, BOTH]:
            raise ValueError('Invalid value for case')
        self.case = case
        if othercase is None:
            othercase = self.others
        if othercase not in [KEEP, FAIL, REMOVE, CONVERT]:
            raise ValueError('Invalid value for othercase')
        self.othercase = othercase
    
    def letter2num(self, char):
        case = get_case(char)
        if self.case is case or self.case is BOTH or self.othercase is CONVERT:
            if case is UPPER:
                return ord(char) - ORD_A + self.start
            else:
                return ord(char) - ORD_a + self.start
        if self.othercase is KEEP:
            return KEEP
        if self.othercase is REMOVE:
            return REMOVE
        raise ValueError('Bad character {}: wrong case.'.format(char))  #FAIL
    
    #REMOVE if the char should be removed
    #KEEP if the char should be kept
    def char2num(self, char):
        if is_letter(char):
            return self.letter2num(char)
        else:
            if self.others is KEEP:
                return KEEP
            if self.others is REMOVE:
                return REMOVE
            raise ValueError('Bad character {}: not a letter.'.format(char))  #FAIL
    
    def str2nums(self, s):
        res = []
        for c in s:
            n = self.char2num(c)
            if type(n) is int:
                res.append(n)
        return res
    
    #also returns a context for converting results back to a string
    #it is a list containing constant chars, UPPER and LOWER
    def str2nums_context(self, s):
        res = []
        context = []
        for c in s:
            n = self.char2num(c)
            if n is KEEP:
                context.append(c)
            elif n is not REMOVE:
                res.append(n)
                if self.othercase is CONVERT and self.case is not BOTH:
                    context.append(self.case)
                else:
                    context.append(get_case(c))
        return res, context
    
    def num2char(self, n, case=None):
        if case is None:
            case = self.case
        if case is UPPER:
            return chr(n - self.start + ORD_A)
        else:
            return chr(n - self.start + ORD_a)
    
    def nums2str(self, nums, context=None):
        if context is None:
            if self.case is UPPER:
                context = [UPPER] * len(s)
            else:
                context = [LOWER] * len(s)
        res = ''
        i = 0
        for ctx in context:
            if type(ctx) is str:
                res += ctx
            else:
                if i >= len(nums):
                    break
                res += self.num2char(nums[i], ctx)
                i += 1
        return res

#context manager that turns a function that works on value lists to one that works on strings
#the function should accept a list of ints between 0 and 25 as its first argument.
#It should return a list of the same kind.
#the raw parameter allows the function to work on raw value lists (so it doesn't change it at all).
def letter_cipher(func):
    @functools.wraps(func)
    def wrapped(s, *args, raw=False, start=0, others=KEEP, case=BOTH, othercase=None, **kwargs):
        if raw:
            return func(s, *args, **kwargs)
        converter = LetterConverter(start, others, case, othercase)
        nums, context = converter.str2nums_context(s)
        nums = func(nums, *args, **kwargs)
        return converter.nums2str(nums, context)
    return wrapped

@letter_cipher
def caesar_encrypt(vals, k):
    return [(x + k) % 26 for x in vals]

@letter_cipher
def caesar_decrypt(vals, k):
    return [(y - k) % 26 for y in vals]

@letter_cipher
def rot13(vals):
    return caesar_encrypt(vals, 13, raw=True)

@letter_cipher
def affine_encrypt(vals, a, b):
    return [(a*x + b) % 26 for x in vals]

@letter_cipher
def affine_decrypt(vals, a, b):
    ainv = num.mod_inverse(a, 26)
    return [((y - b) * ainv) % 26 for y in vals]

@letter_cipher
def lstream_encrypt(vals, stream, stream_start=0):
    converter = LetterConverter(others=FAIL, start=stream_start)
    return [(x + converter.char2num(k)) % 26 for x, k in zip(vals, stream)]

@letter_cipher
def lstream_decrypt(vals, stream, stream_start=0):
    converter = LetterConverter(others=FAIL, start=stream_start)
    return [(x - converter.char2num(k)) % 26 for x, k in zip(vals, stream)]

@letter_cipher
def vigenere_encrypt(vals, key, key_start=0):
    return lstream_encrypt(vals, itertools.cycle(key), stream_start=key_start, raw=True)

@letter_cipher
def vigenere_decrypt(vals, key, key_start=0):
    return lstream_decrypt(vals, itertools.cycle(key), stream_start=key_start, raw=True)

def sub_encrypt(s, subs, others=KEEP):
    res = ''
    for c in s:
        if c in subs:
            res += subs[c]
        else:
            if others is KEEP:
                res += c
            if others is FAIL:
                raise ValueError('Char {} not in substitution dict.'.format(c))
    return res

def sub_decrypt(s, subs, others=KEEP):
    inv = {}
    for key in subs:
        inv[subs[key]] = key
    return sub_encrypt(s, inv, others)
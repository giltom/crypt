import abc
import enum

from crypt import util

ORD_A = ord('A')
ORD_Z = ord('Z')
ORD_a = ord('a')
ORD_z = ord('z')

class LetterAction(enum.Enum):
    KEEP = 0
    FAIL = 1
    REMOVE = 2
    CONVERT = 3

class LetterCase(enum.Enum):
    UPPER = 1
    LOWER = 2
    BOTH = 3

def is_upper(char):
    return ORD_A <= ord(char) <= ORD_Z

def is_lower(char):
    return ORD_a <= ord(char) <= ORD_z

def is_letter(char):
    return is_upper(char) or is_lower(char)

def get_case(char):
    if is_upper(char):
        return LetterCase.UPPER
    if is_lower(char):
        return LetterCase.LOWER
    raise ValueError('Not a letter')

class ClassicalCipher(abc.ABC):
    #If not given, bad_case gets the value of bad_letters
    def __init__(self, start=0, invalid=LetterAction.KEEP, case=LetterCase.BOTH, invalid_case=None):
        self.start = start
        self.invalid = invalid
        self.case = case
        if invalid_case is None:
            self.invalid_case = invalid
        else:
            self.invalid_case = invalid_case
    
    #return KEEP or REMOVE if the char should be kept or removed.
    def char_to_int(self, char):
        if not is_letter(char):
            if self.invalid is LetterAction.KEEP or self.invalid is LetterAction.REMOVE:
                return self.invalid
            raise util.CryptoException('Bad character {}: not a letter'.format(char))
        
        case = get_case(char)
        if case is self.case or self.case is LetterCase.BOTH or self.invalid_case is LetterAction.CONVERT:
            if case is LetterCase.UPPER:
                return ord(char) - ORD_A + self.start
            else:
                return ord(char) - ORD_a + self.start
        
        if self.invalid_case is LetterAction.KEEP or self.invalid_case is LetterAction.REMOVE:
                return self.invalid_case
        raise util.CryptoException('Bad character {}: wrong case'.format(char))
    
    def encrypt(self, plaintext):
        ints, ctx = self._str_2_ints(plaintext)
        cipher_ints = self.encrypt_ints(ints)
        return self._ints_2_str(cipher_ints, ctx)
    
    def decrypt(self, ciphertext):
        ints, ctx = self._str_2_ints(ciphertext)
        plain_ints = self.decrypt_ints(ints)
        return self._ints_2_str(plain_ints, ctx)
    
    @abc.abstractmethod
    def encrypt_ints(self, nums):
        """Encrypt a list of ints and return a list of ints."""
    
    @abc.abstractmethod
    def decrypt_ints(self, nums):
        """Decrypt a list of ints and return a list of ints."""

    #return list of ints, and a context object for converting back: contains chars, UPPER and LOWER
    def _str_2_ints(self, s):
        ints = []
        ctx = []
        for char in s:
            res = self.char_to_int(char)
            if res is LetterAction.KEEP:
                ctx.append(char)
            elif res is not LetterAction.REMOVE:
                ints.append(res)
                if self.invalid_case is LetterAction.CONVERT and self.case is not LetterCase.BOTH:
                    ctx.append(self.case)
                else:
                    ctx.append(get_case(char))
        return ints, ctx

    #Convert the list of ints to a str, using the given context
    def _ints_2_str(self, ints, ctx):
        chars = []
        iter_ints = iter(ints)
        for val in ctx:
            if isinstance(val, str):
                chars.append(val)
            else:
                base = ORD_A if val is LetterCase.UPPER else ORD_a
                char = chr(base + next(iter_ints) - self.start)
                chars.append(char)
        return ''.join(chars)

class ShiftCipher(ClassicalCipher):
    #Classical shift cipehr
    #key must be a number

    def __init__(self, key, **kwargs):
        super().__init__(**kwargs)
        self.key = key
    
    def encrypt_ints(self, nums):
        return [(n + self.key) % 26 for n in nums]
    
    def decrypt_ints(self, nums):
        return [(n - self.key) % 26 for n in nums]
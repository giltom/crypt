from . import util
import itertools

class MersenneTwister:
    STATE_LEN = 624
    TEMPER_MASK_1 = 0x9d2c5680
    TEMPER_MASK_2 = 0xefc60000

    def __init__(self, state, ind=0):
        if ind >= self.STATE_LEN:
            raise ValueError('Index too big')
        self.ind = ind
        self.state = list(state)
        if len(self.state) != self.STATE_LEN:
            raise ValueError('Bad state length')
    
    @classmethod
    def from_seed(cls, seed):
        state = [seed]
        for i in range(1, cls.STATE_LEN):
            prev = state[-1]
            elem = 0x6c078965 * (prev ^ (prev >> 30)) + i
            state.append(util.uint32(elem))
        return cls(state)
    
    #reconstructs the twister out of the outputs of another twister
    #outputs should be an iterable of uint32s, with at least (-start_ind % 624) + 624 elements.
    #the returned twister will have the same output as the given twister from here on.
    #start_ind is the starting index of outputs, e.g. how many numbers have already been generated before this is called.
    @classmethod
    def from_outputs(cls, outputs, start_ind=0):
        iouts = iter(outputs)
        start_ind %= cls.STATE_LEN
        if start_ind != 0:
            for _ in range(cls.STATE_LEN - start_ind):
                next(iouts)
        state = itertools.islice(map(cls.untemper, iouts), cls.STATE_LEN)
        return cls(state)

    def copy(self):
        return self.__class__(self.state, self.ind)
    
    def regenerate(self):
        for i in range(self.STATE_LEN):
            y = self.state[i] & 0x80000000
            y += self.state[(i+1) % self.STATE_LEN] & 0x7fffffff
            z = self.state[(i + 397) % 624]
            self.state[i] = z ^ (y >> 1)
            if y % 2:
                self.state[i] ^= 0x9908b0df

    def next32(self):
        if self.ind == 0:
            self.regenerate()
        val = self.state[self.ind]
        self.ind = (self.ind + 1) % self.STATE_LEN
        return self.temper(val)
    
    def __iter__(self):
        while True:
            yield self.next32()
    
    @classmethod
    def temper(cls, val):
        val ^= val >> 11
        val ^= (val << 7) & cls.TEMPER_MASK_1
        val ^= (val << 15) & cls.TEMPER_MASK_2
        val ^= val >> 18
        return val

    @classmethod
    def untemper(cls, val):
        val ^= val >> 18
        val ^= ((val << 15) & cls.TEMPER_MASK_2)
        val = cls._undo_shift_2(val)
        val = cls._undo_shift_1(val)
        return val
    
    @classmethod
    def _undo_shift_2(cls, val):
        t = val
        for _ in range(5):
            t <<= 7
            t = val ^ (t & cls.TEMPER_MASK_1)
        return t

    @classmethod
    def _undo_shift_1(cls, val):
        t = val
        for _ in range(2):
            t >>= 11
            t ^= val
        return t
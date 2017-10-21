import string
import random

SUITES = {'C' : ('Clubs', 0), 'D' : ('Diamonds', 13), 'H' : ('Hearts', 26), 'S' : ('Spades', 39)}
RANKS = {'A' : ('Ace', 1), 'J' : ('Jack', 11), 'Q' : ('Queen', 12), 'K' : ('King', 13)}
for i in range(2, 11):
    RANKS[str(i)] = (str(i), i)

def isintable(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

class Card:
    def __init__(self, code):
        if isintable(code):
            i = int(code)
            if i < 1 or i > 54:
                raise ValueError('Invalid card ID.')
            self.id = i
        elif type(code) is str:
            if code == 'OA':
                self.id = 53
            elif code == 'OB':
                self.id = 54
            else:
                rank = code[0:len(code)-1]
                suite = code[len(code)-1]
                if suite not in SUITES or rank not in RANKS:
                    raise ValueError('Invalid card format.')
                self.id = SUITES[suite][1] + RANKS[rank][1]

    def __getattr__(self, name):
        if name == 'rank':
            return self.__get_rank()
        if name == 'value':
            return self.__get_value()
        if name == 'suite':
            return self.__get_suite()
        if name == 'code':
            return self.__get_code()
        raise AttributeError('No such attribute.')

    def isjoker(self):
        return self.id == 53 or self.id == 54

    def __get_value(self): #1,2,...,13
        if self.isjoker():
            raise AttributeError('Card is a joker.')
        return ((self.id - 1) % 13) + 1

    def __get_suite(self): #'C','D','H','S'
        if self.isjoker():
            raise AttributeError('Card is a joker.')
        offset = self.id - self.value
        for suite in SUITES:
            if SUITES[suite][1] == offset:
                return suite

    def __get_rank(self): #'A','2',...,'10','J','Q','K'
        if self.isjoker():
            raise AttributeError('Card is a joker.')
        val = self.value
        for rank in RANKS:
            if RANKS[rank][1] == val:
                return rank

    def __get_code(self): #'AS', 'OA', '10C', etc
        if self.id == 53:
            return 'OA'
        if self.id == 54:
            return 'OB'
        return self.rank + self.suite

    def getletter(self): #'A','B','C',...,'Z'
        if self.isjoker():
            raise AttributeError('Card is a joker.')
        if self.id <= 26:
            return string.ascii_uppercase[self.id-1]
        else:
            return string.ascii_uppercase[self.id-27]

    def getnumber(self): #1,2,...,53
        if self.id == 54:
            return 53
        return self.id

    def __int__(self):
        return self.id

    def __repr__(self):
        return 'Card(\'{}\')'.format(self.code)

    def __str__(self):
        if self.id == 53:
            return 'Joker A'
        if self.id == 54:
            return 'Joker B'
        return RANKS[self.rank][0] + ' of ' + SUITES[self.suite][0]

    def __eq__(self, other):
        if type(other) is not Card:
            return NotImplemented
        return self.id == other.id

class Deck:
    def __init__(self, cards=None):
        self.cards = []
        if cards is None:
            cards = list(range(1,55))
            random.shuffle(cards)
        for c in cards:
            self.cards.append(Card(c))
        if sorted(c.id for c in self.cards) != list(range(1,55)):
            raise ValueError('Invalid card list.')

    def __getitem__(self, key):
        if type(key) is int:
            return self.cards[key-1]
        elif type(key) is slice:
            return self.cards[key.start-1:key.stop:key.step]
        else:
            raise TypeError('Invalid index.')

    def __setitem__(self, key, value):
        if type(value) is list:
            val = [Card(x) for x in value]
        else:
            val = Card(value)
        if type(key) is int:
            self.cards[key-1] = val
        elif type(key) is slice:
            self.cards[key.start-1:key.stop:key.step] = val
        else:
            raise TypeError('Invalid index.')

    def position(self, card):
        return self.cards.index(Card(card)) + 1

    def __iter__(self):
        return (c for c in self.cards)

    def __repr__(self):
        return 'Deck([' + ','.join(repr(c) for c in self) + '])'

    def __str__(self):
        return ' '.join(c.code for c in self)

    def rawcardlist(self):
        return ' '.join(str(c.id) for c in self)

    def move(self, card, amount):
        pos = self.position(card) - 1
        if pos + amount > 53:
            newpos = pos + amount - 53
        else:
            newpos = pos + amount
        self.cards.remove(Card(card))
        self.cards.insert(newpos, Card(card))

    def triplecut(self, pos1, pos2):
        self.cards = self[pos2:54] + self[pos1+1:pos2-1] + self[1:pos1]

    def countcut(self, pos):
        self.cards = self[pos+1:53] + self[1:pos] + [self[54]]

import operator
import itertools
from math import sqrt
import numbers
import mpmath as mp

from . import numbers as num
import math

def is_number(thing):
    return isinstance(thing, numbers.Number)

class IVector:
    def __init__(self, *args):
        if len(args) == 0:
            raise ValueError('Provide an argument.')
        elif len(args) == 1 and not is_number(args[0]):
            self.vals = tuple(args[0])
        else:
            self.vals = args
    
    @classmethod
    def zero(cls, n):
        return cls([0]*n)
    
    def __len__(self):
        return len(self.vals)
    
    def __getitem__(self, key):
        if type(key) is slice:
            return IVector(self.vals[key])
        return self.vals[key]
    
    def __contains__(self, val):
        return val in self.vals
    
    def __repr__(self):
        return 'IVector({})'.format(','.join(str(x) for x in self))
    
    def __str__(self):
        return '({})'.format(','.join(str(x) for x in self))
    
    def __bool__(self):
        return any(x != 0 for x in self)
    
    def __hash__(self):
        return __hash__(self.vals)
    
    def __eq__(self, other):
        return isinstance(other, IVector) and self.vals == other.vals
    
    def _check_other(self, other):
        if not isinstance(other, IVector):
            return False
        if len(other) != len(self):
            raise ArithmeticError('Different vector lengths')
        return True
    
    def __add__(self, other):
        if not self._check_other(other):
            return NotImplemented
        return IVector(x + y for x,y in zip(self, other))
    
    def __neg__(self):
        return IVector(-x for x in self)
    
    def __sub__(self, other):
        return self + (-other)
    
    def _scalar_op(self, op, s):
        if not is_number(s):
            return NotImplemented
        return IVector(op(x, s) for x in self)
    
    def __mul__(self, other):
        return self._scalar_op(operator.mul, other)
    
    def __rmul__(self, other):
        return self * other
    
    def __truediv__(self, other):
        return self._scalar_op(operator.truediv, other)
    
    def __floordiv__(self, other):
        return self._scalar_op(operator.floordiv, other)
    
    def __mod__(self, other):
        return self._scalar_op(operator.mod, other)
    
    def __matmul__(self, other):
        if not self._check_other(other):
            return NotImplemented
        return sum(x * y for x,y in zip(self, other))

    def __or__(self, other):
        return self @ other == 0
    
    def norm2(self):
        return self @ self
    
    def inorm(self):
        return num.isqrt(self.norm2())
    
    def norm(self):
        return mp.mpf(self.norm2()).sqrt()

class IPolynomial:
    def __init__(self, *args, shift=0):
        if len(args) == 1 and not is_number(args[0]):
            vals = tuple(args[0])
        else:
            vals = args
        last = len(vals)
        while last > 0 and vals[last - 1] == 0:
            last -= 1
        self.vals = (0,)*shift + vals[0:last]
    
    def __len__(self):
        return len(self.vals)
    
    def degree(self):
        return len(self) - 1
    
    def __getitem__(self, key):
        if key >= len(self):
            return 0
        return self.vals[key]
    
    def __contains__(self, val):
        return val in self.vals
    
    def __iter__(self):
        return iter(self.vals)

    def __bool__(self):
        return len(self.vals) > 0
    
    def __repr__(self):
        return 'IPolynomial({})'.format(','.join(str(x) for x in self))
    
    def __str__(self):
        if not self:
            return '0'
        res = ''
        for i in range(self.degree(), -1, -1):
            a = self[i]
            if a == 0:
                continue
            if len(res) > 0:
                if a > 0:
                    res += ' + '
                else:
                    res += ' - '
                    a *= -1
            if i == 0 or a != 1:
                res += str(a)
            if i > 0:
                if a != 1:
                    res += '*'
                res += 'x'
            if i > 1:
                res += '^' + str(i)
        return res
    
    def __hash__(self):
        return __hash__(self.vals)
    
    def __eq__(self, other):
        return isinstance(other, IPolynomial) and self.vals == other.vals
    
    def __call__(self, val, modulo=None):
        if is_number(val):
            tot = 0
            term = 1
        elif isinstance(val, IPolynomial):
            tot = IPolynomial()
            term = IPolynomial(1)
        else:
            raise ValueError('Argument must be a number or polynomial.')
        for a in self:
            tot += a * term
            term *= val
            if modulo is not None:
                tot %= modulo
                term %= modulo
        return tot
    
    def __add__(self, other):
        if is_number(other):
            other = IPolynomial(other)
        if not isinstance(other, IPolynomial):
            return NotImplemented
        return IPolynomial(x + y for x,y in itertools.zip_longest(self, other, fillvalue=0))
    
    def __radd__(self, other):
        return self + other
    
    def __neg__(self):
        return IPolynomial(-x for x in self)
    
    def __sub__(self, other):
        return self + (-other)
    
    def __rsub__(self, other):
        return (-self) + other
    
    def __lshift__(self, other):
        if type(other) is not int:
            return NotImplemented
        if other < 0:
            raise ValueError('Shift can\'t be negative')
        return IPolynomial((0,)*other + self.vals)
    
    def _scalar_op(self, op, s):
        if not is_number(s):
            return NotImplemented
        return IPolynomial(op(x, s) for x in self)
    
    def __truediv__(self, other):
        return self._scalar_op(operator.truediv, other)
    
    def __floordiv__(self, other):
        return self._scalar_op(operator.floordiv, other)
    
    def __mod__(self, other):
        return self._scalar_op(operator.mod, other)

    def __mul__(self, other):
        if is_number(other):
            return self._scalar_op(operator.mul, other)
        if not isinstance(other, IPolynomial):
            return NotImplemented
        terms = [0]*(self.degree() + other.degree() + 1)
        for i in range(len(self)):
            for j in range(len(other)):
                terms[i + j] += self[i] * other[j]
        return IPolynomial(terms)
    
    def __rmul__(self, other):
        return self * other
    
    def __pow__(self, other, modulo=None):
        if type(other) is not int or (modulo is not None and type(modulo) is not int):
            return NotImplemented
        if other < 0:
            raise ValueError('Can\'t raise to negative power')
        res = IPolynomial(1)
        for _ in range(other):
            res *= self
            if modulo is not None:
                res %= modulo
        return res
    
    def factor_out_power(self):
        first = 0
        while first <= self.degree() and self[first] == 0:
            first += 1
        return IPolynomial(self.vals[first:])
    
    #returns coefficients up to x^n
    def coefficients(self, n=None):
        if n is None:
            return list(self)
        return [self[i] for i in range(n + 1)]

def project_factor(u, v):
    if not u:
        return 0
    return mp.mpf(u @ v) / u.norm2()

def gram_schmidt(basis):
    n = len(basis)
    ortho = []
    u = []
    for i in range(n):
        w = basis[i]
        u.append([None]*n)
        for j in range(i):
            u[i][j] = project_factor(ortho[j], basis[i])
            w -= u[i][j] * ortho[j]
        ortho.append(w)
    return ortho, u

"""
def gram_schmidt(basis):
    ortho = []
    zero = IVector.zero(len(basis))
    for k in range(len(basis)):
        val = basis[k] - sum((project_factor(ortho[j], basis[k]) * ortho[j] for j in range(k)), zero)
        ortho.append(val)
    return ortho
"""

def update_ortho(basis, ortho, u, i, val):
    basis[i] = val
    ortho[i] = val
    for j in range(i):
        u[i][j] = project_factor(ortho[j], val)
        ortho[i] -= u[i][j] * ortho[j]
    for k in range(i+1, len(basis)):
        oldterm = u[k][i] * ortho[i]
        u[k][i] = project_factor(ortho[i], basis[k])
        newterm = u[k][i] * val
        ortho[k] = ortho[k] + oldterm - newterm

def lll(basis, delta=mp.fraction(3, 4)):
    basis = list(basis)
    ortho, u = gram_schmidt(basis)
    n = len(basis) - 1

    k = 1
    while k <= n:
        for j in range(k-1, -1, -1):
            ukj = u[k][j]
            if abs(ukj) > mp.fraction(1,2):
                decval = round(ukj)*basis[j]
                newval = basis[k] - decval
                print('updating ortho')
                update_ortho(basis, ortho, u, k, newval)
                print('done updating')
        ukk1 = u[k][k-1]
        if ortho[k].norm2() >= (delta - ukk1**2) * ortho[k-1].norm2():
            k += 1
            print('inc to', k)
        else:
            temp = basis[k]
            update_ortho(basis, ortho, u, k, basis[k-1])
            update_ortho(basis, ortho, u, k-1, temp)
            ortho, u = gram_schmidt(basis)
            if k > 1:
                k -= 1
                print('dec to', k)
    return basis

#f - a polynomial
#n - an int
#epsilon - 1/7 or less, leave empty to choose automatically
#finds all integer roots of f(x) mod n that are smaller than n^(1/d - epsilon).
def coppersmith(f, n, epsilon):
    delta = f.degree()
    """
    if epsilon is None:
        epsilon = min(1/(delta + 1), 1/math.log(n), 1/7)
    """
    m = math.ceil(1 / (delta * epsilon))
    prec = num.ilog(10, n) * m
    npm = n**m
    mp.mp.dps = prec
    print('delta:', delta, 'm:', m, 'epsilon:', epsilon, 'prec:', prec)

    maxdeg = 0
    polys = []
    for i in range(m):
        polys.append([])
        for j in range(delta):
            gij = ((n**i * f**(m-i)) << j)
            polys[i].append(gij)
            if gij.degree() > maxdeg:
                maxdeg = gij.degree()

    print('starting root comp')
    bound = math.ceil(n ** (mp.fraction(1, delta) - epsilon))
    print('bound:', bound)
    basis = []
    for row in polys:
        for poly in row:
            bpoly = poly(IPolynomial(0, bound))
            basis.append(IVector(bpoly.coefficients(maxdeg)))
    
    lll_basis = lll(basis)
    shortest = min(lll_basis, key=IVector.norm2)
    coeffs = []
    for i, coeff in enumerate(shortest):
        assert num.divides(bound**i, coeff)
        coeffs.append(coeff // bound**i)
    return IPolynomial(coeffs)
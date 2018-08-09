import itertools
import os
import math
import random
import functools

from crypt import const
from crypt import util
from crypt import encodings as enc

#Returns random int between a and b, inclusive, not secure
rand_int = random.randint

def gcd(*nums):
    return functools.reduce(math.gcd, nums)

def divides(a, b):
    return b % a == 0

def product(nums):
    tot = 1
    for num in nums:
        tot *= num
    return tot

#true if square number
def is_square(n):
    start = n - 1
    prev = start
    while True:
        new = (prev + start // prev) >> 1
        if new == prev:
            return False
        if new > prev:
            return True
        prev = new

#integer square root (rounded down)
def isqrt(n):
    if n < 0:
        raise util.CryptoException('Square root of negative integer.')
    x = n
    y = (x + 1) >> 1
    while y < x:
        x = y
        y = (x + n // x) >> 1
    return x

#integer square root, rounded up
def isqrt_ceil(n):
    sqn = isqrt(n)
    if sqn * sqn == n:
        return sqn
    else:
        return sqn + 1

#modular multiplicative inverse of a mod n
def mod_inverse(a, n):
    n0 = n
    a0 = a % n
    t0 = 0
    t = 1
    q = n0 // a0
    r = n0 - q*a0
    while r > 0:
        temp = (t0 - q*t) % n
        t0 = t
        t = temp
        n0 = a0
        a0 = r
        q = n0 // a0
        r = n0 - q*a0
    if a0 != 1:
        raise util.CryptoException('No inverse!')
    return t

#returns r,s,t such that r = gcd(a,b) and sa + tb = r
def extended_euclidian(a, b):
    t0 = 0
    t = 1
    s0 = 1
    s = 0
    q = a // b
    r = a - q * b
    while r > 0:
        temp = t0 - q * t
        t0 = t
        t = temp
        temp = s0 - q*s
        s0 = s
        s = temp
        a = b
        b = r
        q = a // b
        r = a - q * b
    r = b
    return (r,s,t)

#returns continued fraction expansion of n/d
def continued_fraction(n, d):
    q = n // d
    r = n % d
    res = [q]
    while r != 0:
        n = d
        d = r
        q = n // d
        r = n % d
        res.append(q)
    return res

#Convergents of n/d, in the form nominator, denominator
def convergents(n, d):
    frac = continued_fraction(n, d)
    c0 = 1
    c1 = frac[0]
    d0 = 0
    d1 = 1
    res = [(c1,d1)]
    for i in range(1, len(frac)):
        new = frac[i]*c1 + c0
        c0 = c1
        c1 = new
        new = frac[i]*d1 + d0
        d0 = d1
        d1 = new
        res.append((c1, d1))
    return res

#cubic root of integer
def icbrt(a):
    if a < 0:
        raise util.CryptoException('Cubic root of negative integer (not supported currently).')
    n = 0
    while (1 << (3*(n+1)) < a):
        n += 1
    res = 1 << n
    for i in range(n-1, -1, -1):
        val = res | (1 << i)
        if val**3 < a:
            res = val
    if (res + 1)**3 == a:
        return res + 1
    return res

#computes x**y mod n. y can be negative, in which case the multiplicative inverse of x will be used.
def pow_neg(x, y, n):
    if y < 0:
        return pow(mod_inverse(x, n), -y, n)
    return pow(x, y, n)

#Guaranteed deterministic prime check (slow)
def is_prime(n):
    if n % 2 == 0:
        return False
    for q in range(3, isqrt(n) + 1, 2):
        if n % q == 0:
            return False
    return True

#Returns number of consecutive zeros at the LSBs of n
def count_trailing_zeros(n):
    count = 0
    while n & 1 == 0:
        n >>= 1
        count += 1
    return count

#Fast check if n is prime with error probability of at most 1/4. A False answer is always correct, but a True answer may be wrong.
def miller_rabin(n):
    nm1 = n - 1
    k = count_trailing_zeros(nm1)
    m = (nm1) >> k
    a = rand_int(1, nm1)
    b = pow(a, m, n)
    if b == 1:
        return True
    for _ in range(k):
        if b == nm1:
            return True
        b = pow(b, 2, n)
    return False

#Nondeterministic fast prime-checking algorithm (chance of error is 1/(4**iterations))
def is_prime_fast(n, iterations=50):
    for _ in range(iterations):
        if not miller_rabin(n):
            return False
    return True

#Very simple but inefficient prime factoring algorithm
def prime_factors(n):
    facts = itertools.chain(pregen_primes(), itertools.count(max_pregen_prime()+2, 2))
    fact = next(facts)
    while n > 1:
        if n % fact == 0:
            yield fact
            n //= fact
        else:
            fact = next(facts)

#generates a random number with the given number of bits. Do not use for real crypto.
#the MSB is always 1, so there are actually 2^(nbits-1) bits of randomness.
def gen_random_num(nbits):
    nrand = nbits - 1
    randbytes = os.urandom(nrand // 8)
    lastbyte = os.urandom(1)[0]
    mask = 0
    for i in range(0, nrand % 8):
        mask |= 1 << i
    lastbit = 1 << (nbits - 1)
    return enc.bytes2int_big(bytes([lastbyte & mask]) + randbytes) | lastbit

#generates a random prime number with the given number of bits. Do not use for real crypto.
#iterations is the number of iterations for primality testing
def gen_random_prime(nbits, iterations=30):
    while True:
        n = gen_random_num(nbits)
        if is_prime_fast(n, iterations):
            return n

#legendre symbol (a/p), assuming that p is prime
def legendre(a, p):
    res = pow(a, (p-1)//2, p)
    if res == 0 or res == 1:
        return res
    if res == p - 1:
        return -1
    raise util.CryptoException("Error computing legendre")

#jacobi symbol (a/(factors[0]*factors[1]*...)) assuming all factors are prime
def jacobi(a, *factors):
    res = 1
    for fact in factors:
        res *= legendre(a, fact)
    return res

#true if a is a quad residue mod p, assuming that it is prime
def is_quad_residue(a, p):
    return legendre(a, p) == 1

#Generator of a list of pregenerated orimes up to some number (currently 1 billion)
def pregen_primes():
    fp = open(const.PRIMES_FNAME, 'r')
    for line in fp:
        yield int(line, 16)
    fp.close()

def max_pregen_prime():
    if max_pregen_prime.maxprime:
        return max_pregen_prime.maxprime
    fp = open(const.PRIMES_FNAME, 'rb')
    pos = -2
    while True:
        fp.seek(pos, 2)
        if fp.read(1) == b'\n':
            break
        pos -= 1
    fp.seek(pos, 2)
    b = fp.read(-pos)
    fp.close()
    max_pregen_prime.maxprime = int(b, 16)  #cache the result for later
    return max_pregen_prime.maxprime
max_pregen_prime.maxprime = None

#Generates pregenerated primes up to sqrt(n) if it is smaller/equal to max_pregen_prime(n),
#or all pregen primes followed by all odd numbers between max_pregen_prime() and sqrt(n) otherwise.
def possible_pregen_factors(n):
    sqn = isqrt(n)
    if max_pregen_prime() >= sqn:
        return itertools.takewhile(lambda p: p <= sqn, pregen_primes())
    else:
        return itertools.chain(pregen_primes(), range(max_pregen_prime()+2, sqn+1, 2))

#Attempt to factor n=p*q and returns a factor. Only viable if p is near q.
def fermat_factor(n):
    a = isqrt(n)
    if a*a == n:
        return a
    while True:
        a += 1
        b = a*a - n
        if is_square(b):
            break
    return a - isqrt(b)

#Trial division factoring. Returns a factor of n or None if n is prime.
def trial_factor(n):
    if n % 2 == 0:
        return 2
    for fact in range(3, isqrt(n) + 1, 2):
        if n % fact == 0:
            return fact
    return None

#Try to find a prime factor using a list of pregenerated primes, falling back to counting if all primes are used up
def trial_factor_pregen(n):
    if n % 2 == 0:
        return 2
    for p in possible_pregen_factors(n):
        if n % p == 0:
            return p
    return None

#Tries to compute a prime factor p of n, given that the prime factors of p-1 are less/equal to bound.
#Time increases with bound. Good if p-1 has small prime factors.
#Returns None on a failure.
def pollard_pm1_algorithm(n, bound):
    if n % 2 == 0:
        return 2
    a = 2
    for j in range(2, bound + 1):
        a = pow(a, j, n)    #a = 2^(bound!)
    d = gcd(a - 1, n)
    if 1 < d < n:
        return d
    return None

#Calls pollard p-1 algorithm with increasing bound until successful.
#Good if for the prime factor p, p-1 has only small prime factors.
def pollard_pm1_incremental(n):
    for bound in possible_pregen_factors(n):
        res = pollard_pm1_algorithm(n, bound)
        if res:
            return res

#Another attempt at factoring. Always works if p is combosite, but can take time.
#Runs forever if p is prime.
def pollard_rho_algorithm(n, x1=1, f=lambda x: x**2 + 1):
    while True:
        x = x1
        xt = f(x) % n
        p = gcd((x - xt) % n, n)
        while p == 1:
            x = f(x) % n
            xt = f(xt) % n
            xt = f(xt) % n
            p = gcd((x - xt) % n, n)
        if p != n:
            return p
        else:
            x1 = (x1 + 1) % n

#return integer logarithm, rounded down.
def ilog(base, n):
    if n < 0:
        raise util.CryptoException("Log of negative integer.")
    count = 0
    while n >= base:
        count += 1
        n //= base
    return count

def num_bits(n):
    return ilog(2, abs(n)) + 1

#true if the numbers are pairwise coprime
def coprime(*nums):
    return all(gcd(n, m) == 1 for n, m in itertools.combinations(nums, 2))

#equations should be pairs of integers (a,m), where all of the m's are pairwise coprime.
#returns the unique solution, mod the product of all m's, for the system of equations:
#x = a1 (mod m1), x = a2 (mod m2), ...
def chinese_remainder(*equations):
    m = 1
    for ai, mi in equations:
        m *= mi
    return sum(ai * (m//mi) * mod_inverse(m//mi, mi) for ai, mi in equations) % m

#discrete log_a(b) mod n.
#order is the order of a in Z_n. If not given, it is taken to be n-1 (i.e. a is a primitive element mod n)
#Uses time and space O(sqrt(order)) (usually way too much)
def shanks_algorithm(a, b, n, order=None):
    if order is None:
        order = n-1
    m = isqrt_ceil(order)
    l1 = []
    val = 1
    apm = pow(a, m, n)
    for i in range(m): #l1[i] = (j, a^(mi)):
        l1.append((i, val))
        val = (val * apm) % n
    l1.sort(key = lambda t: t[1])   #sort by second coordinate
    l2 = []
    val = b
    ainv = mod_inverse(a, n)
    for i in range(m):  #l2[i] = (i, b*a^(-i)):
        l2.append((i, val))
        val = (val * ainv) % n
    l2.sort(key = lambda t: t[1])
    #find elements of l1 and l2 that have the same 2nd coordinate:
    i = 0
    j = 0
    while l1[i][1] != l2[j][1]:
        if l1[i][1] < l2[j][1]:
            i += 1
        else:
            j += 1
    return (m * l1[i][0] + l2[j][0]) % order

#discrete log_a(b) mod n.
#order is the order of a in Z_n. If not given, it is taken to be n-1 (i.e. a is a primitive element mod n)
def pollard_rho_dislog_algorithm(a, b, n, order=None):
    if order is None:
        order = n - 1

    def f(x, i, j):
        if x % 3 == 1:
            return (b*x % n, i, (j+1) % order)
        if x % 3 == 0:
            return (x**2 % n, 2*i % order, 2*j % order)
        return (a*x % n, (i+1) % order, j)

    x, i, j = f(1, 0, 0)
    xt, it, jt = f(x, i, j)
    while x != xt:
        x, i, j = f(x, i, j)
        xt, it, jt = f(xt, it, jt)
        xt, it, jt = f(xt, it, jt)

    if jt > j:
        d = gcd(jt - j, order)
        di = (i - it) // d
        dj = (jt - j) // d
    else:
        d = gcd(j - jt, order)
        di = (it - i) // d
        dj = (j - jt) // d
    dorder = order // d
    #now we have c*dj = di (mod dorder)
    dc = (mod_inverse(dj, dorder) * (di % dorder)) % dorder
    for k in range(d):
        c = (dc + k*dorder) % order
        if pow(a, c, n) == b:
            return c

#returns the discrete (log_a(b) mod n) mod q^c, where q is prime, q^c divides order, and q^(c+1) doesn't.
#order is the order of a in Z_n. If not given, it is taken to be n-1 (i.e. a is a primitive element mod n)
def pohlig_hellman_algorithm_factor(a, b, n, q, c, order=None):
    SHANKS_MAX_Q = 2**58    #max q for which shank's algorithm will be used instead of pollard's

    if order is None:
        order = n - 1
    res = []    #this will be a base-q representation of the result
    bj = b
    for j in range(c):
        d = pow(bj, order // (q**(j+1)), n)
        base = pow(a, order // q, n)
        if q <= SHANKS_MAX_Q:
            aj = shanks_algorithm(base, d, n, q)
        else:
            aj = pollard_rho_dislog_algorithm(base, d, n, q)
        res.append(aj)
        bj = bj * pow_neg(a, -aj*(q**j), n) % n
    return sum(res[i]*(q**i) for i in range(c))

#returns the discrete log_a(b) mod n. Factors is the complete list of factors in the prime factorization of order, including repetitions.
#for example, list(prime_factors(order))
#order is the order of a in Z_n. If not given, it is taken to be n-1 (i.e. a is a primitive element mod n)
def pohlig_hellman_algorithm(a, b, n, factors, order=None):
    equations = []
    lfactors = list(factors)
    for q in set(lfactors):
        c = lfactors.count(q)
        logmod = pohlig_hellman_algorithm_factor(a, b, n, q, c, order)
        equations.append((logmod, q**c))
    return chinese_remainder(*equations)

#returns integer k-th root of n, rounded down
def iroot(k, n):
    if k <= 0:
        raise util.CryptoException('Bad root order!')
    if k == 1:
        return n
    if k == 2:
        return isqrt(n)
    if k == 3:
        return icbrt(n)
    #we do a binary search in [0,n] because im lazy
    bottom = 0
    top = n
    candidate = 0
    while bottom <= top:
        middle = (top - bottom) // 2 + bottom
        res = middle**k
        if res == n:
            return middle
        if res < n:
            if middle > candidate:
                candidate = middle
            bottom = middle + 1
        else:
            top = middle - 1
    return candidate

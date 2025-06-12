from secrets import token_bytes
from typing import ClassVar, List


def byteLengthFromBitLength(bits):
    assert isinstance(bits, int), 'bitlength must be an int'
    assert bits >= 0, 'bitlength must be nonnegative'
    return (bits + 7) // 8


def byteLengthForValue(value):
    assert isinstance(value, int), 'value must be an int'
    assert value >= 0, "value must not be negative"
    return byteLengthFromBitLength(int.bit_length(value))


def bytesFromInt(value):
    assert isinstance(value, int), 'value must be an int'
    assert value >= 0, 'value must be nonnegative'
    return value.to_bytes(length=byteLengthForValue(value), byteorder='big', signed=False)


def bytesToInt(b):
    assert isinstance(b, bytes), "expected a sequence of bytes"
    return int.from_bytes(b, byteorder='big', signed=False)


def modularInverse(a, mod):
    assert isinstance(a, int), 'a must be int'
    assert isinstance(mod, int), 'mod must be int'
    assert mod > 1, f'invalid mod {mod}'
    assert 0 <= a < mod, f'value out of range {a} given mod {mod}'

    b0 = b = mod
    x0, x1 = 0, 1

    while a > 1:
        assert b != 0, 'value and mod must be coprime'
        q = a // b
        a, b = b, a % b
        x0, x1 = x1 - q * x0, x0

    if x1 < 0:
        x1 += b0

    return x1


def lagrangeInterpolation(x, points, primeMod):
    # points = [(x0, y0), (x1, y1), ...]
    assert primeMod > 1, 'invalid prime mod'
    assert 0 <= x < primeMod, 'out-of-range value'

    for (xi, yi) in points:
        assert 0 <= xi < primeMod and 0 <= yi < primeMod,  'invalid points'

    y = 0
    for i, (xi, yi) in enumerate(points):
        numerator = yi
        denominator = 1

        for j, (xj, yj) in enumerate(points):
            if j == i:
                continue

            numerator *= (x - xj + primeMod) % primeMod
            numerator %= primeMod
            denominator *= (xi - xj + primeMod) % primeMod
            denominator %= primeMod

        y += (numerator * modularInverse(denominator, primeMod)) % primeMod
        y %= primeMod

    return y


class Polynomial:
    pow2Primes: ClassVar = {
        # 2**k + v
        **{
            # mersenne primes
            k: -1
            for k in [
                17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281, 3217, 4253, 4423,
                9689, 9941, 11213, 19937, 21701, 23209, 44497, 86243, 110503, 132049, 216091,
                # 756839, 859433, 1257787, 1398269, 2976221, 3021377, 6972593
            ]
        },
        128: 51,
        192: 133,
        256: 297,
        320: 27,
        384: 231,
        448: 211,
        512: 75,
        768: 183,
        1024: 643,
        1536: 75,
        2048: 981,
        3072: 813,
        4096: 1761,
    }

    @classmethod
    def selectModulus(cls, value, modulus):
        assert isinstance(value, int), f'value must be int (not {type(value).__name__}'

        moduli = cls.pow2Primes

        if modulus is ... or modulus is None:
            for modulus in sorted(moduli.keys()):
                powMod = 2 ** modulus + moduli[modulus]

                if value < powMod:
                    break

        else:
            assert modulus in moduli, f'Invalid modulus {modulus}'
            powMod = 2 ** modulus + moduli[modulus]

        assert value < powMod, f'value is too large {value} for modulus {modulus}'
        return modulus, powMod

    def __init__(self, modulus: int, coefficients: List[int]):
        # coefficients = [a_k, ..., a_1, a_0] where P(x) = a_k*x^k + ... + a_1*x + a_0
        delta = self.pow2Primes.get(modulus)
        assert delta is not None, f'Invalid prime modulus {modulus}'

        primeMod = 2 ** modulus + delta
        assert len(coefficients) < primeMod,  f'Too many coefficients for prime modulus {modulus}'

        for coefficient in coefficients:
            assert isinstance(coefficient, int), 'coefficients must be ints'
            assert 0 <= coefficient < primeMod,  'out-of-range coefficients'

        self.coefficients = coefficients
        self.modulus = modulus
        self.primeMod = primeMod

    def evaluate(self, x):
        assert isinstance(x, int), 'coordinate must be an int'
        assert x != 0, 'coordinate 0 may not be given, as it corresponds to the secret'
        assert 0 <= x < self.primeMod, f'coordinate out-of-range for prime modulus {self.modulus}: {x}'

        y = 0
        primeMod = self.primeMod

        for coefficient in self.coefficients:
            y *= x
            y %= primeMod
            y += coefficient
            y %= primeMod

        return y


class Shamir:
    @classmethod
    def split(cls, secret: bytes, threshold: int, shareCount: int, modulus: int = ...):
        assert 1 < threshold <= shareCount, \
            f'Invalid threshold ({threshold}) for share count ({shareCount})'

        secret = bytes([42]) + secret
        secret_length = len(secret)
        largest_representable_secret = bytesToInt(bytes([255]) * secret_length)
        modulus, primeMod = Polynomial.selectModulus(largest_representable_secret, modulus)

        prime_bytes = byteLengthForValue(primeMod - 1)
        secretInt = bytesToInt(secret)
        coefficients = []

        for i in range(1, threshold):
            coefficients.append(bytesToInt(token_bytes(prime_bytes)) % primeMod)

        coefficients.append(secretInt)
        polynomial = Polynomial(modulus, coefficients)
        shares = {}

        for i in range(1, shareCount + 1):
            shares[i] = bytesFromInt(polynomial.evaluate(i))

        return cls(modulus=modulus, shares=shares, threshold=threshold)

        # return {
        #     "required_shares": required_shares,
        #     "primeMod": bytesFromInt(primeMod),
        #     "shares": shares,
        # }

    def __init__(self, *, modulus, shares, threshold = None):
        self.modulus = modulus
        self.shares = shares
        self.threshold = threshold

    def recover(self):
        shares = self.shares

        if self.threshold:
            assert len(shares) >= self.threshold, f'Required shares {self.threshold} not met (got {len(shares)})'

        primeMod = 2 ** self.modulus + Polynomial.pow2Primes[self.modulus]
        points = []

        for x, y in shares.items():
            assert isinstance(x, int), 'the first entry of each a share must be an int'
            assert isinstance(y, bytes), 'the second entry of each a share must be an array of bytes'

            points.append((x, bytesToInt(y)))

            if len(points) == self.threshold:
                break

        return bytesFromInt(lagrangeInterpolation(0, points, primeMod))[1:]

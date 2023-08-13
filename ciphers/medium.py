import typing
from collections import namedtuple

import numpy as np
from galois import GF

from ciphers import common


MediumKeys = namedtuple('MediumKeys', ['k0', 'k1', 'k0p', 'k1a'])


class Medium:
    _nrounds: int = 2
    _nbits: int = 4
    _ncells: int = 4
    _gf = GF(2 ** _nbits)
    _key_size_bits = 32
    _key_size_bits_half = _key_size_bits // 2

    _sbox: np.ndarray[int] = np.array([0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6])
    _pbox: np.ndarray[int] = np.array([0, 2, 3, 1])
    _pbox_inverse: np.ndarray[int] = np.array([0, 3, 1, 2])
    _m = np.array([[0, 1], [1, 0]], dtype=int)
    _alpha = 0b_1001_0101_0010_1110

    def encrypt(self, plaintext: int, key: int, use_related_key: bool = False) -> int:
        keys = self._key_schedule(key)

        state, *keys = self._to_array(self._ncells, self._nbits, plaintext, *keys)
        state, *keys = self._to_gf(state, *keys)

        keys = MediumKeys(*keys)

        if use_related_key:
            keys = MediumKeys(keys.k0p, keys.k1a, keys.k0, keys.k1)

        # First half.
        state = common.add(state, keys.k0)
        state = common.add(state, keys.k1)
        for i in range(self._nrounds):
            state = self._round(state, keys.k1)

        # Middle rounds.
        state = common.substitute(state, self._sbox)
        state = common.matrix_multiply(state, self._m)
        state = common.substitute(state, self._sbox)

        # Second half.
        for i in range(self._nrounds):
            state = self._round_inverse(state, keys.k1a)

        state = common.add(state, keys.k1a)
        state = common.add(state, keys.k0p)

        return common.array2int(state, self._nbits)

    def decrypt(self, ciphertext: int, key: int) -> int:
        return self.encrypt(ciphertext, key, use_related_key=True)

    # TODO: Add round constants.
    def _round(self, previous_state: np.ndarray[int], round_key: np.ndarray[int]) -> np.ndarray[int]:
        state = previous_state.copy()

        state = common.substitute(state, self._sbox)
        state = common.add(state, round_key)
        state = common.permute(state, self._pbox)
        state = common.matrix_multiply(state, self._m)

        return state

    # TODO: Add round constants.
    def _round_inverse(self, previous_state: np.ndarray[int], round_key: np.ndarray[int]) -> np.ndarray[int]:
        state = previous_state.copy()

        state = common.matrix_multiply(state, self._m)
        state = common.permute(state, self._pbox_inverse)
        state = common.add(state, round_key)
        state = common.substitute(state, self._sbox)

        return state

    def _key_schedule(self, key: int) -> list[int]:
        """
        MANTIS key schedule.

        :param key: key to expand.
        :returns: list of keys ``[k0, k1, k0p, k1a]``, which are specified in MANTIS paper.
        """

        mask = common.get_mask(self._key_size_bits_half)

        k0 = (key & (mask << self._key_size_bits_half)) >> self._key_size_bits_half
        k1 = key & mask
        k0p = (common.rotate_left(k0, self._key_size_bits_half, self._key_size_bits_half - 1) ^
               (k0 >> (self._key_size_bits_half - 1)))
        k1a = k1 ^ self._alpha

        return [k0, k1, k0p, k1a]

    def _to_array(self, cell_amount, cell_size_bits, *numbers: int) -> typing.Iterable[np.ndarray[int]]:
        """
        Convert numbers to arrays.

        :param cell_amount: amount of cells for each array.
        :param cell_size_bits: each cell bit size.
        :param numbers: numbers to convert.
        :returns: iterable of arrays to be unpacked.
        """

        return (common.int2array(number, cell_amount, cell_size_bits) for number in numbers)

    def _to_gf(self, *arrays: np.ndarray[int]) -> typing.Iterable[np.ndarray[int]]:
        """
        Move arrays to GF.

        **Examples**

        ``x, *y = self._to_gf([1, 2, 3], [[2, 3, 4], [3, 4, 5]])`` yields ``x = GF([1, 2, 3])`` and
        ``y = [GF([2, 3, 4]), GF([3, 4, 5]])``

        :param arrays: input arrays to be processed.
        :returns: processed arrays in the same order they were passed.
        """

        return (self._gf(array) for array in arrays)

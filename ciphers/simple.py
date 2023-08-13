import typing

import numpy as np
from galois import GF

from ciphers import common


class Simple:
    """
    Simple is a 2-round 16-bit block cipher with 32-bit key and 4-bit cells inside.
    It is based on SP-network and consists of adding key, substitution and permutation.
    Key schedule is k = k0 || k1 || k2, each key is 64 bit.

    **Examples**

    >>> simple = Simple()
    >>> plaintext = 20438  # 0b_0100_1111_1101_0110 = 0x4fd6
    >>> import secrets
    >>> key = secrets.randbits(32)
    >>> ciphertext = simple.encrypt(plaintext, key)
    """

    # MANTIS involute 4x4 S-box.
    _sbox: np.ndarray[int] = np.array([0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6])

    # Involute P-box from https://www.engr.mun.ca/~howard/PAPERS/ldc_tutorial.pdf.
    _pbox: np.ndarray[int] = np.array([3, 2, 1, 0])

    _nrounds: int = 2

    # This is connected to S-box size.
    _nbits: int = 4

    # This is connected to P-box size.
    _ncells: int = 4

    _gf = GF(2 ** _nbits)

    def encrypt(self, plaintext: int, key: int) -> int:
        state, = self._to_array(self._ncells, self._nbits, plaintext)
        key, = self._to_array(self._nrounds * self._ncells, self._nbits, key)

        state, key = self._to_gf(state, key)
        round_keys = self._key_schedule(key)

        for i in range(self._nrounds):
            state = self._round(state, round_keys[i])

        return common.array2int(state, self._nbits)

    def decrypt(self, ciphertext: int, key: int) -> int:
        state, = self._to_array(self._ncells, self._nbits, ciphertext)
        key, = self._to_array(self._nrounds * self._ncells, self._nbits, key)

        state, key = self._to_gf(state, key)
        round_keys = self._key_schedule(key)[::-1]

        for i in range(self._nrounds):
            state = self._round_inverse(state, round_keys[i])

        return common.array2int(state, self._nbits)

    def encrypt_rounds(self, plaintext: int, round_keys: list[int], nrounds: int) -> int:
        state, *keys = self._to_array(self._ncells, self._nbits, plaintext, *round_keys)
        state, *keys = self._to_gf(state, *keys)

        for i in range(nrounds):
            state = self._round(state, keys[i])

        return common.array2int(state, self._nbits)

    def decrypt_rounds(self, ciphertext: int, round_keys: list[int], nrounds: int) -> int:
        state, *keys = self._to_array(self._ncells, self._nbits, ciphertext, *round_keys)
        state, *keys = self._to_gf(state, *keys[::-1])

        for i in range(nrounds):
            state = self._round_inverse(state, keys[i])

        return common.array2int(state, self._nbits)

    def _round(self, previous_state: np.ndarray[int], round_key: np.ndarray[int]) -> np.ndarray[int]:
        state = previous_state.copy()

        state = common.add(state, round_key)
        state = common.substitute(state, self._sbox)
        state = common.permute(state, self._pbox)  # This is not needed on the last round.

        return state

    def _round_inverse(self, previous_state: np.ndarray[int], round_key: np.ndarray[int]) -> np.ndarray[int]:
        state = previous_state.copy()

        state = common.permute(state, self._pbox)
        state = common.substitute(state, self._sbox)
        state = common.add(state, round_key)

        return state

    def _key_schedule(self, key: np.ndarray[int]) -> list[np.ndarray[int]]:
        return [round_key for round_key in np.split(key, self._nrounds)]

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

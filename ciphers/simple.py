import typing

import numpy as np
from galois import GF

from ciphers import common


class Simple:
    """
    Simple 2-round 64-bit block cipher with 192-bit key and 4-bit cells inside.
    It is based on SP-network and consists of ``add_key``
    Key schedule is k = k0 || k1 || k2, each key is 64 bit.

    **Examples**

    >>> simple = Simple()
    >>> plaintext = np.array([0x1, 0x2, 0x3, 0x4, 0x1, 0x2, 0x3, 0x2, 0x1, 0x2, 0x3, 0x4, 0x1, 0x2, 0x3, 0x2])
    >>> import secrets
    >>> key = np.array([secrets.randbits(4) for _ in range(32)])  # 4 * 32 = 2 * 64 = 2 * (plaintext size)
    >>> simple.encrypt(plaintext, key)
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

    def encrypt(self, plaintext: np.ndarray[int], key: np.ndarray[int]) -> np.ndarray[int]:
        if plaintext.size != self._ncells:
            raise ValueError(f'Invalid plaintext size: {plaintext.size} cells. Should be {self._ncells} cells.')

        if key.size != self._nrounds * self._ncells:
            raise ValueError(f'Invalid key size: {key.size} cells. Should be {3 * self._ncells} cells.')

        state, key = self._prepare_inputs(plaintext, key)
        round_keys = self._key_schedule(key)

        for i in range(self._nrounds):
            state = self._round(state, round_keys[i])

        return state

    def encrypt_rounds(self, plaintext: np.ndarray[int], round_keys: list[np.ndarray[int]], nrounds: int) -> int:
        state, *keys = self._prepare_inputs(plaintext, *round_keys)

        for i in range(nrounds):
            state = self._round(state, keys[i])

        return common.array2int(state, self._nbits)

    def decrypt_rounds(self, ciphertext: np.ndarray[int], round_keys: list[np.ndarray[int]], nrounds: int) -> int:
        state, *keys = self._prepare_inputs(ciphertext, *round_keys[::-1])

        for i in range(nrounds):
            state = self._round_inverse(state, keys[i])

        return common.array2int(state, self._nbits)

    def decrypt(self, ciphertext: np.ndarray[int], key: np.ndarray[int]) -> np.ndarray[int]:
        if ciphertext.size != self._ncells:
            raise ValueError(f'Invalid ciphertext size: {ciphertext.size} cells. Should be {self._ncells} cells.')

        if key.size != self._nrounds * self._ncells:
            raise ValueError(f'Invalid key size: {key.size} cells. Should be {3 * self._ncells} cells.')

        state, key = self._prepare_inputs(ciphertext, key)
        round_keys = self._key_schedule(key)[::-1]

        for i in range(self._nrounds):
            state = self._round_inverse(state, round_keys[i])

        return state

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

    def _prepare_inputs(self, *arrays: np.ndarray[int]) -> typing.Iterable[np.ndarray[int]]:
        """
        Prepare inputs for usage inside block cipher.

        **Examples**

        ``x, *y = self._prepare_inputs([1, 2, 3], [[2, 3, 4], [3, 4, 5]])`` yields ``x = processed [1, 2, 3]`` and
        ``y = [processed [2, 3, 4], processed [3, 4, 5]]``

        :param arrays: input arrays to be processed.
        :returns: processed arrays in the same order they were passed.
        """

        # TODO: Accept ints and convert them to arrays.
        return (self._gf(array) for array in arrays)

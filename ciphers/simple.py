import typing

import numpy as np
from galois import GF

from ciphers import common


class Simple:
    # MANTIS involute 4x4 S-box.
    _sbox: np.ndarray[int] = np.array([0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6])

    # Involute P-box from https://www.engr.mun.ca/~howard/PAPERS/ldc_tutorial.pdf.
    _pbox: np.ndarray[int] = np.array([0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15])

    _nrounds: int = 3

    # This is connected to S-box size.
    _nbits: int = 4

    # This is connected to P-box size.
    _ncells: int = 16

    _gf = GF(2 ** _nbits)

    def encrypt(self, plaintext: np.ndarray[int], key: np.ndarray[int]) -> np.ndarray[int]:
        if plaintext.size != self._ncells:
            raise ValueError(f'Invalid plaintext size: {plaintext.size} cells. Should be {self._ncells} cells.')

        if key.size != 3 * self._ncells:
            raise ValueError(f'Invalid key size: {key.size} cells. Should be {3 * self._ncells} cells.')

        state, key = self._prepare_inputs(plaintext, key)
        round_keys = self._key_schedule(key)

        for i in range(self._nrounds):
            state = self._round(state, round_keys[i])

        return state

    def decrypt(self, ciphertext: np.ndarray[int], key: np.ndarray[int]) -> np.ndarray[int]:
        if ciphertext.size != self._ncells:
            raise ValueError(f'Invalid ciphertext size: {ciphertext.size} cells. Should be {self._ncells} cells.')

        if key.size != 3 * self._ncells:
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
        return (self._gf(array) for array in arrays)

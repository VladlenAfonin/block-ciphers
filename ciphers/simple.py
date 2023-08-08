import typing

import numpy as np
from galois import GF

from ciphers import common


class Simple:
    _sbox: np.ndarray[int] = np.array([0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6])
    _nrounds: int = 3
    _nbits: int = 4
    _ncells: int = 16

    def __init__(self) -> None:
        self._gf = GF(2 ** self._nbits)

    def encrypt(self, plaintext: np.ndarray[int], key: np.ndarray[int]) -> np.ndarray[int]:
        if plaintext.size != self._ncells:
            raise ValueError(f'Invalid plaintext size: {plaintext.size}.')

        if key.size != 3 * self._ncells:
            raise ValueError(f'Invalid key size: {key.size}.')

        ciphertext, key = self._prepare_inputs(plaintext, key)
        round_keys = self._key_schedule(key)

        for i in range(self._nrounds):
            ciphertext = self._round(ciphertext, round_keys[i])

        return ciphertext

    def decrypt(self, ciphertext: np.ndarray[int], key: np.ndarray[int]) -> np.ndarray[int]:
        if ciphertext.size != self._ncells:
            raise ValueError(f'Invalid ciphertext size: {ciphertext.size}.')

        if key.size != 3 * self._ncells:
            raise ValueError(f'Invalid key size: {key.size}.')

        plaintext, key = self._prepare_inputs(ciphertext, key)
        round_keys = self._key_schedule(key)[::-1]

        for i in range(self._nrounds):
            plaintext = self._round_inverse(plaintext, round_keys[i])

        return plaintext

    def _round(self, previous_state: np.ndarray[int], round_key: np.ndarray[int]) -> np.ndarray[int]:
        state = previous_state.copy()

        state = common.substitute(state, self._sbox)
        state = common.add(state, round_key)

        return state

    def _key_schedule(self, key: np.ndarray[int]) -> list[np.ndarray[int]]:
        return [round_key for round_key in np.split(key, self._nrounds)]

    def _round_inverse(self, previous_state: np.ndarray[int], round_key: np.ndarray[int]) -> np.ndarray[int]:
        state = previous_state.copy()

        state = common.add(state, round_key)
        state = common.substitute(state, self._sbox)

        return state

    def _prepare_inputs(self, *arrays: np.ndarray[int]) -> typing.Iterable[np.ndarray[int]]:
        return (self._gf(array) for array in arrays)

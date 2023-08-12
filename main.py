import secrets

import numpy as np

from ciphers import common
from ciphers.common import FixedBitsIterator
from ciphers.simple import Simple


def generate_key(nbits: int, ncells: int) -> np.ndarray:
    return np.array([secrets.randbits(nbits) for _ in range(ncells)])


def main():
    simple = Simple()

    target_key = np.array([4, 5, 4, 1, 2, 15, 0, 12])

    target_plaintext = np.array([1, 2, 3, 4])
    target_ciphertext = np.array([7, 7, 8, 9])

    target_plaintext2 = np.array([2, 3, 4, 5])
    target_ciphertext2 = np.array([3, 6, 3, 0])

    target_plaintext3 = np.array([0, 0, 0, 0])
    target_ciphertext3 = np.array([13, 5, 10, 8])

    key_size = 32
    key_size_half = key_size // 2
    key_iterator = FixedBitsIterator(key_size_half, list(range(key_size_half)))

    s = {}
    for key in key_iterator:
        key_array = common.int2array(key, 4, 4)
        ct = simple.encrypt_rounds(target_plaintext, [key_array], 1)
        s[ct] = key

    for key in key_iterator:
        key_array = common.int2array(key, 4, 4)
        pt = simple.decrypt_rounds(target_ciphertext, [key_array], 1)

        if pt not in s.keys():
            continue

        master_key = np.hstack([common.int2array(s[pt], 4, 4), key_array])
        if np.all(simple.encrypt(target_plaintext2, master_key) == target_ciphertext2):
            if np.all(simple.encrypt(target_plaintext3, master_key) == target_ciphertext3):
                print(master_key)


if __name__ == '__main__':
    main()

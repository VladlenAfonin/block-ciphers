import secrets

import numpy as np

from ciphers import common
from ciphers.common import FixedBitsIterator
from ciphers.simple import Simple


def generate_key(nbits: int, ncells: int) -> np.ndarray:
    return np.array([secrets.randbits(nbits) for _ in range(ncells)])


def main():
    simple = Simple()

    target_key = common.array2int(np.array([4, 5, 4, 1, 2, 15, 0, 12]), 4)

    target_plaintext = common.array2int(np.array([1, 2, 3, 4]), 4)
    target_ciphertext = common.array2int(np.array([7, 7, 8, 9]), 4)

    target_plaintext2 = common.array2int(np.array([2, 3, 4, 5]), 4)
    target_ciphertext2 = common.array2int(np.array([3, 6, 3, 0]), 4)

    target_plaintext3 = common.array2int(np.array([0, 0, 0, 0]), 4)
    target_ciphertext3 = common.array2int(np.array([13, 5, 10, 8]), 4)

    key_size = 32
    key_size_half = key_size // 2
    key_iterator = FixedBitsIterator(key_size_half, list(range(key_size_half)))

    s = {}
    for key in key_iterator:
        ct = simple.encrypt_rounds(target_plaintext, [key], 1)
        s[ct] = key

    for key in key_iterator:
        pt = simple.decrypt_rounds(target_ciphertext, [key], 1)

        if pt not in s.keys():
            continue

        master_key = common.array2int(np.hstack([common.int2array(s[pt], 4, 4), common.int2array(key, 4, 4)]), 4)
        if simple.encrypt(target_plaintext2, master_key) == target_ciphertext2:
            if simple.encrypt(target_plaintext3, master_key) == target_ciphertext3:
                print(common.int2array(master_key, 8, 4))


if __name__ == '__main__':
    main()

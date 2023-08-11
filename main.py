import secrets

import numpy as np

from ciphers import common
from ciphers.simple import Simple


def generate_key(nbits: int, ncells: int) -> np.ndarray:
    return np.array([secrets.randbits(nbits) for _ in range(ncells)])


def main():
    # simple = Simple()
    #
    # plaintext = np.array([0x1, 0x2, 0x3, 0x4, 0x1, 0x2, 0x3, 0x2, 0x1, 0x2, 0x3, 0x4, 0x1, 0x2, 0x3, 0x2])
    # key = generate_key(4, 48)
    #
    # ciphertext = simple.encrypt(plaintext, key)
    # print(f'{ciphertext = }')
    #
    # plaintext = simple.decrypt(ciphertext, key)
    # print(f'{plaintext  = }')

    tg = common.FixedBitsIterator(4, [0, 2], 1)
    print([f'{text:04b}' for text in tg])
    print([f'{text:04b}' for text in tg])


if __name__ == '__main__':
    main()

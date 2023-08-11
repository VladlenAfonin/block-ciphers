import typing

import numpy as np


def substitute(matrix: np.ndarray[int], lookup_table: np.ndarray[int]) -> np.ndarray[int]:
    result = np.empty_like(matrix)
    with np.nditer(matrix) as iterator:
        for a in iterator:
            result[iterator.iterindex] = lookup_table[a]
    return result


def permute(matrix: np.ndarray[int], permutation: np.ndarray[int]) -> np.ndarray[int]:
    result = np.empty_like(matrix)
    with np.nditer(permutation) as iterator:
        for a in iterator:
            result[iterator.iterindex] = matrix[a]
    return result


def add(lhs: np.ndarray[int], rhs: np.ndarray[int]) -> np.ndarray[int]:
    return lhs ^ rhs


def split_int(number: int, mask_size: int, number_length: int) -> np.ndarray[int]:
    if number_length % mask_size != 0:
        raise ValueError('Number length must be multiple of mask size.')

    nsplit = number_length // mask_size
    mask = get_mask(mask_size)
    return np.array([(number & (mask << (mask_size * i))) >> (i * mask_size) for i in range(nsplit)])[::-1]


def array2int(array: np.ndarray[int], cell_size: int) -> int:
    result = 0
    with np.nditer(array) as iterator:
        for sub_number in iterator:
            result |= sub_number << (cell_size * (array.size - 1) - iterator.iterindex * cell_size)
    return result


def hex_string_to_cells(hex_string: str, ncells: int, nbits: int) -> np.ndarray[int]:
    number = int(hex_string, 16)
    return split_int(number, nbits, ncells * nbits)


def rotate_left(number: int, number_size_bits: int, amount: int) -> int:
    amount %= number_size_bits
    mask = get_mask(number_size_bits)
    return mask & (number << amount) | (number >> (number_size_bits - amount))


def get_mask(mask_size: int, bit_indices: typing.Union[list[int], None] = None) -> int:
    """Creates a mask with either all or given bits set.

    **Examples**

    >>> get_mask(4)
    15  # 0b1111

    >>> get_mask(4, [0, 3])
    9  # 0b1001

    :param mask_size: mask size.
    :param bit_indices: indices of bits set to 1. Other bits will be set to 0. Indexing starts from 0.
    :return: generated mask.
    """

    if not bit_indices:
        return (1 << mask_size) - 1

    if any([bit_index >= mask_size for bit_index in bit_indices]):
        raise ValueError(f'Bit index overflow. Mask size: {mask_size}, bit indices: {bit_indices}.')

    result = 0
    for bit_index in bit_indices:
        result |= 1 << bit_index

    return result


class FixedBitsIterator:
    """Iterate over certain bits in numbers of given size.

    **Example**

    >>> fbi = FixedBitsIterator(4, [0, 2], 0)
    >>> [f'{text:04b}' for text in fbi]
    ['1111', '1101', '0111', '0101']
    """

    def __init__(
            self, text_size_bits: int,
            iterator_bit_indices: typing.Union[list[int], None] = None,
            fixed_bits_value: int = 0) -> None:

        self._text_size_bits: int = text_size_bits
        self._iterator_bit_indices: typing.Union[list[int], None] = iterator_bit_indices
        self._fixed_bits_value: int = fixed_bits_value

        self._range = 1 << len(self._iterator_bit_indices)
        self._iterator_bit_indices.sort(reverse=True)

    def __iter__(self):
        self._counter = -1
        return self

    def __next__(self):
        self._counter += 1

        if self._counter == self._range:
            raise StopIteration

        text = get_mask(self._text_size_bits) if self._fixed_bits_value == 1 else 0
        for i, bit_index in enumerate(self._iterator_bit_indices):
            counter_bit = (self._counter >> i) & 1
            text ^= counter_bit << (self._text_size_bits - bit_index - 1)

        return text

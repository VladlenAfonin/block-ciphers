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


def get_mask(mask_size: int) -> int:
    return (1 << mask_size) - 1


def split_int(number: int, mask_size: int, number_length: int) -> np.ndarray[int]:
    if number_length % mask_size != 0:
        raise ValueError('Number length must be multiple of mask size.')

    nsplit = number_length // mask_size
    mask = get_mask(mask_size)
    return np.array([(number & (mask << (mask_size * i))) >> (i * mask_size) for i in range(nsplit)])[::-1]


def hex_string_to_cells(hex_string: str, ncells: int, nbits: int) -> np.ndarray[int]:
    number = int(hex_string, 16)
    return split_int(number, nbits, ncells * nbits)

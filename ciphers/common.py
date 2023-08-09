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

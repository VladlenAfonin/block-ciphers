import typing

import numpy as np


def substitute(matrix: np.ndarray, lookup_table: np.ndarray) -> np.ndarray:
    result = np.empty_like(matrix)
    with np.nditer(matrix) as iterator:
        for a in iterator:
            result[iterator.iterindex] = lookup_table[a]
    return result


def add(lhs: np.ndarray[int], rhs: np.ndarray[int]) -> np.ndarray[int]:
    return lhs ^ rhs


def nameof(variable: typing.Any) -> str:
    return f'{variable=}'.split('=')[0]

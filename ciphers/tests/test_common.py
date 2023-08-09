import unittest

import numpy as np
from parameterized import parameterized

from ciphers import common


class TestCommon(unittest.TestCase):
    @parameterized.expand([
        [np.array([1, 2, 3, 4]), '0x1234', 4, 4],
        [np.array([1, 2, 3, 4]), '0x01020304', 4, 8]
    ])
    def test_hex_string_to_cells(self, expected: np.ndarray[int], input_string: str, ncells: int, nbits: int) -> None:
        self.assertTrue(np.all(expected == common.hex_string_to_cells(input_string, ncells, nbits)))


if __name__ == '__main__':
    unittest.main()

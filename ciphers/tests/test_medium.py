import secrets
import unittest

from ciphers.medium import Medium


class MediumTestCase(unittest.TestCase):
    def test_identity(self):
        plaintext = secrets.randbits(16)
        key = secrets.randbits(32)

        medium = Medium()

        self.assertEqual(plaintext, medium.decrypt(medium.encrypt(plaintext, key), key))


if __name__ == '__main__':
    unittest.main()

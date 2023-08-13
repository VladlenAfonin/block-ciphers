import secrets
import unittest

from ciphers.simple import Simple


class MyTestCase(unittest.TestCase):
    def test_something(self):
        plaintext = secrets.randbits(16)
        key = secrets.randbits(32)

        simple = Simple()
        self.assertEqual(plaintext, simple.decrypt(simple.encrypt(plaintext, key), key))


if __name__ == '__main__':
    unittest.main()

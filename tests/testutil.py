import unittest


class LsTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def assertRaisesX(self, ex, msg):
        # return super().assertRaisesRegex(ex, "^" + msg + "$")
        return super().assertRaisesRegex(ex, msg + "$")  # XXX
import unittest

import LsUtil


class TestLsUtil(unittest.TestCase):
    def setUp(self):
        pass

    def iseq(self, d1, d2):
        for _, val in d1.items():
            val.sort()
        for _, val in d2.items():
            val.sort()
        self.assertEqual(d1, d2)

    def test_dict_inv(self):
        d = {'a': ['x', 'y'], 'b': ['x', 'y', 'z'], 'c': 'w'}
        dinv = LsUtil.dict_inv(d)
        expected = {'w': ['c'], 'x': ['b', 'a'], 'y': ['b', 'a'], 'z': ['b']}
        self.iseq(dinv, expected)

        d = {}
        dinv = LsUtil.dict_inv(d)
        expected = {}
        self.iseq(dinv, expected)

        d = {2: '2', '3': '3'}
        with self.assertRaises(Exception):
            dinv = LsUtil.dict_inv(d)

        d = {2: [2, 3, 'j'], '3': ['a', 'b', 'c']}
        with self.assertRaises(Exception):
            dinv = LsUtil.dict_inv(d)

        d = {'A': ''}
        with self.assertRaises(Exception):
            dinv = LsUtil.dict_inv(d)

        d = {'': 'A'}
        with self.assertRaises(Exception):
            dinv = LsUtil.dict_inv(d)

    def test_find_and_cumsum(self):
        seq = ['a', 'b', ('a', 'b', 'c'), 'a', ('a',), ('a', 'b'), 'b', ('a', 'b'),
               ('a', 'b', 'c', 'd'), 'aa', 'bb', ('aa', 'bb', 'cc'), 'cc']
        self._test_find_and_cumsum_seq(seq)

        # string
        findind, cumsum = LsUtil.find_and_cumsum(seq, 'a', True)
        self.assertEqual(findind, [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, 'a', False)
        self.assertEqual(findind, [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0])

        # tuple, length 1
        findind, cumsum = LsUtil.find_and_cumsum(seq, ('a',), True)
        self.assertEqual(findind, [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, ('a',), False)
        self.assertEqual(findind, [0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0])

        # tuple, length 2
        findind, cumsum = LsUtil.find_and_cumsum(seq, ('a', 'b'), True)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, ('a', 'b'), False)
        self.assertEqual(findind, [0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0])

        # tuple, length 3
        findind, cumsum = LsUtil.find_and_cumsum(seq, ('c', 'a', 'b'), True)
        self.assertEqual(findind, [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, ('c', 'a', 'b'), False)
        self.assertEqual(findind, [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])

        # list, length 1
        findind, cumsum = LsUtil.find_and_cumsum(seq, ['a'], True)
        self.assertEqual(findind, [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, ['a'], False)
        self.assertEqual(findind, [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a',)], True)
        self.assertEqual(findind, [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a',)], False)
        self.assertEqual(findind, [0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a', 'b')], True)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a', 'b')], False)
        self.assertEqual(findind, [0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('c', 'a', 'b')], True)
        self.assertEqual(findind, [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('c', 'a', 'b')], False)
        self.assertEqual(findind, [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])

        # list, length 2
        findind, cumsum = LsUtil.find_and_cumsum(seq, ['a', 'b'], True)
        self.assertEqual(findind, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, ['a', 'b'], False)
        self.assertEqual(findind, [1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0])

        findind, cumsum = LsUtil.find_and_cumsum(seq, ['b', ('a', 'b')], True)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, ['b', ('a', 'b')], False)
        self.assertEqual(findind, [0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0])

        findind, cumsum = LsUtil.find_and_cumsum(seq, ['b', ('b', 'a')], True)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, ['b', ('b', 'a')], False)
        self.assertEqual(findind, [0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0])

        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a', 'b'), 'a'], True)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a', 'b'), 'a'], False)
        self.assertEqual(findind, [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])

        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a',), ('b', 'a')], True)
        self.assertEqual(findind, [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a',), ('b', 'a')], False)
        self.assertEqual(findind, [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])

        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a',), ('b', 'a'), 'q'], True)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, [('a',), ('b', 'a'), 'q'], False)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        findind, cumsum = LsUtil.find_and_cumsum(seq, ['bb', ('a', 'b')], True)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        findind, cumsum = LsUtil.find_and_cumsum(seq, ['bb', ('a', 'b')], False)
        self.assertEqual(findind, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        seq = ['new_trail', 'response', 'context', 'no_response', 'context', 'response',
               'context', 'no_response', ('us', 'context'), 'no_response', 'new_trail', 'response',
               ('cs', 'context'), 'no_response', ('us', 'context'), 'no_response', 'context',
               'no_response']
        self._test_find_and_cumsum_seq(seq)

    def _test_find_and_cumsum_seq(self, seq):
        for patternlen in range(1, len(seq) + 1):
            for i in range(0, len(seq) + 1 - patternlen):
                pattern = seq[i: (i + patternlen)]
                findind, cumsum = LsUtil.find_and_cumsum(seq, pattern, True)
                self.assertEqual(findind[i], 1)
                if patternlen == 1:
                    findind, cumsum = LsUtil.find_and_cumsum(seq, pattern[0], True)
                    self.assertEqual(findind[i], 1)
                    if type(pattern[0]) is tuple:
                        for t in pattern[0]:
                            findind, cumsum = LsUtil.find_and_cumsum(seq, t, False)
                            self.assertEqual(findind[i], 1)
                            if len(pattern[0]) > 1:
                                findind, cumsum = LsUtil.find_and_cumsum(seq, t, True)
                                self.assertTrue(findind[i] != 1)

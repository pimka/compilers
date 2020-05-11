import unittest

from g5 import Parser, ParserException

#python -m unittest tests.py
class TestG5(unittest.TestCase):
    def test_success(self):
        test_case = 'programs/success.txt'
        s = ''
        with open(test_case) as f:
            s = f.read()
        p = Parser(s)
        p.run()

    def test_fail(self):
        path = 'programs/'
        test_cases = [
            'miss_close_bracket.txt',
            'miss_oper.txt'
        ]
        test_cases = [path+test for test in test_cases]

        for test in test_cases:
            s = ''
            with open(test) as f:
                s = f.read()
            p = Parser(s)
            self.assertRaises(ParserException, p.run)

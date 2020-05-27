from unittest import TestCase
from parse import Parser
#python -m unittest test.py

class ParserTestCase(TestCase):
    def test_parser(self):
        cases = [
            ('(1+2)<>3', ['1', '2', '+', '3', '<>']),
            ('1+2*3', ['1', '2', '3', '*', '+']),
            ('1 >= 2', ['1', '2', '>=']),
            ('(1*2+9) = (2*3-6)', ['1', '2', '*', '9', '+', '2', '3', '*', '6', '-', '='])
        ]

        parser = Parser()

        for expr, correct in cases:
            self.assertEqual(parser.parse(expr), correct)

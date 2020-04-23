import unittest

from dfa import DFA
from rpn import RPN
from syntax_tree import SyntaxTree

#python -m unittest tests.py

class TestDFA(unittest.TestCase):
    def testConstruct(self):
        test_regex = [
            '(0|1(01*0)*1)*#',
            '(01*1)*1#',
            '(a|b)*abb#',
            '(a|b)*#',
            '(a*|b*)*#',
            '((000)|(001)|(010)|(011)|(100)|(101)|(110)|(111))*#'
        ]
        for test in test_regex:
            tree = SyntaxTree(RPN(test))
            root_tree = tree.buildTree()
            followpos = root_tree.getFollowpos()
            drtan, nodes, start, term = root_tree.build(followpos, tree.dies_positions)
            dfa = DFA(drtan, nodes, start, term, root_tree.alphabet)

    def _getCases(self):
        tests = {
            '(0|1(01*0)*1)*#' : {
                '': True,
                '0': True,
                '011': True,
                '110':True,
                '1001':True,
                '1100':True,
                '1111':True,
                '10010':True,
                'lupa': False,
                '111': False
            },
            '(01*1)*1#': {
                '': False,
                '1': True,
                '011': True,
                '1001': False
            },
            '(a|b)*abb#': {
                '': False,
                'abb': True,
                'aabb': True,
                'babb': True,
                'ababb':True,
                'ab': False,
            },
            '(a|b)*#': {
                '': True,
                'a': True,
                'b': True,
                'ab': True,
                'ba': True,
                'pupa': False, 
            },
            '(a*|b*)*#': {
                '': True,
                'a': True,
                'b': True,
                'ab': True,
                'ba': True,
                'pupa': False, 
            },
            '((000)|(001)|(010)|(011)|(100)|(101)|(110)|(111))*#': {
                '': True,
                '0': False,
                '10': False,
                '111': True,
                '101': True,
                '1111': False,
                '010001': True
            }
        }

        return tests

    def testMatch(self):
        for pattern, test_case in self._getCases().items():
            tree = SyntaxTree(RPN(pattern))
            root_tree = tree.buildTree()
            followpos = root_tree.getFollowpos()
            drtan, nodes, start, term = root_tree.build(followpos, tree.dies_positions)
            dfa = DFA(drtan, nodes, start, term, root_tree.alphabet)

            for t, accepts in test_case.items():
                self.assertEqual(dfa.match(start, term, drtan, t), accepts)

    def testMinimizeAndMatch(self):
        for pattern, test_case in self._getCases().items():
            tree = SyntaxTree(RPN(pattern))
            root_tree = tree.buildTree()
            followpos = root_tree.getFollowpos()
            drtan, nodes, start, term = root_tree.build(followpos, tree.dies_positions)
            dfa = DFA(drtan, nodes, start, term, root_tree.alphabet)
            dfa.minimize()
            min_dfa, min_start, min_end = dfa.build_minimized(dfa.get_equal())

            for t, accepts in test_case.items():
                self.assertEqual(dfa.match(min_start, min_end, min_dfa, t), accepts)
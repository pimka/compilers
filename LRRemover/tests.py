#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from grammar import ModifiedGrammar
from left_rec_remove import Grammar
# активировать среду перед запуском тестов
#python -m unittest tests.py


class TestGrammar(unittest.TestCase):
    def setUp(self):
        self.kfg = 'KFG.json'
        self.factorization = 'factorization.json'
        self.recursion = 'test_grammar.json'

    def test_build(self):
        cases = {
            self.kfg: {'t': 4, 'nt': 6, 'pr': 14},
            self.factorization: {'t': 6, 'nt': 2, 'pr': 4},
            self.recursion: {'t': 5, 'nt': 2, 'pr': 5},
        }

        for path, info in cases.items():
            grammar = Grammar(path)

            self.assertEqual(len(grammar.terminals), info['t'], f"Unequal terminals count for '{path}'")
            self.assertEqual(len(grammar.nonterminals), info['nt'], f"Unequal nonterminals count for '{path}'")
            self.assertEqual(len(grammar.productions), info['pr'], f"Unequal productions count for '{path}'")


    def test_recursion(self):
        cases = {
            self.recursion: {'t': 5, 'nt': 3, 'pr': 7},
        }

        for path, info in cases.items():
            r_grammar = Grammar(path)
            r_grammar.remove_recursion()

            self.assertEqual(len(r_grammar.terminals), info['t'], f"Unequal terminals count for '{path}'")
            self.assertEqual(len(r_grammar.nonterminals), info['nt'], f"Unequal nonterminals count for '{path}'")
            self.assertEqual(len(r_grammar.productions), info['pr'], f"Unequal productions count for '{path}'")

    def test_factorization(self):
        cases = {
            self.factorization: {'t': 6, 'nt': 3, 'pr': 5},
        }

        for path, info in cases.items():
            r_grammar = Grammar(path)
            r_grammar.left_factorization()

            self.assertEqual(len(r_grammar.terminals), info['t'], f"Unequal terminals count for '{path}'")
            self.assertEqual(len(r_grammar.nonterminals), info['nt'], f"Unequal nonterminals count for '{path}'")
            self.assertEqual(len(r_grammar.productions), info['pr'], f"Unequal productions count for '{path}'")

    def test_kfg(self):
        cases = {
            self.kfg : {'t': 4, 'nt': 7, 'pr': 14},
        }

        for path, info in cases.items():
            r_grammar = Grammar(path)
            mgr = ModifiedGrammar(r_grammar)
            mgr.removeUselessSymbols()
            mgr.removeEpsRules()

            self.assertEqual(len(mgr.terminals), info['t'], f"Unequal terminals count for '{path}'")
            self.assertEqual(len(mgr.nonterminals), info['nt'], f"Unequal nonterminals count for '{path}'")
            self.assertEqual(len(mgr.productions), info['pr'], f"Unequal productions count for '{path}'")
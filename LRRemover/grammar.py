#! /usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import combinations

from left_rec_remove import Grammar


class ModifiedGrammar:
    def __init__(self, grammar):
        self.terminals = grammar.terminals
        self.nonterminals = grammar.nonterminals
        self.productions = grammar.productions
        self.startSymbol = grammar.startSymbolName
        self.__removeCopies()

    def __removeCopies(self):
        new_prod = []
        for pr in self.productions.copy():
            if not pr in new_prod:
                new_prod.append(pr)

        self.productions = new_prod

    def usefulSymbols(self):
        result = set()
        N = { 0: set()}
        i = 0

        while i == 0 or N[i] != N[i-1]:
            i += 1
            alpha = N[i-1] | set([j['name'] for j in self.terminals])
            prods = []
            for nonterminal in self.nonterminals:
                for pr in self.productions:
                    if pr['left'] == nonterminal:
                        for s in pr['right']:
                            if s['name'] in alpha:
                                prods.append(pr)
                                break
                    
            if prods:
                temp = N[i-1].copy()
                for j in prods:
                    temp.add(j['left'])
                N[i] = temp

        result = N[i]
        return result

    def __epsSymbols(self):
        result = set()
        N = { 0: set()}
        i = 0

        while i == 0 or N[i] != N[i-1]:
            i += 1
            prods = []
            for pr in self.productions:
                for s in pr['right']:
                    if s['name'] == 'ε' or s['name'] in N[i-1]:
                        prods.append(pr)
                        break
                    
            if prods:
                temp = N[i-1].copy()
                for j in prods:
                    temp.add(j['left'])
                N[i] = temp

        result = N[i]
        return result

    def removeUselessSymbols(self):
        usefulSymbols = self.usefulSymbols()
        self.nonterminals = set(self.nonterminals) & usefulSymbols
        new_productions = []
        allSymbols = usefulSymbols | set([j['name'] for j in self.terminals])

        for pr in self.productions:
            right_symbols = [i['name'] for i in pr['right']]
            if pr['left'] in allSymbols and \
                set(right_symbols) == set(right_symbols) & allSymbols:
                new_productions.append(pr)

        self.productions = new_productions

        new_terminals = set()
        for pr in self.productions:
            for s in pr['right']:
                if s['isTerminal'] == 'True':
                    new_terminals.add(s['name'])

        for t in self.terminals.copy():
            if not t['name'] in new_terminals:
                self.terminals.remove(t)

    def removeEpsRules(self):
        epsSymbols = self.__epsSymbols()
        new_prods = []

        for pr in self.productions:
            right_elems = [j['name'] for j in pr['right']]
            if set(right_elems) & epsSymbols:
                eps_in_pr = set(right_elems) & epsSymbols
                elems = []
                space_counter = -1
                for idx, value in enumerate(right_elems):
                    if idx == 0 or value in eps_in_pr:
                        elems.append([value])
                        space_counter += 1
                        if idx == 0 and value in eps_in_pr:
                            space_counter += 1
                    elif not set(elems[idx-1]) & eps_in_pr:
                        elems[idx-1].append(value)
                    else:
                        elems.append([value])
                elems.extend(['' for i in range(0, space_counter)])
                all_combinations = list(combinations(elems, len(elems) - space_counter))
                
                for comb in all_combinations.copy():
                    c = list(filter(lambda x: x != '', comb))

                    if not c:
                        all_combinations.remove(comb)
                        continue

                    new_prod = {'left':pr['left'], 'right':[]}
                    for elem in comb:
                        for e in elem:
                            if not e in ['', 'ε']:
                                new_prod['right'].append({
                                    'isTerminal' : f"{not e in self.nonterminals}",
                                    'name' : e
                                })
                    if new_prod['right']:
                        new_prods.append(new_prod)

                if self.startSymbol in epsSymbols and pr['left'] == self.startSymbol:
                    new_prods.append({
                        'left':f"{self.startSymbol}'",
                        'right':[{
                            'isTerminal' : 'False',
                            'name' : self.startSymbol
                        }]
                    })
                    new_prods.append({
                        'left':f"{self.startSymbol}'",
                        'right':[{
                            'isTerminal' : 'True',
                            'name' : 'ε'
                        }]
                    })
                    self.nonterminals.add(f"{self.startSymbol}'")
                    self.startSymbol = f"{self.startSymbol}'"

            else:
                if not 'ε' in [i['name'] for i in pr['right']]:
                    new_prods.append(pr)
        
        self.productions = new_prods
        self.removeUnreachableSymbols()
        self.__sortAll()

    def __sortAll(self):
        sorted_productions = []
        sorted_nonterminals = [self.startSymbol]
        flag = False
        
        while True:
            for n in sorted_nonterminals.copy():
                for p in self.productions:
                    if p['left'] == n and not p in sorted_productions:
                        sorted_productions.append(p)
                        for r in p['right']:
                            if r['isTerminal'] == 'False' and not r['name'] in sorted_nonterminals:
                                sorted_nonterminals.append(r['name'])
            
            if flag:
                break
            if set(sorted_nonterminals) == set(self.nonterminals):
                flag = True

        self.productions = sorted_productions
        self.nonterminals = sorted_nonterminals
        self.__removeCopies()

    def removeUnreachableSymbols(self):
        reachables = set()

        def dfs(nonterminal):
            reachables.add(nonterminal)

            for pr in filter(lambda pr: pr['left'] == nonterminal, self.productions):
                for element in pr['right']:
                    if element['name'] not in reachables:
                        dfs(element['name'])

        dfs(self.startSymbol)
        self.nonterminals = list(filter(lambda nt: nt in reachables, self.nonterminals))
        self.terminals = list(filter(lambda t: t['name'] in reachables, self.terminals))
        self.productions = [pr for pr in self.productions if pr['left'] in reachables]
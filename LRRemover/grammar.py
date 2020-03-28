from left_rec_remove import Grammar

class ModifiedGrammar:
    def __init__(self, grammar):
        self.terminals = grammar.terminals
        self.nonterminals = grammar.nonterminals
        self.productions = grammar.productions
        self.startSymbol = grammar.startSymbolName

    def usefulSymbols(self):
        result = set()
        N = { 0: set()}
        i = 1

        for nonterminal in self.nonterminals:
            prods = []
            alpha = N[i-1] | set([j['name'] for j in self.terminals])

            for pr in self.productions:
                if pr['left'] == nonterminal:
                    for s in pr['right']:
                        if s['name'] in alpha:
                            prods.append(pr)
                            break
                
            if prods:
                temp = N[i-1].copy()
                temp.add(nonterminal)
                N[i] = temp
            else:
                N[i] = N[i-1]
                
            result = N[i]
            i += 1

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

gr = Grammar('LRRemover/test_grammar.json')
gr.remove_recursion()
gr.left_factorization()
mgr = ModifiedGrammar(gr)
mgr.removeUselessSymbols()
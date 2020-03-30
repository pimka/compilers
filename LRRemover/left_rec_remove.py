import json
from collections import namedtuple

class Grammar:
    def __init__(self, path_to_json):
        dict_temp = self.__jsonParser(path_to_json)
        self.terminals = dict_temp['terminals']
        self.nonterminals = dict_temp['nonterminals']
        self.productions = dict_temp['productions']
        self.startSymbolName = dict_temp['startSymbolName']

    def __jsonParser(self, path_to_json):
        file = open(path_to_json)
        json_file = json.load(file)
        file.close()
        return json_file

    def remove_recursion(self):
        for i in range(0, len(self.nonterminals)):
            for j in range(0, i):
                prods = self.__findProduction(self.nonterminals[i], self.nonterminals[j])
                left_prods = self.__findProductionsByLeft(self.nonterminals[j])
                for pr in prods:
                    self.productions.remove(pr)
                    for lpr in left_prods:
                        self.productions.append(self.__createProduction(pr, self.nonterminals[j], lpr))
            
            prods = self.__findProduction(self.nonterminals[i], self.nonterminals[i])
            if prods:
                left_prods = self.__findProductionsByLeft(self.nonterminals[i])
                self.nonterminals.append(f'{self.nonterminals[i]}\'')
                for pr in left_prods:
                    if pr not in prods:
                        pr['right'].append(
                            {
                                'isTerminal' : 'False',
                                'name' : f'{self.nonterminals[i]}\''
                            })
                    else:
                        self.productions.remove(pr)
                        prod = { 'left' : f'{self.nonterminals[i]}\'', 'right' : pr['right'] }
                        for r in pr['right']:
                            if r['name'] == self.nonterminals[i]:
                                prod['right'].remove(r)
                                prod['right'].append(
                                    {
                                        'isTerminal' : 'False',
                                        'name' : f'{self.nonterminals[i]}\''
                                    })

                        self.productions.append(prod)

                self.productions.append({
                    'left' : f'{self.nonterminals[i]}\'',
                    'right' : [
                        {
                            'isTerminal' : 'True',
                            'name' : 'ε'
                        }
                    ]
                })

    def __findProduction(self, left, right):
        result = []
        right = {'isTerminal':'False', 'name':right}
        for prod in self.productions:
            if prod['left'] == left and right == prod['right'][0]:
                result.append(prod)

        return result

    def __findProductionsByLeft(self, left):
        result = []
        for prod in self.productions:
            if prod['left'] == left:
                result.append(prod)

        return result

    def __createProduction(self, prod, replaceNonterminal, replaceProd):
        prod_copy = prod.copy()
        copy_right = []
        for i in prod['right']:
            if i['name'] == replaceNonterminal:
                copy_right.extend(replaceProd['right'])
            else:
                copy_right.append(i)
        prod_copy['right'] = copy_right

        return prod_copy

    def left_factorization(self):
        for nt in self.nonterminals:
            prods = self.__findProductionsByLeft(nt)
            for i in prods.copy():
                if not {'isTerminal':'False','name':nt} in i['right']:
                    prods.remove(i)
            if prods:
                alpha = frozenset(self.__to_tuple(prods[0]['right']))
                for i in prods:
                    alpha = alpha.intersection(frozenset(self.__to_tuple(i['right'])))
                
                if not alpha:
                    return 

                alpha = self.__to_dict(alpha)
                right = alpha + [{
                            'isTerminal' : 'False',
                            'name' : f'{nt}^'
                        }]
                self.productions.append({
                    'left' : nt,
                    'right' : right
                })

                for pr in prods:
                    self.productions.remove(pr)
                    for a in alpha:
                        pr['right'].remove(a)
                    if not pr['right']:
                        pr['right'].append({
                            'isTerminal' : 'True',
                            'name' : 'ε'
                        })
                    self.productions.append({
                        'left':f'{nt}^',
                        'right':pr['right']
                    })

    def __to_tuple(self, data):
        result = []
        symbol = namedtuple('Symbol', ['pos', 'value'])
        for i, j in enumerate(data):
            result.append(symbol(pos=i, value=j['name']))
        
        return result

    def __to_dict(self, data):
        result = []
        data = list(data)
        data.sort(key=lambda i:i.pos)
        for i in data:
            result.append({
                'isTerminal' : f'{not i.value in self.nonterminals}',
                'name' : i.value
            })

        return result
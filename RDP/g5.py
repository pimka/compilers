class ParserException(Exception):
    pass

class Parser:
    ident = 'abc'

    def __init__(self, _input):
        self.input = _input
        self.col = 1
        self.row = 1
        self.i = 0

    def next_char(self, i):
        while True:
            if i >= len(self.input):
                return len(self.input)
            if self.input[i] == ' ':
                self.col += 1
            elif self.input[i] == '\n':
                self.col = 1
                self.row +=1
            else:
                self.col += 1
                return i
            i += 1

    def accept(self, symbol):
        oldCol = self.col
        oldRow = self.row
        i = self.i
        for ch in symbol:
            i = self.next_char(i)
            if i >= len(self.input):
                return False
            if ch != self.input[i]:
                self.col = oldCol
                self.row = oldRow
                return False
            i += 1
        self.i = i
        return True

    def higher_priority_operation(self):
        operations = ['**', 'abs', 'not']
        for op in operations:
            if self.accept(op):
                return True, ('hi_pr_op', op)

        return False, None

    def multiplication_operation(self):
        operations = ['*', '/', 'mod', 'rem']
        for op in operations:
            if self.accept(op):
                return True, ('mult_op', op)

        return False, None

    def unary_additive_operation(self):
        operations = ['+', '-']
        for op in operations:
            if self.accept(op):
                return True, ('un_add_op')

        return False, None

    def binary_additive_operation(self):
        operations = ['+', '-', '&']
        for op in operations:
            if self.accept(op):
                return True, ('bin_add_op')

        return False, None

    def compare_operation(self):
        operations = ['<', '<=', '=', '/>', '>', '>=']
        for op in operations:
            if self.accept(op):
                return True, ('comp_op')

        return False, None

    def logical_operation(self):
        operations = ['and', 'or', 'xor']
        for op in operations:
            if self.accept(op):
                return True, ('log_op')

        return False, None

    def primary(self):
        if self.accept('987'):
            return True, ('primary', '987')
        if self.accept('xyz'):
            return True, ('primary', 'xyz')
        if self.accept('('):
            isSuccess, oper = self.expression()
            if not isSuccess:
                raise ParserException(f'Expression exception in row-{self.row}, col-{self.col}')
            if not self.accept(')'):
                raise ParserException(f'Missing ")" in row-{self.row}, col-{self.col}')
            
            return True, ('primary', oper)

        return False, None

    def multiplier(self):
        isSuccess, oper = self.primary()
        if isSuccess:
            if self.accept('{'):
                if self.accept('**'):
                    isSuccess2, oper2 = self.primary()
                    if not isSuccess2:
                        raise ParserException(f'Primary exception in row-{self.row}, col-{self.col}')
                    if not self.accept('}'):
                        raise ParserException(f'Missing "{"}"}" in row-{self.row}, col-{self.col}')

                    return True, ('mult', '**', oper, oper2)
                
                raise ParserException(f'Missing "**" in row-{self.row}, col-{self.col}')
            
            raise ParserException(f'Missing "{"{"}" in row-{self.row}, col-{self.col}')
        
        if self.accept('abs'):
            isSuccess, oper = self.primary()
            if not isSuccess:
                raise ParserException(f'Primary exception in row-{self.row}, col-{self.col}')
            
            return True, ('mult', ('abs', oper))
        
        if self.accept('not'):
            isSuccess, oper = self.primary()
            if not isSuccess:
                raise ParserException(f'Primary exception in row-{self.row}, col-{self.col}')
            
            return True, ('mult', ('not', oper))

        return False, None

    def term(self):
        isSuccess, oper = self.multiplier()
        if isSuccess:
            if self.accept('{'):
                isSuccessMO, operMO = self.multiplication_operation()
                if isSuccessMO:
                    isSuccessM, operM = self.multiplier()
                    if not isSuccessM:
                        raise ParserException(f'Multiplier exception in row-{self.row}, col-{self.col}')
                    if not self.accept('}'):
                        raise ParserException(f'Missing "{"}"}" in row-{self.row}, col-{self.col}')
                    
                    return True, ('term', operMO, oper, operM)
                
                raise ParserException(f'Missing multiplication operation in row-{self.row}, col-{self.col}')

            raise ParserException(f'Missing "{"{"}" in row-{self.row}, col-{self.col}')

        return False, None

    def simple_expression(self):
        if self.accept('['):
            isSuccessUAO, operUAO = self.unary_additive_operation()
            if isSuccessUAO:
                if self.accept(']'):
                    isSuccessT, operT = self.term()
                    if isSuccessT:
                        if self.accept('{'):
                            isSuccessBAO, operBAO = self.binary_additive_operation()
                            if isSuccessBAO:
                                isSuccessT2, operT2 = self.term()
                                if not isSuccessT2:
                                    raise ParserException(f'Term 2 exception in row-{self.row}, col-{self.col}')
                                if not self.accept('}'):
                                    raise ParserException(f'Missing "{"}"}" in row-{self.row}, col-{self.col}')

                                return True, ('sim_expr', operUAO, operT, operBAO, operT2)

                            raise ParserException(f'BAO exception in row-{self.row}, col-{self.col}')

                        raise ParserException(f'Missing "{"{"}" in row-{self.row}, col-{self.col}')

                    raise ParserException(f'Term exception in row-{self.row}, col-{self.col}')

                raise ParserException(f'Missing "{"]"}" in row-{self.row}, col-{self.col}')

            raise ParserException(f'UAO exception in row-{self.row}, col-{self.col}')

        return False, None

    def compare(self):
        isSuccessSE, operSE = self.simple_expression()
        if isSuccessSE:
            if self.accept('['):
                isSuccessCO, operCO = self.compare_operation()
                if isSuccessCO:
                    isSuccessSE2, operSE2 = self.simple_expression()
                    if not isSuccessSE2:
                        raise ParserException(f'SE 2 exception in row-{self.row}, col-{self.col}')
                    if not self.accept(']'):
                        raise ParserException(f'Missing "{"]"}" in row-{self.row}, col-{self.col}')

                    return True, ('compare', operSE, operCO, operSE2)

                raise ParserException(f'CO exception in row-{self.row}, col-{self.col}')
            
            raise ParserException(f'Missing "{"["}" in row-{self.row}, col-{self.col}')

        return False, None

    def expression(self):
        isSuccessC, operC = self.compare()
        if isSuccessC:
            if self.accept('{'):
                isSuccessLO, operLO = self.logical_operation()
                if isSuccessLO:
                    isSuccessC2, operC2 = self.compare()
                    if not isSuccessC2:
                        raise ParserException(f'Compare 2 exception in row-{self.row}, col-{self.col}')
                    if not self.accept('}'):
                        raise ParserException(f'Missing "{"}"}" in row-{self.row}, col-{self.col}')

                    return True, ('expr', operC, operLO, operC2)

                raise ParserException(f'LO exception in row-{self.row}, col-{self.col}')
            
            raise ParserException(f'Missing "{"{"}" in row-{self.row}, col-{self.col}')
        
        return False, None

    def operator(self):
        if self.accept(self.ident):
            if self.accept('='):
                isSuccessE, operE = self.expression()
                if not isSuccessE:
                    raise ParserException(f'Expression exception in row-{self.row}, col-{self.col}')

                return True, ('oper', operE)

            raise ParserException(f'Missing "=" in row-{self.row}, col-{self.col}')
            
        isSuccessU, operU = self.unit()
        if isSuccessU:
            return True, ('oper', operU)

        return False, None

    def tail(self):
        if self.accept(';'):
            isSuccessO, operO = self.operator()
            if isSuccessO:
                isSuccessT, operT = self.tail()
                if not isSuccessT:
                    raise ParserException(f'Tail exception in row-{self.row}, col-{self.col}')

                return True, ('tail', operO, operT)


            raise ParserException(f'Operator exception in row-{self.row}, col-{self.col}')

        return True, ('tail')

    def operator_list(self):
        isSuccessO, operO = self.operator()
        if isSuccessO:
            isSuccessT, operT = self.tail()
            if not isSuccessT:
                raise ParserException(f'Operator list exception in row-{self.row}, col-{self.col}')

            return True, ('oper_list', operO, operT)

        return False, None

    def unit(self):
        if self.accept('{'):
            isSuccessOL, operOL = self.operator_list()
            if not isSuccessOL:
                raise ParserException(f'Unit exception in row-{self.row}, col-{self.col}')
            if not self.accept('}'):
                raise ParserException(f'Missing "{"}"}" in row-{self.row}, col-{self.col}')

            return True, ('unit', operOL)

        return False, None

    def program(self):
        isSuccessU, operU = self.unit()
        if isSuccessU:
            return True, ('prog', operU)

        return False, None

    def run(self):
        _, program = self.program()

        return self.i == len(self.input), program

if __name__ == "__main__":
    filename = 'RDP/programs/success.txt'
    with open(filename) as f:
        s = f.read()

    parser = Parser(s)
    print(parser.run())
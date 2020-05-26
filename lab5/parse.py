class Parser:
    rel_op = ['<', '<=', '=', '<>', '>', '>=']
    bin_add_op = ['+', '-']
    mult_op = ['*', '/']
    tokens = [str(i) for i in range(10)]

    def __next(self, string):
        current = string[0]

        if current in ('>', '=') and len(string) > 1 and string[1] == '=':
            current += string[1]
            string = string[2:]

        elif current in ('<') and len(string) > 1 and string[1] in ('=', '>'):
            current += string[1]
            string = string[2:]

        else:
            string = string[1:]

        return string, current

    def parse(self, input_string):
        stack = ['$']
        string = ''.join(input_string.split(' ')) + '$'
        postfix_stack = []
        tokens_stack = []

        while stack != ['$', 'E'] or string != '$':
            string, token = self.__next(string)

            if token in self.tokens:
                tokens_stack.append(token)

            last_token = [i for i in stack if i != 'E'][-1]
            priority = self.__priority(last_token, token)

            if priority is None:
                raise Exception(f'Not found for {last_token} -- {token}')

            elif priority == '>':
                string = token + string

                if not stack:
                    raise Exception(
                        f'Stack is empty for token {token} and string {string}')

                for i in range(1, len(stack)):
                    _slice = stack[-i:]
                    reduction_result = self.reduction(_slice)

                    if reduction_result is not None:
                        stack = stack[:-i]
                        stack.append(reduction_result)

                        if len(_slice) == 3 and _slice[0] != '(':
                            while len(tokens_stack) > 0:
                                postfix_stack.append(tokens_stack.pop(0))
                            postfix_stack.append(_slice[1])
                        break
            else:
                stack.append(token)

        return postfix_stack

    def reduction(self, stack):
        if len(stack) == 3:
            if stack == ['(', 'E', ')']:
                return 'E'
            if stack[0] == stack[2] == 'E' and stack[1] in self.rel_op + self.bin_add_op + self.mult_op:
                return 'E'

        elif len(stack) == 1 and stack[0] in self.tokens:
            return 'E'

        return None

    def __priority(self, curr_token, next_token):
        if curr_token in self.bin_add_op:
            if next_token in self.bin_add_op + self.rel_op + [')', '$']:
                return '>'
            else:
                return '<'

        elif curr_token in self.mult_op:
            if next_token in self.mult_op + self.bin_add_op + self.rel_op + [')', '$']:
                return '>'
            else:
                return '<'

        elif curr_token in self.rel_op:
            if next_token in self.rel_op + [')', '$']:
                return '>'
            else:
                return '<'

        elif curr_token in self.tokens:
            if next_token in self.mult_op + self.bin_add_op + self.rel_op + [')', '$']:
                return '>'
            else:
                return None

        elif curr_token == '(':
            if next_token in self.bin_add_op + self.mult_op + self.rel_op + self.tokens + ['(', ')']:
                return '<'
            else:
                return None

        elif curr_token == ')':
            if next_token in self.bin_add_op + self.mult_op + self.rel_op + [')', '$']:
                return '>'
            else:
                return None

        elif curr_token == '$':
            if next_token in self.bin_add_op + self.mult_op + self.rel_op + self.tokens + ['(']:
                return '<'
            else:
                return None

        else:
            return None


if __name__ == "__main__":
    test = '(1*2+9) >= (2*3-6)'
    p = Parser()
    print(p.parse(test))

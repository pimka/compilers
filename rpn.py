class Character:
    def __init__(self, ch, caret=False, dot=False):
        self.ch = ch
        self.caret = caret
        self.dot = dot

    def __eq__(self, other_ch):
        if isinstance(other_ch, Character):
            return self.ch == other_ch.ch and \
                self.caret == other_ch.caret and \
                self.dot == other_ch.dot
        elif isinstance(other_ch, str):
            result = self.ch == other_ch
            if self.dot:
                result = True
            return result if not self.caret else not result
        else:
            raise NotImplemented

    def __repr__(self):
        if self.caret:
            return "Character<^%s>" % self.ch
        else:
            return "Character<%s>" % self.ch

class Operator:
    def __init__(self, op):
        self.op = op
    
    def __eq__(self, other_op):
        return self.op == other_op.op

    def __repr__(self):
        return "Operator<%s>" % self.op

class _Concat:
    def __repr__(self):
        return "Concatenation"
Concat = _Concat()

class _Disj:
    def __repr__(self):
        return "Disjunction"
Disj = _Disj()

def RPN(expression):
    expression = expression
    stack = []
    buffer = []
    in_round = False
    round_count = 0
    atoms_count = 0
    alt_count = 0
    for c in expression:
        if in_round and c != ')':
            if c == '(':
                round_count += 1
            buffer.append(c)
            continue
        elif c in '+*':
            if atoms_count == 0:
                raise Exception()
            if isinstance(stack[-1], Operator):
                raise Exception()
            stack.append(Operator(c))
        elif c == '|':
            if atoms_count == 0:
                raise Exception()
            atoms_count -= 1
            while atoms_count:
                stack.append(Concat)
                atoms_count -= 1
            alt_count += 1
        elif c == '(':
            in_round = True
            round_count += 1
        elif c == ')':
            round_count -= 1
            if round_count != 0:
                buffer.append(')')
                continue
            in_round = False
            expr = RPN(''.join(buffer))
            if expr is None:
                raise Exception()
            buffer = []
            if atoms_count > 1:
                stack.append(Concat)
                atoms_count -= 1
            stack.extend(expr)
            atoms_count += 1
        else:
            if atoms_count > 1:
                stack.append(Concat)
                atoms_count -= 1
            char = Character(c, dot=c == '.')
            stack.append(char)
            atoms_count += 1
    if atoms_count > 1:
        stack.append(Concat)
    while alt_count:
        stack.append(Disj)
        alt_count -= 1
    return stack
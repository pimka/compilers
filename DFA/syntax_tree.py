from rpn import _Concat, Concat, Character, _Disj, RPN, Operator
from collections import defaultdict


class Node:
    def __init__(self, value, position=None, left=None, right=None, nullable=False, firstpos=None, lastpos=None):
        self.left = left
        self.right = right
        self.value = value
        self.position = position
        self.nullable = nullable
        self.firstpos = firstpos
        self.lastpos = lastpos
        self.alphabet = set()

    def __repr__(self):
        return "<%s>(%s) -> [%s, %s]" % (self.value, self.position, self.left, self.right)

    def getFollowpos(self):
        result = defaultdict(frozenset)
        return self._getFollowpos(result)
    
    def _getFollowpos(self, result):
        if isinstance(self.value, _Concat):
            for i in self.left.lastpos:
                result[i] = result[i].union(self.right.firstpos)
        elif isinstance(self.value, Operator) and self.value.op == '*':
            for i in self.lastpos:
                result[i] = result[i].union(self.firstpos)

        if self.left is not None:
            result = self.left._getFollowpos(result)
        if self.right is not None:
            result = self.right._getFollowpos(result)

        return result

    def getAlphabet(self):
        if isinstance(self.value, Character) and self.value.ch != '#':
            self.alphabet.add(self.value.ch)
        if self.left is not None:
            self.alphabet.update(self.left.getAlphabet())
        if self.right is not None:
            self.alphabet.update(self.right.getAlphabet())
        return self.alphabet

    def getNode(self, ch, positions):
        node = set()
        if isinstance(self.value, Character) and self.value.ch == ch and self.position in positions:
            node.add(self)
        if self.left is not None:
            node.update(self.left.getNode(ch, positions))
        if self.right is not None:
            node.update(self.right.getNode(ch, positions))
        return node

    def build(self, followpos, lastpos):
        s0 = frozenset(self.firstpos)
        dstates = {s0 : False}
        s = self._get_next(dstates)
        start = s
        dtran = dict()
        nods = []
        terminals = []
        while True:
            s = frozenset(s)
            dstates[s] = True
            nods.append(s)
            if not s.isdisjoint(lastpos):
                terminals.append(s)
            for a in self.getAlphabet():
                nodes = self.getNode(a, s)
                fp = set()

                if nodes:
                    for n in s:
                        if n in [temp.position for temp in nodes]:
                            fp = fp.union(followpos[n])
                    if not frozenset(fp) in dstates.keys():
                        dstates[frozenset(fp)] = False
                    dtran[s, a] = fp

            s = self._get_next(dstates)
            if s is None:
                break

        return dtran, nods, start, terminals

    def _get_next(self, states):
        for k, v in states.items():
            if not v:
                return k
        return None

class SyntaxTree:
    def __init__(self, stack_expression):
        self.stack_expression = stack_expression
        self.tree = []
        self.dies_positions = set()

    def buildTree(self):
        counter = 1
        for ch in self.stack_expression:
            if isinstance(ch, Character):
                node = Node(ch, counter, nullable=False, firstpos={counter}, lastpos={counter})
                self.tree.append(node)
                if ch.ch == '#':
                    self.dies_positions.add(counter)
                counter += 1
            elif isinstance(ch, _Concat):
                right = self.tree.pop()
                left = self.tree.pop()

                if left.nullable:
                    firstpos = left.firstpos.union(right.firstpos)
                else:
                    firstpos = left.firstpos

                if right.nullable:
                    lastpos = left.lastpos.union(right.lastpos)
                else:
                    lastpos = right.lastpos

                node = Node(ch, left=left, right=right, nullable=left.nullable and right.nullable, \
                    firstpos=firstpos, lastpos=lastpos)
                self.tree.append(node)
            elif isinstance(ch, _Disj):
                right = self.tree.pop()
                left = self.tree.pop()
                node = Node(ch, left=left, right=right, nullable=left.nullable or right.nullable, \
                    firstpos=left.firstpos.union(right.firstpos), lastpos=left.lastpos.union(right.lastpos))
                self.tree.append(node)
            elif ch.op == '+':
                left = self.tree.pop()
                st_node = Node(ch, left=left, nullable=True, firstpos=left.firstpos, lastpos=left.lastpos)
                
                if left.nullable:
                    firstpos = left.firstpos.union(st_node.firstpos)
                else:
                    firstpos = left.firstpos

                node = Node(ch, left=left, right=st_node, nullable=left.nullable and st_node.nullable, \
                    firstpos=firstpos, lastpos=st_node.lastpos)
                self.tree.append(node)
            elif ch.op == '*':
                left = self.tree.pop()
                node = Node(ch, left=left, nullable=True, firstpos=left.firstpos, lastpos=left.lastpos)
                self.tree.append(node)
        return self.tree.pop()
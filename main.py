from dfa import DFA
from rpn import RPN
from syntax_tree import SyntaxTree

tree = SyntaxTree(RPN('((000)|(001)|(010)|(011)|(100)|(101)|(110)|(111))*#'))
root_tree = tree.buildTree()
followpos = root_tree.getFollowpos()
drtan, nodes, start, term = root_tree.build(followpos, tree.dies_positions)
dfa = DFA(drtan, nodes, start, term, root_tree.alphabet)
dfa.minimize()
min_dfa, min_start, min_end = dfa.build_minimized(dfa.get_equal())

test_string = ''
print(dfa.match(start, term, drtan, test_string))
print(dfa.match(min_start, min_end, min_dfa, test_string))

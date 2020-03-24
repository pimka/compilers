from syntax_tree import SyntaxTree, Node
from rpn import RPN

def is_true(x) -> bool:
    print(x)
    return x

class DFA:
    def __init__(self, transition, nodes, start, terminal, alphabet):
        self.transition = transition
        self.alphabet = alphabet
        self.start = start
        self.terminal = self._get_terminal(terminal, nodes)
        self.queue = []
        self.min_transition = None
        self.nodes = nodes
        self.states_count = len(nodes)
        self.marked = [[False for _ in range(0, self.states_count)] for _ in range(0, self.states_count)]

    def minimize(self):
        delta_back = self._build_delta_back()
        possible = self.DFS(self.transition.copy(), dict.fromkeys(self.transition.keys(), False), \
            list(self.transition.keys())[0][0], True)
        for i in range(0, self.states_count):
            for j in range(0, self.states_count):
                if not self.marked[i][j] and self.terminal[self.nodes[i]] != self.terminal[self.nodes[j]]:
                    self.marked[i][j], self.marked[j][i] = True, True
                    self.queue.append((i, j))

        while self.queue:
            u, v = self.queue.pop(0)
            for c in self.alphabet:
                if delta_back.get((self.nodes[u], c)) and delta_back.get((self.nodes[v], c)):
                    for r in delta_back[(self.nodes[u], c)]:
                        for s in delta_back[(self.nodes[v], c)]:
                            r_cof = self.nodes.index(r)
                            s_cof = self.nodes.index(s)
                            if not self.marked[r_cof][s_cof]:
                                self.marked[r_cof][s_cof], self.marked[s_cof][r_cof] = True, True
                                self.queue.append((r_cof, s_cof))

        return self.marked

    def get_equal(self):
        component = [-1 for i in range(0, self.states_count)]
        components_count = -1
        for i in range(0, self.states_count):
            if component[i] == -1:
                components_count += 1
                component[i] = components_count
                for j in range(i+1, self.states_count):
                    if not self.marked[i][j]:
                        component[j] = components_count
        return component

    def _get_terminal(self, terminals, nodes):
        result = dict().fromkeys(nodes, False)
        for k in result:
            if k in terminals:
                result[k] = True
        return result
        
    def _build_delta_back(self):
        delta_back = dict()
        for node in self.nodes:
            for rbr in self.transition:
                if not bool(node.symmetric_difference(self.transition[rbr])):
                    if delta_back.get((node, rbr[1])):
                        delta_back[node, rbr[1]].append(rbr[0])
                    else:
                        delta_back[node, rbr[1]] = [rbr[0]]
        return delta_back

    def DFS(self, transition, watched, start, is_first=False):
        result = set()
        for key in transition:
            if not bool(start.symmetric_difference(key[0])) and bool(start.symmetric_difference(transition[key])) \
                and (not watched[key] or is_first):
                result.add(key[0])
                watched[key] = True
                result = result.union(self.DFS(transition, watched, transition[key]))
        return result

    def build_minimized(self, component):
        if component == [i for i in range(0, self.states_count)]:
            buf = [k for k, v in self.terminal.items() if v]
            return self.transition, self.start, buf
        
        new_transition = dict()
        start, end = set(), set()
        merge_nodes = { key : [] for key in set(component) }
        for i in range(0, self.states_count):
            merge_nodes[component[i]].append(self.nodes[i])
        for i in merge_nodes:
            for tr in self.transition:
                if tr[0] in merge_nodes[i]:
                    if self.transition[tr] == tr[0]:
                        new_transition[frozenset({i}), tr[1]] = {i}
                    else:
                        for it in merge_nodes.items():
                            if self.transition[tr] in it[1]:
                                new_transition[frozenset({i}), tr[1]] = {it[0]}

                    if tr[0] == self.start:
                        start.add(i)
                    if self.terminal[tr[0]]:
                        end.add(i)
        
        return new_transition, frozenset(start), [frozenset({i}) for i in end]

    def match(self, start, end, transition, expression):
        key = start

        if expression == '' and key in end:
            return True

        for index, el in enumerate(expression):
            if transition.get((key, el)):
                key = frozenset(transition[(key, el)])
                if index == len(expression)-1:
                    return key in end
            else:
                return False

        return False
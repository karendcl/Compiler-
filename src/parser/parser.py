from typing import List
from src.cmp.pycompiler import Item, EOF
from src.cmp.automata import State, multiline_formatter
from src.cmp.utils import Token, ContainerSet
from src.parser.utils import compute_firsts, expand, compress


class ShiftReduceParser:
    '''
    Base Class for Shift-Reduce Parsers

    :param G: Grammar
    :param verbose: boolean, if True prints the stack and the input at each step
    '''
    SHIFT = "SHIFT"
    REDUCE = "REDUCE"
    OK = "OK"

    def __init__(self, G, verbose=True):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()
        self.pseudo_actions ={}
        self.get_actions_str()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def get_actions_str(self):
        for i in self.action:
            state = i[0]
            lookahead = str(i[1])
            self.pseudo_actions[(state,lookahead)] = self.action[i]



    def __call__(self, w: List[Token], get_shift_reduce=True):
        stack = [0]
        cursor = 0
        output = []
        operations = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])

            if (state, lookahead) not in self.action:
                print("Error. Aborting...")
                return None

            if self.action[state, lookahead] == self.OK:
                action = self.OK
            else:
                action, tag = self.action[state, lookahead]
            if action == self.SHIFT:
                operations.append(self.SHIFT)
                stack += [lookahead, tag]
                cursor += 1
            elif action == self.REDUCE:
                operations.append(self.REDUCE)
                output.append(tag)
                head, body = tag
                for symbol in reversed(body):
                    stack.pop()
                    assert stack.pop() == symbol
                    state = stack[-1]
                goto = self.goto[state, head]
                stack += [head, goto]
            elif action == self.OK:
                stack.pop()
                assert stack.pop() == self.G.startSymbol
                assert len(stack) == 1
                return output if not get_shift_reduce else (output, operations)
            else:
                raise Exception('Invalid action!!!')


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        automaton = build_LR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (ShiftReduceParser.OK, None))
                    else:
                        for lookahead in item.lookaheads:
                            self._register(self.action, (idx, lookahead), (ShiftReduceParser.REDUCE, prod))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self._register(self.action, (idx, next_symbol),
                                       (ShiftReduceParser.SHIFT, node[next_symbol.Name][0].idx))
                    else:
                        self._register(self.goto, (idx, next_symbol), node[next_symbol.Name][0].idx)

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value


def build_LR1_automaton(G):
    assert len(G.startSymbol.productions) == 1, "Grammar must be augmented"

    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])

    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in G.terminals + G.nonTerminals:
            items = current_state.state
            kernel = goto_lr1(items, symbol, just_kernel=True)
            if not kernel:
                continue
            try:
                next_state = visited[kernel]
            except KeyError:
                closure = goto_lr1(items, symbol, firsts)
                next_state = visited[kernel] = State(frozenset(closure), True)
                pending.append(kernel)

            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(multiline_formatter)
    return automaton


def closure_lr1(items, firsts):
    closure = ContainerSet(*items)
    changed = True
    while changed:
        changed = False
        new_items = ContainerSet()
        for item in closure:
            new_items.extend(expand(item, firsts))
        changed = closure.update(new_items)

    return compress(closure)


def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    assert (
        just_kernel or firsts is not None
    ), "`firsts` must be provided if `just_kernel=False`"
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)


def evaluate_reverse_parse(right_parse, operations, tokens):
    if not right_parse or not operations or not tokens:
        return

    right_parse = iter(right_parse)
    tokens = iter(tokens)
    stack = []
    for operation in operations:
        if operation == ShiftReduceParser.SHIFT:
            token = next(tokens)
            stack.append(token)
        elif operation == ShiftReduceParser.REDUCE:
            production = next(right_parse)
            _, body = production
            attributes = production.attributes
            assert all(
                rule is None for rule in attributes[1:]
            ), "There must be only synteticed attributes."
            rule = attributes[0]

            if len(body):
                synteticed = [None] + stack[-len(body) :]
                value = rule(None, synteticed)
                stack[-len(body) :] = [value]
            else:
                stack.append(rule(None, None))
        else:
            raise Exception("Invalid action!!!")

    assert len(stack) == 1
    assert isinstance(next(tokens).token_type, EOF)
    return stack[0]
from src.cmp.utils import ContainerSet

##CP6
class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }

        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)

        self.vocabulary.discard('')

    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return []

    def epsilon_closure(self, states):
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for next_state in self.epsilon_transitions(state):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def move(self, states, symbol):
        moves = set()
        for state in states:
            try:
                moves.update(self.transitions[state][symbol])
            except KeyError:
                pass
        return self.epsilon_closure(moves)

    def recognize(self, string):
        current_states = self.epsilon_closure({self.start})
        for symbol in string:
            current_states = self.move(current_states, symbol)
        return bool(self.finals.intersection(current_states))


class DFA(NFA):

    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)

        transitions = { key: [value] for key, value in transitions.items() }
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start

    def _move(self, symbol):
        ActualChar = self.current
        if symbol not in self.transitions[ActualChar]:
            raise Exception("Transition Error")

        self.current = self.transitions[ActualChar][symbol][0]

    def _reset(self):
        self.current = self.start

    def recognize(self, string):
        self._reset()
        try:
            for Char in string:
                self._move(Char)
        except Exception:
            return False

        return self.current in self.finals
    
    
## nfa to dfa Methods:

def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            moves.update(automaton.transitions[state][symbol])
        except KeyError:
            pass

    return moves


def epsilon_closure(automaton, states):
    pending = [s for s in states]  # equivalente a list(states) pero me gusta así :p
    closure = {s for s in states}  # equivalente a  set(states) pero me gusta así :p

    while pending:
        state = pending.pop()

        for Ste in automaton.epsilon_transitions(state):
            if Ste not in closure:
                closure.add(Ste)
                pending.append(Ste)

    return ContainerSet(*closure)


def nfa_to_dfa(automaton):
    transitions = {}

    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [ start ]

    pending = [ start ]
    while pending:
        state = pending.pop()

        for symbol in automaton.vocabulary:
            NewState = epsilon_closure(automaton, move(automaton, state, symbol))

            if len(NewState) == 0:
                continue

            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:

                if NewState in states:
                    NewState.id = states.index(NewState)

                else:
                    NewState.id = len(states)
                    NewState.is_final = any(Ste in automaton.finals for Ste in NewState)

                    pending.append(NewState)
                    states.append(NewState)

                if len(NewState) > 0:
                    transitions[state.id, symbol] = NewState.id

    finals = [state.id for state in states if state.is_final]
    dfa = DFA(len(states), finals, transitions)
    return dfa
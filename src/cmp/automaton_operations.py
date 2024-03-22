from src.cmp.automaton import NFA, DFA
from src.cmp.utils import DisjointSet

##CP7
def automata_union(a1, a2):
    transitions = {}

    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        # Relocate a1 transitions ...
        
        if origin == a1.start:
            AtmStart = [0, origin+d1]
        else:
            AtmStart = [origin+d1]

        for Start in AtmStart:
            AtmTransition = [D+d1 for D in destinations]

            transitions[(Start, symbol)] = AtmTransition

    for (origin, symbol), destinations in a2.map.items():
        # Relocate a2 transitions ...
        
        if origin == a2.start:
            AtmStart = [0, origin+d2]
        else:
            AtmStart = [origin+d2]

        for Start in AtmStart:
            AtmTransition = [D+d2 for D in destinations]

            transitions[(Start, symbol)] = AtmTransition

    # Add transitions from start state ...

    transitions[(start, '')] = [a1.start+d1, a2.start+d2]

    # Add transitions to final state ...

    for State in a1.finals:
        transitions[(State+d1, '')] = [final]
        
    for State in a2.finals:
        transitions[(State+d2, '')] = [final]

    states = a1.states + a2.states + 2
    finals = { final }

    return NFA(states, finals, transitions, start)


def automata_concatenation(a1, a2):
    transitions = {}
    start = 0
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        # Relocate a1 transitions

        for _ in destinations:
            transitions[(origin+d1, symbol)] = {D+d1 for D in destinations}

    
    for (origin, symbol), destinations in a2.map.items():
        # Relocate a2 transitions
        
        for _ in destinations:
            transitions[(origin+d2, symbol)] = {D+d2 for D in destinations}

    # Add transitions to final state

    for State in a1.finals:
        transitions[(State+d1, '')] = {d2}

    for State in a2.finals:
        transitions[(State+d2, '')] = {final}

    states = a1.states + a2.states + 1
    finals = { final }

    return NFA(states, finals, transitions, start)


def automata_closure(a1):
    transitions = {}

    start = 0
    d1 = 1
    final = a1.states + d1

    for (origin, symbol), destinations in a1.map.items():
        ## Relocate automaton transitions ...

        Start = origin+d1
        AtmTransition = [D+d1 for D in destinations]
        transitions[(Start, symbol)] = AtmTransition

    ## Add transitions from start state ...

    transitions[(start, '')] = [a1.start+d1, final]

    ## Add transitions to final state and to start state ...

    for State in a1.finals:
        transitions[(State+d1, '')] = [start, final]

    states = a1.states + 2
    finals = { final }

    return NFA(states, finals, transitions, start)

def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:

        ATMTransitions = automaton.transitions[member.value]

        Tags = []
        for symbol in vocabulary:
            if symbol in ATMTransitions:
                Tags.append(ATMTransitions[symbol][0])
            else:
                Tags.append(None)

        splitKey = tuple((partition[Tag].representative if Tag in partition.nodes else None) for Tag in Tags)

        try:
            split[splitKey].append(member.value)
        except KeyError:
            split[splitKey] = [member.value]

    return [group for group in split.values()]


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))

    ## partition = { NON-FINALS | FINALS }

    partition.merge(Ste for Ste in automaton.finals)
    partition.merge(Ste for Ste in range(automaton.states) if Ste not in automaton.finals)

    while True:
        new_partition = DisjointSet(*range(automaton.states))

        ## Split each group if needed (use distinguish_states(group, automaton, partition))

        for Group in partition.groups:
            for i in distinguish_states(Group, automaton, partition):
                new_partition.merge(i)

        if len(new_partition) == len(partition):
            break

        partition = new_partition

    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)

    states = [s for s in partition.representatives]

    transitions = {}
    for i, state in enumerate(states):
        ## origin = ???
        origin = state.value

        for symbol, destinations in automaton.transitions[origin].items():

            Rep = partition[destinations[0]].representative
            RepIndex = states.index(Rep)

            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                transitions[i, symbol] = RepIndex

    ## finals = ???
    ## start  = ???
    finals = []
    for i, Ste in enumerate(states):
        if Ste.value in automaton.finals:
            finals.append(i)
            
    start = states.index(partition[automaton.start].representative)

    return DFA(len(states), finals, transitions, start)
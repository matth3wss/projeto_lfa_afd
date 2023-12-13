def orderedStates(states):
    for key, value in sorted(states.items()):
        print(f"{key} : {value}")

def determinize(states):
    new_states = {}

    for _ in range(len(states)):
        for key, value in sorted(states.items()):
            for symbol, transitions in value.items():
                if len(transitions) > 1:
                    new_state = ''.join(transitions)
                    new_states[new_state] = {}

                    for old_state in transitions:
                        if states[old_state]:
                            for k, v in states[old_state].items():
                                for transition in v:
                                    new_states[new_state].setdefault(k, []).append(transition)

                    del states[old_state]

                    value[symbol] = [new_state]

    states.update(new_states)

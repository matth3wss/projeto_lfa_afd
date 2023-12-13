import finiteAutomata as lfa
import sys
import csv

def check(state):
    if state == 82:
        state += 2
    else:
        state += 1
    return state

def read_csv(file_path):
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            lines = [line for line in reader if line]
            print(lines)
        return lines
    except FileNotFoundError:
        print(f'Arquivo {file_path} não encontrado.')
        exit(1)

def create_states(lines):
    states = {}
    initialState = 0
    state = 64
    states['S'] = {}

    for line in lines:
        if line[0] != "<":
            for char in line:
                if not initialState:
                    state = check(state)
                    initialState = 1
                    states['S'].setdefault(char, []).append(chr(state))
                    states[chr(state)] = {}
                else:
                    state = check(state)
                    if state == 84:
                        states[chr(state - 2)].setdefault(char, []).append(chr(state))
                    else:
                        states[chr(state - 1)].setdefault(char, []).append(chr(state))
                    states[chr(state)] = {}
            initialState = 0
        else:
            rule = line.replace(' ::= ', ' | ').split(' | ')
            input_state = 'S' if rule[0][1] == 'S' else chr(state)
            createState = 0

            for m in range(1, len(rule)):
                if rule[m][0] != 'ε':
                    if rule[0][1] != rule[m][2]:
                        state = check(state)
                        states[chr(state)] = {}
                        createState = 1
                    states[input_state].setdefault(rule[m][0], []).append(chr(state))
                else:
                    states[input_state].setdefault(None, []).append('ε')

            if createState == 1:
                state = check(state)
                states[chr(state)] = {}

    return states

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print('Uso: python %s <caminho completo do arquivo CSV>' % sys.argv[0])
#         exit(1)

# csv_file_path = sys.argv[1]


lines = read_csv("./entrada.csv")
automaton_states = create_states(lines)

print("Autômato Finito Não-Determinístico:\n")
lfa.orderedStates(automaton_states)
lfa.determinize(automaton_states)
print("Autômato determinizado")
lfa.orderedStates(automaton_states)
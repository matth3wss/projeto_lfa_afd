import csv
import pandas as pd
from collections import OrderedDict as od
import string
from classes.RegexPatterns import RegexPatterns
from classes.Alphabet import Alphabet

patterns = RegexPatterns()
alphabet = Alphabet()


def extract_terminals(csv_df):
    """
    Extrai as letras terminais das palavras reservadas obtidas ao analisar um DataFrame contendo strings.

    Parâmetros:
    - csv_df (pandas.DataFrame): O DataFrame contendo strings a serem analisadas.

    Retorna:
    lista: Uma lista de letras terminais individuais obtidas das palavras reservadas.
    """
    terminal_letters = [c for word in (row["word"] for row in reserved_words_and_counts(
        csv_df))for char in word for c in char]
    return terminal_letters


def unique_terminal_letters(csv_df):
    """
    Extrai letras terminais únicas de um DataFrame contendo strings.

    Parâmetros:
    - csv_df (pandas.DataFrame): O DataFrame contendo strings a serem analisadas.

    Retorna:
    lista: Uma lista de letras terminais únicas encontradas nas strings.

    Nota:
    - A função ignora letras maiúsculas, 'ε' (épsilon) e caracteres não alfabéticos.
    - Utiliza o 'collections.OrderedDict' para preservar a ordem das letras terminais únicas.
    """
    terminal_letters = list(od.fromkeys(
        (c for row in csv_df.values for char in row for c in char if c.islower() and c != 'ε')))
    return terminal_letters


def reserved_words_and_counts(csv_df):
    """
    Analisa um DataFrame contendo strings e extrai palavras reservadas, juntamente com suas contagens de caracteres.

    Parâmetros:
    - csv_df (pandas.DataFrame): O DataFrame contendo strings a serem analisadas.

    Retorna:
    lista: Uma lista de dicionários, cada um contendo informações sobre uma palavra reservada, incluindo a própria palavra
        e a contagem de caracteres. O formato do dicionário é o seguinte:
        [
            {"word": str, "size": int},
            {"word": str, "size": int},
            ...
        ]

    Nota:
    - Palavras reservadas são identificadas como strings em minúsculas, excluindo o caractere '<'.
    - A função calcula o tamanho (contagem de caracteres) de cada palavra reservada.
    - A lista retornada contém dicionários com informações sobre cada palavra reservada e seu tamanho.
    """
    reserved_words = [
        row for row in csv_df.values for char in row if not patterns.variable(char)]
    size = [len(c) for word in reserved_words for c in word]

    json_data = []
    for word, size in zip(reserved_words, size):
        json = {
            "word": word,
            "size": size
        }
        json_data.append(json)

    return json_data


def create_afnd_skeleton(csv_df):
    """
    Cria o esqueleto de um AFND (Autômato Finito Não Determinístico) representado como um DataFrame.

    Parâmetros:
    - csv_df (pandas.DataFrame): O DataFrame contendo strings a serem analisadas.

    Retorna:
    pandas.DataFrame: O esqueleto do AFND representado como um DataFrame com cabeçalhos de coluna apropriados.

    Nota:
    - O DataFrame inclui colunas para o alfabeto ('sigma') e letras terminais.
    - As linhas representam estados no AFND.
    - A primeira linha é o estado inicial ('S'), e as linhas subsequentes representam estados rotulados com letras maiúsculas.
    - Células vazias indicam transições que não estão definidas.
    """
    terminal_letters = unique_terminal_letters(csv_df)
    afnd_skeleton_df = pd.DataFrame(
        columns=['sigma'] + [str(c) for c in terminal_letters])
    afnd_skeleton_df.at[0, 'sigma'] = 'S'

    alphabet = list(string.ascii_uppercase)
    size = len(extract_terminals(csv_df))

    symbols = [symbol for letters in alphabet[:size] for symbol in letters]
    for i, symbol in enumerate(symbols):
        afnd_skeleton_df.at[i+1, "sigma"] = symbol

    afnd_skeleton_df = afnd_skeleton_df.fillna('')

    return afnd_skeleton_df


def extract_variables_df(csv_df):
    """
    Extrai informações sobre variáveis de um DataFrame contendo strings.

    Parâmetros:
    - csv_df (pandas.DataFrame): O DataFrame contendo strings a serem analisadas.

    Retorna:
    lista: Uma lista de dicionários, cada um contendo informações sobre uma variável, incluindo o símbolo,
        terminais associados e variáveis associadas. O formato do dicionário é o seguinte:
        [
            {"symbol": str, "terminals": list, "variables": list},
            {"symbol": str, "terminals": list, "variables": list},
            ...
        ]

    Nota:
    - A função utiliza expressões regulares para encontrar padrões de símbolos e variáveis nas strings do DataFrame.
    - O resultado é uma lista de dicionários contendo informações sobre cada variável encontrada.
    """

    lines = [str(row)
             for row in csv_df.values for char in row if patterns.symbol(char)]
    rg = []

    for line in lines:
        symbol = [match[1]
                  for match in patterns.symbol(line) if patterns.variable(line)]
        terminals = [match[0] for match in patterns.variable(line)]
        variables = [match[1] for match in patterns.variable(line)]

        json = {
            "symbol": symbol,
            "terminals": terminals,
            "variables": variables
        }
        rg.append(json)
    return rg


def extract_variables_list(words):
    """
    Extrai informações sobre variáveis de uma lista de palavras.

    Parâmetros:
    - words (list): A lista de palavras a serem analisadas.

    Retorna:
    lista: Uma lista de dicionários, cada um contendo informações sobre uma variável, incluindo o símbolo,
        terminais associados e variáveis associadas. O formato do dicionário é o seguinte:
        [
            {"symbol": str, "terminals": list, "variables": list},
            {"symbol": str, "terminals": list, "variables": list},
            ...
        ]

    Nota:
    - A função utiliza expressões regulares para encontrar padrões de símbolos e variáveis na lista de palavras.
    - Os símbolos são identificados com base nos valores adjacentes à ocorrência do "::=" na lista.
    - Os resultados são organizados em uma lista de dicionários, cada um representando uma variável.
    """
    symbols = [letter for word in words for string in word if not patterns.variable(
        string) and patterns.symbol_alt(string) for letter in string if letter.isalpha()]
    rg = []

    for i, symbol in enumerate(symbols):
        terminals = []
        variables = []
        for j, word in enumerate(words[i]):
            if not patterns.variable(word):
                continue
            terminals.append([match[0] for match in patterns.variable(
                word) if patterns.variable(word) is not None])
            variables.append([match[1] for match in patterns.variable(
                word) if patterns.variable(word) is not None])
        json = {
            "symbol": symbol,
            "terminals": terminals,
            "variables": variables
        }
        rg.append(json)
    return rg


def replace_variables(afnd_df, csv_df, last_state):
    alphabet = list(string.ascii_uppercase)

    old_variables = list(od.fromkeys(variable for line in extract_variables_df(
        csv_df) for variable in line["variables"]))
    new_states_count = len(old_variables)
    index_last_state = alphabet.index(last_state) + 1
    total = new_states_count + index_last_state
    new_symbols = [symbol for letters in alphabet[index_last_state:total]
                   for symbol in letters]

    # Update the "sigma" column in afnd_df starting from the end
    for i, symbol in enumerate(new_symbols, start=index_last_state):
        afnd_df.at[i+1, "sigma"] = symbol

    sentences = [str(word) for row in csv_df.values for char in row if patterns.symbol(
        char) for sentence in row for word in sentence.split()]
    new_sentences = sentences.copy()

    new_variables = []

    for i in range(new_states_count):
        for j, word in enumerate(new_sentences):
            match = patterns.variable(word)
            if not match:
                continue
            for m in match:
                if m[1] == old_variables[i]:
                    new_sentences[j] = f"{m[0]}<{new_symbols[i]}>"
                    json_data = {
                        "old_variable": old_variables[i],
                        "new_variable": new_symbols[i]
                    }
                    new_variables.append(json_data)

    new_variables = [dict(t) for t in {tuple(d.items())
                                       # remove duplicates
                                       for d in new_variables}]
    # sort by new variable
    new_variables = sorted(new_variables, key=lambda k: k['new_variable'])

    symbols = [word for word in new_sentences if not patterns.variable(
        word) and patterns.symbol_alt(word)]

    # recria a nested list, não sei como funciona "copilot fez"
    def recreate_nested_structure(new_sentences, symbols):
        nested_list = []

        for i, symbol in enumerate(symbols):
            words = []
            for j, word in enumerate(new_sentences):
                if i == len(symbols) - 1:
                    if j > new_sentences.index(symbol):
                        words.append(word)
                else:
                    if j > new_sentences.index(symbol) and j < new_sentences.index(symbols[i + 1]):
                        words.append(word)
            words.insert(0, symbol)
            nested_list.append(words)

        return nested_list

    new_words = recreate_nested_structure(new_sentences, symbols)

    for data in new_variables:
        for i, words in enumerate(new_words):
            new_words[i] = [word.replace(f'<{data["old_variable"]}>', f'<{
                                         data["new_variable"]}>') for word in words]

    afnd_df = afnd_df.fillna('')

    return afnd_df, new_words


def insert_value_df(df, search_column, search_row, target_column, value):
    """ Esta função insere um valor em uma célula de um DataFrame, ou concatena o valor com o valor existente na célula.

    Args:
        df (pandas.DataFrame): O DataFrame a ser modificado
        search_column (str): O nome da coluna a ser pesquisada
        search_row (str): O valor da linha a ser pesquisada
        target_column (str): O nome da coluna onde o valor será inserido ou concatenado
        value (str): O valor a ser inserido ou concatenado  

    Returns:
        df: O DataFrame modificado

    """
    if value == '' or value == None:
        df.fillna('', inplace=True)
        return df
    if df.loc[df[search_column] == search_row, target_column].any() == False:
        df.loc[df[search_column] == search_row, target_column] = value
        return df
    df.loc[df[search_column] == search_row, target_column] += f"{','}{value}"
    return df


def populate_variables(afnd_df, words):
    """
    Preenche o AFND (Autômato Finito Não Determinístico) com informações sobre variáveis.

    Parâmetros:
    - afnd_df (pandas.DataFrame): O DataFrame representando o AFND.
    - words (list): A lista de palavras contendo informações sobre variáveis.

    Retorna:
    pandas.DataFrame: O DataFrame do AFND atualizado com informações sobre variáveis.

    Nota:
    - A função extrai informações sobre variáveis a partir da lista de palavras e popula as células correspondentes no AFND.
    - Os dados são preenchidos nas células do AFND de acordo com as informações sobre variáveis encontradas.
    """
    new_variables = extract_variables_list(words)

    for new_variable in new_variables:
        for i, terminals, variables in zip(range(len(new_variable["terminals"])), new_variable["terminals"], new_variable["variables"]):
            for terminal, variable in zip(terminals, variables):
                afnd_df = insert_value_df(
                    afnd_df, 'sigma', new_variable["symbol"], terminal, variable)
    return afnd_df


def create_afnd(csv_df):
    """
    Cria um AFND (Autômato Finito Não Determinístico) representado como um DataFrame.

    Parâmetros:
    - csv_df (pandas.DataFrame): O DataFrame contendo strings a serem analisadas.

    Retorna:
    pandas.DataFrame: O DataFrame representando o AFND gerado.

    Nota:
    - A função cria o esqueleto do AFND utilizando a função 'create_afnd_skeleton'.
    - Em seguida, preenche o AFND com transições com base nas palavras reservadas e variáveis do DataFrame de entrada.
    """

    afnd_df = create_afnd_skeleton(csv_df)
    reserved_counts = reserved_words_and_counts(csv_df)
    final_states = []
    flag = False

    for row in reserved_counts:

        initial_state = 'S'

        word = [c for char in row["word"] for c in char]

        for i, char in enumerate(word):
            if not final_states:  # Se não for um estado final
                if not flag:  # Se estiver vazio, não tem estado final até o fim da primeira palavra
                    afnd_df = insert_value_df(
                        afnd_df, 'sigma', initial_state, char, alphabet.index_to_letter(i))
                    last_state = alphabet.index_to_letter(i)
                    flag = True
                    continue

                if flag and last_state == alphabet.index_to_letter(0):
                    afnd_df = insert_value_df(
                        afnd_df, 'sigma', last_state, char, alphabet.index_to_letter(1))
                    last_state = alphabet.index_to_letter(1)

                elif last_state != alphabet.index_to_letter(0):
                    afnd_df = insert_value_df(
                        afnd_df, 'sigma', last_state, char, alphabet.get_next_letter(last_state))
                    last_state = alphabet.get_next_letter(last_state)
            else:
                if last_state in (final_states):
                    if not afnd_df.loc[afnd_df['sigma'] == last_state, char].isna().all():
                        afnd_df = insert_value_df(
                            afnd_df, 'sigma', initial_state, char, alphabet.get_next_letter(last_state))
                        last_state = alphabet.get_next_letter(last_state)
                    continue
                afnd_df = insert_value_df(
                    afnd_df, 'sigma', last_state, char, alphabet.get_next_letter(last_state))
                last_state = alphabet.get_next_letter(last_state)

        if final_states is not None:
            final_states.append(last_state)
    afnd_df, words = replace_variables(afnd_df, csv_df, last_state)

    afnd_df = populate_variables(afnd_df, words)
    return afnd_df, final_states


def remove_unreachable_states(afnd_df):
    """
    Remove estados inalcançáveis de um AFND (Autômato Finito Não Determinístico).

    Parâmetros:
    - afnd_df (pandas.DataFrame): O DataFrame representando o AFND.

    Retorna:
    pandas.DataFrame: O DataFrame do AFND com estados inalcançáveis removidos.

    Nota:
    - A função remove estados inalcançáveis do AFND, ou seja, estados que não são alcançados a partir do estado inicial.
    - A função itera sobre as linhas do DataFrame e remove estados inalcançáveis.
    """
    visited_states = set()

    def recursive_search(state):
        for terminal in afnd_df.columns[1:]:
            if afnd_df.loc[afnd_df['sigma'] == state, terminal].any():
                states = afnd_df.loc[afnd_df['sigma'] ==
                                     state, terminal].str.split(",").values[0]
                for s in states:
                    if s != '' and s not in visited_states:
                        visited_states.add(s)
                        recursive_search(s)
        return sorted(visited_states)  # Sort the visited states

    # drop unreachable states
    reachable_states = recursive_search('S')
    unreachable_states = [state for state in afnd_df['sigma']
                          if state not in reachable_states and state != 'S']
    afnd_df = afnd_df[~afnd_df['sigma'].isin(unreachable_states)]

    return afnd_df


def remove_dead_states(afnd_df, final_states):
    """
    Remove estados mortos de um AFND (Autômato Finito Não Determinístico).

    Parâmetros:
    - afnd_df (pandas.DataFrame): O DataFrame representando o AFND.
    - final_states (list): Lista de estados finais.

    Retorna:
    pandas.DataFrame: O DataFrame do AFND com estados mortos removidos.

    # Nota:
    - A função remove estados mortos do AFND, ou seja, estados que não podem alcançar um estado final.
    - A função itera sobre as linhas do DataFrame e remove estados mortos.
    """
    final_states_set = set(final_states)

    def can_reach_final_state(state):
        visited_states = set()  # Estados visitados
        stack = [state]  # Pilha de estados a serem visitados

        while stack:
            current_state = stack.pop()  # Remove o último estado da pilha para processamento
            if current_state in visited_states:
                continue
            visited_states.add(current_state)
            if current_state in final_states_set:
                return True

            for terminal in afnd_df.columns[1:]:
                # Obtém os próximos estados possíveis a partir do estado atual e da entrada do terminal atual
                next_states = afnd_df.loc[afnd_df['sigma'] ==
                                          current_state, terminal].str.split(",").values

                if next_states.size > 0:
                    for next_state in next_states[0]:
                        if next_state and next_state not in visited_states:
                            stack.append(next_state)

        return False

    # Encontra todos os estados mortos
    dead_states = set()
    for state in afnd_df['sigma']:
        if not can_reach_final_state(state):
            dead_states.add(state)

    for state in dead_states:     # Remove todas as transições dos estados mortos
        for column in afnd_df.columns[1:]:
            afnd_df[column] = afnd_df[column].apply(lambda x: ','.join(
                [elem for elem in str(x).split(',') if elem.strip() != state]))

    # Remove os estados mortos do AFND
    afnd_df = afnd_df[~afnd_df['sigma'].isin(dead_states)]

    return afnd_df


def determinize_afnd(csv_df, afnd_df):
    """
    Preenche uma linha do AFND (Autômato Finito Determinístico) com o símbolo de indeterminismo. Juntamente com os estados de cada transição.

    Parâmetros:
    - csv_df (pandas.DataFrame): O DataFrame contendo strings a serem analisadas.
    - afnd_df (pandas.DataFrame): O DataFrame representando o AFND gerado.
    - indeterminism_symbol (str): O símbolo de indeterminismo a ser utilizado.

    Retorna:
    pandas.DataFrame: O DataFrame do AFD atualizado com o símbolo de indeterminismo.
    """
    indeterminisms = [(afnd_df.loc[afnd_df[terminal].str.len() > 1, terminal]).tolist() for terminal in afnd_df.columns[1:]
                      # Lista de listas contendo os indeterminismos iniciais do AFND
                      if not afnd_df.loc[afnd_df[terminal].str.len() > 1, terminal].empty]

    all_indeterminisms = indeterminisms.copy()

    columns = unique_terminal_letters(csv_df)

    while indeterminisms:
        for indeterminism in enumerate(indeterminisms):
            # Converte a lista de apenas um elemento para uma string [A,B] -> "A,B"
            [indeterminism_symbol] = indeterminisms[0]
            last_index = afnd_df['sigma'].index[-1]
            afnd_df.at[last_index + 1, "sigma"] = indeterminism_symbol

            # Percorre os estados do indeterminismo
            for state in afnd_df['sigma'].iloc[-1].split(','):
                for column in columns:  # Percorre as colunas do AFND
                    afnd_df = insert_value_df(afnd_df, 'sigma', indeterminism_symbol,
                                              column, afnd_df.loc[afnd_df['sigma'] == state, column].iloc[0])
            indeterminisms.pop(0)

            # Seleciona a última linha do AFND
            last_row_df = afnd_df.iloc[-1].to_frame().T
            new_indeterminisms = [(last_row_df.loc[last_row_df[terminal].str.len() > 1, terminal]).tolist() for terminal in last_row_df.columns[1:]
                                  # Seleciona os indeterminismos da última linha do AFND
                                  if not last_row_df.loc[last_row_df[terminal].str.len() > 1, terminal].empty]

            # Adiciona os novos indeterminismos à lista de indeterminismos
            indeterminisms.extend(new_indeterminisms)
            # Lista de listas contendo todos os indeterminismos do AFD
            all_indeterminisms.extend(new_indeterminisms)

    for indeterminism in all_indeterminisms:
        value = indeterminism[0]
        indeterminism_without_comma = value.replace(',', '')

        for col in afnd_df.columns:
            # Use the apply method to apply the transformation to each cell
            afnd_df[col] = afnd_df[col].apply(
                lambda x: f'[{indeterminism_without_comma}]' if x == value else x)
    return afnd_df


def af_mapping(csv_df: pd.DataFrame) -> list:
    pass


def lexical_recognition(afd_df: pd.DataFrame) -> pd.DataFrame:
    pass

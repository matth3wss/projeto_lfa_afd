# Construção de Autômato Finito Determinístico (AFD)

O algoritmo foi criado com o intuito de funcionar com qualquer gramática regular, contanto que siga o formato do arquivo de entrada `entrada.csv`.

## Requisitos

- Todo o código foi desenvolvido na versão `3.12.1` do Python, pois tenho aversão a coisa velha.
- Tecnicamente, eu só usei as bibliotecas `pandas` e `ipykernel`, mas o comando `pip freeze > requirements.txt` retorna tudo o que as duas bibliotecas usam, então eu deixei assim mesmo.
- `OPTIONAL` Eu uso ambientes virtuais durante o meu desenvolvimento.

## Instalação

```bash
pip install -r requirements.txt
```

## Problemas Conhecidos

- O algoritmo não trata o caso em que os novos símbolos criados alcançam a letra "S", copiando os valores do símbolo de entrada ("S") para a variável.

- O algoritmo também não trata o caso em que os novos símbolos ultrapassam o tamanho do alfabeto, lançando um erro de `index_out_of_range`.

- Talvez quando um indeterminismo criar mais de um indeterminismo, o algoritmo não trate corretamente.

## Implementações Não Realizadas

- O algoritmo não coloca asteriscos nos símbolos finais.

## Considerações Finais

- Se houver alguma parte que você não entendeu, saiba que o copilot foi quem fez a maior parte, eu apenas dei alguns pitacos.
- Meu código é o único que usa letras, e não cria tabela usando `\n` e `\t`.
- Apresentei o trabalho em 18/12/2023, por volta das 21:00. O professor já estava indo embora. Contudo, finalizei o trabalho em 31/12/2023 às 20:06.
- Euem, nunca vi criar tabela com print().

## Agradecimentos

- Agradeço à minha amiga Gabrieli por ter me ajudado a realizar o trabalho antes da apresentação e por ter ficado horas comigo em uma chamada no Discord ao decorrer de dois dias.
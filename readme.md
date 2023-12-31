## Instalação

```bash
pip install -r requirements.txt
```

## Problemas conhecidos

- O algoritmo não trata o caso em que os novos símbolos criados alcançam a letra S, copiando os valores do símbolo de entrada (S) para a variável.

- O algoritmo também não trata o caso em que os novos símbolos ultrapassam o tamanho do alfabeto, lançando um erro de `index out of range`.
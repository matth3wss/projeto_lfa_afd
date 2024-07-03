from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup as bs


class LrTableConverter:
    def __init__(self, html_webpage: bytes) -> None:
        """Construtor da classe LrTableConverter

        Parameters
        ----------
        html_webpage : str
            Página HTML com a tabela LR.
        """
        self.html_webpage = html_webpage
        self.soup = bs(html_webpage, "html.parser")
        self.table = self.soup.find("div", {"id": "lrTableView"}).find("table")

    def decompose_table(self):
        """Elimina as colunas ACTION, GOTO e LR table da tabela LR."""

        for th in self.table.find_all("th"):
            if th.text == "ACTION" or th.text == "GOTO" or th.text == "LR table":
                th.decompose()

    def convert_to_csv(self) -> pd.DataFrame:
        """Converte a tabela LR para um DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame com a tabela LR.
        """
        self.decompose_table()

        table_df = (
            pd.read_html(StringIO(str(self.table)))[0].droplevel(0, axis=1).fillna("")
        )

        return table_df

    def get_action_column_length(self) -> int:
        """Retorna a quantidade de colunas que são agrupadas na coluna ACTION.

        Returns
        -------
        int
            Quantidade de colunas que são agrupadas na coluna ACTION.
        """
        return self.table.find("th", string="ACTION").get("colspan")

    def get_goto_column_length(self) -> int:
        """Retorna a quantidade de colunas que são agrupadas na coluna GOTO.

        Returns
        -------
        int
            Quantidade de colunas que são agrupadas na coluna GOTO.
        """
        return self.table.find("th", string="GOTO").get("colspan")
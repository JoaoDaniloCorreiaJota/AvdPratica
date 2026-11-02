from pathlib import Path

import pandas as pd

# Caminho relativo à raiz do projeto (funciona no seu computador e no Streamlit Cloud)
RAIZ = Path(__file__).resolve().parent.parent
CAMINHO = RAIZ / "data" / "clean" / "dataset.csv"


def load_data():
    if not CAMINHO.exists():
        raise FileNotFoundError(
            f"Não achei {CAMINHO}. Gere o arquivo rodando a célula de exportação do "
            "notebook eda-com-downloads.ipynb (df.to_csv('data/clean/dataset.csv', index=False))."
        )
    df = pd.read_csv(CAMINHO)
    # Se o arquivo usa ";" como separador, tudo vem numa coluna só: lê de novo com sep=";"
    if df.shape[1] == 1 and ";" in str(df.columns[0]):
        df = pd.read_csv(CAMINHO, sep=";")
    return df
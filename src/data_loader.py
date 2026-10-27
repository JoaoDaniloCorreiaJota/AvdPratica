import pandas as pd

CAMINHO = r"C:\Users\joaod\Downloads\archive\flags.csv"


def load_data():
    return pd.read_csv(CAMINHO, sep=";")

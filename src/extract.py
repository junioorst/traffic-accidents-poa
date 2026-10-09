import pandas as pd
import json
import os


def extract_csv_data(file_path: str):
    df = pd.read_csv(file_path, sep=";")
    return df


if __name__ == "__main__":
    df_acidentes = extract_csv_data("data/raw/cat_acidentes.csv")
    print(df_acidentes)

    print("\nInformações do DataFrame:")
    print(df_acidentes.info())

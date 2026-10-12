import pandas as pd


def extract_csv_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=";")
    return df


if __name__ == "__main__":
    df_vitimas = extract_csv_data("data/raw/cat_vitimas.csv")

    # print("TABELA DE VÍTIMAS - 3 PRIMEIROS REGISTROS:")
    # print(df_vitimas.head(3).T)

    # print("\nTipo de dados das colunas:")
    # print(df_vitimas.dtypes)

    # print("\nNúmero de valores nulos por coluna:")
    # print(df_vitimas.isnull().sum())

    # print("\nDimensões do DataFrame:")
    # print(df_vitimas.shape)

    # print("\nValores únicos na coluna 'id':")
    # print(df_vitimas["id"].is_unique)

    print("\nValores na coluna 'sexo':")
    print(df_vitimas["sexo"].value_counts())

    print("\nValores na coluna 'sit_vitima':")
    print(df_vitimas["sit_vitima"].value_counts())

    print("\nValores na coluna 'tipo_veic':")
    print(df_vitimas["tipo_veic"].value_counts())
    print("\nValores na coluna 'fx_et':")
    print(df_vitimas["fx_et"].value_counts())
    print("\nValores na coluna 'periododia':")
    print(df_vitimas["periododia"].value_counts())

import pandas as pd


def extract_csv_data(file_path: str):
    df = pd.read_csv(file_path, sep=";")
    return df


if __name__ == "__main__":
    df_acidentes = extract_csv_data("data/raw/cat_acidentes.csv")

    # print("TABELA DE ACIDENTES - 3 PRIMEIROS REGISTROS:")
    # print(df_acidentes.head(3).T)

    # print("\nTipo de dados das colunas:")
    # print(df_acidentes.dtypes)

    # print("\nNúmero de valores nulos por coluna:")
    # print(df_acidentes.isnull().sum())

    print(df_acidentes.dtypes)
    
    print("\nNúmero de valores nulos por coluna:")
    print(df_acidentes.isnull().sum())

    print("\nVALORES DA COLUNA 'UPS':")
    print(df_acidentes["ups"].value_counts())

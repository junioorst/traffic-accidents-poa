import pandas as pd


def extract_csv_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=";")
    return df


if __name__ == "__main__":
    df_vitimas = extract_csv_data("data/raw/cat_vitimas.csv")

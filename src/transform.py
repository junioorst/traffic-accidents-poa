import pandas as pd
from extract import extract_csv_data

def transform_date_types(df: pd.DataFrame) -> pd.DataFrame:
    
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df["hora"] = pd.to_datetime(df["hora"].str.split(".").str[0], format="%H:%M:%S", errors="coerce").dt.time
    return df


if __name__ == "__main__":
    extracted_df = extract_csv_data("data/raw/cat_acidentes.csv")
    transformed_df = transform_date_types(extracted_df)
    
    print(transformed_df["hora"].isnull().sum())
    
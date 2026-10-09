import pandas as pd
from extract import extract_csv_data    

def transform_date_types(df: pd.DataFrame) -> pd.DataFrame:
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df["hora"] = pd.to_datetime(df["hora"].str.split(".").str[0], format="%H:%M:%S", errors="coerce").dt.time
    return df

def transform_numeric_types(df: pd.DataFrame) -> pd.DataFrame:
    df["idacidente"] = pd.to_numeric(df["idacidente"].str.split(",").str[0], errors="coerce")
    df["queda_arr"] = df["queda_arr"].astype("int64")
    return df

def drop_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["data_extracao", "predial1", "consorcio"])
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    transformed_df = drop_columns(df)
    transformed_df = transform_date_types(transformed_df)
    transformed_df = transform_numeric_types(transformed_df)
    return transformed_df
    

if __name__ == "__main__":
    extracted_df = extract_csv_data("data/raw/cat_acidentes.csv")
    transformed_df = transform(extracted_df)
    
    print(transformed_df.shape)
    
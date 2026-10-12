import pandas as pd
from extract import extract_csv_data


def transform_date_types(df: pd.DataFrame) -> pd.DataFrame:
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df["hora"] = pd.to_datetime(
        df["hora"].str.split(".").str[0], format="%H:%M:%S", errors="coerce"
    ).dt.time
    return df


def transform_numeric_types(df: pd.DataFrame) -> pd.DataFrame:
    df["idacidente"] = pd.to_numeric(
        df["idacidente"].str.split(",").str[0], errors="coerce"
    )
    df["queda_arr"] = df["queda_arr"].astype("int64")
    return df


def drop_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["data_extracao", "predial1", "consorcio"])
    return df


def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    valid_columns = [
        "id",
        "idacidente",
        "idade",
        "sexo",
        "sit_vitima",
        "fx_et",
        "tipo_veic",
        "periododia",
    ]
    df = df[valid_columns]
    return df


def transform_age(df: pd.DataFrame) -> pd.DataFrame:
    df["idade"] = df["idade"].astype("Int64")
    return df


def replace_unknown_values(df: pd.DataFrame) -> pd.DataFrame:
    df["sexo"] = df["sexo"].replace("NAO INFORMADO", pd.NA)
    df["sit_vitima"] = df["sit_vitima"].replace("NAOINFORMADO", pd.NA)
    df["fx_et"] = df["fx_et"].replace("NI", pd.NA)
    return df


def transform_accidents(df: pd.DataFrame) -> pd.DataFrame:
    transformed_df = drop_columns(df)
    transformed_df = transform_date_types(transformed_df)
    transformed_df = transform_numeric_types(transformed_df)
    return transformed_df


def transform_victims(df: pd.DataFrame) -> pd.DataFrame:
    transformed_df = select_columns(df)
    transformed_df = replace_unknown_values(transformed_df)
    transformed_df = transform_age(transformed_df)
    return transformed_df


if __name__ == "__main__":
    extracted_df = extract_csv_data("data/raw/cat_vitimas.csv")
    transformed_df = transform_victims(extracted_df)

    print(transformed_df["idade"].dtype)
    print(transformed_df["sexo"].isnull().sum())
    print(transformed_df["sit_vitima"].isnull().sum())
    print(transformed_df["fx_et"].isnull().sum())
    print(transformed_df["idade"].isnull().sum())

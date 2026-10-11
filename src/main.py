import pandas as pd

from extract import extract_csv_data
from transform import transform
from load import create_db_engine, load_data

if __name__ == "__main__":
    extracted_data = extract_csv_data("data/raw/cat_acidentes.csv")
    transformed_data = transform(extracted_data)
    db_engine = create_db_engine()
    load_data(transformed_data, db_engine)

    print(pd.read_sql("SELECT COUNT(*) FROM acidentes WHERE hora IS NULL", db_engine))

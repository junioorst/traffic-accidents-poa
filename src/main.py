import pandas as pd
from sqlalchemy import Time

from extract import extract_csv_data
from transform import transform_accidents, transform_victims
from load import create_db_engine, load_data

if __name__ == "__main__":
    extracted_data = extract_csv_data("data/raw/cat_acidentes.csv")
    transformed_data = transform_accidents(extracted_data)
    db_engine = create_db_engine()
    load_data(transformed_data, "acidentes", db_engine, dtype={"hora": Time()})

    extracted_data = extract_csv_data("data/raw/cat_vitimas.csv")
    transformed_data = transform_victims(extracted_data)
    load_data(transformed_data, "vitimas", db_engine)

    print(
        pd.read_sql(
            "SELECT COUNT(*) FROM vitimas v LEFT JOIN acidentes a ON v.idacidente = a.idacidente WHERE a.idacidente IS NULL",
            db_engine,
        )
    )

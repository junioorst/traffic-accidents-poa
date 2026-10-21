import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, inspect, text


def create_db_engine() -> Engine:
    load_dotenv()

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")

    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url)

    return engine


def load_data(
    df: pd.DataFrame, table_name: str, engine: Engine, dtype: dict | None = None
) -> None:
    if inspect(engine).has_table(table_name):
        with engine.begin() as conn:
            conn.execute(text(f'TRUNCATE TABLE "{table_name}"'))
            df.to_sql(table_name, conn, if_exists="append", index=False, dtype=dtype)
    else:
        df.to_sql(table_name, engine, index=False, dtype=dtype)


if __name__ == "__main__":
    engine = create_db_engine()
    print(engine)

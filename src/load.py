import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import Engine, Time, create_engine


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
    df.to_sql(table_name, engine, if_exists="replace", index=False, dtype=dtype)


if __name__ == "__main__":
    engine = create_db_engine()
    print(engine)

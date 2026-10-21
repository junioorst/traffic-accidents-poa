import pendulum
from airflow.sdk import dag, task

DATA_PATH = "/opt/airflow/data/raw"
DATASETS = {
    "acidentes-de-transito-acidentes": "cat_acidentes.csv",
    "acidentes-de-transito-vitimas": "cat_vitimas.csv",
}


@dag(
    dag_id="traffic_accidents_pipeline",
    schedule="0 6 2 * *",
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Sao_Paulo"),
    catchup=False,
    tags=["traffic-accidents"],
)
def traffic_accidents_pipeline():

    @task
    def load_accidents():
        from sqlalchemy import Time

        from extract import extract_csv_data
        from load import create_db_engine, load_data
        from transform import transform_accidents

        df = extract_csv_data(f"{DATA_PATH}/cat_acidentes.csv")
        df = transform_accidents(df)
        engine = create_db_engine()
        load_data(df, "acidentes", engine, dtype={"hora": Time()})

        print(f"Accidents loaded: {len(df)}")
        return len(df)

    @task
    def load_victims():
        from extract import extract_csv_data
        from load import create_db_engine, load_data
        from transform import transform_victims

        df = extract_csv_data(f"{DATA_PATH}/cat_vitimas.csv")
        df = transform_victims(df)
        engine = create_db_engine()
        load_data(df, "vitimas", engine)

        print(f"Victims loaded: {len(df)}")
        return len(df)

    @task.bash
    def dbt_build():
        return (
            "/home/airflow/dbt_venv/bin/dbt build "
            "--project-dir /opt/airflow/acidentes_dbt "
            "--profiles-dir /opt/airflow/acidentes_dbt/profiles"
        )

    @task.sensor(poke_interval=30 * 60, timeout=5 * 24 * 60 * 60, mode="reschedule")
    def wait_for_update():

        from source import get_csv_resource

        month_start = pendulum.now("America/Sao_Paulo").start_of("month")

        for dataset_id in DATASETS:
            resource = get_csv_resource(dataset_id)
            if resource["last_modified"] < month_start:
                print(f"{dataset_id} not updated yet: {resource['last_modified']}")
                return False

        print("All datasets updated this month")
        return True

    @task
    def download_csvs():
        from source import download_file, get_csv_resource

        for dataset_id, file_name in DATASETS.items():
            resource = get_csv_resource(dataset_id)
            download_file(resource["url"], f"{DATA_PATH}/{file_name}")
            print(f"Downloaded {file_name}")

    (
        wait_for_update()
        >> download_csvs()
        >> [load_accidents(), load_victims()]
        >> dbt_build()
    )


traffic_accidents_pipeline()

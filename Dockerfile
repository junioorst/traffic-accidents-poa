FROM apache/airflow:3.3.1


RUN pip install --no-cache-dir \
    "apache-airflow==3.3.1" \
    "pandas==3.0.6" \
    "psycopg[binary]==3.3.6" \
    "python-dotenv==1.2.4"

RUN python -m venv /home/airflow/dbt_venv && \
    /home/airflow/dbt_venv/bin/pip install --no-cache-dir \
    "dbt-core==1.12.6" \
    "dbt-postgres==1.11.0"
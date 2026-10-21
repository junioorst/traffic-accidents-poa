from datetime import datetime
from airflow.sdk import dag, task


@dag(  # [DECLARAR] "esta função é uma DAG"
    dag_id="teste_ola",  # [NOMEAR] o nome que aparece na tela
    schedule=None,  # [AGENDAR] None = só roda quando você mandar
    start_date=datetime(2026, 10, 1),
    catchup=False,  # [NÃO RETROCEDER] não roda datas passadas
)
def teste_ola():

    @task  # [ETAPA 1] uma task
    def dizer_ola():
        print("Olá, Airflow!")

    @task  # [ETAPA 2] outra task
    def dizer_tchau():
        print("Tchau, Airflow!")

    dizer_ola() >> dizer_tchau()  # [ORDEM] primeiro um, depois o outro


teste_ola()  # [REGISTRAR] cria a DAG

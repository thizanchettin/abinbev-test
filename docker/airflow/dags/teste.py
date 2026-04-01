# dags/teste.py
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(
    dag_id="dag_teste",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    def hello():
        print("Airflow funcionando!")

    t1 = PythonOperator(
        task_id="hello",
        python_callable=hello,
    )

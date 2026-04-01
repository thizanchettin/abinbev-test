FROM apache/airflow:2.10.4

RUN pip install --no-cache-dir \
    "apache-airflow-providers-databricks" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.12.txt"

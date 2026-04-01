from __future__ import annotations

from datetime import datetime

import requests
from airflow import DAG
from airflow.models import Variable
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.utils.task_group import TaskGroup

DATABRICKS_CONN_ID = "databricks_default"
JOB_NAME = "[dev service_principal] runner-job-dev"

TELEGRAM_TOKEN = Variable.get("telegram_token", default_var="")
TELEGRAM_CHAT_ID = Variable.get("telegram_chat_id", default_var="")
ALERT_EMAIL = Variable.get("alert_email", default_var="")


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(
        url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    )


def on_failure_callback(context: dict) -> None:
    dag_id = context["dag"].dag_id
    task_id = context["task"].task_id
    execution_date = context["execution_date"]
    log_url = context["task_instance"].log_url
    send_telegram(
        f"Task Failed\n"
        f"DAG: `{dag_id}`\n"
        f"Task: `{task_id}`\n"
        f"Execution: `{execution_date}`\n"
        f"Logs: {log_url}"
    )


def on_retry_callback(context: dict) -> None:
    dag_id = context["dag"].dag_id
    task_id = context["task"].task_id
    try_number = context["task_instance"].try_number
    send_telegram(f"Task Retry\nDAG: `{dag_id}`\nTask: `{task_id}`\nAttempt: `{try_number}`")


def on_dag_failure_callback(context: dict) -> None:
    dag_id = context["dag"].dag_id
    execution_date = context["execution_date"]
    send_telegram(f"DAG Failed\nDAG: `{dag_id}`\nExecution: `{execution_date}`")


def make_operator(task_id: str, layer: str) -> DatabricksRunNowOperator:
    return DatabricksRunNowOperator(
        task_id=task_id,
        databricks_conn_id=DATABRICKS_CONN_ID,
        job_name=JOB_NAME,
        python_params=["--layer", layer],
        on_failure_callback=on_failure_callback,
        on_retry_callback=on_retry_callback,
    )


with DAG(
    dag_id="medallion_pipeline",
    description="Medallion pipeline: Bronze → Silver → Gold",
    start_date=datetime(2026, 3, 31),
    schedule="0 6 * * *",
    catchup=False,
    on_failure_callback=on_dag_failure_callback,
    default_args={
        "email": [ALERT_EMAIL],
        "email_on_failure": True,
        "email_on_retry": True,
        "retries": 1,
    },
    tags=["medallion", "spark"],
) as dag:
    with TaskGroup("bronze", tooltip="Ingestion") as tg_bronze:
        t_bronze = make_operator(task_id="engine", layer="bronze")

    with TaskGroup("silver", tooltip="Transformation") as tg_silver:
        t_silver = make_operator(task_id="engine", layer="silver")

    with TaskGroup("gold", tooltip="Aggregation") as tg_gold:
        t_gold = make_operator(task_id="engine", layer="gold")

    tg_bronze >> tg_silver >> tg_gold

FROM apache/airflow:2.8.3-python3.11

# Copia DAGs
COPY dags /opt/airflow/dags

# Copia pyproject.toml e lockfile
COPY pyproject.toml uv.lock /opt/airflow/

# Instala uv e sincroniza dependências do projeto
RUN pip install --upgrade pip setuptools wheel && \
    pip install uv && \
    uv sync

USER airflow

EXPOSE 8080

ENTRYPOINT ["bash", "-c", "airflow db init && airflow scheduler & airflow webserver"]
**Choose your language / Escolha o idioma:**
- [English Version](#US)
- [Versão em Português](#BR)

---

<a id="US"></a>

# abinbev-pipeline

Medallion data pipeline (Bronze → Silver → Gold) that consumes the Open
Brewery DB API, processes data with Apache Spark on Databricks, and
orchestrates execution using Apache Airflow with Telegram and email
notifications/alerts.

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Make](https://community.chocolatey.org/packages/make#files)
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
- [Databricks Free Trial](https://login.databricks.com/signup?provider=DB_FREE_TIER) account with Unity Catalog enabled
- Gmail account with [App Password](https://myaccount.google.com/apppasswords) enabled
- Telegram bot created via[@BotFather](https://t.me/BotFather)
- GitHub account with access to GitHub Actions

---

## Project Structure

```
abinbev-pipeline/
    ├── spark/
    │   └── abinbev_test/
    │       ├── runner.py
    │       ├── bronze/
    │       │   ├── engine.py
    │       │   └── schema.py
    │       ├── silver/
    │       │   └── engine.py
    │       ├── gold/
    │       │   └── engine.py
    │       └── utils/
    │           ├── client.py
    │           ├── config.py
    │           ├── logger.py
    │           └── spark.py
    ├── docker/
    │   └── airflow/
    │       ├── Dockerfile
    │       ├── docker-compose.yaml
    │       └── dags/
    │           └── medallion_pipeline.py
    ├── tests/
    ├── pyproject.toml
    ├── databricks.yml
    ├── Makefile
    ├── .env.template
    └── .gitignore

```

---

## 1. Clone the repository

``` bash
git clone https://github.com/thizanchettin/abinbev-test.git
cd abinbev-pipeline
```

---

## 2. Configure the Python environment

``` bash
uv sync --group dev
```

---

## 3. Configure environment variables

Copy the template and fill it with your credentials:

``` bash
cp .env.template docker/airflow/.env
```

Edit the `docker/airflow/.env` file with your credentials.

```env
# Databricks — Personal Access Token
DATABRICKS_TOKEN=your-databricks-personal-access-token
DATABRICKS_HOST=your-workspace.cloud.databricks.com

# Gmail SMTP — use a App Password
AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT=587
AIRFLOW__SMTP__SMTP_STARTTLS=True
AIRFLOW__SMTP__SMTP_SSL=False
AIRFLOW__SMTP__SMTP_USER=your-gmail-address@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD=your-gmail-app-password
AIRFLOW__SMTP__SMTP_MAIL_FROM=your-gmail-address@gmail.com

# Telegram — Bot token and chat id via /getUpdates
AIRFLOW__VARIABLES__TELEGRAM_TOKEN=your-telegram-bot-token
AIRFLOW__VARIABLES__TELEGRAM_CHAT_ID=your-telegram-chat-id

# E-mail para alertas
AIRFLOW__VARIABLES__ALERT_EMAIL=your-alert-email@gmail.com
```

> The `.env` file is in `.gitignore` and will never be committed.

---

## 4. Configure Databricks

### 4.1 Obtain the Personal Access Token

In your Databricks workspace: **Settings → Developer → Access tokens → Generate new token**. Copy the token and paste on `.env`

### 4.2 Obtain the Databricks Host

Workspace URL without `https://`. Example: `adb-1234567890.12.azuredatabricks.net`.

### 4.3 Authenticate Databricks CLI

``` bash
databricks configure
```

Provide the host (`https://seu-workspace.cloud.databricks.com`) and token when requested.

### 4.4 Create schema in Unity Catalog

Execute:

``` sql
CREATE CATALOG IF NOT EXISTS workspace;
CREATE SCHEMA IF NOT EXISTS workspace.data_lake;
```

### 4.5 Deploy the bundle

``` bash
uv build
databricks bundle deploy
```

At this point, you can already run the job manually in Databricks by providing the **--layer** parameter in the job call with the possible values **bronze**, **silver**, or **gold**. To do this, locate the job in the `Jobs & Pipelines` section and select the **Run now with different settings** option

Another option is to run the pipeline through Airflow, but you will need to edit the `medallion_pipeline.py` file. When running the bundle, the Databricks CLI will add `[dev service_principal]` to the filename if the command is executed by a Service Principal; however, since this is a manual execution with PAT, the filename will look like `[dev username]`.

Find the snippet below in the `medallion_pipeline.py` file and adjust the name as appropriate for your scenario:

``` python
from __future__ import annotations

from datetime import datetime

import requests
from airflow import DAG
from airflow.models import Variable
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.utils.task_group import TaskGroup

DATABRICKS_CONN_ID = "databricks_default"
JOB_NAME = "[dev service_principal] runner-job-dev" #<<<------ Here

TELEGRAM_TOKEN = Variable.get("telegram_token", default_var="")
TELEGRAM_CHAT_ID = Variable.get("telegram_chat_id", default_var="")
ALERT_EMAIL = Variable.get("alert_email", default_var="")
```

If you choose to continue configuring the pipeline as described in the following steps, it is very likely that no changes will be necessary.

---

## 5. Configure GitHub Actions

Register the following secrets in GitHub:

| Secret | Description |
|---|---|
| `DATABRICKS_HOST` | Workspace URL, ex: `https://adb-123.azuredatabricks.net` |
| `DATABRICKS_CLIENT_ID` | Service Principal Client ID |
| `DATABRICKS_CLIENT_SECRET` | Service Principal Client Secret |

> Automatic deployment occurs on pushes to the `main` branch.

---

## 6. Configure Telegram

1. Open Telegram and start a conversation with [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions to create the bot — save the token
3. Start a conversation with your bot
4. Go to `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to get the `chat_id`
5. Fill in `AIRFLOW__VARIABLES__TELEGRAM_TOKEN` and `AIRFLOW__VARIABLES__TELEGRAM_CHAT_ID` in `.env`

---

## 7. Configure Gmail

1. Sign in to your Google account at [myaccount.google.com](https://myaccount.google.com)
2. Go to **Security → Two-step verification** and enable it
3. Go to **Security → App passwords**, create a password for “Mail,” and save it
4. Fill in `AIRFLOW__SMTP__SMTP_USER`, `AIRFLOW__SMTP__SMTP_PASSWORD`, and `AIRFLOW__SMTP__SMTP_MAIL_FROM` in the `.env` file

---

## 8. Start Airflow

To correctly execute the instructions below, `make` must be installed. See the `Makefile` section for more details.

The first time, run the following commands in order:

```bash
make build    # builds the Docker image with the Databricks provider
make init     # initializes the database and creates the admin user
make up       # starts the services
```

Access Airflow at [http://localhost:8080](http://localhost:8080) using the `admin` username and `admin` password.

The `medallion_pipeline` DAG runs daily at 06:00 UTC and executes the Bronze → Silver → Gold tiers in sequence, each triggering the job in Databricks via the `DatabricksRunNowOperator`.

---

## 9. Run tests

``` bash
uv run pytest --cov --cov-report=xml
```

---

## Makefile

All Docker commands are managed by the Makefile. To view the complete list:

```bash
make help
```

| Command | Description |
|---|---|
| `make build` | Builds the Airflow Docker image |
| `make init` | Initializes the database and creates the admin user (first time only) |
| `make up` | Starts all services in the background |
| `make down` | Stops all services |
| `make restart` | Stops and restarts |
| `make logs` | Monitors logs for all services |
| `make logs-scheduler` | Monitors only the scheduler logs |
| `make logs-webserver` | Monitors only the webserver logs |
| `make clean` | Removes containers and volumes |
| `make reset` | Full reset: clean + build + init + up |

If you don’t have the utility yet, the easiest way to install `make` is through `Chocolatey`. If you don’t have it installed yet, run:

``` bash
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

And then:

``` bash
choco install make
```

---

## Security — Sensitive Files

The files below are in `.gitignore` and **should never be committed**:

| File | Reason |
|---|---|
| `docker/airflow/.env` | Contains tokens, passwords, and credentials |


Always use `.env.template` as a reference and never remove it from the repository.

---

<a id="BR"></a>

# abinbev-pipeline

Pipeline de dados medallion (Bronze → Silver → Gold) que consome a [Open Brewery DB API](https://www.openbrewerydb.org/), processa os dados com Apache Spark no Databricks e orquestra a execução via Apache Airflow com notificações/alertas por Telegram e e-mail.

---

## Pré-requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Make](https://community.chocolatey.org/packages/make#files)
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
- Conta no [Databricks Free Trial](https://login.databricks.com/signup?provider=DB_FREE_TIER) com Unity Catalog habilitado
- Conta no Gmail com [App Password](https://myaccount.google.com/apppasswords) habilitada
- Bot do Telegram criado via [@BotFather](https://t.me/BotFather)
- Conta no GitHub com acesso a GitHub Actions

---

## Estrutura do projeto

```
abinbev-pipeline/
├── spark/
│   └── abinbev_test/
│       ├── runner.py
│       ├── bronze/
│       │   ├── engine.py
│       │   └── schema.py
│       ├── silver/
│       │   └── engine.py
│       ├── gold/
│       │   └── engine.py
│       └── utils/
│           ├── client.py
│           ├── config.py
│           ├── logger.py
│           └── spark.py
├── docker/
│   └── airflow/
│       ├── Dockerfile
│       ├── docker-compose.yaml
│       └── dags/
│           └── medallion_pipeline.py
├── tests/
├── pyproject.toml
├── databricks.yml
├── Makefile
├── .env.template
└── .gitignore
```

---

## 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/abinbev-pipeline.git
cd abinbev-pipeline
```

---

## 2. Configurar o ambiente Python

```bash
uv sync --group dev
```

---

## 3. Configurar variáveis de ambiente

Copie o template e preencha com suas credenciais:

```bash
cp .env.template docker/airflow/.env
```

Edite o arquivo `docker/airflow/.env`:

```env
# Databricks — Personal Access Token do seu workspace
DATABRICKS_TOKEN=your-databricks-personal-access-token
DATABRICKS_HOST=your-workspace.cloud.databricks.com

# Gmail SMTP — use um App Password, não a senha da conta
AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT=587
AIRFLOW__SMTP__SMTP_STARTTLS=True
AIRFLOW__SMTP__SMTP_SSL=False
AIRFLOW__SMTP__SMTP_USER=your-gmail-address@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD=your-gmail-app-password
AIRFLOW__SMTP__SMTP_MAIL_FROM=your-gmail-address@gmail.com

# Telegram — token do bot criado via @BotFather e seu chat_id via /getUpdates
AIRFLOW__VARIABLES__TELEGRAM_TOKEN=your-telegram-bot-token
AIRFLOW__VARIABLES__TELEGRAM_CHAT_ID=your-telegram-chat-id

# E-mail para alertas
AIRFLOW__VARIABLES__ALERT_EMAIL=your-alert-email@gmail.com
```

> O arquivo `.env` está no `.gitignore` e nunca será commitado.

---

## 4. Configurar o Databricks

### 4.1 Obter o Personal Access Token

No seu workspace Databricks: **Settings → Developer → Access tokens → Generate new token**. Copie o token e coloque no `.env`.

### 4.2 Obter o Databricks Host

É a URL do seu workspace sem `https://`, por exemplo: `adb-1234567890.12.azuredatabricks.net`.

### 4.3 Autenticar o Databricks CLI

```bash
databricks configure
```

Informe o host (`https://seu-workspace.cloud.databricks.com`) e o token quando solicitado.

### 4.4 Criar o schema no Unity Catalog

No SQL Editor do Databricks, execute:

```sql
CREATE CATALOG IF NOT EXISTS workspace;
CREATE SCHEMA IF NOT EXISTS workspace.data_lake;
```

> Os nomes de catalog e schema podem ser customizados via variáveis de ambiente `UC_CATALOG` e `UC_SCHEMA` no job do Databricks.

### 4.5 Fazer o deploy do bundle

```bash
uv build
databricks bundle deploy
```

Nesse ponto já é possível executar o job manualmente no Databricks, fornecendo o parâmetro **--layer** na chamada do job com os possíveis valores **bronze**, **silver** ou **gold**. Para isso encontre o job na seção Jobs & Pipelines e selecione a opção **Run now with different settings**

Outra opção é executar o fluxo através do Airflow, porém será necessário editar o arquivo `medallion_pipeline.py`. Ao executar o bundle, o Databricks CLI irá adicionar `[dev service_principal]` ao nome do arquivo se o comando for executado por um Service Principal, entretanto por ser uma execução manual com PAT, o nome do arquivo ficará parecido com `[dev nomedousuário]`.

Encontre o trecho abaixo no arquivo `medallion_pipeline.py` e ajuste o nome da forma adquada ao seu cenário:

``` python
from __future__ import annotations

from datetime import datetime

import requests
from airflow import DAG
from airflow.models import Variable
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.utils.task_group import TaskGroup

DATABRICKS_CONN_ID = "databricks_default"
JOB_NAME = "[dev service_principal] runner-job-dev" #<<<------ Ajuste aqui

TELEGRAM_TOKEN = Variable.get("telegram_token", default_var="")
TELEGRAM_CHAT_ID = Variable.get("telegram_chat_id", default_var="")
ALERT_EMAIL = Variable.get("alert_email", default_var="")
```

Caso opte por prosseguir com a configuração do pipeline como descrito nos próximos passos, é muito provável que nenhuma mudança deva ser feita.

---

## 5. Configurar GitHub Actions

Os secrets abaixo precisam ser cadastrados em **Settings → Secrets and variables → Actions** no seu repositório GitHub:

| Secret | Descrição |
|---|---|
| `DATABRICKS_HOST` | URL do workspace, ex: `https://adb-123.azuredatabricks.net` |
| `DATABRICKS_CLIENT_ID` | Client ID do Service Principal |
| `DATABRICKS_CLIENT_SECRET` | Client Secret do Service Principal |

### Criar um Service Principal no Databricks

1. No workspace: **Settings → Identity and access → Service principals → Add service principal**
2. Crie o Service Principal e gere um Client Secret
3. Dê permissão de **Contributor** no workspace para o Service Principal
4. Cadastre o `CLIENT_ID` e `CLIENT_SECRET` nos secrets do GitHub

> O deploy automático via GitHub Actions ocorre a cada push na branch `main`.

---

## 6. Configurar o Telegram

1. Abra o Telegram e inicie uma conversa com [@BotFather](https://t.me/BotFather)
2. Envie `/newbot` e siga as instruções para criar o bot — guarde o token
3. Inicie uma conversa com o seu bot
4. Acesse `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates` para obter o `chat_id`
5. Preencha `AIRFLOW__VARIABLES__TELEGRAM_TOKEN` e `AIRFLOW__VARIABLES__TELEGRAM_CHAT_ID` no `.env`

---

## 7. Configurar o Gmail

1. Acesse sua conta Google em [myaccount.google.com](https://myaccount.google.com)
2. Vá em **Segurança → Verificação em duas etapas** e ative
3. Vá em **Segurança → Senhas de app**, crie uma senha para "Mail" e guarde
4. Preencha `AIRFLOW__SMTP__SMTP_USER`, `AIRFLOW__SMTP__SMTP_PASSWORD` e `AIRFLOW__SMTP__SMTP_MAIL_FROM` no `.env`

---

## 8. Subir o Airflow

To correctly execute the instructions below, `make` must be installed. See the `Makefile` section for more details.

The first time, run the following commands in order:

```bash
make build    # builds the Docker image with the Databricks provider
make init     # initializes the database and creates the admin user
make up       # starts the services
```

Access Airflow at [http://localhost:8080](http://localhost:8080) using the `admin` username and `admin` password.

The `medallion_pipeline` DAG runs daily at 06:00 UTC and executes the Bronze → Silver → Gold tiers in sequence, each triggering the job in Databricks via the `DatabricksRunNowOperator`.

---

## 9. Executar os testes

```bash
uv run pytest --cov --cov-report=xml
```

---

## Makefile

Todos os comandos Docker são gerenciados pelo Makefile. Para ver a lista completa:

```bash
make help
```

| Comando | Descrição |
|---|---|
| `make build` | Builda a imagem Docker do Airflow |
| `make init` | Inicializa o banco de dados e cria o usuário admin (apenas na primeira vez) |
| `make up` | Sobe todos os serviços em background |
| `make down` | Para todos os serviços |
| `make restart` | Para e sobe novamente |
| `make logs` | Acompanha os logs de todos os serviços |
| `make logs-scheduler` | Acompanha apenas os logs do scheduler |
| `make logs-webserver` | Acompanha apenas os logs do webserver |
| `make clean` | Remove containers e volumes |
| `make reset` | Reset completo: clean + build + init + up |

Caso ainda não tenha o utilitário, a forma mais simples de se instalar o `make` é através do `Chocolatey`. Caso ainda não tenha ele instalado, execute:

``` bash
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

E depois:

``` bash
choco install make
```

---

## Segurança — arquivos sensíveis

Os arquivos abaixo estão no `.gitignore` e **nunca devem ser commitados**:

| Arquivo | Motivo |
|---|---|
| `docker/airflow/.env` | Contém tokens, senhas e credenciais |


Use sempre o `.env.template` como referência e nunca remova-o do repositório.

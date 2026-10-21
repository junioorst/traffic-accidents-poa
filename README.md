# Traffic Accidents POA 🚦

An end-to-end data pipeline that extracts, transforms and loads public traffic accident data from Porto Alegre (Brazil) into a containerized PostgreSQL database, modeling accidents and victims as two related tables, and serves the results through a BI dashboard.

The pipeline is orchestrated by **Apache Airflow**, which runs monthly, waits for the city to publish updated data, downloads it, reloads the database and rebuilds the dbt models automatically.

---

## 📊 Dashboard

Built with **Metabase**, running as a container alongside PostgreSQL, and reading the analytics tables modeled with dbt.

![Traffic accidents dashboard](docs/images/dashboard.png)

**Key findings**

- Accidents grew steadily from 2021 to 2025, with a sharp drop in **May 2024**, the month of the floods that paralyzed Porto Alegre
- **Motorcycles** account for **22,693 victims** (about 60% of all victims), 2.3 times more than cars, the second most common vehicle type
- Accidents peak during commuting hours, at **8 AM** and especially **6 PM** (6,840 accidents)
- **63.3%** of accidents caused only property damage, **36.2%** caused injuries and **0.5%** were fatal (447 cases)

---

## 🏗️ Architecture

```mermaid
flowchart LR
    subgraph Airflow["Apache Airflow (monthly schedule)"]
        A[wait_for_update<br/>CKAN API sensor] --> B[download_csvs]
        B --> C[load_accidents]
        B --> D[load_victims]
        C --> E[dbt_build]
        D --> E
    end

    B -. writes .-> F[(data/raw CSVs)]
    C -. writes .-> G[(PostgreSQL<br/>public: raw tables)]
    D -. writes .-> G
    E -. builds .-> H[(PostgreSQL<br/>analytics: staging and marts)]
    G --> H
    H --> I[Metabase dashboard]
```

---

## 🛠️ Tech Stack

- **Python 3.12**
- **Pandas** for extraction and transformation
- **Pytest** for unit tests of the transformation logic
- **PostgreSQL 16** as the database
- **Apache Airflow 3** for orchestration and scheduling, running with LocalExecutor on a custom Docker image
- **dbt Core** for in-database modeling, data tests and documentation
- **Docker & Docker Compose** to run PostgreSQL, Metabase and Airflow in isolated, reproducible containers
- **SQLAlchemy + psycopg** for the database connection
- **python-dotenv** for credentials management
- **Metabase** for the BI dashboard

---

## 📁 Data Source

Open data published by EPTC (Porto Alegre's traffic authority) through the city's open data portal:

- [**Acidentes**](https://dadosabertos.poa.br/dataset/acidentes-de-transito-acidentes) (accidents): one row per traffic accident
- [**Vítimas**](https://dadosabertos.poa.br/dataset/acidentes-de-transito-vitimas) (victims): one row per person involved in an accident with injuries or fatalities

The datasets are updated monthly by the city and licensed under [Creative Commons Attribution (CC-BY)](http://www.opendefinition.org/licenses/cc-by).

---

## 🗂️ Data Model

The victims dataset originally repeated every accident attribute (location, date, vehicles involved). It was **normalized**: the `vitimas` table keeps only victim-specific columns and references its accident through `idacidente`.

```
 acidentes (1) ───────< (N) vitimas
   idacidente               id
   data, hora               idacidente
   log1, log2               idade, fx_et
   latitude, longitude      sexo
   tipo_acid, ups           sit_vitima
   feridos, mortes ...      tipo_veic
   vehicle counts ...       periododia
```

---

## 🧱 dbt Modeling

The raw tables loaded by the Python pipeline are modeled with **dbt** into two layers inside PostgreSQL:

- **Staging** (views): `stg_acidentes` removes the records with invalid future dates; `stg_vitimas` selects victim-specific columns
- **Marts** (tables): `fct_acidentes` adds a readable severity column; `fct_vitimas` joins each victim with its accident's date, time and location

A single rule written once in staging propagates to every downstream table: filtering 4 invalid accidents also removed their victim from `fct_vitimas`, without any extra filter.

![dbt lineage graph](docs/images/dbt_lineage.png)

---

## 🔁 Orchestration

The whole pipeline runs as a single Airflow DAG, scheduled for the 2nd day of each month:

- **`wait_for_update`**: a sensor that queries the open data portal's CKAN API and waits until both datasets have been updated in the current month, checking every 30 minutes for up to 5 days
- **`download_csvs`**: downloads the CSV files, writing to a temporary file first so an interrupted download never corrupts existing data
- **`load_accidents`** and **`load_victims`**: run in parallel, reusing the same extract, transform and load functions as the standalone pipeline
- **`dbt_build`**: rebuilds the dbt models and runs all data tests

Loading uses `TRUNCATE` and insert inside a single transaction, so dependent dbt views are preserved and a failed load never leaves an empty table.

![Airflow DAG](docs/images/airflow_dag.png)

---

## 🔄 Transformations

**Accidents**
- Dropped metadata and low-value columns (`data_extracao`, `predial1`, `consorcio`)
- Converted `data` to `datetime` and `hora` to `time` (removing a 7-digit fractional suffix)
- Converted `idacidente` from text (`678074,0`) to integer
- Explicitly typed `hora` as `TIME` in PostgreSQL

**Victims**
- Selected only the 8 victim-specific columns (normalized model)
- Converted `idade` to nullable integer (`Int64`), preserving missing values
- Standardized "unknown" values: the same concept appeared as `NAO INFORMADO`, `NAOINFORMADO`, `NI` and empty values across columns, and all were unified as `NULL`

---

## ✅ Data Quality

**Automated data tests (dbt)**
- 14 tests run on every `dbt build`, covering raw sources and final tables
- Uniqueness and not-null checks on accident and victim IDs
- Accepted values for severity weights (`ups`) and severity labels
- **Referential integrity:** every victim references an existing accident
- A custom test monitors accidents with future dates in the source, as a warning

**Unit tests**
- 8 Pytest tests cover every transformation function, protecting against regressions such as date formats silently turning valid values into nulls

**Issues found in the source data**
- **4 accidents with future dates** (up to 2029), beyond the data extraction date. They are filtered out in the dbt staging layer and monitored by a warning-level test
- An unusually high number of accidents at **midnight**, suggesting unknown times may be recorded as `00:00`

---

## 📂 Project Structure

```
traffic-accidents-poa/
├── dags/
│   └── traffic_accidents_pipeline.py   # Airflow DAG
├── data/raw/              # Source CSV files (downloaded by the DAG)
├── docs/images/           # Dashboard, dbt lineage and Airflow DAG screenshots
├── src/
│   ├── source.py          # Queries the CKAN API and downloads the CSV files
│   ├── extract.py         # Reads the CSV files
│   ├── transform.py       # Cleans and normalizes both datasets
│   ├── load.py            # Loads DataFrames into PostgreSQL
│   └── main.py            # Runs the pipeline without Airflow
├── tests/
│   └── test_transform.py  # Unit tests for the transformations
├── acidentes_dbt/
│   ├── models/
│   │   ├── staging/       # Source declarations and staging views
│   │   └── marts/         # Final tables and their tests
│   ├── tests/             # Custom data tests
│   ├── profiles/          # dbt profile used inside Airflow (reads environment variables)
│   └── dbt_project.yml    # dbt project configuration
├── Dockerfile             # Custom Airflow image with pandas, psycopg and dbt
├── docker-compose.yml     # PostgreSQL, Metabase and Airflow services
├── .env.example           # Template for credentials and settings
├── pytest.ini
└── requirements.txt
```

---

## ⚙️ How to Run

**Prerequisites:** Docker and Docker Compose (on Windows, Docker Desktop with WSL2). Python 3.12+ is only needed to run the unit tests.

1. **Clone the repository**

```bash
   git clone https://github.com/junioorst/traffic-accidents-poa.git
   cd traffic-accidents-poa
```

2. **Configure the credentials**

```bash
   cp .env.example .env
```

   Fill in `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` in the `.env` file. On Linux, also set `AIRFLOW_UID` to the output of `id -u`, so files created by Airflow belong to your user.

3. **Build the Airflow image and start all services**

```bash
   docker compose build
   docker compose up -d
```

4. **Run the pipeline**

   Open `http://localhost:8080` (user `airflow`, password `airflow`), unpause the `traffic_accidents_pipeline` DAG and trigger it. It downloads the data, loads PostgreSQL and builds the dbt models.

5. **Run the unit tests**

```bash
   python3 -m venv .venv          # On Windows: python -m venv .venv
   source .venv/bin/activate      # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pytest
```

6. **Open the dashboard**

   Go to `http://localhost:3000`, create an admin account and add a PostgreSQL database with host **`postgres`** (the Docker Compose service name), port `5432` and the credentials from your `.env` file. The analytics tables are in the `analytics` schema.

---

## 🔍 Example Query

Victims by vehicle type and accident zone, using the dbt mart (no join needed):

```sql
SELECT regiao, tipo_veic, COUNT(*) AS victims
FROM analytics.fct_vitimas
GROUP BY regiao, tipo_veic
ORDER BY victims DESC;
```

---

## 🗺️ Roadmap

- [x] Extraction, transformation and loading with Pandas
- [x] PostgreSQL with Docker Compose
- [x] Normalized accidents and victims model
- [x] Unit tests for transformations with Pytest
- [x] BI dashboard with Metabase
- [x] dbt models (staging and marts) with data tests
- [x] Orchestration with Apache Airflow

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

# Traffic Accidents POA 🚦

An end-to-end data pipeline that extracts, transforms and loads public traffic accident data from Porto Alegre (Brazil) into a containerized PostgreSQL database, modeling accidents and victims as two related tables, and serves the results through a BI dashboard.

This project is being built incrementally as a modern data engineering portfolio, evolving towards dbt modeling and Apache Airflow orchestration.

---

## 📊 Dashboard

Built with **Metabase**, running as a container alongside PostgreSQL in the same Docker Compose setup.

![Traffic accidents dashboard](docs/images/dashboard.png)

**Key findings**

- Accidents grew steadily from 2021 to 2025, with a sharp drop in **May 2024**, the month of the floods that paralyzed Porto Alegre
- **Motorcycles** account for **22,694 victims** (about 60% of all victims), 2.3 times more than cars, the second most common vehicle type
- Accidents peak during commuting hours, at **8 AM** and especially **6 PM** (6,840 accidents)
- **63.3%** of accidents caused only property damage, **36.2%** caused injuries and **0.5%** were fatal (447 cases)

---

## 🏗️ Architecture

```
 data/raw/*.csv
      │
      ▼
 ┌──────────┐    ┌────────────┐    ┌─────────────┐
 │ extract  │───▶│ transform  │───▶│    load     │
 │ (pandas) │    │ (pandas)   │    │ (SQLAlchemy)│
 └──────────┘    └─────┬──────┘    └──────┬──────┘
                       │                  │ port 5432
                 tested with              ▼
                   Pytest      ┌──────────────────────────────┐
                               │      Docker Compose          │
                               │                              │
                               │  PostgreSQL 16               │
                               │   ├── acidentes (87,323)     │
                               │   └── vitimas   (37,857)     │
                               │          │                   │
                               │          ▼                   │
                               │  Metabase (port 3000)        │
                               └──────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Python 3.12**
- **Pandas** for extraction and transformation
- **Pytest** for unit tests of the transformation logic
- **PostgreSQL 16** as the database
- **Docker & Docker Compose** to run PostgreSQL and Metabase in isolated, reproducible containers
- **SQLAlchemy + psycopg** for the database connection
- **python-dotenv** for credentials management
- **Metabase** for the BI dashboard

---

## 📁 Data Source

Open data published by EPTC (Porto Alegre's traffic authority) through the city's open data portal:

- [**Acidentes**](https://dadosabertos.poa.br/dataset/acidentes-de-transito-acidentes) (accidents): one row per traffic accident
- [**Vítimas**](https://dadosabertos.poa.br/dataset/acidentes-de-transito-vitimas) (victims): one row per person involved in an accident with injuries or fatalities

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

**Validations**
- Row counts validated after loading (87,323 accidents and 37,857 victims)
- Null counts compared before and after every transformation, ensuring no valid data was silently lost
- Severity weights (`ups`) confirmed to contain only the expected values: 1 (property damage), 5 (injuries) and 13 (fatalities)
- `fx_et = 'NI'` matches exactly the 5,484 victims with missing age
- **Referential integrity:** every victim references an existing accident (0 orphan records)

**Unit tests**
- 8 Pytest tests cover every transformation function, protecting against regressions such as date formats silently turning valid values into nulls

**Issues found in the source data**
- **4 accidents with future dates** (up to 2029), beyond the data extraction date. They are excluded from the dashboard and will be handled in the dbt layer
- An unusually high number of accidents at **midnight**, suggesting unknown times may be recorded as `00:00`

---

## 📂 Project Structure

```
traffic-accidents-poa/
├── data/raw/              # Source CSV files
├── docs/images/           # Dashboard screenshot
├── src/
│   ├── extract.py         # Reads the CSV files
│   ├── transform.py       # Cleans and normalizes both datasets
│   ├── load.py            # Loads DataFrames into PostgreSQL
│   └── main.py            # Orchestrates the full pipeline
├── tests/
│   └── test_transform.py  # Unit tests for the transformations
├── docker-compose.yml     # PostgreSQL and Metabase services
├── .env.example           # Template for database credentials
├── pytest.ini
└── requirements.txt
```

---

## ⚙️ How to Run

**Prerequisites:** Docker, Docker Compose and Python 3.12+

1. **Clone the repository**

```bash
   git clone https://github.com/junioorst/traffic-accidents-poa.git
   cd traffic-accidents-poa
```

2. **Configure the credentials**

```bash
   cp .env.example .env
```

   Fill in `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` in the `.env` file.

3. **Start PostgreSQL and Metabase**

```bash
   docker compose up -d
```

4. **Create the virtual environment and install dependencies**

```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
```

5. **Run the pipeline**

```bash
   python src/main.py
```

6. **Run the tests**

```bash
   pytest
```

7. **Open the dashboard**

   Go to `http://localhost:3000`, create an admin account and add a PostgreSQL database with host **`postgres`** (the Docker Compose service name), port `5432` and the credentials from your `.env` file.

---

## 🔍 Example Query

Victims by vehicle type and accident region:

```sql
SELECT a.regiao, v.tipo_veic, COUNT(*) AS victims
FROM vitimas v
JOIN acidentes a ON v.idacidente = a.idacidente
GROUP BY a.regiao, v.tipo_veic
ORDER BY victims DESC;
```

---

## 🗺️ Roadmap

- [x] Extraction, transformation and loading with Pandas
- [x] PostgreSQL with Docker Compose
- [x] Normalized accidents and victims model
- [x] Unit tests for transformations with Pytest
- [ ] BI dashboard with Metabase
- [ ] dbt models (staging and marts) with data tests (uniqueness, not null, referential integrity)
- [ ] Orchestration with Apache Airflow

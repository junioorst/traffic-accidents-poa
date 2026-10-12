# Traffic Accidents POA 🚦

An end-to-end data pipeline that extracts, transforms and loads public traffic accident data from Porto Alegre (Brazil) into a containerized PostgreSQL database, modeling accidents and victims as two related tables.

This project is being built incrementally as a modern data engineering portfolio, evolving towards dbt, a BI dashboard and Apache Airflow orchestration.

---

## 🏗️ Architecture

```
 data/raw/*.csv
      │
      ▼
 ┌──────────┐    ┌────────────┐    ┌──────────┐
 │ extract  │───▶│ transform  │───▶│   load   │
 │ (pandas) │    │ (pandas)   │    │(SQLAlchemy)
 └──────────┘    └────────────┘    └────┬─────┘
                                        │ port 5432
                                        ▼
                        ┌───────────────────────────────┐
                        │ PostgreSQL 16 (Docker Compose) │
                        │   ├── acidentes  (87,323 rows) │
                        │   └── vitimas    (37,857 rows) │
                        └───────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Python 3.12**
- **Pandas** for extraction and transformation
- **PostgreSQL 16** as the database
- **Docker & Docker Compose** to run PostgreSQL in an isolated, reproducible container
- **SQLAlchemy + psycopg** for the database connection
- **python-dotenv** for credentials management

---

## 📊 Data Source

Open data published by EPTC (Porto Alegre's traffic authority) through the city's open data portal:

- **Acidentes** (accidents): one row per traffic accident
- **Vítimas** (victims): one row per person involved in an accident with injuries or fatalities

Official data dictionaries are available in the `docs/` folder.

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

## ✅ Data Quality Checks

- Row counts validated after loading (87,323 accidents and 37,857 victims)
- Null counts compared before and after every transformation, ensuring no valid data was silently lost
- Severity weights (`ups`) confirmed to contain only the expected values: 1 (property damage), 5 (injuries) and 13 (fatalities)
- `fx_et = 'NI'` matches exactly the 5,484 victims with missing age
- **Referential integrity:** every victim references an existing accident (0 orphan records)

---

## 💡 Highlights

- **About 60% of all victims were on motorcycles** (22,694 of 37,857)
- Of all accidents, 63.3% caused only property damage, 36.2% caused injuries and 0.5% were fatal

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

3. **Start the database**

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
- [ ] Primary and foreign key constraints
- [ ] dbt models (staging and marts) with data tests
- [ ] BI dashboard (Metabase)
- [ ] Orchestration with Apache Airflow
- [ ] Automated tests with Pytest
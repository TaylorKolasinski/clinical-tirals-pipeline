# Clinical Trials Data Pipeline

This repository implements a data pipeline to ingest, transform, embed, and load clinical trial data into a PostgreSQL database with support for semantic search using vector embeddings. The pipeline is modular, efficient, and designed to handle large datasets.

---

## How to Run the Pipeline

### Prerequisites

1. **Install Docker and Docker Compose**:
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)
   - [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

### Steps to Run

1. **Build and Start Services**:
   ```bash
   docker-compose up --build
   ```

2. **Trigger the Pipeline Manually**:
   ```bash
   docker-compose run app python /app/main.py
   ```

3. **Run Tests**:
   ```bash
   docker-compose run tests
   ```

4. **View Cron Logs**:
   ```bash
   docker exec -it clinical_trials_app tail -f /var/log/cron.log
   ```

5. **Verify Cron Job Scheduling**:
   ```bash
   docker exec -it clinical_trials_app crontab -l
   ```
   - Ensure the cron job entry includes the correct schedule (e.g., `0 3 * * * python /app/main.py >> /var/log/cron.log 2>&1`).

---

## Project Structure

- **`app/`**: Core pipeline logic.
  - `main.py`: Orchestrates ingestion, transformation, embedding, and loading.
  - `ingest.py`: Handles data ingestion.
  - `transform.py`: Transforms raw data.
  - `embeddings.py`: Generates embeddings using `sentence-transformers`.
  - `load.py`: Loads data into PostgreSQL.
  - `search.py`: Implements semantic search.
- **`db/init/`**: Database schema and initialization scripts.
- **`cronjob`**: Configures the cron job to run daily at 3 AM.
- **`Dockerfile`**: Defines the Docker image.
- **`docker-compose.yml`**: Sets up multi-container services.
- **`tests/`**: Unit tests.

---

## How It Works

1. **Ingestion**:
   - Fetches clinical trial data via API.
2. **Transformation**:
   - Cleans and structures raw data.
3. **Embedding**:
   - Generates semantic embeddings for search.
4. **Loading**:
   - Stores data and embeddings in PostgreSQL with `pgvector`.
5. **Search**:
   - Enables similarity-based searches using embeddings.

---

## Testing the Pipeline

1. **Access PostgreSQL**:
   ```bash
   docker exec -it clinical_trials_db psql -U user -d clinical_trial
   ```

2. **Verify Tables**:
   ```sql
   SELECT * FROM clinical_trials LIMIT 5;
   SELECT * FROM clinical_trial_embeddings LIMIT 5;
   ```

3. **Run Semantic Search**:
   ```bash
   docker-compose run app python -c "from search import search_trials; print(search_trials(query='NSCLC immunotherapy', top_k=5))"
   ```

---

## Airflow Integration Example

To schedule this pipeline in Airflow, create a DAG like the following:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'clinical_trials_pipeline',
    default_args=default_args,
    description='A DAG to run the clinical trials data pipeline',
    schedule_interval='0 3 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

run_pipeline = BashOperator(
    task_id='run_pipeline',
    bash_command='docker-compose run app python /app/main.py',
    dag=dag,
)
```

### Steps to Use This DAG
1. Save the above code as `clinical_trials_dag.py` in your Airflow `dags/` directory.
2. Start Airflow Scheduler and Webserver:
   ```bash
   airflow scheduler & airflow webserver
   ```
3. Confirm the DAG is listed in the Airflow UI and trigger it manually or wait for the schedule to execute.

---

## Future Enhancements

- Add CI/CD pipelines for automated testing.
- GPU acceleration for large-scale embedding generation.
- Monitoring and alerting for pipeline health.
- Web interface for data interaction and searches.

---

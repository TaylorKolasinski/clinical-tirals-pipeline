import logging
import time
from ingest import ingest_data
from transform import transform_data
from embeddings import generate_embeddings
from load import load_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def measure_execution_time(func):
    """Decorator to measure execution time of pipeline stages."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logging.info(f"{func.__name__} completed in {elapsed_time:.2f} seconds.")
        return result
    return wrapper

@measure_execution_time
def execute_stage(stage_func, stage_name, *args, **kwargs):
    """Execute a pipeline stage with error handling."""
    try:
        logging.info(f"Starting stage: {stage_name}")
        return stage_func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Stage '{stage_name}' failed: {e}", exc_info=True)
        raise

def main():
    logging.info("Pipeline execution started.")
    try:
        # Step 1: Ingest data
        raw_data = execute_stage(ingest_data, "Data Ingestion")

        # Step 2: Transform data
        transformed_data = execute_stage(transform_data, "Data Transformation", raw_data)

        # Step 3: Generate embeddings
        enriched_data = execute_stage(generate_embeddings, "Generate Embeddings", transformed_data)

        # Step 4: Load data
        execute_stage(load_data, "Data Loading", enriched_data)

        logging.info("Pipeline execution completed successfully.")
    except Exception as e:
        logging.error(f"Pipeline execution failed: {e}", exc_info=True)


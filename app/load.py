import logging
import psycopg2
import os
from psycopg2.extras import execute_batch
import numpy as np
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BATCH_SIZE = 500

def load_data(trials):
    """
    Load clinical trial data and embeddings into PostgreSQL.

    Args:
        trials (list): List of trial dictionaries containing data and embeddings.
    """
    logging.info("Starting data load into PostgreSQL.")
    try:
        # Connect to the database
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = conn.cursor()

        # Load clinical trials data in batches
        for i in range(0, len(trials), BATCH_SIZE):
            batch = trials[i:i + BATCH_SIZE]

            # Prepare data for clinical_trials table
            trials_data = []
            embeddings_data = []

            for trial in batch:
                # Handle numpy.ndarray conversion to JSON or list
                title_embedding = (
                    json.dumps(trial["title_embedding"].tolist())
                    if isinstance(trial.get("title_embedding"), np.ndarray)
                    else None
                )

                disease_embedding = (
                    json.dumps(trial["disease_embedding"].tolist())
                    if isinstance(trial.get("disease_embedding"), np.ndarray)
                    else None
                )

                intervention_embedding = (
                    json.dumps(trial["intervention_embedding"].tolist())
                    if isinstance(trial.get("intervention_embedding"), np.ndarray)
                    else None
                )

                trials_data.append(
                    (
                        trial["nct_number"],
                        trial["title"],
                        trial.get("disease", "N/A"),
                        trial.get("phase", "N/A"),
                        trial.get("intervention", "N/A"),
                        trial.get("status", "N/A"),
                        trial.get("last_update"),
                    )
                )

                embeddings_data.append(
                    (
                        trial["nct_number"],
                        title_embedding,
                        disease_embedding,
                        intervention_embedding,
                    )
                )

            execute_batch(cursor, """
                INSERT INTO clinical_trials (nct_number, title, disease, phase, intervention, status, last_update)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (nct_number) DO UPDATE SET
                title = EXCLUDED.title, disease = EXCLUDED.disease, phase = EXCLUDED.phase,
                intervention = EXCLUDED.intervention, status = EXCLUDED.status, last_update = EXCLUDED.last_update;
            """, trials_data)

            execute_batch(cursor, """
                INSERT INTO clinical_trial_embeddings (trial_id, title_embedding, disease_embedding, intervention_embedding)
                VALUES ((SELECT trial_id FROM clinical_trials WHERE nct_number = %s), %s, %s, %s)
                ON CONFLICT (trial_id) DO NOTHING;
            """, embeddings_data)

            conn.commit()
            logging.info(f"Batch {i // BATCH_SIZE + 1} loaded successfully.")

        # Close the connection
        cursor.close()
        conn.close()
        logging.info("Data load completed successfully.")

    except psycopg2.Error as db_error:
        logging.error(f"Database error occurred: {db_error}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Unexpected error during data load: {e}", exc_info=True)
        raise

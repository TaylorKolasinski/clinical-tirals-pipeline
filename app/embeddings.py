from sentence_transformers import SentenceTransformer
import logging
from time import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load the SentenceTransformer model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2', use_auth_token=False)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}", exc_info=True)
    raise

def generate_embeddings(trials, batch_size=256):
    """
    Generate embeddings for the trials using batching for efficiency.
    Args:
        trials (list): List of trial dictionaries.
        batch_size (int): Number of items to process in a single batch.
    Returns:
        list: List of trial dictionaries enriched with embeddings.
    """
    logging.info("Starting embedding generation for trials.")
    try:
        if not isinstance(trials, list):
            raise ValueError("Input trials must be a list of dictionaries.")

        # Prepare batched input texts
        titles = [trial.get('title', "") for trial in trials]
        diseases = [trial.get('disease', "") for trial in trials]
        interventions = [trial.get('intervention', "") for trial in trials]

        # Initialize lists to store embeddings
        title_embeddings = []
        disease_embeddings = []
        intervention_embeddings = []

        start_time = time()

        # Generate embeddings in batches
        for i in range(0, len(trials), batch_size):
            logging.info(f"Processing batch {i // batch_size + 1}/{-(-len(trials) // batch_size)}")

            title_batch = titles[i:i + batch_size]
            disease_batch = diseases[i:i + batch_size]
            intervention_batch = interventions[i:i + batch_size]

            title_embeddings.extend(model.encode(title_batch, batch_size=batch_size, convert_to_tensor=False))
            disease_embeddings.extend(model.encode(disease_batch, batch_size=batch_size, convert_to_tensor=False))
            intervention_embeddings.extend(model.encode(intervention_batch, batch_size=batch_size, convert_to_tensor=False))

        # Assign embeddings back to trials
        for trial, title_emb, disease_emb, intervention_emb in zip(trials, title_embeddings, disease_embeddings, intervention_embeddings):
            trial['title_embedding'] = title_emb
            trial['disease_embedding'] = disease_emb
            trial['intervention_embedding'] = intervention_emb

        elapsed_time = time() - start_time
        logging.info(f"Generated embeddings for {len(trials)} trials in {elapsed_time:.2f} seconds.")
    except Exception as e:
        logging.error(f"Error generating embeddings: {e}", exc_info=True)
        raise

    return trials

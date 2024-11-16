import logging
from sentence_transformers import SentenceTransformer, util
import psycopg2
import os
import numpy as np
import ast
import torch

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load the Sentence Transformer model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2', use_auth_token=False)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}", exc_info=True)
    raise

def search_trials(query, top_k=5):
    """
    Search for clinical trials based on a user query.

    Args:
        query (str): The search query.
        top_k (int): Number of top results to return.

    Returns:
        list: Top-k clinical trials matching the query.
    """
    logging.info(f"Searching for clinical trials with query: {query}")
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = conn.cursor()

        # Generate embeddings for the query
        query_embedding = model.encode(query, convert_to_tensor=True).to(dtype=torch.float32)

        # Fetch all trial data and their embeddings from the database
        cursor.execute("""
            SELECT ct.trial_id, ct.title, ct.disease, ct.intervention, 
                   cte.title_embedding, cte.disease_embedding, cte.intervention_embedding
            FROM clinical_trials AS ct
            INNER JOIN clinical_trial_embeddings AS cte
            ON ct.trial_id = cte.trial_id
        """)
        trials = cursor.fetchall()

        if not trials:
            logging.info("No trials found in the database.")
            return []

        # Prepare the list of trials and their embeddings
        trial_data = []
        trial_embeddings = []

        for trial in trials:
            trial_id, title, disease, intervention, title_emb, disease_emb, intervention_emb = trial
            trial_data.append((trial_id, title, disease, intervention))
            trial_embeddings.append({
                "title_emb": torch.tensor(ast.literal_eval(title_emb), dtype=torch.float32),
                "disease_emb": torch.tensor(ast.literal_eval(disease_emb), dtype=torch.float32),
                "intervention_emb": torch.tensor(ast.literal_eval(intervention_emb), dtype=torch.float32),
            })

        # Calculate similarity scores
        results = []
        for i, embeddings in enumerate(trial_embeddings):
            title_score = util.cos_sim(query_embedding, embeddings["title_emb"]).item()
            disease_score = util.cos_sim(query_embedding, embeddings["disease_emb"]).item()
            intervention_score = util.cos_sim(query_embedding, embeddings["intervention_emb"]).item()
            total_score = title_score + disease_score + intervention_score
            results.append((trial_data[i], total_score))

        # Sort results by similarity score in descending order and get the top_k results
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)[:top_k]

        if not sorted_results:
            logging.info("No relevant trials found.")
            return []

        # Log the results
        logging.info(f"Found {len(sorted_results)} relevant trials.")
        for trial, score in sorted_results:
            logging.info(f"Trial ID: {trial[0]}, Title: {trial[1]}, Score: {score:.4f}")

        cursor.close()
        conn.close()

        return [trial for trial, score in sorted_results]

    except psycopg2.Error as db_error:
        logging.error(f"Database error occurred: {db_error}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Unexpected error during search: {e}", exc_info=True)
        raise

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create clinical_trials table
CREATE TABLE clinical_trials (
    trial_id SERIAL PRIMARY KEY,
    nct_number VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    disease TEXT DEFAULT 'Unknown',
    phase TEXT DEFAULT 'N/A',
    intervention TEXT,
    status TEXT DEFAULT 'N/A',
    last_update DATE
);

-- Create clinical_trial_embeddings table
CREATE TABLE clinical_trial_embeddings (
    trial_id INT PRIMARY KEY REFERENCES clinical_trials(trial_id) ON DELETE CASCADE,
    title_embedding VECTOR(384),
    disease_embedding VECTOR(384),
    intervention_embedding VECTOR(384)
);

-- Indexes for optimization
CREATE INDEX idx_disease ON clinical_trials (disease);
CREATE INDEX idx_intervention ON clinical_trials (intervention);
CREATE INDEX idx_status ON clinical_trials (status);
CREATE INDEX idx_last_update ON clinical_trials (last_update);
CREATE INDEX idx_title_fulltext ON clinical_trials USING gin(to_tsvector('english', title));

-- Indexes for vector similarity search
CREATE INDEX idx_title_embedding ON clinical_trial_embeddings USING ivfflat (title_embedding) WITH (lists = 100);
CREATE INDEX idx_disease_embedding ON clinical_trial_embeddings USING ivfflat (disease_embedding) WITH (lists = 100);
CREATE INDEX idx_intervention_embedding ON clinical_trial_embeddings USING ivfflat (intervention_embedding) WITH (lists = 100);

# Base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    libpq-dev python3-dev build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Set PYTHONPATH to allow imports from /app
ENV PYTHONPATH=/app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Pre-download the SentenceTransformer model to cache it (uncomment if needed)
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the application files
COPY . .

# Configure cron job
COPY cronjob /etc/cron.d/clinical_trials_cron
RUN chmod 0644 /etc/cron.d/clinical_trials_cron && crontab /etc/cron.d/clinical_trials_cron

# Ensure log directory and file exist
RUN mkdir -p /var/log && touch /var/log/cron.log

# Default command: Start cron in the foreground and log output
CMD ["cron", "-f"]

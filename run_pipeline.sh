#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# --- 1. Argument Check ---
if [ "$#" -ne 2 ]; then
    echo "Usage: ./run_pipeline.sh <data_version> <gcp_key_path>"
    echo "Example: ./run_pipeline.sh v0 /home/jupyter/my-key.json"
    exit 1
fi

DATA_VERSION=$1
GCP_KEY_PATH=$2

# --- 2. Setup Environment ---
echo "--- Setting up environment ---"
source venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=$GCP_KEY_PATH
echo "Venv activated. Python is at: $(which python)"

# --- 3. Set Data Version ---
echo "--- Setting data version to $DATA_VERSION in params.yaml ---"
sed -i "s/data_version:.*/data_version: $DATA_VERSION/" params.yaml

# --- 4. Run DVC Pipeline ---
echo "--- Running DVC pipeline ---"
# This will now run 'process_data', 'feast_apply', and 'train'
dvc repro

# --- 5. Commit and Tag ---
echo "--- Committing results and tagging ---"
git add .
git commit -m "chore: Completed pipeline run for $DATA_VERSION"

TAG_NAME="run-$DATA_VERSION"
git tag -a $TAG_NAME -m "Completed pipeline run for data version $DATA_VERSION"

# --- 6. Push to DVC and Git ---
echo "--- Pushing data and code ---"
dvc push
git push origin main --tags

echo "--- Pipeline run $DATA_VERSION complete! ---"

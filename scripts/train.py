import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os
import yaml # Import yaml

# --- 1. Load Parameters ---
with open("params.yaml", 'r') as f:
    params = yaml.safe_load(f)

# Use paths and params from file
PROCESSED_DATA_PATH = params['train']['processed_path']
MODEL_PATH = params['train']['model_path']
TEST_SIZE = params['train']['test_size']
RANDOM_STATE = params['train']['random_state']
N_ESTIMATORS = params['train']['n_estimators']
MAX_DEPTH = params['train']['max_depth']

print("--- Starting Basic Model Training ---")
print(f"Loading data from {PROCESSED_DATA_PATH}...")
df = pd.read_parquet(PROCESSED_DATA_PATH)

features = ["rolling_avg_10", "volume_sum_10"]
target = "target"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)
print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")

model = RandomForestClassifier(n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH, random_state=RANDOM_STATE)
model.fit(X_train, y_train)

preds = model.predict(X_test)
accuracy = accuracy_score(y_test, preds)

print(f"Model Accuracy: {accuracy:.4f}")

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")

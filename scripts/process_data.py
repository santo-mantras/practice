import pandas as pd
import numpy as np
import os
import glob
import sys
import yaml # Import yaml

# --- 1. Load Parameters ---
with open("params.yaml", 'r') as f:
    params = yaml.safe_load(f)

# Use paths from params file
RAW_DATA_PATH = params['process_data']['raw_path']
PROCESSED_DATA_PATH = params['process_data']['processed_path']
DATA_VERSION = params['process_data']['data_version']

def load_data(version_path):
    print(f"Loading data from: {version_path}")
    paths = glob.glob(f"{version_path}/*.csv")
    all_dfs = []
    for path in paths:
        stock_id = os.path.basename(path).split("_")[0]
        df = pd.read_csv(path)
        df['stock_id'] = stock_id
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)

def process_data(df):
    print("Processing data...")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['stock_id', 'timestamp'])
    
    value_cols = ['open', 'high', 'low', 'close', 'volume']
    
    print("Filling time gaps...")
    df = df.set_index('timestamp').groupby('stock_id')[value_cols].resample('1min').ffill()
    df = df.reset_index()
    
    print("Creating feature: rolling_avg_10")
    df['rolling_avg_10'] = df.groupby('stock_id')['close'].rolling(10, min_periods=1).mean().reset_index(0, drop=True)
    
    print("Creating feature: volume_sum_10")
    df['volume_sum_10'] = df.groupby('stock_id')['volume'].rolling(10, min_periods=1).sum().reset_index(0, drop=True)
    
    print("Creating target variable...")
    df['target_price_5min'] = df.groupby('stock_id')['close'].shift(-5)
    df['target'] = (df['target_price_5min'] > df['close']).astype(int)
    
    df = df.dropna(subset=['target', 'rolling_avg_10', 'volume_sum_10', 'target_price_5min'])
    df = df.rename(columns={'timestamp': 'event_timestamp'})
    
    final_cols = ['event_timestamp', 'stock_id', 'rolling_avg_10', 'volume_sum_10', 'target']
    df_final = df[final_cols].copy()
    
    print(f"Processed data shape: {df_final.shape}")
    return df_final

if __name__ == "__main__":
    print(f"--- Starting Data Processing (Version: {DATA_VERSION}) ---")
    
    raw_df_v0 = load_data(os.path.join(RAW_DATA_PATH, 'v0'))
    
    if DATA_VERSION == 'v1':
        print("Appending v1 data...")
        raw_df_v1 = load_data(os.path.join(RAW_DATA_PATH, 'v1'))
        raw_df = pd.concat([raw_df_v0, raw_df_v1], ignore_index=True)
    else:
        raw_df = raw_df_v0

    processed_df = process_data(raw_df)
    
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    processed_df.to_parquet(PROCESSED_DATA_PATH, index=False)
    # The print statement now uses the variable
    print(f"Processing complete. Output saved to {PROCESSED_DATA_PATH}")

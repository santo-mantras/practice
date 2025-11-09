import pandas as pd
import numpy as np
import os

def generate_stock_data(ticker, start_date, days):
    """Generates synthetic minute-level stock data."""
    print(f"Generating data for {ticker}...")
    daterange = pd.date_range(start_date, periods=days * 390, freq='1min')
    
    # Create timestamps for market hours only (9:30 - 16:00)
    market_times = daterange.time
    market_open = (market_times >= pd.to_datetime('09:30').time()) & (market_times <= pd.to_datetime('16:00').time())
    daterange = daterange[market_open]

    n = len(daterange)
    if n == 0:
        print(f"No market-hour data generated for {ticker}.")
        return None
        
    data = pd.DataFrame(index=daterange)
    data['timestamp'] = data.index
    
    price = np.random.randint(100, 2000)
    volume = np.random.randint(1000, 5000)
    prices = [price]
    volumes = [volume]
    
    for _ in range(1, n):
        price += np.random.normal(0, 0.1)
        volume = max(100, volume + np.random.randint(-100, 100))
        prices.append(price)
        volumes.append(volume)
        
    data['close'] = prices
    data['open'] = data['close'].shift(1).fillna(data['close'])
    data['high'] = data[['open', 'close']].max(axis=1) + np.random.rand(n) * 0.1
    data['low'] = data[['open', 'close']].min(axis=1) - np.random.rand(n) * 0.1
    data['volume'] = volumes
    
    data = data.reset_index(drop=True)[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    return data

# --- Main execution ---
data_map = {
    'v0': ['AARTIIND', 'ABCAPITAL'],
    'v1': ['ABFRL', 'ADANIENT', 'ADANIGAS']
}
start_date = '2020-01-01'
days_per_stock = 30 # Generate 30 days of data

for version, tickers in data_map.items():
    version_path = f"data/raw/{version}"
    os.makedirs(version_path, exist_ok=True)
    
    for ticker in tickers:
        df = generate_stock_data(ticker, start_date, days_per_stock)
        if df is not None:
            file_path = os.path.join(version_path, f"{ticker}_EQNSENSE_MINUTE.csv")
            df.to_csv(file_path, index=False)
            print(f"Saved {file_path}")
            
print("All sample data generated.")

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ml_service import LightGBMService
from app.services.data_fetcher import MarketDataFetcher
import pandas as pd

def test_lgbm():
    print("Testing LightGBM Service Integration...")
    
    service = LightGBMService()
    symbol = 'BANKNIFTY'
    
    # 1. Test data fetching and feature preparation
    fetcher = MarketDataFetcher()
    data = fetcher.fetch_data(symbol, period='6mo')
    if data is None or data.empty:
        print("Failed to fetch data for testing.")
        return
        
    print(f"Fetched {len(data)} rows for {symbol}")
    
    # 2. Test model training
    print("Testing model training...")
    success = service.train_model(symbol, period='1y')
    if success:
        print("Model trained and saved successfully.")
    else:
        print("Model training failed.")
        return
        
    # 3. Test prediction
    print("Testing prediction...")
    prob = service.predict(symbol, data)
    if prob is not None:
        print(f"Prediction probability for {symbol}: {prob:.4f}")
    else:
        print("Prediction failed.")

if __name__ == "__main__":
    test_lgbm()

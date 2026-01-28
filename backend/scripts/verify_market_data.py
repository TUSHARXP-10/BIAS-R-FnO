
import sys
import os
import pandas as pd

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.data_fetcher import MarketDataFetcher
from app.services.technical_analysis import TechnicalAnalyzer

def test_market_data():
    print("Testing Market Data Fetching for SENSEX...")
    fetcher = MarketDataFetcher()
    try:
        # Fetch 5-day data with 5-minute interval? 
        # yfinance history supports interval='5m' for recent data
        ticker_symbol = fetcher.INDIAN_SYMBOLS['SENSEX']
        import yfinance as yf
        ticker = yf.Ticker(ticker_symbol)
        # Fetch 1 day of 5m data
        data = ticker.history(period='1d', interval='5m')
        
        if data.empty:
            print("No data received for SENSEX (5m). Market might be closed or API issue.")
            # Fallback to daily for testing logic
            data = ticker.history(period='1mo', interval='1d')
            print("Fetched Daily data instead.")
        
        print(f"Data shape: {data.shape}")
        print(data.tail())
        
        print("\nCalculating Indicators...")
        ta = TechnicalAnalyzer(data)
        ta.calculate_all_indicators() # This method updates internal dict, but returns nothing?
        # Wait, let's check TechnicalAnalyzer code again. 
        # It calculates indicators and stores them in a dictionary?
        # The method calculate_all_indicators returns nothing but populates a local dict 'indicators' 
        # inside the method but doesn't seem to store it in self?
        
        # Let's re-read TechnicalAnalyzer code carefully.
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_market_data()

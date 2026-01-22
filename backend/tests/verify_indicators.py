import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.data_fetcher import MarketDataFetcher
from app.services.technical_analysis import TechnicalAnalyzer
import pandas as pd

def verify():
    # Fetch Bank Nifty data
    fetcher = MarketDataFetcher()
    print("Fetching data for BANKNIFTY...")
    try:
        data = fetcher.fetch_data('BANKNIFTY', period='3mo')
        print(f"Fetched {len(data)} candles.")
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Calculate indicators
    analyzer = TechnicalAnalyzer(data)
    indicators = analyzer.calculate_all_indicators()
    signals = analyzer.get_signal()
    trend = analyzer.get_trend()

    # Print results
    print("="*50)
    print("BANK NIFTY TECHNICAL ANALYSIS CHECK")
    print("="*50)
    print(f"Date: {data.index[-1]}")
    print(f"Current Price: {indicators['current_price']}")
    print(f"Trend: {trend}")
    print(f"\nIndicators:")
    print(f"  RSI (14): {indicators['rsi']}")
    print(f"  MACD: {indicators['macd']}")
    print(f"  EMA 20: {indicators['ema_20']}")
    print(f"  EMA 50: {indicators['ema_50']}")
    print(f"  Bollinger Upper: {indicators['bb_upper']}")
    print(f"  Bollinger Lower: {indicators['bb_lower']}")
    print(f"\nSignals:")
    for signal in signals:
        print(f"  - {signal}")
    print("="*50)
    print("Please verify these values against TradingView or another source.")

if __name__ == "__main__":
    verify()

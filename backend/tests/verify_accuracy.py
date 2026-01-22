# backend/tests/verify_accuracy.py
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.data_fetcher import MarketDataFetcher
from app.services.technical_analysis import TechnicalAnalyzer
import talib
import numpy as np
import pandas as pd

fetcher = MarketDataFetcher()
# Use 1y period to ensure enough data for EMA 200 and stable MACD/RSI
data = fetcher.fetch_data('BANKNIFTY', period='1y')
analyzer = TechnicalAnalyzer(data)
indicators = analyzer.calculate_all_indicators()

print("="*60)
print("BANK NIFTY VERIFICATION (Compare with TradingView)")
print("="*60)
print(f"Latest data timestamp: {data.index[-1]}")
print(f"Latest close: {data['Close'].iloc[-1]}")
print(f"Current Price: {indicators['current_price']}")
print(f"RSI (14): {indicators['rsi']}")
print(f"MACD: {indicators['macd']}")
print(f"MACD Signal: {indicators['macd_signal']}")
print(f"EMA 20: {indicators['ema_20']}")
print(f"EMA 50: {indicators['ema_50']}")
print(f"EMA 200: {indicators['ema_200']}")
print(f"ATR: {indicators['atr']}")
print(f"ADX: {indicators['adx']}")
print("\nDebug arrays (last 5):")
close = data['Close'].values
macd, macd_signal, macd_hist = talib.MACD(close, 12, 26, 9)
rsi = talib.RSI(close, timeperiod=14)
np.set_printoptions(precision=2, suppress=True)
print(f"MACD last5: {macd[-5:]}")
print(f"Signal last5: {macd_signal[-5:]}")
print(f"Hist last5: {macd_hist[-5:]}")
print(f"RSI last5: {rsi[-5:]}")
ema12_pd = pd.Series(close).ewm(span=12, adjust=False).mean().values
ema26_pd = pd.Series(close).ewm(span=26, adjust=False).mean().values
macd_pd = ema12_pd - ema26_pd
signal_pd = pd.Series(macd_pd).ewm(span=9, adjust=False).mean().values
hist_pd = macd_pd - signal_pd
print("\nPandas EWM MACD check:")
print(f"MACD(pd) last1: {macd_pd[-1]:.2f}, Signal(pd) last1: {signal_pd[-1]:.2f}, Hist(pd) last1: {hist_pd[-1]:.2f}")
macd_log, macd_signal_log, macd_hist_log = talib.MACD(np.log(close), 12, 26, 9)
print("\nLog-price MACD check:")
print(f"MACD(log) last1: {macd_log[-1]:.4f}, Signal(log) last1: {macd_signal_log[-1]:.4f}, Hist(log) last1: {macd_hist_log[-1]:.4f}")
macd_pct_last = ((ema12_pd[-1] - ema26_pd[-1]) / ema26_pd[-1]) * 100
signal_pct_last = pd.Series(((ema12_pd - ema26_pd) / ema26_pd) * 100).ewm(span=9, adjust=False).mean().values[-1]
hist_pct_last = macd_pct_last - signal_pct_last
print("\nPercent MACD check:")
print(f"MACD(%) last1: {macd_pct_last:.4f}, Signal(%) last1: {signal_pct_last:.4f}, Hist(%) last1: {hist_pct_last:.4f}")
print("="*60)
print("⚠️  MANUALLY VERIFY THESE AGAINST TRADINGVIEW")
print("="*60)

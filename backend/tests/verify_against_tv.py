from app.services.tv_fetcher import TradingViewFetcher
from app.services.technical_analysis import TechnicalAnalyzer
import talib
import numpy as np
import pandas as pd

def verify_tv():
    tv = TradingViewFetcher()
    print("Fetching TradingView data for NSE:BANKNIFTY (1D)...")
    try:
        data = tv.fetch_data('NSE:BANKNIFTY', interval='1D', n_bars=300)
        print(f"Fetched {len(data)} candles from TradingView.")
        print(f"Latest timestamp: {data.index[-1]}")
        print(f"Latest close: {data['Close'].iloc[-1]}")
        analyzer = TechnicalAnalyzer(data)
        indicators = analyzer.calculate_all_indicators()
        print("="*60)
        print("BANK NIFTY VERIFICATION (TradingView candles)")
        print("="*60)
        print(f"Current Price: {indicators['current_price']}")
        print(f"RSI (14): {indicators['rsi']}")
        print(f"MACD(abs): {indicators['macd']} | Signal: {indicators['macd_signal']} | Hist: {indicators['macd_histogram']}")
        print(f"MACD(%)  : {indicators.get('macd_pct')} | Signal: {indicators.get('macd_pct_signal')} | Hist: {indicators.get('macd_pct_histogram')}")
        print(f"MACD(log): {indicators.get('macd_log')} | Signal: {indicators.get('macd_log_signal')} | Hist: {indicators.get('macd_log_histogram')}")
        print(f"EMA 20: {indicators['ema_20']} | EMA 50: {indicators['ema_50']} | EMA 200: {indicators['ema_200']}")
        print("="*60)
        print("Compare these with TradingView indicator readouts (same timeframe and symbol).")
    except Exception as e:
        print(f"Could not fetch TradingView candles: {e}")
        print("Falling back to TradingView indicator API (tradingview_ta).")
        tv_ind = tv.fetch_indicators(symbol='BANKNIFTY', exchange='NSE', interval='1D')
        print("="*60)
        print("BANK NIFTY VERIFICATION (TradingView indicators)")
        print("="*60)
        print(f"Current Price: {tv_ind.get('current_price')}")
        print(f"RSI (14): {tv_ind.get('rsi')}")
        print(f"MACD(abs): {tv_ind.get('macd')} | Signal: {tv_ind.get('macd_signal')} | Hist: {tv_ind.get('macd_histogram')}")
        print(f"EMA 20: {tv_ind.get('ema_20')} | EMA 50: {tv_ind.get('ema_50')} | EMA 200: {tv_ind.get('ema_200')}")
        print("="*60)
        print("Compare these with Yahoo-derived indicators to assess source differences.")

if __name__ == "__main__":
    verify_tv()

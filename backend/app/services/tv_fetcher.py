try:
    from tvDatafeed import TvDatafeed, Interval
except ImportError:
    TvDatafeed = None
    Interval = None
import pandas as pd

class TradingViewFetcher:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.client = None
        if TvDatafeed is not None:
            try:
                self.client = TvDatafeed(username=self.username, password=self.password)
            except Exception:
                self.client = TvDatafeed()

    def fetch_data(self, symbol='NSE:BANKNIFTY', interval='1D', n_bars=300):
        if TvDatafeed is None:
            raise RuntimeError("tvDatafeed not installed. Please install with `pip install tvdatafeed`.")
        if self.client is None:
            raise RuntimeError("TradingView client not initialized.")
        tv_interval = Interval.in_1_day if interval == '1D' else Interval.in_1_hour
        data = self.client.get_hist(symbol=symbol, interval=tv_interval, n_bars=n_bars)
        if data is None or data.empty:
            raise ValueError(f"No TradingView data for {symbol}")
        data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
        return data

    def fetch_indicators(self, symbol='BANKNIFTY', exchange='NSE', interval='1D'):
        try:
            from tradingview_ta import TA_Handler, Interval
        except Exception:
            raise RuntimeError("tradingview_ta not installed. Install with `pip install tradingview_ta`.")
        tv_interval = Interval.INTERVAL_1_DAY if interval == '1D' else Interval.INTERVAL_1_HOUR
        handler = TA_Handler(
            symbol=symbol,
            screener="india",
            exchange=exchange,
            interval=tv_interval
        )
        analysis = handler.get_analysis()
        ind = analysis.indicators
        return {
            'current_price': ind.get('close'),
            'rsi': ind.get('RSI'),
            'macd': ind.get('MACD.macd'),
            'macd_signal': ind.get('MACD.signal'),
            'macd_histogram': ind.get('MACD.hist'),
            'ema_20': ind.get('EMA20'),
            'ema_50': ind.get('EMA50'),
            'ema_200': ind.get('EMA200')
        }

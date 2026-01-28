import yfinance as yf
from datetime import datetime, timedelta

class MarketDataFetcher:
    
    INDIAN_SYMBOLS = {
        'BANKNIFTY': '^NSEBANK',
        'NIFTY': '^NSEI',
        'SENSEX': '^BSESN',
        'NIFTY50': '^NSEI',
        'INDIAVIX': '^INDIAVIX'
    }

    GLOBAL_SYMBOLS = {
        'S&P 500': '^GSPC',
        'NASDAQ': '^IXIC',
        'NIKKEI': '^N225',
        'HANG SENG': '^HSI'
    }
    
    def fetch_data(self, symbol, period='3mo'):
        """
        Fetch market data from Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., 'BANKNIFTY', '^NSEBANK', 'RELIANCE.NS')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y')
        
        Returns:
            pandas DataFrame with OHLCV data
        """
        # Convert Indian index shortcuts to Yahoo Finance symbols
        ticker_symbol = self.INDIAN_SYMBOLS.get(symbol.upper(), symbol)
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
            
            return data
        
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")
    
    def get_latest_price(self, symbol):
        """Get latest price for a symbol"""
        data = self.fetch_data(symbol, period='1d')
        return data['Close'].iloc[-1]

    def get_market_summary(self):
        """
        Fetch summary of global and domestic indices.
        Returns a dictionary with symbol, price, and percent change.
        """
        summary = {}
        all_symbols = {**self.INDIAN_SYMBOLS, **self.GLOBAL_SYMBOLS}
        
        for name, symbol in all_symbols.items():
            try:
                # Fetch 5d to ensure we have previous close even after weekends/holidays
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    current_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_close
                    change = current_close - prev_close
                    change_pct = (change / prev_close) * 100
                    
                    summary[name] = {
                        "current": current_close,
                        "change": change,
                        "change_pct": change_pct
                    }
                else:
                    summary[name] = None
            except Exception as e:
                print(f"Error fetching summary for {name}: {e}")
                summary[name] = None
                
        return summary

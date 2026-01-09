import yfinance as yf
from datetime import datetime, timedelta

class MarketDataFetcher:
    
    INDIAN_SYMBOLS = {
        'BANKNIFTY': '^NSEBANK',
        'NIFTY': '^NSEI',
        'SENSEX': '^BSESN',
        'NIFTY50': '^NSEI'
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

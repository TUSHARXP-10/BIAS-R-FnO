import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import os
import talib
import numpy as np

class ChartGenerator:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), 'charts')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_chart(self, symbol, data, indicators=None, support_resistance=None):
        """
        Create candlestick chart with indicators
        data: DataFrame with OHLCV
        indicators: dict with pre-calculated indicators (optional)
        support_resistance: dict with support/resistance levels (optional)
        """
        # Ensure data is sorted
        data = data.sort_index()
        
        # Calculate indicators if not provided
        if not indicators:
            indicators = {}
            indicators['bb_upper'], indicators['bb_middle'], indicators['bb_lower'] = talib.BBANDS(data['Close'], timeperiod=20)
        
        # Setup plot
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), 
                                             gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # 1. Candlestick Chart (Price Action)
        # -----------------------------------
        
        # Prepare data for plotting
        dates = mdates.date2num(data.index)
        opens = data['Open'].values
        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values
        
        # Draw candlesticks
        width = 0.6
        for i in range(len(dates)):
            date = dates[i]
            open_p = opens[i]
            close_p = closes[i]
            high_p = highs[i]
            low_p = lows[i]
            
            color = 'green' if close_p >= open_p else 'red'
            
            # High-Low line
            ax1.plot([date, date], [low_p, high_p], color=color, linewidth=1)
            
            # Open-Close rectangle
            rect_height = abs(close_p - open_p)
            rect_bottom = min(open_p, close_p)
            # If open == close (doji), make it visible
            if rect_height == 0:
                rect_height = 0.01 * close_p 
            
            rect = Rectangle((date - width/2, rect_bottom), width, rect_height,
                             facecolor=color, edgecolor=color)
            ax1.add_patch(rect)

        # Plot Overlays (EMAs, BB)
        # Calculate EMAs locally to ensure alignment if not in indicators
        ema_20 = talib.EMA(data['Close'], timeperiod=20)
        ema_50 = talib.EMA(data['Close'], timeperiod=50)
        
        ax1.plot(dates, ema_20, label='EMA 20', color='blue', linewidth=1.5, alpha=0.8)
        ax1.plot(dates, ema_50, label='EMA 50', color='orange', linewidth=1.5, alpha=0.8)
        
        # Bollinger Bands
        if 'bb_upper' in indicators and 'bb_lower' in indicators:
            # Need to align with current data slice if indicators are pre-calculated
            # But here we assume data passed is the same length as indicators or we recalculate
            # Safer to recalculate for the chart to match the visual x-axis exactly
            bb_upper, _, bb_lower = talib.BBANDS(data['Close'], timeperiod=20)
            ax1.plot(dates, bb_upper, color='gray', linestyle='--', alpha=0.5, label='BB Upper')
            ax1.plot(dates, bb_lower, color='gray', linestyle='--', alpha=0.5, label='BB Lower')
            ax1.fill_between(dates, bb_upper, bb_lower, color='gray', alpha=0.1)

        ax1.set_title(f'{symbol} - Price Action & Technicals', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis_date()
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # 2. RSI Subplot
        # --------------
        rsi = talib.RSI(data['Close'], timeperiod=14)
        ax2.plot(dates, rsi, color='purple', linewidth=1.5)
        ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(30, color='green', linestyle='--', alpha=0.5)
        ax2.fill_between(dates, 30, 70, color='gray', alpha=0.1)
        ax2.set_ylabel('RSI (14)', fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis_date()
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # 3. MACD Subplot
        # ---------------
        macd, signal, hist = talib.MACD(data['Close'], 12, 26, 9)
        ax3.plot(dates, macd, label='MACD', color='blue', linewidth=1.5)
        ax3.plot(dates, signal, label='Signal', color='orange', linewidth=1.5)
        
        # Color histogram bars
        hist_safe = np.nan_to_num(hist, nan=0.0, posinf=0.0, neginf=0.0)
        hist_colors = ['green' if h >= 0 else 'red' for h in hist_safe]
        ax3.bar(dates, hist_safe, color=hist_colors, alpha=0.5, width=width)
        
        ax3.axhline(0, color='black', linewidth=0.5)
        ax3.set_ylabel('MACD', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3)
        ax3.xaxis_date()
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # Formatting
        plt.tight_layout()
        
        # Save
        filename = f"{symbol}_chart.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath

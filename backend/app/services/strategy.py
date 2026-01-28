
import pandas as pd
from .technical_analysis import TechnicalAnalyzer

class TradingStrategy:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.ta = TechnicalAnalyzer(data)
        self.indicators = self.ta.calculate_all_indicators()

    def get_signal(self):
        """
        Returns:
            dict: {
                "action": "BUY_CALL" | "BUY_PUT" | "WAIT",
                "reason": str,
                "confidence": "HIGH" | "MEDIUM" | "LOW"
            }
        """
        if self.data.empty:
            return {"action": "WAIT", "reason": "No data", "confidence": "LOW"}

        # Extract latest indicators
        close = self.indicators.get('current_price')
        ema_20 = self.indicators.get('ema_20')
        ema_50 = self.indicators.get('ema_50')
        rsi = self.indicators.get('rsi')
        macd = self.indicators.get('macd')
        macd_signal = self.indicators.get('macd_signal')
        adx = self.indicators.get('adx')

        if not all([close, ema_20, ema_50, rsi, macd, macd_signal]):
            return {"action": "WAIT", "reason": "Insufficient indicators", "confidence": "LOW"}

        # Trend Checks
        bullish_trend = (close > ema_20) and (ema_20 > ema_50)
        bearish_trend = (close < ema_20) and (ema_20 < ema_50)

        # Momentum Checks
        bullish_momentum = (rsi > 50) and (macd > macd_signal)
        bearish_momentum = (rsi < 50) and (macd < macd_signal)

        # ADX Confirmation (Optional but good)
        strong_trend = adx > 20 if adx else False

        # Decision Logic
        if bullish_trend and bullish_momentum:
            confidence = "HIGH" if strong_trend else "MEDIUM"
            return {
                "action": "BUY_CALL",
                "reason": f"Bullish Trend (EMA) + Momentum (RSI {rsi:.1f}, MACD X). ADX: {adx:.1f}",
                "confidence": confidence
            }
        
        elif bearish_trend and bearish_momentum:
            confidence = "HIGH" if strong_trend else "MEDIUM"
            return {
                "action": "BUY_PUT",
                "reason": f"Bearish Trend (EMA) + Momentum (RSI {rsi:.1f}, MACD X). ADX: {adx:.1f}",
                "confidence": confidence
            }

        return {
            "action": "WAIT",
            "reason": f"Choppy/Neutral. Close: {close}, EMA20: {ema_20}, RSI: {rsi:.1f}",
            "confidence": "LOW"
        }

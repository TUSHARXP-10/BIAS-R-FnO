import talib
import numpy as np
import pandas as pd

class TechnicalAnalyzer:
    def __init__(self, data):
        """
        data: pandas DataFrame with columns: Open, High, Low, Close, Volume
        """
        self.data = data
        self.close = data['Close'].values
        self.high = data['High'].values
        self.low = data['Low'].values
        self.open = data['Open'].values
        self.volume = data['Volume'].values if 'Volume' in data.columns else None
    
    def _safe_float(self, value, precision=2):
        """Safely convert numpy/talib values to float, handling NaN"""
        if isinstance(value, (float, np.floating)) and (np.isnan(value) or np.isinf(value)):
            return None
        try:
            return round(float(value), precision)
        except (ValueError, TypeError):
            return None

    def calculate_all_indicators(self):
        """Calculate all major technical indicators"""
        indicators = {}
        
        # Current Price Info
        indicators['current_price'] = self._safe_float(self.close[-1])
        indicators['high'] = self._safe_float(self.high[-1])
        indicators['low'] = self._safe_float(self.low[-1])
        indicators['open'] = self._safe_float(self.open[-1])
        
        # RSI (Relative Strength Index)
        rsi = talib.RSI(self.close, timeperiod=14)
        indicators['rsi'] = self._safe_float(rsi[-1])
        
        # MACD
        close_series = pd.Series(self.close)
        ema12 = close_series.ewm(span=12, adjust=False).mean()
        ema26 = close_series.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        hist_line = macd_line - signal_line
        indicators['macd'] = self._safe_float(macd_line.iloc[-1], 2)
        indicators['macd_signal'] = self._safe_float(signal_line.iloc[-1], 2)
        indicators['macd_histogram'] = self._safe_float(hist_line.iloc[-1], 2)
        macd_log_series = pd.Series(np.log(self.close)).ewm(span=12, adjust=False).mean() - pd.Series(np.log(self.close)).ewm(span=26, adjust=False).mean()
        signal_log_series = macd_log_series.ewm(span=9, adjust=False).mean()
        hist_log_series = macd_log_series - signal_log_series
        indicators['macd_log'] = self._safe_float(macd_log_series.iloc[-1], 6)
        indicators['macd_log_signal'] = self._safe_float(signal_log_series.iloc[-1], 6)
        indicators['macd_log_histogram'] = self._safe_float(hist_log_series.iloc[-1], 6)
        macd_pct_series = (ema12 - ema26) / ema26 * 100
        signal_pct_series = macd_pct_series.ewm(span=9, adjust=False).mean()
        hist_pct_series = macd_pct_series - signal_pct_series
        indicators['macd_pct'] = self._safe_float(macd_pct_series.iloc[-1], 4)
        indicators['macd_pct_signal'] = self._safe_float(signal_pct_series.iloc[-1], 4)
        indicators['macd_pct_histogram'] = self._safe_float(hist_pct_series.iloc[-1], 4)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = talib.BBANDS(
            self.close, 
            timeperiod=20, 
            nbdevup=2, 
            nbdevdn=2
        )
        indicators['bb_upper'] = self._safe_float(bb_upper[-1])
        indicators['bb_middle'] = self._safe_float(bb_middle[-1])
        indicators['bb_lower'] = self._safe_float(bb_lower[-1])
        
        # EMAs
        ema_20 = talib.EMA(self.close, timeperiod=20)
        ema_50 = talib.EMA(self.close, timeperiod=50)
        ema_200 = talib.EMA(self.close, timeperiod=200)
        indicators['ema_20'] = self._safe_float(ema_20[-1])
        indicators['ema_50'] = self._safe_float(ema_50[-1])
        indicators['ema_200'] = self._safe_float(ema_200[-1])
        
        # ATR (Average True Range)
        atr = talib.ATR(self.high, self.low, self.close, timeperiod=14)
        indicators['atr'] = self._safe_float(atr[-1])
        
        # ADX (Trend Strength)
        adx = talib.ADX(self.high, self.low, self.close, timeperiod=14)
        indicators['adx'] = self._safe_float(adx[-1])
        
        # Stochastic
        slowk, slowd = talib.STOCH(
            self.high, 
            self.low, 
            self.close,
            fastk_period=14,
            slowk_period=3,
            slowd_period=3
        )
        indicators['stoch_k'] = self._safe_float(slowk[-1])
        indicators['stoch_d'] = self._safe_float(slowd[-1])
        
        return indicators
    
    def get_trend(self):
        """Relaxed trend classification"""
        indicators = self.calculate_all_indicators()
        current_price = indicators.get('current_price')
        ema_20 = indicators.get('ema_20')
        ema_50 = indicators.get('ema_50')
        
        if any(v is None for v in [current_price, ema_20, ema_50]):
            return "Neutral"
            
        # Relaxed Bullish: Price above EMA 20, or EMA 20 above EMA 50
        if current_price > ema_20:
            return "Bullish"
        # Relaxed Bearish: Price below EMA 20, or EMA 20 below EMA 50
        elif current_price < ema_20:
            return "Bearish"
        else:
            return "Neutral"
    
    def get_signal(self):
        """Generate trading signals based on indicators"""
        rsi = talib.RSI(self.close, timeperiod=14)[-1]
        macd, macd_signal, _ = talib.MACD(self.close, 12, 26, 9)
        adx = talib.ADX(self.high, self.low, self.close, timeperiod=14)[-1]
        
        signals = []
        
        trend = self.get_trend()
        rsi_value = None if np.isnan(rsi) else float(rsi)
        adx_value = None if np.isnan(adx) else float(adx)
        macd_value = None if np.isnan(macd[-1]) else float(macd[-1])
        macd_signal_value = None if np.isnan(macd_signal[-1]) else float(macd_signal[-1])

        if adx_value is None:
            signals.append("Trend strength unavailable")
        elif adx_value < 20:
            signals.append(f"Weak trend strength (ADX {adx_value:.2f}) → range-biased, avoid trend trades")
        elif adx_value < 25:
            signals.append(f"Moderate trend strength (ADX {adx_value:.2f}) → cautious trend-following")
        else:
            signals.append(f"Strong trend strength (ADX {adx_value:.2f}) → trend-following favorable")

        if trend == "Bullish":
            signals.append("Trend bias: Bullish")
        elif trend == "Bearish":
            signals.append("Trend bias: Bearish")
        else:
            signals.append("Trend bias: Neutral")

        if rsi_value is not None:
            if rsi_value < 30:
                if adx_value is not None and adx_value < 20:
                    signals.append(f"RSI oversold ({rsi_value:.2f}) but trend strength weak → wait")
                else:
                    signals.append(f"RSI oversold ({rsi_value:.2f}) supports bounce only with trend confirmation")
            elif rsi_value > 70:
                if adx_value is not None and adx_value < 20:
                    signals.append(f"RSI overbought ({rsi_value:.2f}) but trend strength weak → avoid chasing")
                else:
                    signals.append(f"RSI overbought ({rsi_value:.2f}) warns of exhaustion in trend")
            else:
                signals.append(f"RSI neutral ({rsi_value:.2f})")

        if macd_value is not None and macd_signal_value is not None:
            if macd_value > macd_signal_value:
                if adx_value is not None and adx_value < 20:
                    signals.append("MACD bullish crossover but trend strength weak → lower weight")
                else:
                    signals.append("MACD bullish crossover supports trend bias")
            else:
                if adx_value is not None and adx_value < 20:
                    signals.append("MACD bearish crossover but trend strength weak → lower weight")
                else:
                    signals.append("MACD bearish crossover supports trend bias")
        
        return signals
    
    def get_volume_context(self):
        """Analyze volume relative to recent average"""
        if self.volume is None or len(self.volume) < 20:
            return {'surge': False, 'ratio': 1.0}
            
        avg_volume = np.mean(self.volume[-20:])
        current_volume = self.volume[-1]
        surge_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        return {
            'surge': surge_ratio > 1.2,  # 20% surge
            'ratio': round(float(surge_ratio), 2),
            'current': int(current_volume),
            'average': int(avg_volume)
        }

    def get_support_resistance(self):
        """Calculate support and resistance levels (last 20 candles)"""
        recent_highs = self.high[-20:]
        recent_lows = self.low[-20:]
        
        resistance = round(float(np.max(recent_highs)), 2)
        support = round(float(np.min(recent_lows)), 2)
        
        return {
            'resistance': resistance,
            'support': support
        }
    
    def _risk_reward(self, entry_price, target_price, stop_price):
        try:
            r = abs(entry_price - stop_price)
            rr = abs(target_price - entry_price) / r if r > 0 else None
            return round(float(rr), 2) if rr is not None else None
        except Exception:
            return None
    
    def generate_actionable_plan(self):
        indicators = self.calculate_all_indicators()
        sr = self.get_support_resistance()
        trend = self.get_trend()
        rsi = indicators.get('rsi')
        adx = indicators.get('adx')
        ema_20 = indicators.get('ema_20')
        current_price = indicators.get('current_price')
        support = sr.get('support')
        resistance = sr.get('resistance')
        vol_ctx = self.get_volume_context()
        
        if any(v is None for v in [rsi, adx, ema_20, current_price, support, resistance]):
            return {
                'decision': 'NO TRADE',
                'reason': 'Insufficient data',
                'entry_condition': 'Do not enter',
                'target_1': None,
                'target_2': None,
                'stop_loss': None,
                'invalidation': f"Wait for ADX > 20 or breakout of ₹{support}-₹{resistance}",
                'risk_reward': None
            }

        # Enhanced Decision Logic:
        # 1. Trend confirmation (Relaxed EMA)
        # 2. ADX expansion (Trend strength)
        # 3. Volume surge (Confirmation)
        # 4. Breakout of recent S/R
        
        is_breakout_up = current_price > resistance
        is_breakout_down = current_price < support
        
        if (trend == "Bullish" or is_breakout_up) and adx > 18 and rsi < 75:
            decision = "LONG"
            entry_condition = f"Above ₹{max(ema_20, resistance):.2f}"
            target_1 = round(current_price * 1.01, 2)
            target_2 = round(current_price * 1.02, 2)
            stop_loss = support
            invalidation = f"Below ₹{support:.2f}"
            reason = f"{'Breakout' if is_breakout_up else 'Trend'} confirmed (ADX {adx:.1f}, Vol Ratio {vol_ctx['ratio']})"
            rr = self._risk_reward(current_price, target_1, stop_loss)
            
        elif (trend == "Bearish" or is_breakout_down) and adx > 18 and rsi > 25:
            decision = "SHORT"
            entry_condition = f"Below ₹{min(ema_20, support):.2f}"
            target_1 = round(current_price * 0.99, 2)
            target_2 = round(current_price * 0.98, 2)
            stop_loss = resistance
            invalidation = f"Above ₹{resistance:.2f}"
            reason = f"{'Breakdown' if is_breakout_down else 'Trend'} confirmed (ADX {adx:.1f}, Vol Ratio {vol_ctx['ratio']})"
            rr = self._risk_reward(current_price, target_1, stop_loss)
            
        else:
            decision = "NO TRADE"
            entry_condition = "Do not enter"
            target_1 = None
            target_2 = None
            stop_loss = None
            invalidation = f"Wait for ADX > 20 or breakout of ₹{support}-₹{resistance}"
            
            # Detailed reason for NO TRADE
            reasons = []
            if adx <= 18: reasons.append(f"weak trend (ADX {adx:.1f})")
            if rsi >= 75: reasons.append("overbought RSI")
            if rsi <= 25: reasons.append("oversold RSI")
            if not (is_breakout_up or is_breakout_down): reasons.append("inside range")
            
            reason = f"No clear trigger: {', '.join(reasons)}" if reasons else "Choppy conditions"
            rr = None
            
        return {
            'decision': decision,
            'reason': reason,
            'entry_condition': entry_condition,
            'target_1': target_1,
            'target_2': target_2,
            'stop_loss': stop_loss,
            'invalidation': invalidation,
            'risk_reward': rr
        }
    
    def get_candlestick_patterns(self):
        """Detect candlestick patterns"""
        patterns = []
        
        # Doji
        if talib.CDLDOJI(self.open, self.high, self.low, self.close)[-1] != 0:
            patterns.append("Doji")
        
        # Hammer
        if talib.CDLHAMMER(self.open, self.high, self.low, self.close)[-1] != 0:
            patterns.append("Hammer")
        
        # Shooting Star
        if talib.CDLSHOOTINGSTAR(self.open, self.high, self.low, self.close)[-1] != 0:
            patterns.append("Shooting Star")
        
        # Engulfing
        engulfing = talib.CDLENGULFING(self.open, self.high, self.low, self.close)[-1]
        if engulfing > 0:
            patterns.append("Bullish Engulfing")
        elif engulfing < 0:
            patterns.append("Bearish Engulfing")
        
        return patterns if patterns else ["No significant patterns detected"]

    def get_trade_bias(self):
        plan = self.generate_actionable_plan()
        indicators = self.calculate_all_indicators()
        sr = self.get_support_resistance()
        trend = self.get_trend()
        current_price = indicators.get('current_price')
        adx = indicators.get('adx')
        rsi = indicators.get('rsi')
        
        if plan['decision'] == 'LONG':
            primary_bias = 'LONG'
            stance = 'Long'
            confidence = 8
            invalidation = sr.get('support')
            confirmation = sr.get('resistance')
            execution = f"Enter {plan['entry_condition']}. Targets: ₹{plan['target_1']} / ₹{plan['target_2']}. SL: ₹{plan['stop_loss']}."
        elif plan['decision'] == 'SHORT':
            primary_bias = 'SHORT'
            stance = 'Short'
            confidence = 8
            invalidation = sr.get('resistance')
            confirmation = sr.get('support')
            execution = f"Enter {plan['entry_condition']}. Targets: ₹{plan['target_1']} / ₹{plan['target_2']}. SL: ₹{plan['stop_loss']}."
        else:
            primary_bias = 'NO TRADE'
            stance = 'No trade'
            # Calculate confidence based on actual market conditions
            if adx and adx < 15:
                confidence = 2
                reason = f"Very weak trend strength (ADX: {adx:.1f})"
            elif adx and 15 <= adx <= 20:
                confidence = 3
                reason = f"Weak trend strength (ADX: {adx:.1f})"
            elif rsi and (rsi < 40 or rsi > 60):
                confidence = 4
                reason = f"RSI extreme ({rsi:.1f}) but no clear trend"
            else:
                confidence = 3
                reason = f"Choppy market conditions"
            
            invalidation = sr.get('support')
            confirmation = sr.get('resistance')
            
            # More detailed execution plan with actual values
            execution = f"Do not enter. {reason}. "
            if adx:
                execution += f"Current ADX: {adx:.1f} (wait for ADX > 20). "
            execution += f"Price range: ₹{current_price:.2f} between support (₹{sr['support']}) and resistance (₹{sr['resistance']}). "
            execution += f"Wait for clear breakout above ₹{sr['resistance']} (for LONG) or below ₹{sr['support']} (for SHORT)."
        return {
            'primary_bias': primary_bias,
            'stance': stance,
            'confidence': confidence,
            'invalidation': invalidation,
            'confirmation': confirmation,
            'execution': execution
        }

    def get_risk_context(self):
        indicators = self.calculate_all_indicators()
        atr = indicators.get('atr')
        adx = indicators.get('adx')
        current_price = indicators.get('current_price')
        if atr is None or current_price is None or adx is None:
            return {
                'atr': atr,
                'atr_percentage': None,
                'volatility': "Unknown",
                'sizing_advice': "Insufficient data",
                'adx': adx,
                'trend_strength': "Unknown",
                'trend_advice': "Gather more data"
            }
        atr_pct = (atr / current_price) * 100
        if atr_pct > 2:
            volatility = "High"
            sizing_advice = "Reduce position size, wider stops needed"
        elif atr_pct > 1:
            volatility = "Moderate"
            sizing_advice = "Normal position sizing acceptable"
        else:
            volatility = "Low"
            sizing_advice = "Can use tighter stops, standard sizing"
        if adx > 25:
            trend_strength = "Strong"
            trend_advice = "Trend-following strategies favorable"
        elif adx > 20:
            trend_strength = "Moderate"
            trend_advice = "Mixed signals, use caution"
        else:
            trend_strength = "Weak"
            trend_advice = "Range-bound likely, avoid trend trades"
        return {
            'atr': round(float(atr), 2),
            'atr_percentage': round(float(atr_pct), 2),
            'volatility': volatility,
            'sizing_advice': sizing_advice,
            'adx': round(float(adx), 2),
            'trend_strength': trend_strength,
            'trend_advice': trend_advice
        }

    def get_market_regime(self):
        indicators = self.calculate_all_indicators()
        trend = self.get_trend()
        adx = indicators.get('adx')
        current_price = indicators.get('current_price')
        atr = indicators.get('atr')
        if adx is None or current_price is None or atr is None:
            return {'regime': 'Unknown', 'description': 'Insufficient data'}
        atr_pct = (atr / current_price) * 100
        if adx > 25 and atr_pct < 1.5:
            regime = "Strong Trend"
            description = "Trending cleanly"
        elif adx > 25 and atr_pct > 2:
            regime = "Volatile Trend"
            description = "Trending but choppy"
        elif adx < 20 and atr_pct < 1.5:
            regime = "Range-Bound"
            description = "Low volatility consolidation"
        else:
            regime = "Weak Trend / Range-biased"
            description = f"with {trend.lower()} tilt"
        return {'regime': regime, 'description': description}

    def get_position_sizing(self):
        risk_context = self.get_risk_context()
        trade_bias = self.get_trade_bias()
        volatility = risk_context.get('volatility')
        confidence = trade_bias.get('confidence', 0)
        if volatility == "High":
            size_multiplier = 0.5
            advice = "Reduce position size to 50% of normal"
        elif volatility == "Moderate":
            size_multiplier = 0.75
            advice = "Use 75% of normal position size"
        else:
            size_multiplier = 1.0
            advice = "Standard position sizing acceptable"
        if confidence < 5:
            advice += " (low conviction → further reduce or avoid)"
        return {'size_multiplier': size_multiplier, 'advice': advice}

    def get_overall_signal(self):
        indicators = self.calculate_all_indicators()
        adx = indicators.get('adx')
        trend = self.get_trend()
        if adx is None:
            return "Unknown"
        if adx < 20:
            return f"Mixed ({trend} trend, weakening momentum)"
        return trend

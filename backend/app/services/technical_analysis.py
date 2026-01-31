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
        """Tighter trend classification using EMA alignment"""
        indicators = self.calculate_all_indicators()
        current_price = indicators.get('current_price')
        ema_20 = indicators.get('ema_20')
        ema_50 = indicators.get('ema_50')
        
        if any(v is None for v in [current_price, ema_20, ema_50]):
            return "Neutral"
        
        # Stronger alignment criteria
        if current_price > ema_20 and ema_20 > ema_50:
            return "Bullish"
        elif current_price < ema_20 and ema_20 < ema_50:
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

    def calculate_pivot_points(self):
        if len(self.close) < 2:
            return None
        idx = -2 if len(self.close) >= 2 else -1
        high = self.high[idx]
        low = self.low[idx]
        close = self.close[idx]
        
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            'pivot': round(float(pivot), 2),
            'r1': round(float(r1), 2),
            's1': round(float(s1), 2),
            'r2': round(float(r2), 2),
            's2': round(float(s2), 2),
            'r3': round(float(r3), 2),
            's3': round(float(s3), 2)
        }

    def calculate_cpr_levels(self):
        """Central Pivot Range (CPR) using previous day OHLC (popular in India)"""
        if len(self.close) < 2:
            return None
        idx = -2 if len(self.close) >= 2 else -1
        high = float(self.high[idx])
        low = float(self.low[idx])
        close = float(self.close[idx])
        pivot = (high + low + close) / 3.0
        bc = (high + low) / 2.0
        tc = (2 * pivot) - bc
        width = tc - bc
        return {
            'pivot': round(pivot, 2),
            'bc': round(bc, 2),
            'tc': round(tc, 2),
            'width': round(width, 2)
        }

    def calculate_confidence_score(self, trend, adx, rsi, vol_surge):
        """
        Compute a confidence score (0-100) based on weighted factors.
        
        Weights:
        - Trend Alignment: 30
        - Trend Strength (ADX): 25
        - Momentum (RSI): 25
        - Volume Support: 20
        """
        score = 0
        details = []
        
        # 1. Trend Alignment (30 pts)
        if trend in ["Bullish", "Bearish"]:
            score += 30
            details.append("Trend Aligned (+30)")
        else:
            score += 10 # Partial credit for stability
            details.append("Trend Neutral (+10)")
            
        # 2. Trend Strength (ADX) (25 pts)
        if adx > 25:
            score += 25
            details.append(f"Strong ADX {adx:.1f} (+25)")
        elif adx > 20:
            score += 15
            details.append(f"Moderate ADX {adx:.1f} (+15)")
        else:
            score += 5
            details.append(f"Weak ADX {adx:.1f} (+5)")
            
        # 3. Momentum (RSI) (25 pts)
        # Bullish context
        if trend == "Bullish":
            if 40 <= rsi <= 70: 
                score += 25
                details.append("RSI Bullish Zone (+25)")
            elif rsi > 70:
                score += 10
                details.append("RSI Overbought (+10)")
            else:
                score += 5
                details.append("RSI Weak (+5)")
        # Bearish context
        elif trend == "Bearish":
            if 30 <= rsi <= 60:
                score += 25
                details.append("RSI Bearish Zone (+25)")
            elif rsi < 30:
                score += 10
                details.append("RSI Oversold (+10)")
            else:
                score += 5
                details.append("RSI Weak (+5)")
        # Neutral context
        else:
            if 40 <= rsi <= 60:
                score += 25
                details.append("RSI Range Stable (+25)")
            else:
                score += 10
        
        # 4. Volume Support (20 pts)
        if vol_surge:
            score += 20
            details.append("Volume Surge (+20)")
        else:
            score += 10
            details.append("Volume Normal (+10)")
            
        return score, details

    def get_market_regime(self):
        indicators = self.calculate_all_indicators()
        trend = self.get_trend()
        adx = indicators.get('adx')
        current_price = indicators.get('current_price')
        atr = indicators.get('atr')
        
        if any(v is None for v in [adx, current_price, atr]):
            return {'regime': 'Unknown', 'description': 'Insufficient data'}
            
        atr_pct = (atr / current_price) * 100
        
        # Strict Regime Definitions
        if adx > 25:
            if atr_pct < 2.0:
                regime = "Strong Trend"
                description = f"Clean {trend} movement"
            else:
                regime = "Volatile Trend"
                description = f"Choppy {trend} movement"
        elif adx < 20:
            regime = "Range-Bound"
            description = "Sideways / Consolidation"
        else:
            regime = "Weak Trend"
            description = f"Drifting {trend}"
            
        return {'regime': regime, 'description': description}

    def get_support_resistance(self):
        """Calculate Context Support and Resistance (Daily Timeframe)"""
        # Context Levels (HTF) - 20 day High/Low
        if len(self.close) < 20:
             return {'support': self._safe_float(min(self.low)), 'resistance': self._safe_float(max(self.high))}
             
        recent_high = max(self.high[-20:])
        recent_low = min(self.low[-20:])
        
        return {
            'support': self._safe_float(recent_low),
            'resistance': self._safe_float(recent_high)
        }

    def get_candlestick_patterns(self):
        """Identify key candlestick patterns"""
        patterns = []
        # Engulfing
        engulfing = talib.CDLENGULFING(self.open, self.high, self.low, self.close)
        if engulfing[-1] == 100: patterns.append("Bullish Engulfing")
        elif engulfing[-1] == -100: patterns.append("Bearish Engulfing")
        
        # Hammer
        hammer = talib.CDLHAMMER(self.open, self.high, self.low, self.close)
        if hammer[-1] == 100: patterns.append("Hammer")
        
        # Shooting Star
        star = talib.CDLSHOOTINGSTAR(self.open, self.high, self.low, self.close)
        if star[-1] == -100: patterns.append("Shooting Star")
        
        # Doji
        doji = talib.CDLDOJI(self.open, self.high, self.low, self.close)
        if doji[-1] == 100: patterns.append("Doji")
        
        return patterns if patterns else ["No significant pattern"]

    def get_risk_context(self):
        """Analyze volatility and risk environment"""
        indicators = self.calculate_all_indicators()
        atr = indicators.get('atr')
        current_price = indicators.get('current_price')
        
        if not atr or not current_price:
            return {'volatility': 'Unknown', 'atr': 0, 'atr_percentage': 0}
            
        atr_pct = (atr / current_price) * 100
        
        if atr_pct > 2.0:
            volatility = "High"
        elif atr_pct > 1.0:
            volatility = "Moderate"
        else:
            volatility = "Low"
            
        return {
            'volatility': volatility,
            'atr': atr,
            'atr_percentage': round(atr_pct, 2)
        }

    def get_trade_bias(self):
        """Legacy wrapper for confidence score to support existing calls"""
        trend = self.get_trend()
        indicators = self.calculate_all_indicators()
        vol_ctx = self.get_volume_context()
        
        score, _ = self.calculate_confidence_score(
            trend, 
            indicators.get('adx'), 
            indicators.get('rsi'), 
            vol_ctx['surge']
        )
        
        return {
            'bias': trend,
            'confidence': score,
            'strength': 'Strong' if score > 60 else 'Weak'
        }

    def _risk_reward(self, entry, target, stop):
        """Calculate Risk-Reward Ratio"""
        if not all([entry, target, stop]):
            return None
        # Ensure all inputs are numbers
        try:
            entry = float(entry)
            target = float(target)
            stop = float(stop)
        except (ValueError, TypeError):
            return None
            
        risk = abs(entry - stop)
        reward = abs(target - entry)
        if risk == 0: return 0
        return round(reward / risk, 2)

    def recommend_strikes(self, current_price, decision, step=100):
        """Recommend specific Option Strikes based on decision"""
        if decision not in ["LONG", "SHORT"]:
            return "N/A"
            
        # Round to nearest step (e.g., 100 for Nifty/Sensex approx)
        atm = round(current_price / step) * step
        
        if decision == "LONG":
            # Bullish: Buy ATM or slightly OTM Call
            return f"Buy CE: {atm} (ATM) or {atm + step} (OTM)"
        elif decision == "SHORT":
            # Bearish: Buy ATM or slightly OTM Put
            return f"Buy PE: {atm} (ATM) or {atm - step} (OTM)"
        return "N/A"

    def generate_actionable_plan(self):
        indicators = self.calculate_all_indicators()
        sr = self.get_support_resistance() # Context Levels (Daily)
        pivots = self.calculate_pivot_points() # Execution Levels (Intraday)
        trend = self.get_trend()
        
        rsi = indicators.get('rsi')
        adx = indicators.get('adx')
        ema_20 = indicators.get('ema_20')
        current_price = indicators.get('current_price')
        vol_ctx = self.get_volume_context()
        
        # 1. Get Regime FIRST (Regime Lock)
        regime_data = self.get_market_regime()
        regime = regime_data['regime']
        
        if any(v is None for v in [rsi, adx, ema_20, current_price]):
            return {
                'decision': 'NO TRADE',
                'reason': 'Insufficient data',
                'entry_condition': 'N/A',
                'target_1': None, 'target_2': None, 'stop_loss': None,
                'invalidation': 'N/A', 'risk_reward': None,
                'regime': 'Unknown', 'confidence': 0, 'strikes': 'N/A',
                'verdict': 'Data Insufficient'
            }

        # 2. Compute Confidence
        confidence_score, confidence_details = self.calculate_confidence_score(
            trend, adx, rsi, vol_ctx['surge']
        )
        
        # 3. Decision Logic based on Regime
        decision = "NO TRADE"
        entry_condition = "Wait"
        target_1 = target_2 = stop_loss = None
        invalidation = "N/A"
        reason = "N/A"
        verdict = "Stay Flat"
        
        # Execution boundaries: Prefer CPR (TC/BC). Targets: standard pivots.
        if self.calculate_cpr_levels():
            cpr = self.calculate_cpr_levels()
            exec_pivot = cpr['pivot']
            exec_upper = cpr['tc']
            exec_lower = cpr['bc']
        else:
            exec_pivot = (sr['resistance'] + sr['support']) / 2
            exec_upper = sr['resistance']
            exec_lower = sr['support']
        if pivots:
            exec_r1 = pivots['r1']; exec_r2 = pivots['r2']; exec_r3 = pivots['r3']
            exec_s1 = pivots['s1']; exec_s2 = pivots['s2']; exec_s3 = pivots['s3']
        else:
            diff = exec_upper - exec_lower
            exec_r1 = exec_upper; exec_s1 = exec_lower
            exec_r2 = exec_r1 + diff; exec_s2 = exec_s1 - diff
            exec_r3 = exec_r2 + diff; exec_s3 = exec_s2 - diff

        # LOGIC CORE
        if regime in ["Strong Trend", "Volatile Trend"]:
            # Trend Following
            if trend == "Bullish":
                if confidence_score > 65:
                    decision = "LONG"
                    # Entry aligned to CPR boundaries
                    entry_condition = f"Breakout > {exec_upper:.0f} or Pullback to {exec_pivot:.0f}"
                    stop_loss = round(exec_lower, 2)
                    target_1 = round(exec_r2, 2)
                    target_2 = round(exec_r3, 2)
                    invalidation = f"Close below {exec_lower:.0f}"
                    reason = f"Bullish Trend (Score {confidence_score})"
                    verdict = "BUY DIPS or BREAKOUT"
                else:
                    decision = "NO TRADE"
                    reason = f"Bullish but low confidence ({confidence_score})"
                    verdict = "WATCHLIST ONLY (Weak Confidence)"
                    
            elif trend == "Bearish":
                if confidence_score > 65:
                    decision = "SHORT"
                    entry_condition = f"Breakdown < {exec_lower:.0f} or Pullback to {exec_pivot:.0f}"
                    stop_loss = round(exec_upper, 2)
                    target_1 = round(exec_s2, 2)
                    target_2 = round(exec_s3, 2)
                    invalidation = f"Close above {exec_upper:.0f}"
                    reason = f"Bearish Trend (Score {confidence_score})"
                    verdict = "SELL RALLIES or BREAKDOWN"
                else:
                    decision = "NO TRADE"
                    reason = f"Bearish but low confidence ({confidence_score})"
                    verdict = "WATCHLIST ONLY (Weak Confidence)"
                    
        elif regime == "Range-Bound":
            # Range Trading
            if confidence_score > 50: # Lower threshold for range
                decision = "RANGE TRADE"
                entry_condition = f"Buy near {exec_lower:.0f} / Sell near {exec_upper:.0f}"
                stop_loss = "Tight (0.5%)" 
                target_1 = round(exec_pivot, 2)
                target_2 = round(exec_upper if trend=="Bullish" else exec_lower, 2)
                invalidation = "Range Breakout"
                reason = "Market consolidating (Low ADX)"
                verdict = "PLAY THE EDGES (Fade highs/lows)"
            else:
                decision = "NO TRADE"
                reason = "Choppy / No clear boundaries"
                verdict = "STAY FLAT (Choppy)"
                
        elif regime == "Weak Trend":
             decision = "NO TRADE"
             reason = "Trend too weak, momentum absent"
             verdict = "STAY FLAT (Waiting for Momentum)"
             
        # 3.1 Pivot Gate: avoid countertrend entries
        if decision == "LONG" and current_price is not None and exec_pivot is not None:
            if current_price <= exec_pivot:
                decision = "NO TRADE"
                reason = f"Price below pivot ({exec_pivot}) → avoid countertrend long"
                verdict = "STAY FLAT (Below Pivot)"
                target_1 = target_2 = stop_loss = None
                invalidation = "N/A"
        if decision == "SHORT" and current_price is not None and exec_pivot is not None:
            if current_price >= exec_pivot:
                decision = "NO TRADE"
                reason = f"Price above pivot ({exec_pivot}) → avoid countertrend short"
                verdict = "STAY FLAT (Above Pivot)"
                target_1 = target_2 = stop_loss = None
                invalidation = "N/A"
        
        # 3.2 Momentum Gate: align RSI with direction near actionable zones
        if decision == "LONG" and rsi is not None:
            if rsi < 50:
                decision = "NO TRADE"
                reason = f"RSI {rsi:.1f} < 50 → momentum not supportive for long"
                verdict = "STAY FLAT (Weak Momentum)"
                target_1 = target_2 = stop_loss = None
                invalidation = "N/A"
        if decision == "SHORT" and rsi is not None:
            if rsi > 50:
                decision = "NO TRADE"
                reason = f"RSI {rsi:.1f} > 50 → momentum not supportive for short"
                verdict = "STAY FLAT (Weak Momentum)"
                target_1 = target_2 = stop_loss = None
                invalidation = "N/A"

        # 3.3 EMA slope gate: require slope alignment with direction
        if decision in ["LONG", "SHORT"]:
            ema20_series = talib.EMA(self.close, timeperiod=20)
            ema50_series = talib.EMA(self.close, timeperiod=50)
            ema20_slope = float(ema20_series[-1] - ema20_series[-2]) if not np.isnan(ema20_series[-1]) and not np.isnan(ema20_series[-2]) else 0.0
            ema50_slope = float(ema50_series[-1] - ema50_series[-2]) if not np.isnan(ema50_series[-1]) and not np.isnan(ema50_series[-2]) else 0.0
            if decision == "LONG" and (ema20_slope <= 0 or ema50_slope <= 0):
                decision = "NO TRADE"
                reason = "EMA slopes not supportive for long"
                verdict = "STAY FLAT (Slope Mismatch)"
                target_1 = target_2 = stop_loss = None
                invalidation = "N/A"
            if decision == "SHORT" and (ema20_slope >= 0 or ema50_slope >= 0):
                decision = "NO TRADE"
                reason = "EMA slopes not supportive for short"
                verdict = "STAY FLAT (Slope Mismatch)"
                target_1 = target_2 = stop_loss = None
                invalidation = "N/A"

        # 4. Safety Check: R:R & Inversions
        # Ensure SL is closer than Target 1 for directional trades
        if decision in ["LONG", "SHORT"] and stop_loss and target_1:
            dist_target = abs(target_1 - current_price)
            dist_stop = abs(current_price - stop_loss)
            
            # If SL is wider than Target, force adjustment or kill trade
            if dist_stop > dist_target:
                 # Adjust SL to be tighter (e.g., recent swing or 0.5%)
                 # Or simply downgrade to NO TRADE if no logical tight stop exists
                 # Here we will tighten SL to 1:1.5 implied
                 if decision == "LONG":
                     stop_loss = round(current_price - (dist_target / 1.5), 2)
                 else:
                     stop_loss = round(current_price + (dist_target / 1.5), 2)
                 invalidation = f"Tightened SL: {stop_loss}"

        rr = self._risk_reward(current_price, target_1, stop_loss) if target_1 and stop_loss else None
        strikes = self.recommend_strikes(current_price, decision, step=100) # Assuming Sensex/Nifty step

        return {
            'decision': decision,
            'reason': reason,
            'entry_condition': entry_condition,
            'target_1': target_1,
            'target_2': target_2,
            'stop_loss': stop_loss,
            'invalidation': invalidation,
            'risk_reward': rr,
            'regime': regime,
            'confidence': confidence_score,
            'confidence_details': confidence_details,
            'verdict': verdict,
            'strikes': strikes,
            'pivots': pivots
        }

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

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

class SentimentState(Enum):
    BULLISH = "Bullish Bias"
    BEARISH = "Bearish Bias"
    NEUTRAL = "Neutral / Range-bound"
    VOLATILE = "High Volatility / No Trade Zone"

class TradingPreference(Enum):
    LONG = "Long"
    SHORT = "Short"
    NON_DIRECTIONAL = "Non-directional"
    STAY_FLAT = "Stay Flat"

@dataclass
class SentimentInput:
    # 1. Global Cues
    gift_nifty_change_pct: Optional[float] = None
    us_indices_change_pct: Dict[str, float] = field(default_factory=dict) # {"S&P 500": 0.5, "NASDAQ": -0.2}
    asia_market_change_pct: Dict[str, float] = field(default_factory=dict) # {"NIKKEI": 1.0, "HANG SENG": 0.5}
    
    # 2. Domestic Market Cues
    sensex_prev_close_vs_high_low: Optional[str] = None # "NEAR_HIGH", "NEAR_LOW", "MID"
    advance_decline_ratio: Optional[float] = None
    india_vix_change_pct: Optional[float] = None
    fii_dii_net_flow: Optional[float] = None # Positive for inflow, Negative for outflow
    
    # 3. Options & Volatility
    atm_iv_change_pct: Optional[float] = None
    pcr_total: Optional[float] = None
    pcr_near_expiry: Optional[float] = None
    oi_buildup: Optional[str] = None # "LONG_BUILDUP", "SHORT_BUILDUP", "LONG_UNWINDING", "SHORT_COVERING"
    
    # 4. Event Flags
    is_major_event_day: bool = False # Budget, RBI, Earnings
    event_notes: List[str] = field(default_factory=list)

@dataclass
class TradingImplication:
    preferred_strategy: str
    avoid: str

@dataclass
class SentimentOutput:
    market_sentiment: str
    confidence_score: float # 0-100
    supporting_factors: List[str]
    risk_notes: List[str]
    trading_implication: TradingImplication

class MarketSentimentEngine:
    def analyze(self, inputs: SentimentInput) -> SentimentOutput:
        score = 0.0
        max_score = 0.0
        factors = []
        risks = []
        
        # --- 1. Global Cues Analysis ---
        global_score = 0
        global_weight = 0
        
        # US Indices
        for name, change in inputs.us_indices_change_pct.items():
            global_weight += 1
            if change > 0.5:
                global_score += 1
                factors.append(f"{name} closed strong (+{change:.2f}%)")
            elif change < -0.5:
                global_score -= 1
                factors.append(f"{name} closed weak ({change:.2f}%)")
            else:
                factors.append(f"{name} flat ({change:.2f}%)")
        
        # Asian Markets
        for name, change in inputs.asia_market_change_pct.items():
            global_weight += 1
            if change > 0.5:
                global_score += 1
                factors.append(f"{name} trading up (+{change:.2f}%)")
            elif change < -0.5:
                global_score -= 1
                factors.append(f"{name} trading down ({change:.2f}%)")

        # Normalize Global Score (-1 to 1)
        normalized_global = (global_score / global_weight) if global_weight > 0 else 0
        
        # --- 2. Domestic Cues Analysis ---
        domestic_score = 0
        
        # SENSEX Close Position
        if inputs.sensex_prev_close_vs_high_low == "NEAR_HIGH":
            domestic_score += 0.5
            factors.append("SENSEX closed near day's high")
        elif inputs.sensex_prev_close_vs_high_low == "NEAR_LOW":
            domestic_score -= 0.5
            factors.append("SENSEX closed near day's low")

        # VIX
        if inputs.india_vix_change_pct is not None:
            if inputs.india_vix_change_pct > 5.0:
                domestic_score -= 1 # High rising volatility often bearish/volatile
                risks.append(f"India VIX spiked (+{inputs.india_vix_change_pct:.2f}%)")
            elif inputs.india_vix_change_pct < -3.0:
                domestic_score += 0.5 # Cooling off, supportive
                factors.append(f"India VIX cooling off ({inputs.india_vix_change_pct:.2f}%)")
        
        # FII Flow
        if inputs.fii_dii_net_flow is not None:
            if inputs.fii_dii_net_flow > 500: # Crores
                domestic_score += 1
                factors.append("Positive FII/DII Net Flow")
            elif inputs.fii_dii_net_flow < -500:
                domestic_score -= 1
                risks.append("Negative FII/DII Net Flow")

        # --- 3. Options Data Analysis ---
        options_score = 0
        
        # PCR
        if inputs.pcr_total is not None:
            if inputs.pcr_total > 1.2:
                options_score += 1
                factors.append(f"PCR Bullish ({inputs.pcr_total:.2f})")
            elif inputs.pcr_total < 0.7:
                options_score -= 1
                factors.append(f"PCR Bearish ({inputs.pcr_total:.2f})")
            else:
                factors.append(f"PCR Neutral ({inputs.pcr_total:.2f})")

        # --- Synthesis ---
        # Weighted Final Score: Global (40%) + Domestic (30%) + Options (30%)
        # But handle missing data weights
        
        final_raw_score = (normalized_global * 0.4) + (domestic_score * 0.3) + (options_score * 0.3)
        # Range approx -1 to 1
        
        # Determine State
        state = SentimentState.NEUTRAL
        confidence = 50.0
        
        if inputs.is_major_event_day:
            state = SentimentState.VOLATILE
            confidence = 80.0
            risks.append("MAJOR EVENT DAY - CAUTION")
            for note in inputs.event_notes:
                risks.append(note)
        else:
            if final_raw_score > 0.3:
                state = SentimentState.BULLISH
                confidence = 60 + (final_raw_score * 40) # Scale to 60-100
            elif final_raw_score < -0.3:
                state = SentimentState.BEARISH
                confidence = 60 + (abs(final_raw_score) * 40)
            else:
                state = SentimentState.NEUTRAL
                confidence = 50 + (1 - abs(final_raw_score)) * 30

        confidence = min(max(confidence, 0), 100)
        
        # Determine Implication
        trading_imp = TradingImplication(
            preferred_strategy="Non-directional / Scalping",
            avoid="Aggressive directional bets"
        )
        
        if state == SentimentState.BULLISH:
            trading_imp = TradingImplication(
                preferred_strategy="Long on dips (Call Buying / Put Writing)",
                avoid="Shorting against momentum"
            )
        elif state == SentimentState.BEARISH:
            trading_imp = TradingImplication(
                preferred_strategy="Short on rise (Put Buying / Call Writing)",
                avoid="Bottom fishing"
            )
        elif state == SentimentState.VOLATILE:
            trading_imp = TradingImplication(
                preferred_strategy="Stay Flat / Straddles (if experienced)",
                avoid="Naked directional options"
            )

        return SentimentOutput(
            market_sentiment=state.value,
            confidence_score=round(confidence, 1),
            supporting_factors=factors[:5], # Top 5
            risk_notes=risks[:3], # Top 3
            trading_implication=trading_imp
        )

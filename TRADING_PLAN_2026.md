# SENSEX Trading Strategy & Plan (Jan 29 - Jan 31, 2026)

**Objective:** Maximize total account value starting from ₹3000.
**Market:** SENSEX (BSE Index)
**Instruments:** Options Buying (Calls/Puts)
**Timeframe:** Intraday (1min, 5min, 15min)

## 1. Capital Management & Position Sizing
*   **Total Capital:** ₹3000
*   **Allocation per Trade:** 40-50% (₹1200 - ₹1500). 
    *   *Rationale:* With such small capital, we need to commit a significant portion to afford even one lot of SENSEX options, especially if premiums are > ₹100.
*   **Max Risk per Trade:** ₹300 - ₹500 (10-15% of total capital).
*   **Risk:Reward Ratio:** Minimum 1:2. Target at least ₹600 profit for a ₹300 risk.

## 2. Instrument Selection
*   **Expiry:** Current Week Expiry (likely Jan 30, 2026, if Friday is expiry, or Jan 29 if today is expiry).
    *   *Note:* SENSEX expiry is typically Friday. If Jan 29 is Thursday, tomorrow (Jan 30) is expiry. Gamma risk will be high.
*   **Strike Selection:**
    *   **Delta:** 0.3 - 0.5 (ATM or slightly OTM).
    *   **Premium Range:** ₹50 - ₹150.
    *   Avoid deep OTM (< ₹20) as probability of profit is low.
    *   Avoid deep ITM (> ₹200) as capital doesn't allow it.

## 3. Technical Setup & Entry Criteria
We will use the following confluence factors. A trade requires at least **2 confirmations**.

### A. Trend Following (Moving Averages)
*   **Setup:** Price crosses above/below EMA 20 on 5min chart.
*   **Confirmation:** EMA 20 > EMA 50 for Long; EMA 20 < EMA 50 for Short.
*   **Entry:** Retest of EMA 20 or breakout of recent swing high/low with volume.

### B. Momentum (RSI & MACD)
*   **RSI (14):** 
    *   Long: RSI crosses above 40 or 50 from below.
    *   Short: RSI crosses below 60 or 50 from above.
    *   *Divergence:* Bullish divergence at support (Long), Bearish divergence at resistance (Short).
*   **MACD:**
    *   MACD Line crosses Signal Line.
    *   Histogram expansion confirms momentum.

### C. Price Action
*   **Support/Resistance:** Trade bounces off major daily levels or breakouts.
*   **Patterns:** Flags, Triangles, Double Top/Bottom on 5min/15min.
*   **Candlesticks:** Engulfing bars, Hammers, Shooting Stars at key levels.

## 4. Execution Rules
1.  **Stop Loss (SL):** HARD STOP placed immediately upon entry.
    *   Technical SL: Below recent swing low (Long) / Above swing high (Short).
    *   Max Premium SL: 20-30% of option premium.
2.  **Targets (TGT):**
    *   T1: 1:1.5 Risk (Move SL to Cost).
    *   T2: 1:2 Risk (Book 50% or Trail aggressive).
    *   T3: Trail with EMA 9 or previous candle low.
3.  **Timing:**
    *   Morning: 09:15 - 10:30 (Volatility capture).
    *   Mid-day: 10:30 - 13:00 (Caution: Chop zone).
    *   Afternoon: 13:00 - 15:15 (Trend moves/Zero-Hero on Expiry).

## 5. Daily Routine (Jan 29 - Jan 31)
*   **Pre-Market:** Analyze Daily/Hourly charts for key levels. Check Global Cues/GIFT Nifty.
*   **Live:** Wait for setup. Do NOT chase candles.
*   **Post-Market:** Review trades. Update journal.

## 6. Zero-Tolerance Rules
*   No averaging down losers.
*   No carrying positions overnight (unless substantial profit buffer exists and trend is strong).
*   Stop trading for the day if 2 consecutive Stop Losses are hit (-₹1000 drawdown).
*   Stop trading if Daily Target (₹1000+) is reached, unless a "A+" setup appears.

---
**Status:** READY
**Capital:** ₹3000
**Bot Configuration:** Updated

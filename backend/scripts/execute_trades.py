import os
import json
import argparse
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

load_dotenv(os.path.join(backend_dir, ".env"))

from math import floor
from datetime import datetime, time
from zoneinfo import ZoneInfo
from app.services.data_fetcher import MarketDataFetcher
from app.services.strategy import TradingStrategy

scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
from groww_client import GrowwClient

def ist_now():
    return datetime.now(ZoneInfo("Asia/Kolkata"))

def in_window(start_h: int, start_m: int, end_h: int, end_m: int):
    now = ist_now().time()
    return time(start_h, start_m) <= now <= time(end_h, end_m)

def is_weekend():
    return ist_now().weekday() >= 5

def lot_capacity(capital: float, allocation_pct: float, premium: float, lot_size: int, buffer_per_lot: float = 50.0) -> int:
    alloc = capital * allocation_pct
    per_lot = premium * lot_size + buffer_per_lot
    return max(0, int(alloc // per_lot))

def passes_filters(premium: float, spread: float, d_oi: float, premium_min: float, premium_max: float, max_spread_pct: float, oi_change_pct: float, signal_type: str, contract_type: str) -> bool:
    # Check if contract matches signal (BUY_CALL -> CE, BUY_PUT -> PE)
    if signal_type == "BUY_CALL" and contract_type != "CE":
        return False
    if signal_type == "BUY_PUT" and contract_type != "PE":
        return False
    
    return (premium_min <= premium <= premium_max) and (spread <= max_spread_pct) and (d_oi >= oi_change_pct)

def generate_mock_chain(spot_price: float):
    """Generate synthetic option chain for simulation/testing when API fails"""
    print(f"Generating mock option chain around spot: {spot_price}")
    contracts = []
    
    # Round spot to nearest 100
    atm_strike = round(spot_price / 100) * 100
    strikes = [atm_strike - 200, atm_strike - 100, atm_strike, atm_strike + 100, atm_strike + 200]
    
    for strike in strikes:
        # Simple mock premium logic
        dist = abs(spot_price - strike)
        # Call Premium
        if strike <= spot_price: # ITM/ATM Call
            ce_prem = (spot_price - strike) + 150 - (dist * 0.1)
        else: # OTM Call
            ce_prem = max(10, 150 - (dist * 0.5))
            
        # Put Premium
        if strike >= spot_price: # ITM/ATM Put
            pe_prem = (strike - spot_price) + 150 - (dist * 0.1)
        else: # OTM Put
            pe_prem = max(10, 150 - (dist * 0.5))
            
        contracts.append({
            "symbol": f"SENSEX26JAN{strike}CE",
            "premium": round(ce_prem, 1),
            "oi_change_pct": 0.1,
            "spread_pct": 0.01
        })
        contracts.append({
            "symbol": f"SENSEX26JAN{strike}PE",
            "premium": round(pe_prem, 1),
            "oi_change_pct": 0.1,
            "spread_pct": 0.01
        })
        
    return contracts

def fetch_option_chain(url: str, spot_price: float = 0):
    if not url:
        print("No OPTION_CHAIN_URL provided.")
        return generate_mock_chain(spot_price) if spot_price > 0 else []
        
    try:
        import requests
        print(f"Fetching option chain from: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        
        content_type = r.headers.get('Content-Type', '')
        if 'text/html' in content_type or url.endswith('.html'):
            print("Warning: URL is an HTML page. Using Mock Chain for Simulation.")
            return generate_mock_chain(spot_price) if spot_price > 0 else []
            
        data = r.json()
        contracts = data.get("contracts", [])
        print(f"Found {len(contracts)} contracts.")
        return contracts
    except Exception as e:
        print(f"Error fetching option chain: {e}. Using Mock.")
        return generate_mock_chain(spot_price) if spot_price > 0 else []

def get_current_option_price(symbol: str, spot_price: float):
    """
    Simulate fetching current option price.
    In real world, this would call an API.
    For simulation, we regenerate mock chain and find the symbol.
    """
    contracts = generate_mock_chain(spot_price)
    for c in contracts:
        if c["symbol"] == symbol:
            return c["premium"]
    return None

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--index", default="SENSEX")
    args = p.parse_args()
    
    if is_weekend():
        print("Weekend. Skipping trading.")
        return
        
    start_h = int(os.environ.get("TRADING_START_H", "10"))
    start_m = int(os.environ.get("TRADING_START_M", "0"))
    end_h = int(os.environ.get("TRADING_END_H", "14"))
    end_m = int(os.environ.get("TRADING_END_M", "0"))
    
    if not in_window(start_h, start_m, end_h, end_m):
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print("Outside window. Skipping trading.")
            return
        else:
            print("Outside window, but running locally for testing. Proceeding...")
            
    capital = float(os.environ.get("CAPITAL", "0"))
    premium_min = float(os.environ.get("PREMIUM_MIN", "50"))
    premium_max = float(os.environ.get("PREMIUM_MAX", "200"))
    allocation_pct = float(os.environ.get("ALLOCATION_PCT", "0.6"))
    max_spread_pct = float(os.environ.get("MAX_SPREAD_PCT", "0.02"))
    oi_change_pct = float(os.environ.get("OI_CHANGE_PCT", "0.08"))
    lot_size = int(os.environ.get("SENSEX_LOT_SIZE", os.environ.get("LOT_SIZE", "0")))
    is_expiry = os.environ.get("IS_EXPIRY_DAY", "false").lower() == "true"
    url = os.environ.get("OPTION_CHAIN_URL", "")
    state_path = os.path.join(backend_dir, "signals", "trade_state.json")
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    
    if capital <= 0 or lot_size <= 0:
        print("Invalid capital or lot size.")
        sys.exit(1)
        
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = {}
        
    today_key = ist_now().strftime("%Y-%m-%d")
    prev = state.get(today_key, {})
    
    # --- TRADE MANAGEMENT START ---
    # Check if we have an OPEN trade (trades_executed >= 1 and outcome is NOT set)
    trades_done = int(prev.get("trades_executed", 0))
    is_open = trades_done >= 1 and "outcome" not in prev
    
    if is_open:
        print("Managing open trade...")
        symbol = prev.get("symbol")
        entry_price = prev.get("entry_price")
        
        # Fetch current spot to simulate option price update
        fetcher = MarketDataFetcher()
        current_spot = 0.0
        try:
            import yfinance as yf
            ticker = yf.Ticker("^BSESN")
            market_data = ticker.history(period="1d", interval="5m") # Latest
            if not market_data.empty:
                 current_spot = market_data['Close'].iloc[-1]
        except Exception:
            pass
            
        if current_spot > 0:
            current_prem = get_current_option_price(symbol, current_spot)
            if current_prem:
                print(f"Current Price for {symbol}: {current_prem} (Entry: {entry_price})")
                
                # SL/TP Logic
                # SL: 30% loss
                sl_price = entry_price * 0.7
                # TP: 50% profit (1:1.5 approx) or Trailing
                tp_price = entry_price * 1.5
                
                if current_prem <= sl_price:
                    print(f"STOP LOSS HIT! Exiting @ {current_prem}")
                    prev["outcome"] = "loss"
                    prev["exit_price"] = current_prem
                    prev["exit_reason"] = "SL Hit"
                    prev["status"] = "CLOSED"
                    state[today_key] = prev
                    with open(state_path, "w", encoding="utf-8") as f:
                        json.dump(state, f, indent=2)
                    return # Exit after closing
                    
                elif current_prem >= tp_price:
                    print(f"TARGET HIT! Exiting @ {current_prem}")
                    prev["outcome"] = "profit"
                    prev["exit_price"] = current_prem
                    prev["exit_reason"] = "TP Hit"
                    prev["status"] = "CLOSED"
                    state[today_key] = prev
                    with open(state_path, "w", encoding="utf-8") as f:
                        json.dump(state, f, indent=2)
                    return # Exit after closing
                else:
                    print("Holding position...")
                    return # Continue holding, don't enter new trade
            else:
                print("Could not fetch current option price. Holding.")
                return
        else:
            print("Could not fetch spot price. Holding.")
            return

    # If previous trade was closed (profit/loss), decide if we can trade again?
    # For now, plan says "Stop trading for the day if 2 consecutive Stop Losses are hit"
    # Or "Stop trading if Daily Target is reached".
    # Simplification: If outcome is profit, stop. If loss, maybe allow 1 more?
    if prev.get("outcome") == "profit":
        print("Daily Target Reached (Profit). No more trades.")
        return
        
    if prev.get("outcome") == "loss" and trades_done >= 2:
        print("Max daily losses reached. No more trades.")
        return
        
    # --- TRADE MANAGEMENT END ---

    # --- STRATEGY EXECUTION START (NEW ENTRY) ---
    print("Fetching SENSEX market data for potential entry...")
    fetcher = MarketDataFetcher()
    current_spot = 0.0
    signal = {"action": "WAIT"}
    
    try:
        import yfinance as yf
        ticker = yf.Ticker("^BSESN")
        market_data = ticker.history(period="5d", interval="5m")
        
        if market_data.empty:
            print("No market data available. Exiting.")
            return
            
        strategy = TradingStrategy(market_data)
        signal = strategy.get_signal()
        current_spot = strategy.indicators.get('current_price', 0.0)
        print(f"Spot: {current_spot}")
        print(f"Strategy Signal: {signal}")
        
        if signal["action"] == "WAIT":
            print("Signal is WAIT. No trade.")
            return
            
    except Exception as e:
        print(f"Error executing strategy: {e}")
        return
    # --- STRATEGY EXECUTION END ---

    eff_spread = max_spread_pct * (0.75 if is_expiry else 1.0)
    eff_oi = oi_change_pct + (0.05 if is_expiry else 0.0)
    
    # Pass current_spot to fetch_option_chain for mock generation if needed
    contracts = fetch_option_chain(url, current_spot)
    
    # Sort contracts by premium (cheaper first) to find affordable ones
    contracts.sort(key=lambda x: float(x.get("premium", 0.0)))
    
    selected = None
    
    for c in contracts:
        symbol = c.get("symbol", "")
        premium = float(c.get("premium", 0.0))
        d_oi = float(c.get("oi_change_pct", 0.0))
        spread = float(c.get("spread_pct", 1.0))
        c_type = "CE" if "CE" in symbol else "PE" if "PE" in symbol else "UNKNOWN"
        
        if passes_filters(premium, spread, d_oi, premium_min, premium_max, eff_spread, eff_oi, signal["action"], c_type):
            selected = {"symbol": symbol, "premium": premium, "type": c_type}
            break
            
    if not selected:
        print("No candidate passed filters.")
        return
        
    lots = lot_capacity(capital, allocation_pct, selected["premium"], lot_size)
    if lots < 1:
        print(f"Insufficient capital for {selected['symbol']} @ {selected['premium']}. Cap: {lots}")
        return
        
    client = GrowwClient()
    side = "BUY"
    
    if client.live:
        res = client.place_option_order(selected["symbol"], side, lots, selected["premium"])
        print(f"Order result: {res}")
    else:
        print(f"[DRY-RUN] {side} {lots} lot(s) {selected['symbol']} @ {selected['premium']} (Signal: {signal['action']})")
        
    state[today_key] = {
        "trades_executed": trades_done + 1, 
        "symbol": selected["symbol"], 
        "entry_price": selected["premium"], 
        "signal": signal,
        "logged_at": ist_now().isoformat()
    }
    
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    main()

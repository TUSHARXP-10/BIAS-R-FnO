import os
import json
import argparse
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from math import floor
from datetime import datetime, time
from zoneinfo import ZoneInfo
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

def passes_filters(premium: float, spread: float, d_oi: float, premium_min: float, premium_max: float, max_spread_pct: float, oi_change_pct: float) -> bool:
    return (premium_min <= premium <= premium_max) and (spread <= max_spread_pct) and (d_oi >= oi_change_pct)

def fetch_option_chain(url: str):
    if not url:
        print("No OPTION_CHAIN_URL provided.")
        return []
    try:
        import requests
        print(f"Fetching option chain from: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        
        # Check if response is HTML or JSON
        content_type = r.headers.get('Content-Type', '')
        if 'text/html' in content_type or url.endswith('.html'):
            print("Warning: URL is an HTML page. HTML parsing is not yet implemented.")
            print("To fix this, provide a JSON API URL or update the parser for BSE HTML.")
            return []
            
        data = r.json()
        contracts = data.get("contracts", [])
        print(f"Found {len(contracts)} contracts.")
        return contracts
    except Exception as e:
        print(f"Error fetching option chain: {e}")
        return []

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
    allocation_pct = float(os.environ.get("ALLOCATION_PCT", "0.3"))
    max_spread_pct = float(os.environ.get("MAX_SPREAD_PCT", "0.02"))
    oi_change_pct = float(os.environ.get("OI_CHANGE_PCT", "0.08"))
    lot_size = int(os.environ.get("SENSEX_LOT_SIZE", os.environ.get("LOT_SIZE", "0")))
    is_expiry = os.environ.get("IS_EXPIRY_DAY", "false").lower() == "true"
    url = os.environ.get("OPTION_CHAIN_URL", "")
    state_path = os.path.join("backend", "signals", "trade_state.json")
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
    trades_done = int(prev.get("trades_executed", 0))
    if trades_done >= 1 and prev.get("outcome") == "profit":
        print("Previous trade profit. No next trade.")
        return
    eff_spread = max_spread_pct * (0.75 if is_expiry else 1.0)
    eff_oi = oi_change_pct + (0.05 if is_expiry else 0.0)
    contracts = fetch_option_chain(url)
    selected = None
    for c in contracts:
        symbol = c.get("symbol", "")
        premium = float(c.get("premium", 0.0))
        d_oi = float(c.get("oi_change_pct", 0.0))
        spread = float(c.get("spread_pct", 1.0))
        if passes_filters(premium, spread, d_oi, premium_min, premium_max, eff_spread, eff_oi):
            selected = {"symbol": symbol, "premium": premium}
            break
    if not selected:
        print("No candidate passed filters.")
        return
    lots = lot_capacity(capital, allocation_pct, selected["premium"], lot_size)
    if lots < 1:
        print("Insufficient capital.")
        return
    client = GrowwClient()
    if client.live:
        res = client.place_option_order(selected["symbol"], "BUY", lots, selected["premium"])
        print(f"Order result: {res}")
    else:
        print(f"[DRY-RUN] BUY {lots} {selected['symbol']} @ {selected['premium']}")
    state[today_key] = {"trades_executed": trades_done + 1, "symbol": selected["symbol"], "entry_price": selected["premium"], "logged_at": ist_now().isoformat()}
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f)

if __name__ == "__main__":
    main()

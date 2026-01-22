import os

class GrowwClient:
    def __init__(self, secret_env="GROWW_TOTP_SECRET"):
        self.secret = os.environ.get(secret_env)
        self.client = None
        self.live = os.environ.get("GROWW_ORDER_MODE", "dry").lower() == "live"
        self.api_key = os.environ.get("GROWW_API_KEY")
        self.api_secret = os.environ.get("GROWW_API_SECRET")
        try:
            if self.live:
                import groww
                if self.secret:
                    self.client = groww.Client.totp_login(totp_secret=self.secret)
                elif self.api_key and self.api_secret:
                    self.client = groww.Client.api_key_login(api_key=self.api_key, api_secret=self.api_secret)
        except Exception:
            self.client = None
            self.live = False

    def place_option_order(self, symbol: str, side: str, qty_lots: int, limit_price: float):
        if self.live and self.client:
            try:
                return self.client.orders.place(
                    symbol=symbol,
                    product="FNO",
                    side=side,
                    qty=qty_lots,
                    order_type="LIMIT",
                    price=limit_price,
                )
            except Exception as e:
                print(f"[LIVE-ERROR] {e}")
                return None
        print(f"[DRY-RUN] {side} {qty_lots} lot(s) {symbol} @ {limit_price}")
        return {"status": "dry-run"}

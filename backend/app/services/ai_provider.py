import os

class OpenAIProvider:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.enabled = bool(self.api_key)

    def explain_report(self, report_data: dict) -> str:
        if not self.enabled:
            return ""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            ap = report_data.get("action_plan", {})
            indicators = report_data.get("indicators", {})
            mr = report_data.get("market_regime", {})
            symbol = report_data.get("symbol", "")
            prompt = (
                f"Symbol: {symbol}\n"
                f"Decision: {ap.get('decision','N/A')} | Reason: {ap.get('reason','')}\n"
                f"Trend: {report_data.get('trend','')} | RSI: {indicators.get('rsi')} | ADX: {indicators.get('adx')}\n"
                f"Regime: {mr.get('regime','')} {mr.get('description','')}\n"
                f"Write a concise 3–4 sentence explanation suitable for a trading report. "
                f"Emphasize deterministic rules and avoid advice."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=180,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return ""

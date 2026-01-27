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
                f"Market Data for {symbol}:\n"
                f"- Trend: {report_data.get('trend','Neutral')}\n"
                f"- Decision: {ap.get('decision','N/A')}\n"
                f"- Reason: {ap.get('reason','')}\n"
                f"- RSI: {indicators.get('rsi', 'N/A')}\n"
                f"- ADX: {indicators.get('adx', 'N/A')}\n"
                f"- Current Price: ₹{indicators.get('current_price', 'N/A')}\n"
                f"- Resistance: ₹{report_data.get('support_resistance', {}).get('resistance', 'N/A')}\n"
                f"- Support: ₹{report_data.get('support_resistance', {}).get('support', 'N/A')}\n\n"
                f"Task: Provide a high-conviction, professional market analysis (3-4 sentences). "
                f"Focus on what the indicators are telling us right now. "
                f"If the decision is 'NO TRADE', explain the specific criteria (like ADX or price levels) that must be met for a setup to emerge. "
                f"Avoid generic phrases. Be direct and technical."
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

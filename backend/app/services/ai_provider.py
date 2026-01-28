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
                f"- Current Price: {indicators.get('current_price')}\n"
                f"- RSI: {indicators.get('rsi')} | ADX: {indicators.get('adx')}\n"
                f"- MACD: {indicators.get('macd')} | MACD Signal: {indicators.get('macd_signal')}\n"
                f"- Bollinger: Upper {indicators.get('bb_upper')} | Lower {indicators.get('bb_lower')}\n"
                f"- Market Regime: {mr.get('regime','')} ({mr.get('description','')})\n"
                f"- Decision: {ap.get('decision','N/A')} | Reason: {ap.get('reason','')}\n\n"
                f"Write a professional, dashing, and elaborate technical commentary.\n"
                f"For SENSEX, specifically mention how the setup aligns with global cues and bank stocks if applicable.\n"
                f"Structure the response in 3 bullet points:\n"
                f"1. **Market Structure**: Explain the trend and key levels.\n"
                f"2. **Momentum & Volatility**: Analyze RSI/ADX and VIX implication.\n"
                f"3. **Actionable Trade Setup**: Explicitly state entry, stop-loss, and target zones.\n"
                f"If decision is 'NO TRADE', explain why patience is profitable here."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return ""

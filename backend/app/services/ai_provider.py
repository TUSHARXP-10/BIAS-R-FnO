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
                f"Write a professional, direct technical commentary.\n"
                f"If decision is 'NO TRADE', list exact triggers to activate a setup:\n"
                f"1) ADX threshold and expansion requirement\n"
                f"2) Breakout above resistance {report_data.get('support_resistance',{}).get('resistance')} or breakdown below support {report_data.get('support_resistance',{}).get('support')}\n"
                f"3) Confirmation using MACD direction/crossover and RSI state\n"
                f"Keep it concise and action-focused."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=320,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return ""

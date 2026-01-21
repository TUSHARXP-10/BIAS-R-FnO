from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import os
from datetime import datetime
from app.services.signal_tracker import SignalTracker

class ReportGenerator:
    def generate_pdf(self, report_data, is_weekly=False):
        signal_tracker = SignalTracker()
        # Ensure reports dir exists at project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up three levels to get to project root: services -> app -> backend -> project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        reports_dir = os.path.join(project_root, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        symbol = report_data.get('symbol', 'UNKNOWN')
        if is_weekly:
            filename = f"weekly_report_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        else:
            filename = f"report_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        decision_style = ParagraphStyle('Decision', parent=styles['Heading1'])
        decision_positive_style = ParagraphStyle('DecisionPositive', parent=styles['Heading1'])
        story = []
        
        # Title
        title_style = styles['Title']
        display_symbol = str(symbol).upper()
        story.append(Paragraph(f"{display_symbol} DAILY TRADING REPORT", title_style))
        report_date = report_data.get('date')
        tf = report_data.get('timeframe', {})
        story.append(Paragraph(f"📅 Date: {report_date}", styles['Normal']))
        story.append(Paragraph(f"📊 Timeframe: {tf.get('chart_interval', '1 Day')} Chart ({tf.get('data_period', '')})", styles['Normal']))
        story.append(Paragraph(f"⏳ Trade Horizon: {tf.get('analysis_type', '')}", styles['Normal']))
        story.append(Paragraph("This report is for swing/positional traders. Intraday traders should ignore this.", styles['Normal']))
        story.append(Spacer(1, 12))

        ap = report_data.get('action_plan', {})
        ap_decision = ap.get('decision', 'N/A')
        if ap_decision == "NO TRADE":
            decision_style.textColor = colors.red
            story.append(Paragraph(f"🔴 FINAL DECISION: {ap_decision}", decision_style))
        else:
            decision_positive_style.textColor = colors.green
            story.append(Paragraph(f"🟢 FINAL DECISION: {ap_decision}", decision_positive_style))
        story.append(Paragraph(f"Reason: {ap.get('reason', 'N/A')}", styles['Normal']))
        if ap_decision == "NO TRADE":
            story.append(Paragraph("Next Action: WAIT", styles['Normal']))
        story.append(Spacer(1, 10))

        mr = report_data.get('market_regime', {})
        mr_text = f"🧠 Market Regime: {mr.get('regime', 'N/A')} {(' - ' + mr.get('description')) if mr.get('description') else ''}"
        story.append(Paragraph(mr_text, styles['Normal']))
        story.append(Spacer(1, 10))

        # Extract data
        trend = report_data.get('trend', 'Neutral')
        indicators = report_data.get('indicators', {})
        sr = report_data.get('support_resistance', {})
        rc = report_data.get('risk_context', {})
        ps = report_data.get('position_sizing', {})
        tb = report_data.get('trade_bias', {})
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        overall_signal = report_data.get('overall_signal', 'Neutral')
        if ap_decision == "NO TRADE":
            overall_signal = "Neutral (No Trade)"
            summary_text = f"""
            <b>{symbol}</b> currently has <b>no actionable setup</b>.<br/>
            Regime: <b>{mr.get('regime', 'N/A')}</b> {(' - ' + mr.get('description')) if mr.get('description') else ''}<br/>
            Latest close: <b>{indicators.get('current_price', 'N/A')}</b><br/>
            Overall signal: <b>{overall_signal}</b>
            """
        else:
            if ap_decision in ["LONG", "SHORT"]:
                overall_signal = f"{ap_decision} bias"
            summary_text = f"""
            <b>{symbol}</b> is currently showing a <b>{trend}</b> trend.<br/>
            Latest close: <b>{indicators.get('current_price', 'N/A')}</b><br/>
            Overall signal: <b>{overall_signal}</b>
            """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Paragraph(f"Confidence Score: {tb.get('confidence', 'N/A')}/10", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Key Levels", styles['Heading2']))
        story.append(Paragraph(f"Resistance: {sr.get('resistance', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Support: {sr.get('support', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 10))

        story.append(Paragraph("If–Then Decision Logic", styles['Heading2']))
        logic_text = f"""
        IF ADX > 20 AND price > ₹{sr.get('resistance', 'N/A')} → Look for LONG<br/>
        IF ADX > 20 AND price < ₹{sr.get('support', 'N/A')} → Look for SHORT<br/>
        ELSE → NO TRADE
        """
        story.append(Paragraph(logic_text, styles['Normal']))
        story.append(Spacer(1, 10))

        if ap_decision in ["LONG", "SHORT"]:
            story.append(Paragraph("Trade Setup", styles['Heading2']))
            setup_text = f"""
            Direction: {ap_decision}<br/>
            Entry: {ap.get('entry_condition', 'N/A')}<br/>
            Target 1: {ap.get('target_1', 'N/A')}<br/>
            Target 2: {ap.get('target_2', 'N/A')}<br/>
            Stop Loss: {ap.get('stop_loss', 'N/A')}<br/>
            Risk:Reward: {ap.get('risk_reward', 'N/A')}
            """
            story.append(Paragraph(setup_text, styles['Normal']))
            story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("If No Trade – What To Wait For", styles['Heading2']))
            no_trade_text = f"""
            Condition 1: ADX > 20 and breakout above ₹{sr.get('resistance', 'N/A')}<br/>
            Condition 2: ADX > 20 and breakdown below ₹{sr.get('support', 'N/A')}<br/>
            Current Price: ₹{indicators.get('current_price', 'N/A')}<br/>
            Status: No trigger — wait
            """
            story.append(Paragraph(no_trade_text, styles['Normal']))
            story.append(Spacer(1, 10))

        story.append(Paragraph("Risk Assessment", styles['Heading2']))
        rc_text = f"""
        Volatility: {rc.get('volatility', 'N/A')}<br/>
        ATR: ₹{rc.get('atr', 'N/A')} ({rc.get('atr_percentage', 'N/A')}% of price)<br/>
        Position sizing guidance: {ps.get('advice', 'N/A')}<br/>
        Conviction score: {tb.get('confidence', 'N/A')}/10
        """
        story.append(Paragraph(rc_text, styles['Normal']))
        story.append(Spacer(1, 10))

        rsi = indicators.get('rsi')
        adx = indicators.get('adx')
        rsi_state = "neutral"
        if rsi is not None:
            if rsi >= 70:
                rsi_state = "overbought"
            elif rsi <= 30:
                rsi_state = "oversold"
        active_text = f"""
        Trend strength: {rc.get('trend_strength', 'N/A')} (ADX: {adx if adx is not None else 'N/A'}) drives the decision.<br/>
        Momentum: RSI {rsi if rsi is not None else 'N/A'} is {rsi_state}, but trend strength has priority.
        """
        story.append(Paragraph("Active Signals (Interpreted)", styles['Heading2']))
        story.append(Paragraph(active_text, styles['Normal']))
        story.append(Spacer(1, 10))

        story.append(Paragraph("What Not To Do", styles['Heading2']))
        if ap_decision == "NO TRADE":
            dont_text = """
            • Buy just because RSI is oversold<br/>
            • Short inside the range without ADX expansion<br/>
            • Trade without a clear breakout or breakdown trigger
            """
        else:
            dont_text = """
            • Chase price without the stated entry condition<br/>
            • Ignore the stop loss or move it wider<br/>
            • Oversize positions during high ATR volatility
            """
        story.append(Paragraph(dont_text, styles['Normal']))
        story.append(Spacer(1, 10))

        chart_path = report_data.get('chart_path')
        if chart_path and os.path.exists(chart_path):
            im = Image(chart_path, width=500, height=500) 
            story.append(im)
            story.append(Spacer(1, 20))

        
        story.append(Paragraph("Indicator Snapshot", styles['Heading2']))
        
        table_data = [
            ["Indicator", "Value"],
            ["RSI (14)", indicators.get('rsi', 'N/A')],
            ["MACD", indicators.get('macd', 'N/A')],
            ["MACD Signal", indicators.get('macd_signal', 'N/A')],
            ["Bollinger Upper", indicators.get('bb_upper', 'N/A')],
            ["Bollinger Lower", indicators.get('bb_lower', 'N/A')],
            ["EMA 20", indicators.get('ema_20', 'N/A')],
            ["EMA 50", indicators.get('ema_50', 'N/A')],
            ["EMA 200", indicators.get('ema_200', 'N/A')],
            ["ATR", indicators.get('atr', 'N/A')],
            ["ADX", indicators.get('adx', 'N/A')]
        ]
        
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        story.append(Paragraph("Appendix: Indicator Notes", styles['Heading2']))
        guide_text = """
        <b>RSI:</b> Momentum gauge. Overbought above 70, oversold below 30.<br/>
        <b>MACD:</b> Trend-following momentum and crossover signal.<br/>
        <b>Bollinger Bands:</b> Volatility bands used for squeeze and breakout context.<br/>
        <b>EMA:</b> Weighted trend averages (20/50/200).<br/>
        <b>ADX:</b> Trend strength; below 20 is weak or range.
        """
        story.append(Paragraph(guide_text, styles['Normal']))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Data Methodology", styles['Heading2']))
        methodology_text = """
        <b>Market Data Source:</b> Yahoo Finance (Daily OHLCV)<br/>
        <b>Analysis Timeframe:</b> Daily, last 3 months unless specified<br/>
        <b>Calculations:</b> Standard TA-Lib algorithms (RSI, MACD, Bollinger Bands, EMA)<br/><br/>
        <b>Important:</b> Indicator values may differ from other platforms due to data timing, symbol selection, and vendor-specific adjustments.
        EMAs and RSI are validated within ~1% of TradingView for matching timeframe/symbol. MACD may differ; use primarily for direction/crossovers.
        """
        story.append(Paragraph(methodology_text, styles['Normal']))
        story.append(Spacer(1, 10))

        story.append(Paragraph("Disclaimer", styles['Heading2']))
        disclaimer_text = "Informational only. Not financial advice."
        story.append(Paragraph(disclaimer_text, styles['Italic']))
        
        # Log the signal
        signal_tracker.log_signal(symbol, ap_decision, indicators.get('current_price', 'N/A'), report_date)
        
        doc.build(story)
        return filepath

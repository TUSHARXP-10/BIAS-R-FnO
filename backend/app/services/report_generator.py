from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import os
from datetime import datetime
from app.services.signal_tracker import SignalTracker

class ReportGenerator:
    def generate_pdf(self, report_data):
        signal_tracker = SignalTracker()
        # Ensure reports dir exists at project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up three levels to get to project root: services -> app -> backend -> project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        reports_dir = os.path.join(project_root, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        symbol = report_data.get('symbol', 'UNKNOWN')
        filename = f"report_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = styles['Title']
        display_symbol = str(symbol).upper()
        story.append(Paragraph(f"Trading Report for {display_symbol}", title_style))
        report_date = report_data.get('date')
        story.append(Paragraph(f"Date: {report_date}", styles['Normal']))
        story.append(Spacer(1, 20))

        tf = report_data.get('timeframe', {})
        tf_text = f"📊 Analysis Timeframe: {tf.get('chart_interval', '1 Day')} Chart ({tf.get('data_period', '')})<br/>🎯 Trade Horizon: {tf.get('analysis_type', '')}"
        story.append(Paragraph(tf_text, styles['Normal']))
        story.append(Spacer(1, 10))
        mr = report_data.get('market_regime', {})
        mr_text = f"📊 Market Regime: {mr.get('regime', 'N/A')} {(' - ' + mr.get('description')) if mr.get('description') else ''}"
        story.append(Paragraph(mr_text, styles['Normal']))
        story.append(Spacer(1, 10))

        ap = report_data.get('action_plan', {})
        story.append(Paragraph("Action Plan", styles['Heading2']))
        ap_text = f"""
        Decision: <b>{ap.get('decision', 'N/A')}</b><br/>
        Reason: {ap.get('reason', 'N/A')}<br/>
        Entry: {ap.get('entry_condition', 'N/A')}<br/>
        Target 1: {ap.get('target_1', 'N/A')}<br/>
        Target 2: {ap.get('target_2', 'N/A')}<br/>
        Stop Loss: {ap.get('stop_loss', 'N/A')}<br/>
        Risk:Reward: {ap.get('risk_reward', 'N/A')}<br/>
        Invalidation: {ap.get('invalidation', 'N/A')}
        """
        story.append(Paragraph(ap_text, styles['Normal']))
        ap_decision = ap.get('decision', 'N/A')
        if ap_decision == "NO TRADE":
            sr = report_data.get('support_resistance', {})
            indicators = report_data.get('indicators', {})
            rc = report_data.get('risk_context', {})
            ps = report_data.get('position_sizing', {})
            potential_text = f"""
            ⏳ <b>POTENTIAL SETUPS (WAIT FOR TRIGGER)</b><br/>
            Long Trigger: ADX > 20 + breakout above ₹{sr.get('resistance', 'N/A')}<br/>
            Short Trigger: ADX > 20 + breakdown below ₹{sr.get('support', 'N/A')}<br/>
            Current Price: ₹{indicators.get('current_price', 'N/A')}<br/>
            Status: No trigger — stay flat
            """
            story.append(Paragraph(potential_text, styles['Normal']))
            story.append(Spacer(1, 6))
            risk_critical = f"""
            ⚠️ <b>RISK ASSESSMENT (CRITICAL)</b><br/>
            ATR: ₹{rc.get('atr', 'N/A')} ({rc.get('atr_percentage', 'N/A')}% of price)<br/>
            Volatility: {rc.get('volatility', 'N/A')} → {rc.get('sizing_advice', 'N/A')}<br/>
            Trend Strength: {rc.get('trend_strength', 'N/A')} (ADX: {rc.get('adx', 'N/A')})<br/>
            Position Guidance: {ps.get('advice', 'N/A')}
            """
            story.append(Paragraph(risk_critical, styles['Normal']))
        story.append(Spacer(1, 10))

        # Extract data
        trend = report_data.get('trend', 'Neutral')
        indicators = report_data.get('indicators', {})
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        overall_signal = report_data.get('overall_signal', 'Neutral')
        mr = report_data.get('market_regime', {})
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
        story.append(Spacer(1, 10))

        # Market Chart
        chart_path = report_data.get('chart_path')
        if chart_path and os.path.exists(chart_path):
            # Scale image to fit width (approx 450-500 points for letter)
            # Increased height for 3-panel chart
            im = Image(chart_path, width=500, height=500) 
            story.append(im)
            story.append(Spacer(1, 20))
        
        # Technical Analysis Detail
        story.append(Paragraph("Technical Analysis Detail", styles['Heading2']))
        
        # Trend Analysis
        trend = report_data.get('trend', 'Neutral')
        trend_color = "green" if trend == "Bullish" else "red" if trend == "Bearish" else "black"
        story.append(Paragraph(f"Trend: <font color='{trend_color}'><b>{trend}</b></font>", styles['Normal']))
        story.append(Spacer(1, 10))

        tb = report_data.get('trade_bias', {})
        story.append(Paragraph("TRADE BIAS", styles['Heading2']))
        tb_text = f"Primary Bias: {tb.get('primary_bias', 'N/A')}<br/>Current Stance: {tb.get('stance', 'N/A')}<br/>Conviction: {tb.get('confidence', 'N/A')}/10<br/><br/>Execution Plan: {tb.get('execution', 'N/A')}<br/><br/>Invalidation Level: ₹{tb.get('invalidation', 'N/A')}<br/>Confirmation Level: ₹{tb.get('confirmation', 'N/A')}"
        story.append(Paragraph(tb_text, styles['Normal']))
        story.append(Spacer(1, 10))

        rc = report_data.get('risk_context', {})
        story.append(Paragraph("RISK ASSESSMENT", styles['Heading2']))
        rc_text = f"ATR: ₹{rc.get('atr', 'N/A')} ({rc.get('atr_percentage', 'N/A')}% of price)<br/>Volatility: {rc.get('volatility', 'N/A')} → {rc.get('sizing_advice', 'N/A')}<br/>Expected Daily Range: ±{rc.get('atr', 'N/A')} points<br/><br/>ADX: {rc.get('adx', 'N/A')} ({rc.get('trend_strength', 'N/A')})<br/>Trend Strength: {rc.get('trend_strength', 'N/A')} → {rc.get('trend_advice', 'N/A')}"
        story.append(Paragraph(rc_text, styles['Normal']))
        ps = report_data.get('position_sizing', {})
        story.append(Paragraph(f"Position Sizing Guidance: {ps.get('advice', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 10))

        # Signals
        if report_data.get('signals'):
            story.append(Paragraph("<b>Active Signals:</b>", styles['Normal']))
            for signal in report_data.get('signals', []):
                story.append(Paragraph(f"• {signal}", styles['Normal']))
            story.append(Spacer(1, 10))

        
        # Technical Indicators Table
        story.append(Paragraph("Technical Indicators", styles['Heading2']))
        
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

        # Support & Resistance
        story.append(Paragraph("Support & Resistance", styles['Heading2']))
        sr = report_data.get('support_resistance', {})
        story.append(Paragraph(f"Resistance: {sr.get('resistance', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Support: {sr.get('support', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 10))

        # Patterns
        story.append(Paragraph("Candlestick Patterns", styles['Heading2']))
        for pattern in report_data.get('patterns', []):
            story.append(Paragraph(f"• {pattern}", styles['Normal']))
        story.append(Spacer(1, 10))

        # Educational Guide
        story.append(Paragraph("Understanding This Report", styles['Heading2']))
        guide_text = """
        <b>RSI (Relative Strength Index):</b> Measures momentum. Values > 70 suggest the asset is overbought (potential drop), while < 30 suggest oversold (potential rise).<br/>
        <b>MACD:</b> Trend-following momentum indicator. Crossovers between the MACD line and Signal line can indicate trend changes.<br/>
        <b>Bollinger Bands:</b> A volatility indicator. Prices often rebound from the upper/lower bands. Squeezes indicate low volatility and potential breakout.<br/>
        <b>EMA (Exponential Moving Average):</b> Weighted averages of price. EMA 20/50 are for short/medium trends, EMA 200 for long-term trend.<br/>
        <b>ADX:</b> Measures trend strength. ADX > 25 indicates a strong trend (up or down). < 20 indicates a weak or ranging market.
        """
        story.append(Paragraph(guide_text, styles['Normal']))
        story.append(Spacer(1, 20))

        # Data Methodology
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

        # Disclaimer
        story.append(Paragraph("Disclaimer", styles['Heading2']))
        disclaimer_text = """
        This report is generated by MarketInsight Pro for informational purposes only. 
        It does not constitute financial advice, investment recommendations, or an offer to buy or sell any securities. 
        Trading in financial markets involves a high degree of risk and may not be suitable for all investors. 
        Past performance is not indicative of future results. Please consult with a qualified financial advisor before making any investment decisions.
        """
        story.append(Paragraph(disclaimer_text, styles['Italic']))
        
        # Log the signal
        signal_tracker.log_signal(symbol, ap_decision, indicators.get('current_price', 'N/A'), report_date)
        
        doc.build(story)
        return filepath

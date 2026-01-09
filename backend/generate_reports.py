#!/usr/bin/env python3
"""
Standalone script to generate trading reports for multiple symbols.
This script is designed to be run by GitHub Actions or manually.
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_fetcher import MarketDataFetcher
from app.services.technical_analysis import TechnicalAnalyzer
from app.services.report_generator import ReportGenerator
from app.services.chart_generator import ChartGenerator

def generate_report_for_symbol(symbol, report_date):
    """Generate report for a single symbol."""
    print(f"Generating report for {symbol} on {report_date}...")
    
    try:
        # Fetch market data
        data_fetcher = MarketDataFetcher()
        market_data = data_fetcher.fetch_data(symbol, '3mo')
        
        # Perform technical analysis
        analyzer = TechnicalAnalyzer(market_data)
        indicators = analyzer.calculate_all_indicators()
        trend = analyzer.get_trend()
        signals = analyzer.get_signal()
        support_resistance = analyzer.get_support_resistance()
        patterns = analyzer.get_candlestick_patterns()
        trade_bias = analyzer.get_trade_bias()
        risk_context = analyzer.get_risk_context()
        market_regime = analyzer.get_market_regime()
        position_sizing = analyzer.get_position_sizing()
        overall_signal = analyzer.get_overall_signal()
        action_plan = analyzer.generate_actionable_plan()
        
        timeframe = {
            'data_period': '3 months daily data',
            'analysis_type': 'Swing/Positional (1-5 days)',
            'chart_interval': '1 Day'
        }
        
        # Generate Chart
        chart_generator = ChartGenerator()
        chart_path = chart_generator.generate_chart(symbol, market_data, indicators, support_resistance)

        # Prepare report data
        report_data = {
            'symbol': symbol,
            'date': report_date.strftime('%Y-%m-%d %H:%M:%S'),
            'indicators': indicators,
            'trend': trend,
            'signals': signals,
            'support_resistance': support_resistance,
            'patterns': patterns,
            'chart_path': chart_path,
            'trade_bias': trade_bias,
            'risk_context': risk_context,
            'timeframe': timeframe,
            'market_regime': market_regime,
            'position_sizing': position_sizing,
            'overall_signal': overall_signal,
            'action_plan': action_plan
        }
        
        # Generate PDF
        report_generator = ReportGenerator()
        pdf_path = report_generator.generate_pdf(report_data)
        
        print(f"✅ Report generated for {symbol}: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Error generating report for {symbol}: {str(e)}")
        return None

def main():
    """Main function to generate reports for all symbols."""
    # Symbols to generate reports for
    symbols = ['SENSEX', 'BANKNIFTY', 'NIFTY50']
    
    # Use today's date if no date is provided
    report_date = datetime.now()
    
    # Ensure reports directory exists at repo root
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(repo_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    print(f"Starting report generation...")
    print(f"Report date: {report_date.strftime('%Y-%m-%d')}")
    print(f"Reports will be saved to: {reports_dir}")
    print(f"Generating reports for: {', '.join(symbols)}")
    
    generated_files = []
    for symbol in symbols:
        pdf_path = generate_report_for_symbol(symbol, report_date)
        if pdf_path:
            generated_files.append(pdf_path)
    
    print(f"\nReport generation complete!")
    print(f"Generated {len(generated_files)} out of {len(symbols)} reports.")
    for file in generated_files:
        print(f"- {file}")
    
    return generated_files

if __name__ == "__main__":
    main()

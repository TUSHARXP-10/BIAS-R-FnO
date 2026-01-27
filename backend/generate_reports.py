#!/usr/bin/env python3
"""
Standalone script to generate trading reports for multiple symbols.
This script is designed to be run by GitHub Actions or manually.
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app.services.data_fetcher import MarketDataFetcher
from app.services.technical_analysis import TechnicalAnalyzer
from app.services.report_generator import ReportGenerator
from app.services.chart_generator import ChartGenerator

def generate_report_for_symbol(symbol, report_date, is_weekly=False, name_prefix=None):
    """Generate report for a single symbol."""
    print(f"Generating report for {symbol} on {report_date}...")
    
    try:
        # Fetch market data (use 1 month for weekly reports to get more recent data)
        data_fetcher = MarketDataFetcher()
        data_period = '1mo' if is_weekly else '3mo'
        market_data = data_fetcher.fetch_data(symbol, data_period)
        
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
        
        if is_weekly:
            timeframe = {
                'data_period': '1 month daily data',
                'analysis_type': 'Weekly Consolidated Report',
                'chart_interval': '1 Day'
            }
        else:
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
        pdf_path = report_generator.generate_pdf(report_data, is_weekly, name_prefix)
        
        print(f"✅ Report generated for {symbol}: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Error generating report for {symbol}: {str(e)}")
        return None

def delete_old_reports(reports_dir, keep_latest_only=True):
    if not os.path.exists(reports_dir):
        print(f"Reports directory not found: {reports_dir}")
        return 0
    
    print(f"Deleting old reports from: {reports_dir}")
    files_deleted = 0
    
    # Symbols we generate reports for
    symbols = ['SENSEX', 'BANKNIFTY', 'NIFTY50']
    
    for filename in os.listdir(reports_dir):
        file_path = os.path.join(reports_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.pdf'):
            # If we want to keep the latest, we should ideally check dates
            # But for simplicity and to avoid clutter, we delete all PDFs 
            # and let the generator create fresh ones.
            try:
                os.remove(file_path)
                files_deleted += 1
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
    
    print(f"Deleted {files_deleted} old reports.")
    return files_deleted

def main():
    return main_with_tag()

def run_cleanup():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_reports_dir = os.path.join(repo_root, 'reports')
    backend_reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    os.makedirs(repo_reports_dir, exist_ok=True)
    os.makedirs(backend_reports_dir, exist_ok=True)
    deleted_repo = delete_old_reports(repo_reports_dir)
    deleted_backend = delete_old_reports(backend_reports_dir)
    print(f"Cleanup complete. Repo deleted: {deleted_repo}, Backend deleted: {deleted_backend}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["generate", "cleanup"], default=os.getenv("REPORT_MODE", "generate"))
    parser.add_argument("--run-tag", default=os.getenv("REPORT_TAG"))
    return parser.parse_args()

def run():
    args = parse_args()
    report_date = datetime.now()
    current_day = report_date.strftime('%A').lower()
    
    # Always clean up old reports before generating new ones to avoid "mess"
    run_cleanup()
    
    if args.mode == "cleanup":
        # If only cleanup was requested, we are done
        return []
        
    if args.run_tag == "r1" and current_day in ["saturday", "sunday"]:
        print("Skipping night run on weekend")
        return []
    
    generated_files = main_with_tag(args.run_tag)
    
    # Fail with error code if no reports were generated during a generate run
    if not generated_files:
        print("❌ Error: No reports were generated!")
        sys.exit(1)
        
    return generated_files

def main_with_tag(run_tag=None):
    symbols = ['SENSEX', 'BANKNIFTY', 'NIFTY50']
    report_date = datetime.now()
    current_day = report_date.strftime('%A').lower()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_reports_dir = os.path.join(repo_root, 'reports')
    os.makedirs(repo_reports_dir, exist_ok=True)
    backend_reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    os.makedirs(backend_reports_dir, exist_ok=True)
    generated_files = []
    is_weekend = current_day in ['saturday', 'sunday']
    if is_weekend:
        print("Generating weekly consolidated report for past 5 days...")
        for symbol in symbols:
            pdf_path = generate_report_for_symbol(symbol, report_date, is_weekly=True)
            if pdf_path:
                generated_files.append(pdf_path)
    else:
        print(f"Generating daily reports for: {', '.join(symbols)}")
        for symbol in symbols:
            pdf_path = generate_report_for_symbol(symbol, report_date, is_weekly=False, name_prefix=run_tag)
            if pdf_path:
                generated_files.append(pdf_path)
    print("\nReport generation complete!")
    print(f"Generated {len(generated_files)} out of {len(symbols)} reports.")
    for file in generated_files:
        print(f"- {file}")
    return generated_files

if __name__ == "__main__":
    run()

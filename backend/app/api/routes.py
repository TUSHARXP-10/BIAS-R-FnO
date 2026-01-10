from flask import jsonify, request, send_from_directory, send_file, current_app
from . import bp
from ..services.data_fetcher import MarketDataFetcher
from ..services.technical_analysis import TechnicalAnalyzer
from ..services.report_generator import ReportGenerator
from ..services.chart_generator import ChartGenerator
from datetime import datetime
import os

data_fetcher = MarketDataFetcher()
report_generator = ReportGenerator()
chart_generator = ChartGenerator()

@bp.route('/reports/view/<filename>', methods=['GET'])
def view_report(filename):
    """Serve PDF reports"""
    # Get project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    reports_dir = os.path.join(project_root, 'reports')
    return send_from_directory(reports_dir, filename)

@bp.route('/reports/preview/<filename>/<int:page>', methods=['GET'])
def preview_report_page(filename, page):
    """Render a PDF page to PNG for quick preview"""
    try:
        import fitz
        import io
        # Get project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        reports_dir = os.path.join(project_root, 'reports')
        pdf_path = os.path.join(reports_dir, filename)
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'File not found'}), 404
        doc = fitz.open(pdf_path)
        if page < 1 or page > len(doc):
            return jsonify({'error': 'Invalid page index'}), 400
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = doc.load_page(page - 1).get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")
        return send_file(io.BytesIO(img_bytes), mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'trading-report-generator-api'})

@bp.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """Fetch market data for a symbol"""
    try:
        period = request.args.get('period', '3mo')
        data = data_fetcher.fetch_data(symbol, period)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'data': data.tail(10).to_dict('records'),  # Last 10 candles
            'latest_price': float(data['Close'].iloc[-1])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/reports/generate', methods=['POST'])
def generate_report():
    """Generate trading report with technical analysis"""
    try:
        data = request.json
        symbol = data.get('symbol', 'BANKNIFTY')
        period = data.get('period', '3mo')
        report_date_str = data.get('report_date')
        
        if report_date_str:
            report_datetime = datetime.strptime(report_date_str, '%Y-%m-%d')
        else:
            report_datetime = datetime.now()
        
        # Fetch market data
        market_data = data_fetcher.fetch_data(symbol, period)
        
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
            'data_period': '3 months daily data' if period == '3mo' else period,
            'analysis_type': 'Swing/Positional (1-5 days)',
            'chart_interval': '1 Day'
        }
        
        # Generate Chart
        chart_path = chart_generator.generate_chart(symbol, market_data, indicators, support_resistance)

        # Prepare report data
        report_data = {
            'symbol': symbol,
            'date': report_datetime.strftime('%Y-%m-%d %H:%M:%S'),
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
        
        # Clean up old reports before generating new ones
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        reports_dir = os.path.join(project_root, 'reports')
        
        # Delete all old reports except weekly ones (if any)
        files_deleted = 0
        for filename in os.listdir(reports_dir):
            file_path = os.path.join(reports_dir, filename)
            if os.path.isfile(file_path) and filename.endswith('.pdf'):
                os.remove(file_path)
                files_deleted += 1
        print(f"Deleted {files_deleted} old reports from {reports_dir}")
        
        # Generate PDF
        pdf_path = report_generator.generate_pdf(report_data)
        
        return jsonify({
            'success': True,
            'report_path': pdf_path,
            'data': report_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

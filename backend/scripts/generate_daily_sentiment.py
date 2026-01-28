import os
import sys
import json
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.services.data_fetcher import MarketDataFetcher
from backend.app.services.sentiment_engine import MarketSentimentEngine, SentimentInput

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_and_analyze():
    """
    Orchestrates the data fetching and sentiment analysis.
    Saves the output to 'backend/data/daily_sentiment.json'.
    """
    logger.info("Starting Daily Market Sentiment Analysis...")
    
    fetcher = MarketDataFetcher()
    engine = MarketSentimentEngine()
    
    # 1. Fetch Data
    logger.info("Fetching Market Data...")
    market_summary = fetcher.get_market_summary()
    
    # Extract Global Cues
    us_indices = {}
    asia_markets = {}
    
    if market_summary.get('S&P 500'):
        us_indices['S&P 500'] = market_summary['S&P 500']['change_pct']
    if market_summary.get('NASDAQ'):
        us_indices['NASDAQ'] = market_summary['NASDAQ']['change_pct']
        
    if market_summary.get('NIKKEI'):
        asia_markets['NIKKEI'] = market_summary['NIKKEI']['change_pct']
    if market_summary.get('HANG SENG'):
        asia_markets['HANG SENG'] = market_summary['HANG SENG']['change_pct']

    # Extract Domestic Cues
    vix_change = None
    if market_summary.get('INDIAVIX'):
        vix_change = market_summary['INDIAVIX']['change_pct']
    
    # Note: Advanced data (PCR, OI, FII) would need specialized fetchers or scraping.
    # For now, we use the indices data we have.
    
    # 2. Construct Input
    inputs = SentimentInput(
        us_indices_change_pct=us_indices,
        asia_market_change_pct=asia_markets,
        india_vix_change_pct=vix_change,
        # Default/Placeholder for missing data points
        sensex_prev_close_vs_high_low="MID",
        pcr_total=1.0, # Neutral default
        is_major_event_day=False 
    )
    
    # 3. Analyze
    logger.info("Analyzing Sentiment...")
    output = engine.analyze(inputs)
    
    # 4. Save Output
    output_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "market_sentiment": output.market_sentiment,
        "confidence_score": output.confidence_score,
        "supporting_factors": output.supporting_factors,
        "risk_notes": output.risk_notes,
        "trading_implication": {
            "preferred_strategy": output.trading_implication.preferred_strategy,
            "avoid": output.trading_implication.avoid
        }
    }
    
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    output_path = os.path.join(data_dir, 'daily_sentiment.json')
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    logger.info(f"Sentiment Analysis Complete. Output saved to: {output_path}")
    print(json.dumps(output_data, indent=2))

if __name__ == "__main__":
    fetch_and_analyze()

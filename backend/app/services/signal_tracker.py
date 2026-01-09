import json
from datetime import datetime
import os

class SignalTracker:
    def __init__(self):
        # Ensure the directory for signals_log.json exists
        self.signals_dir = os.path.join(os.getcwd(), 'signals')
        os.makedirs(self.signals_dir, exist_ok=True)
        self.signals_file = os.path.join(self.signals_dir, "signals_log.json")
    
    def log_signal(self, symbol, decision, price, date):
        """Log today's signal for future accuracy check"""
        signal = {
            'symbol': symbol,
            'date': date,
            'decision': decision,
            'entry_price': price,
            'logged_at': datetime.now().isoformat()
        }
        
        # Append to log file
        with open(self.signals_file, 'a') as f:
            f.write(json.dumps(signal) + '\n')
    
    def check_outcome(self, signal_date):
        """Check if signal was correct after 1-3 days"""
        # Compare entry price vs price 1-3 days later
        # Mark as profitable/loss
        pass

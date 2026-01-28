import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ml_service import OptionDecayService

def generate_sample_option_data(symbol='SENSEX', n_rows=100):
    """Generate synthetic option data for testing"""
    base_date = datetime.now()
    dates = [base_date - timedelta(hours=i) for i in range(n_rows)]
    dates.reverse()
    
    # Synthetic underlying price
    underlying_prices = 70000 + np.cumsum(np.random.normal(0, 100, n_rows))
    underlying_df = pd.DataFrame({'Close': underlying_prices}, index=dates)
    
    # Synthetic option data
    strike = 70000
    expiry = base_date + timedelta(hours=24) # Shorter expiry for more decay
    
    option_data = []
    for i, price in enumerate(underlying_prices):
        # Premium decays as time passes and price moves
        tte_days = (expiry - dates[i]).total_seconds() / (24 * 3600)
        
        # If tte is negative, it's expired
        if tte_days < 0:
            premium = max(0, price - strike)
        else:
            intrinsic = max(0, price - strike)
            # Higher time value that decays quickly as tte approaches 0
            time_value = (tte_days * 1000) if tte_days > 0 else 0
            premium = intrinsic + time_value + np.random.normal(0, 5)
        
        option_data.append({
            'Timestamp': dates[i],
            'Close': max(2, premium),
            'Open_Interest': 10000 + np.random.randint(-100, 100),
            'Volume': 5000 + np.random.randint(-500, 500),
            'Strike': strike,
            'Expiry': expiry,
            'Type': 'CALL'
        })
    
    option_df = pd.DataFrame(option_data).set_index('Timestamp')
    return option_df, underlying_df

def test_option_decay():
    print("Testing Option Decay Service...")
    
    service = OptionDecayService()
    symbol = 'SENSEX_OPT'
    
    # 1. Generate synthetic data
    option_df, underlying_df = generate_sample_option_data()
    print(f"Generated {len(option_df)} rows of synthetic option data.")
    
    # 2. Test feature preparation
    print("Testing feature preparation...")
    X, y_class, y_reg = service.prepare_option_features(option_df, underlying_df)
    print(f"Features prepared. Shape: {X.shape}")
    print(f"Target distribution (is_dying): {y_class.value_counts().to_dict()}")
    
    # 3. Test model training
    print("Testing model training...")
    success = service.train_decay_model(symbol, option_df, underlying_df)
    if success:
        print("Option decay models trained successfully.")
    else:
        print("Model training failed.")
        return
        
    # 4. Test prediction
    print("Testing prediction...")
    # Use the last row features for prediction
    last_row = X.iloc[-1].values
    prob = service.predict_decay(symbol, last_row)
    if prob is not None:
        print(f"Probability of high decay regime: {prob:.4f}")
    else:
        print("Prediction failed.")

if __name__ == "__main__":
    test_option_decay()

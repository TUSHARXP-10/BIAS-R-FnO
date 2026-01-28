import os
import pandas as pd
import numpy as np
import lightgbm as lgb
from app.services.technical_analysis import TechnicalAnalyzer
from app.services.data_fetcher import MarketDataFetcher
import joblib
from datetime import datetime, timedelta

class LightGBMService:
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        self.fetcher = MarketDataFetcher()

    def _prepare_features(self, df):
        """Prepare features for LightGBM using TechnicalAnalyzer indicators"""
        df = df.copy()
        
        # Basic Price Features
        df['returns'] = df['Close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        # Technical Indicators
        import talib
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        
        df['rsi'] = talib.RSI(close, timeperiod=14)
        macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        df['macd'] = macd
        df['macd_signal'] = macdsignal
        
        df['ema_20'] = talib.EMA(close, timeperiod=20)
        df['ema_50'] = talib.EMA(close, timeperiod=50)
        
        df['adx'] = talib.ADX(high, low, close, timeperiod=14)
        
        # Target: 1 if next day close is higher, else 0
        df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        # Drop rows with NaN (due to indicators and shift)
        df = df.dropna()
        
        features = ['rsi', 'macd', 'macd_signal', 'ema_20', 'ema_50', 'adx', 'volatility', 'returns']
        return df[features], df['target']

    def train_model(self, symbol, period='2y'):
        """Train a LightGBM model for a specific symbol"""
        print(f"Training LightGBM model for {symbol}...")
        df = self.fetcher.fetch_data(symbol, period=period)
        if df is None or df.empty:
            print(f"No data found for {symbol}")
            return False
            
        X, y = self._prepare_features(df)
        
        # Split into train and test
        train_size = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
        
        params = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'verbose': -1
        }
        
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        model = lgb.train(
            params,
            train_data,
            num_boost_round=100,
            valid_sets=[valid_data],
            callbacks=[lgb.early_stopping(stopping_rounds=10)]
        )
        
        model_path = os.path.join(self.model_dir, f"lgb_{symbol}.pkl")
        joblib.dump(model, model_path)
        return True

    def predict(self, symbol, current_df):
        """Predict the probability of a price increase for the next period"""
        model_path = os.path.join(self.model_dir, f"lgb_{symbol}.pkl")
        if not os.path.exists(model_path):
            success = self.train_model(symbol)
            if not success: return None
                
        model = joblib.load(model_path)
        X, _ = self._prepare_features(current_df)
        if X.empty: return None
            
        latest_features = X.iloc[-1:].values
        prediction_prob = model.predict(latest_features)[0]
        return float(prediction_prob)

    def get_feature_importance(self, symbol):
        """Return feature importance for a symbol's model"""
        model_path = os.path.join(self.model_dir, f"lgb_{symbol}.pkl")
        if not os.path.exists(model_path):
            return None
        model = joblib.load(model_path)
        importance = model.feature_importance(importance_type='gain')
        features = ['rsi', 'macd', 'macd_signal', 'ema_20', 'ema_50', 'adx', 'volatility', 'returns']
        return dict(zip(features, [round(float(v), 2) for v in importance]))

class OptionDecayService:
    """Service to predict option premium decay (BSE-style options)"""
    def __init__(self, model_dir="models/options"):
        self.model_dir = model_dir
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def prepare_option_features(self, option_df, underlying_df):
        """
        Prepare features for option decay prediction.
        option_df: DataFrame with ['Close', 'Open_Interest', 'Volume', 'Strike', 'Expiry', 'Type']
        underlying_df: DataFrame with underlying price data
        """
        df = option_df.copy()
        
        # Ensure dates are datetime
        df['Expiry'] = pd.to_datetime(df['Expiry'])
        
        # 1. Time-to-expiry (TTE)
        # Use index as timestamp if it's datetime, otherwise ensure it's a column
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        df['tte'] = (df['Expiry'] - df.index).dt.total_seconds() / (24 * 3600)
        
        # 2. Moneyness (M = S/K for Calls, K/S for Puts)
        # We need to join with underlying price at the same timestamp
        # underlying_df index should also be DatetimeIndex
        df = df.join(underlying_df['Close'].rename('underlying_price'), how='inner')
        
        def calculate_moneyness(row):
            s = row['underlying_price']
            k = row['Strike']
            if row['Type'].upper() == 'CALL':
                return s / k
            else:
                return k / s
        
        df['moneyness'] = df.apply(calculate_moneyness, axis=1)
        
        # 3. Premium Decay Rate (Target)
        # Target: (Premium_t - Premium_t+1) / Premium_t
        df['decay_rate'] = (df['Close'] - df['Close'].shift(-1)) / df['Close']
        
        # 4. Binary Target: Expires Worthless
        # (Simplified: if price at expiry would be 0 based on current underlying path)
        # For a CALL: if S_expiry <= K, it expires worthless.
        # Since we don't have S_expiry in training, we use a proxy:
        # if decay_rate is very high (> 5% per bar) and tte is low (< 2 days), it's likely dying.
        df['is_dying'] = ((df['decay_rate'] > 0.05) & (df['tte'] < 2.0)).astype(int)
        
        # 5. Volume/OI Ratio
        df['vol_oi_ratio'] = df['Volume'] / (df['Open_Interest'] + 1)
        
        # 6. Underlying Volatility
        df['underlying_vol'] = underlying_df['Close'].pct_change().rolling(window=20).std()
        
        # Drop rows with NaN
        df = df.dropna()
        
        features = ['tte', 'moneyness', 'vol_oi_ratio', 'underlying_vol', 'Close']
        return df[features], df['is_dying'], df['decay_rate']

    def train_decay_model(self, symbol, option_data, underlying_data):
        """Train LightGBM for option decay prediction"""
        X, y_class, y_reg = self.prepare_option_features(option_data, underlying_data)
        
        # Train Classification Model (High Decay Regime)
        params_class = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'verbose': -1
        }
        
        dtrain = lgb.Dataset(X, label=y_class)
        model_class = lgb.train(params_class, dtrain, num_boost_round=100)
        
        # Train Regression Model (Decay Rate)
        params_reg = {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'verbose': -1
        }
        
        dtrain_reg = lgb.Dataset(X, label=y_reg)
        model_reg = lgb.train(params_reg, dtrain_reg, num_boost_round=100)
        
        # Save models
        joblib.dump(model_class, os.path.join(self.model_dir, f"decay_class_{symbol}.pkl"))
        joblib.dump(model_reg, os.path.join(self.model_dir, f"decay_reg_{symbol}.pkl"))
        
        return True

    def predict_decay(self, symbol, current_option_row):
        """
        Predict the probability of high decay regime for an option.
        current_option_row: List or array of features [tte, moneyness, vol_oi_ratio, underlying_vol, Close]
        """
        # Load models
        class_path = os.path.join(self.model_dir, f"decay_class_{symbol}.pkl")
        if not os.path.exists(class_path):
            return None
            
        model_class = joblib.load(class_path)
        
        # Ensure input is 2D
        features = np.array(current_option_row).reshape(1, -1)
        prediction = model_class.predict(features)[0]
        return float(prediction)

    def get_decay_importance(self, symbol):
        """Return feature importance for option decay model"""
        model_path = os.path.join(self.model_dir, f"decay_class_{symbol}.pkl")
        if not os.path.exists(model_path):
            return None
        model = joblib.load(model_path)
        importance = model.feature_importance(importance_type='gain')
        features = ['tte', 'moneyness', 'vol_oi_ratio', 'underlying_vol', 'Close']
        return dict(zip(features, [round(float(v), 2) for v in importance]))

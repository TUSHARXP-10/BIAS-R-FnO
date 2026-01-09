from datetime import datetime
from . import db
import uuid

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    preferences = db.Column(db.JSON)

class MarketData(db.Model):
    __tablename__ = 'market_data'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    open = db.Column(db.Numeric(10, 2))
    high = db.Column(db.Numeric(10, 2))
    low = db.Column(db.Numeric(10, 2))
    close = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.BigInteger)
    __table_args__ = (db.UniqueConstraint('symbol', 'timestamp', name='_symbol_timestamp_uc'),)

class Indicator(db.Model):
    __tablename__ = 'indicators'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    rsi = db.Column(db.Numeric(5, 2))
    macd = db.Column(db.Numeric(10, 4))
    macd_signal = db.Column(db.Numeric(10, 4))
    bb_upper = db.Column(db.Numeric(10, 2))
    bb_lower = db.Column(db.Numeric(10, 2))
    atr = db.Column(db.Numeric(10, 2))
    indicators_json = db.Column(db.JSON)
    __table_args__ = (db.UniqueConstraint('symbol', 'date', name='_symbol_date_uc'),)

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50))
    headline = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    source = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    sentiment_score = db.Column(db.Numeric(3, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    asset_type = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    report_date = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(255))
    metadata_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class IPO(db.Model):
    __tablename__ = 'ipos'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.Date)
    price_range = db.Column(db.String(50))
    lot_size = db.Column(db.Integer)
    subscription_status = db.Column(db.String(100))
    grey_market_premium = db.Column(db.Numeric(10, 2))
    pe_ratio = db.Column(db.Numeric(10, 2))
    data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OptionData(db.Model):
    __tablename__ = 'options_data'
    id = db.Column(db.Integer, primary_key=True)
    underlying_symbol = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    strike_price = db.Column(db.Numeric(10, 2), nullable=False)
    option_type = db.Column(db.String(4), nullable=False) # CALL or PUT
    ltp = db.Column(db.Numeric(10, 2))
    open_interest = db.Column(db.BigInteger)
    delta = db.Column(db.Numeric(5, 4))
    gamma = db.Column(db.Numeric(5, 4))
    theta = db.Column(db.Numeric(5, 4))
    vega = db.Column(db.Numeric(5, 4))
    timestamp = db.Column(db.DateTime, nullable=False)
    __table_args__ = (db.UniqueConstraint('underlying_symbol', 'expiry_date', 'strike_price', 'option_type', 'timestamp', name='_option_uc'),)

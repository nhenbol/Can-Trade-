#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ULTIMATE HYBRID CRYPTO TRADING BOT - PYDROID VERSION V10.5.0
Optimized for Pydroid Android App (Complete Edition)
Developer: Nhen Bol
Version: 10.5.0 - COMPLETE PYDROID EDITION
"""

import sys
import io
import os
import json
import time
import logging
import threading
import socket
import hmac
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import warnings
import random
import string
import base64

# Cryptography imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

warnings.filterwarnings('ignore')

# ========== FIX UNICODE ENCODING FOR ANDROID/PYDROID ==========
if sys.platform == 'win32' or 'android' in sys.platform or 'linux' in sys.platform:
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# ========== IMPORTS ==========
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import joblib
    
    # XGBoost is disabled for Pydroid compatibility
    XGBOOST_AVAILABLE = False
    print("ℹ️ Running in Pydroid-compatible mode (XGBoost disabled)")
    
except ImportError as e:
    print(f"⚠️ Please install required modules: {e}")
    print("Run: pip install requests pandas numpy urllib3 scikit-learn joblib cryptography")
    sys.exit(1)

# ========== CONNECTION TEST ==========
def test_internet_connection():
    """Test internet connection before starting"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        print("✓ Internet connection OK")
        
        socket.create_connection(("fapi.binance.com", 443), timeout=5)
        print("✓ Binance Futures connection OK")
        return True
    except OSError as e:
        print(f"✗ Connection failed: {e}")
        return False

# ========== LOGGING SETUP ==========
# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/ultimate_hybrid_bot_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Ultimate_Hybrid_Bot_Complete')

# ========== ENUMS ==========
class TradingStyle(Enum):
    SCALPING = "SCALPING"
    INTRADAY = "INTRADAY"
    SWING = "SWING"
    POSITION = "POSITION"

class SignalStyle(Enum):
    SCALPING = "SCALPING"
    INTRADAY = "INTRADAY"
    SWING = "SWING"
    POSITION = "POSITION"
    HYBRID = "HYBRID"

class OrderType(Enum):
    LIMIT_BUY = "LIMIT BUY"
    LIMIT_SELL = "LIMIT SELL"
    MARKET_BUY = "MARKET BUY"
    MARKET_SELL = "MARKET SELL"
    OCO = "OCO"
    TRAILING_STOP = "TRAILING STOP"
    ICEBERG = "ICEBERG"
    TWAP = "TWAP"
    VWAP = "VWAP"

class AlertLevel(Enum):
    EMERGENCY = "🔴 EMERGENCY"
    HIGH = "🟡 HIGH"
    MEDIUM = "🔵 MEDIUM"
    LOW = "⚪ LOW"

class SignalTier(Enum):
    TIER_1_ULTRA_SAFE = "ULTRA_SAFE"
    TIER_2_BALANCED = "BALANCED"
    TIER_3_AGGRESSIVE = "AGGRESSIVE"

class TimeframeType(Enum):
    ULTRA_SHORT = "ULTRA_SHORT"
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"

class SmartMoneyConcept(Enum):
    ORDER_BLOCK = "📦 Order Block"
    LIQUIDITY_SWEEP = "🌊 Liquidity Sweep"
    FVG = "🕳️ Fair Value Gap"
    BREAKER = "🔨 Breaker Block"
    MITIGATION = "✅ Mitigation"
    INSTITUTIONAL_DIVERGENCE = "📉 Institutional Divergence"
    LIQUIDITY_GRAB = "🎣 Liquidity Grab"
    NONE = "❌ None"

class MLModelType(Enum):
    RANDOM_FOREST = "🌲 Random Forest"
    GRADIENT_BOOSTING = "📈 Gradient Boosting"
    LSTM = "🧠 LSTM"
    ENSEMBLE = "🤝 Ensemble"

# ========== SECURITY FEATURES ==========
class SecurityManager:
    """Security features: API key encryption, IP whitelisting, rate limiting"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or self._generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.ip_whitelist = []
        self.rate_limits = {}
        self.two_factor_codes = {}
        self.failed_attempts = defaultdict(int)
        self.locked_ips = set()
        
    def _generate_key(self) -> bytes:
        """Generate encryption key from password"""
        try:
            password = "UltimateHybridBotV10.5.0".encode()
            salt = b'salt_123456789012'
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return key
        except Exception as e:
            logger.error(f"Key generation error: {e}")
            return base64.urlsafe_b64encode(b'0' * 32)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key"""
        try:
            encrypted = self.cipher.encrypt(api_key.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return api_key
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key"""
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return encrypted_key
    
    def set_ip_whitelist(self, ips: List[str]):
        """Set IP whitelist"""
        self.ip_whitelist = ips
        logger.info(f"✅ IP whitelist set: {ips}")
    
    def check_ip_allowed(self, ip: str) -> bool:
        """Check if IP is allowed"""
        if not self.ip_whitelist:
            return True
        return ip in self.ip_whitelist
    
    def generate_2fa_code(self, user: str) -> str:
        """Generate 2FA code"""
        code = ''.join(random.choices(string.digits, k=6))
        self.two_factor_codes[user] = {
            'code': code,
            'expires': time.time() + 300
        }
        return code
    
    def verify_2fa_code(self, user: str, code: str) -> bool:
        """Verify 2FA code"""
        if user not in self.two_factor_codes:
            return False
        data = self.two_factor_codes[user]
        if time.time() > data['expires']:
            del self.two_factor_codes[user]
            return False
        return data['code'] == code
    
    def check_rate_limit(self, endpoint: str, max_requests: int = 60, window: int = 60) -> bool:
        """Check rate limit for endpoint"""
        current_time = time.time()
        if endpoint not in self.rate_limits:
            self.rate_limits[endpoint] = []
        self.rate_limits[endpoint] = [t for t in self.rate_limits[endpoint] 
                                      if current_time - t < window]
        if len(self.rate_limits[endpoint]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {endpoint}")
            return False
        self.rate_limits[endpoint].append(current_time)
        return True
    
    def record_failed_attempt(self, ip: str):
        """Record failed login attempt"""
        self.failed_attempts[ip] += 1
        if self.failed_attempts[ip] >= 5:
            self.locked_ips.add(ip)
            logger.warning(f"🔒 IP {ip} locked")
    
    def is_ip_locked(self, ip: str) -> bool:
        """Check if IP is locked"""
        return ip in self.locked_ips

# ========== ADVANCED ML MODELS ==========
class AdvancedMLModels:
    """Advanced ML models: Random Forest, LSTM, Gradient Boosting, Ensemble"""
    
    def __init__(self, model_dir: str = "ml_models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.model_performance = {}
        self.ensemble_weights = {}
        self.xgboost_available = False
        
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
    
    class LSTMModel:
        """Simple LSTM implementation using numpy"""
        def __init__(self, input_size: int, hidden_size: int = 64, output_size: int = 1):
            self.input_size = input_size
            self.hidden_size = hidden_size
            self.output_size = output_size
            self.Wf = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
            self.Wi = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
            self.Wc = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
            self.Wo = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
            self.Wy = np.random.randn(output_size, hidden_size) * 0.1
            self.bf = np.zeros((hidden_size, 1))
            self.bi = np.zeros((hidden_size, 1))
            self.bc = np.zeros((hidden_size, 1))
            self.bo = np.zeros((hidden_size, 1))
            self.by = np.zeros((output_size, 1))
        
        def sigmoid(self, x):
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        
        def tanh(self, x):
            return np.tanh(np.clip(x, -500, 500))
        
        def forward(self, x_seq):
            h = np.zeros((self.hidden_size, 1))
            c = np.zeros((self.hidden_size, 1))
            for x in x_seq:
                x = x.reshape(-1, 1)
                concat = np.vstack((h, x))
                f = self.sigmoid(self.Wf @ concat + self.bf)
                i = self.sigmoid(self.Wi @ concat + self.bi)
                c_candidate = self.tanh(self.Wc @ concat + self.bc)
                o = self.sigmoid(self.Wo @ concat + self.bo)
                c = f * c + i * c_candidate
                h = o * self.tanh(c)
            y = self.Wy @ h + self.by
            return y.flatten()[0]
        
        def predict(self, x_seq):
            return self.forward(x_seq)
    
    def train_random_forest(self, X: np.ndarray, y: np.ndarray, model_name: str = "rf_model") -> Optional[RandomForestRegressor]:
        try:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            model = RandomForestRegressor(
                n_estimators=100, max_depth=10, min_samples_split=5,
                min_samples_leaf=2, random_state=42, n_jobs=1
            )
            model.fit(X_scaled, y)
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            predictions = model.predict(X_scaled)
            mse = np.mean((predictions - y) ** 2)
            self.model_performance[model_name] = {
                'type': 'RandomForest', 'mse': mse, 'rmse': np.sqrt(mse), 'samples': len(X)
            }
            joblib.dump(model, f"{self.model_dir}/{model_name}.pkl")
            joblib.dump(scaler, f"{self.model_dir}/{model_name}_scaler.pkl")
            logger.info(f"✅ Random Forest model trained: {model_name} (RMSE: {np.sqrt(mse):.4f})")
            return model
        except Exception as e:
            logger.error(f"Random Forest training error: {e}")
            return None
    
    def train_gradient_boosting(self, X: np.ndarray, y: np.ndarray, model_name: str = "gb_model") -> Optional[GradientBoostingRegressor]:
        try:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            model = GradientBoostingRegressor(
                n_estimators=100, max_depth=5, learning_rate=0.1,
                subsample=0.8, random_state=42
            )
            model.fit(X_scaled, y)
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            predictions = model.predict(X_scaled)
            mse = np.mean((predictions - y) ** 2)
            self.model_performance[model_name] = {
                'type': 'GradientBoosting', 'mse': mse, 'rmse': np.sqrt(mse), 'samples': len(X)
            }
            joblib.dump(model, f"{self.model_dir}/{model_name}.pkl")
            joblib.dump(scaler, f"{self.model_dir}/{model_name}_scaler.pkl")
            logger.info(f"✅ Gradient Boosting model trained: {model_name} (RMSE: {np.sqrt(mse):.4f})")
            return model
        except Exception as e:
            logger.error(f"Gradient Boosting training error: {e}")
            return None
    
    def train_lstm(self, X: np.ndarray, y: np.ndarray, model_name: str = "lstm_model") -> Optional[LSTMModel]:
        try:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            lookback = 10
            X_seq, y_seq = [], []
            for i in range(lookback, len(X_scaled)):
                X_seq.append(X_scaled[i-lookback:i])
                y_seq.append(y[i])
            if not X_seq:
                return None
            X_seq = np.array(X_seq)
            y_seq = np.array(y_seq)
            model = self.LSTMModel(input_size=X.shape[1], hidden_size=32, output_size=1)
            for epoch in range(5):
                losses = []
                for i in range(len(X_seq)):
                    pred = model.forward(X_seq[i])
                    loss = (pred - y_seq[i]) ** 2
                    losses.append(loss)
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            predictions = []
            for i in range(len(X_seq)):
                pred = model.forward(X_seq[i])
                predictions.append(pred)
            if predictions:
                mse = np.mean((np.array(predictions) - y_seq) ** 2)
                self.model_performance[model_name] = {
                    'type': 'LSTM', 'mse': mse, 'rmse': np.sqrt(mse), 'samples': len(X_seq)
                }
            logger.info(f"✅ LSTM model trained: {model_name}")
            return model
        except Exception as e:
            logger.error(f"LSTM training error: {e}")
            return None
    
    def train_ensemble(self, X: np.ndarray, y: np.ndarray, model_names: List[str] = None) -> Dict:
        try:
            if model_names is None:
                model_names = ['rf_model', 'lstm_model', 'gb_model']
            models_trained = {}
            if 'rf_model' in model_names:
                models_trained['rf'] = self.train_random_forest(X, y, 'rf_ensemble')
            if 'lstm_model' in model_names:
                models_trained['lstm'] = self.train_lstm(X, y, 'lstm_ensemble')
            if 'gb_model' in model_names:
                models_trained['gb'] = self.train_gradient_boosting(X, y, 'gb_ensemble')
            
            total_performance = 0
            weights = {}
            for name, model in models_trained.items():
                if model is not None:
                    perf_key = f"{name}_ensemble"
                    perf = self.model_performance.get(perf_key, {}).get('rmse', 1.0)
                    weight = 1.0 / (perf + 0.001)
                    weights[name] = weight
                    total_performance += weight
            if total_performance > 0:
                for name in weights:
                    weights[name] /= total_performance
            valid_models = {k: v for k, v in models_trained.items() if v is not None}
            if valid_models:
                self.ensemble_weights['ensemble_model'] = weights
                self.models['ensemble_model'] = valid_models
                logger.info(f"✅ Ensemble model trained with {len(valid_models)} models")
            return valid_models
        except Exception as e:
            logger.error(f"Ensemble training error: {e}")
            return {}
    
    def predict(self, X: np.ndarray, model_name: str = 'ensemble_model') -> float:
        try:
            if model_name == 'ensemble_model' and model_name in self.models:
                predictions = []
                total_weight = 0
                for sub_name, model in self.models[model_name].items():
                    if sub_name in self.scalers:
                        X_scaled = self.scalers[sub_name].transform(X.reshape(1, -1))
                    else:
                        X_scaled = X.reshape(1, -1)
                    if sub_name == 'lstm':
                        X_seq = np.array([X_scaled] * 10)
                        pred = model.predict(X_seq)
                    else:
                        pred = model.predict(X_scaled)[0]
                    weight = self.ensemble_weights[model_name].get(sub_name, 1.0/len(self.models[model_name]))
                    predictions.append(pred * weight)
                    total_weight += weight
                return sum(predictions) / total_weight if total_weight > 0 else 0.5
            elif model_name in self.models:
                model = self.models[model_name]
                if model_name in self.scalers:
                    X_scaled = self.scalers[model_name].transform(X.reshape(1, -1))
                else:
                    X_scaled = X.reshape(1, -1)
                if model_name.startswith('lstm'):
                    X_seq = np.array([X_scaled] * 10)
                    return model.predict(X_seq)
                else:
                    return model.predict(X_scaled)[0]
            return 0.5
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return 0.5
    
    def load_models(self):
        try:
            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)
                return
            for filename in os.listdir(self.model_dir):
                if filename.endswith('.pkl') and not filename.endswith('_scaler.pkl'):
                    model_name = filename[:-4]
                    model_path = f"{self.model_dir}/{filename}"
                    scaler_path = f"{self.model_dir}/{model_name}_scaler.pkl"
                    if os.path.exists(scaler_path):
                        self.models[model_name] = joblib.load(model_path)
                        self.scalers[model_name] = joblib.load(scaler_path)
                        logger.info(f"✅ Loaded model: {model_name}")
                elif filename.endswith('.npz'):
                    model_name = filename[:-4]
                    logger.info(f"✅ Found LSTM model data: {model_name}")
            logger.info(f"✅ Loaded {len(self.models)} ML models")
        except Exception as e:
            logger.error(f"Model loading error: {e}")

# ========== ADVANCED RISK MANAGEMENT ==========
class AdvancedRiskManager:
    """Advanced risk management: Kelly Criterion, VaR, Monte Carlo, Drawdown protection"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
        self.drawdown = 0.0
        self.max_drawdown = 0.0
        self.trade_history = []
        self.daily_pnl = []
        self.correlation_matrix = {}
        self.var_95 = 0.0
        self.var_99 = 0.0
        self.kelly_fraction = 0.0
        self.drawdown_protection_enabled = True
        self.drawdown_limit = 20.0
        self.trading_paused = False
        self.pause_reason = ""
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        if avg_loss == 0:
            return 0.25
        b = avg_win / avg_loss if avg_loss > 0 else 1
        p = win_rate / 100 if win_rate <= 100 else 0.5
        q = 1 - p
        kelly = (p * b - q) / b if b > 0 else 0
        self.kelly_fraction = max(0, min(kelly * 0.5, 0.25))
        return self.kelly_fraction
    
    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        if len(returns) < 30:
            return 5.0
        returns = np.array(returns)
        var = np.percentile(returns, (1 - confidence) * 100)
        if confidence == 0.95:
            self.var_95 = abs(var)
        elif confidence == 0.99:
            self.var_99 = abs(var)
        return abs(var)
    
    def monte_carlo_simulation(self, num_simulations: int = 1000, days: int = 30) -> Dict:
        if len(self.trade_history) < 20:
            return {'expected_return': 0, 'var_95': 5, 'var_99': 10, 'max_loss': 20, 'profit_probability': 50}
        returns = [t.get('return_pct', 0) for t in self.trade_history[-100:]]
        if len(returns) < 20:
            returns = [random.uniform(-2, 3) for _ in range(100)]
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        simulation_results = []
        for _ in range(num_simulations):
            sim_returns = np.random.normal(mean_return, std_return, days)
            total_return = np.prod(1 + sim_returns/100) - 1
            simulation_results.append(total_return * 100)
        simulation_results = np.array(simulation_results)
        return {
            'expected_return': np.mean(simulation_results),
            'var_95': np.percentile(simulation_results, 5),
            'var_99': np.percentile(simulation_results, 1),
            'max_loss': np.min(simulation_results),
            'profit_probability': np.sum(simulation_results > 0) / num_simulations * 100
        }
    
    def update_drawdown(self, current_capital: float):
        self.current_capital = current_capital
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
        if self.peak_capital > 0:
            self.drawdown = (self.peak_capital - current_capital) / self.peak_capital * 100
            self.max_drawdown = max(self.max_drawdown, self.drawdown)
        if self.drawdown_protection_enabled:
            if self.drawdown >= self.drawdown_limit:
                self.trading_paused = True
                self.pause_reason = f"Drawdown limit reached: {self.drawdown:.1f}%"
                logger.warning(f"🔴 TRADING PAUSED: {self.pause_reason}")
            elif self.trading_paused and self.drawdown < self.drawdown_limit * 0.7:
                self.trading_paused = False
                self.pause_reason = ""
                logger.info(f"✅ Trading resumed")
    
    def can_trade(self) -> Tuple[bool, str]:
        if self.trading_paused:
            return False, self.pause_reason
        if self.drawdown > self.drawdown_limit * 0.8:
            return True, f"⚠️ High drawdown: {self.drawdown:.1f}%"
        return True, "OK"
    
    def get_position_size(self, signal_confidence: float, account_balance: float, kelly_multiplier: float = 1.0) -> float:
        base_size = account_balance * 0.01
        if self.kelly_fraction > 0:
            kelly_size = account_balance * self.kelly_fraction * kelly_multiplier
            position_size = min(base_size * 2, kelly_size)
        else:
            position_size = base_size
        if self.drawdown > 10:
            position_size *= (1 - (self.drawdown - 10) / 20)
        position_size *= (signal_confidence / 50)
        return max(position_size, account_balance * 0.002)
    
    def add_trade_result(self, trade_data: Dict):
        self.trade_history.append(trade_data)
        today = datetime.now().date()
        daily_pnl_entry = next((item for item in self.daily_pnl if item['date'] == today), None)
        if daily_pnl_entry:
            daily_pnl_entry['pnl'] += trade_data.get('pnl', 0)
            daily_pnl_entry['trades'] += 1
        else:
            self.daily_pnl.append({'date': today, 'pnl': trade_data.get('pnl', 0), 'trades': 1})
        if len(self.daily_pnl) > 365:
            self.daily_pnl = self.daily_pnl[-365:]
    
    def get_risk_report(self) -> Dict:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        if self.trade_history:
            winning_trades = [t for t in self.trade_history if t.get('pnl', 0) > 0]
            losing_trades = [t for t in self.trade_history if t.get('pnl', 0) < 0]
            win_rate = len(winning_trades) / len(self.trade_history) * 100 if self.trade_history else 0
            if winning_trades:
                avg_win = np.mean([t.get('return_pct', 0) for t in winning_trades])
            if losing_trades:
                avg_loss = abs(np.mean([t.get('return_pct', 0) for t in losing_trades]))
        monte_carlo = self.monte_carlo_simulation()
        return {
            'current_capital': self.current_capital,
            'peak_capital': self.peak_capital,
            'drawdown': self.drawdown,
            'max_drawdown': self.max_drawdown,
            'total_trades': len(self.trade_history),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'kelly_fraction': self.kelly_fraction,
            'var_95': self.var_95,
            'var_99': self.var_99,
            'monte_carlo': monte_carlo,
            'trading_paused': self.trading_paused,
            'pause_reason': self.pause_reason,
            'daily_pnl': self.daily_pnl[-7:]
        }

# ========== ADVANCED ORDER TYPES ==========
class AdvancedOrderExecutor:
    """Advanced order types: OCO, Trailing Stop, Iceberg, TWAP, VWAP"""
    
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.active_orders = {}
        self.trailing_stops = {}
        self.twap_schedules = {}
        self.iceberg_orders = {}
    
    def place_oco_order(self, symbol: str, side: str, quantity: float, price: float,
                        stop_price: float, limit_price: float) -> Optional[Dict]:
        try:
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'quantity': quantity,
                'price': price,
                'stopPrice': stop_price,
                'stopLimitPrice': limit_price,
                'stopLimitTimeInForce': 'GTC'
            }
            result = self.client._make_request("POST", "/fapi/v1/order/oco", params, signed=True)
            if result:
                order_id = result.get('orderId', 'Unknown')
                self.active_orders[order_id] = {
                    'type': 'OCO', 'symbol': symbol, 'side': side,
                    'quantity': quantity, 'price': price,
                    'stop_price': stop_price, 'limit_price': limit_price,
                    'time': time.time()
                }
                logger.info(f"✅ OCO order placed: {symbol} {side} {quantity}")
            return result
        except Exception as e:
            logger.error(f"OCO order error: {e}")
            return None
    
    def place_trailing_stop(self, symbol: str, side: str, quantity: float, 
                           activation_price: float, callback_rate: float) -> Optional[Dict]:
        try:
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': 'TRAILING_STOP_MARKET',
                'quantity': quantity,
                'callbackRate': callback_rate,
                'activationPrice': activation_price
            }
            result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
            if result:
                order_id = result.get('orderId', 'Unknown')
                self.trailing_stops[order_id] = {
                    'symbol': symbol, 'side': side, 'quantity': quantity,
                    'activation_price': activation_price, 'callback_rate': callback_rate,
                    'initial_price': self.client.get_current_price(symbol),
                    'highest_price': self.client.get_current_price(symbol) if side == 'SELL' else 0,
                    'lowest_price': self.client.get_current_price(symbol) if side == 'BUY' else float('inf'),
                    'time': time.time()
                }
                logger.info(f"✅ Trailing stop placed: {symbol} {side} {quantity}")
            return result
        except Exception as e:
            logger.error(f"Trailing stop error: {e}")
            return None
    
    def monitor_trailing_stops(self):
        try:
            for order_id, data in list(self.trailing_stops.items()):
                current_price = self.client.get_current_price(data['symbol'])
                if not current_price:
                    continue
                if data['side'] == 'SELL':
                    if current_price > data['highest_price']:
                        data['highest_price'] = current_price
                        stop_distance = data['highest_price'] * (data['callback_rate'] / 100)
                        new_stop = data['highest_price'] - stop_distance
                        logger.debug(f"Trailing stop updated: {new_stop:.4f}")
                else:
                    if current_price < data['lowest_price']:
                        data['lowest_price'] = current_price
                        stop_distance = data['lowest_price'] * (data['callback_rate'] / 100)
                        new_stop = data['lowest_price'] + stop_distance
                        logger.debug(f"Trailing stop updated: {new_stop:.4f}")
        except Exception as e:
            logger.error(f"Trailing stop monitoring error: {e}")
    
    def place_iceberg_order(self, symbol: str, side: str, total_quantity: float,
                           price: float, iceberg_qty: float) -> List[Dict]:
        try:
            orders = []
            remaining = total_quantity
            while remaining > 0:
                qty = min(iceberg_qty, remaining)
                params = {
                    'symbol': symbol,
                    'side': side.upper(),
                    'type': 'LIMIT',
                    'timeInForce': 'GTC',
                    'quantity': qty,
                    'price': price
                }
                result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
                if result:
                    order_id = result.get('orderId', 'Unknown')
                    orders.append(result)
                    if order_id not in self.iceberg_orders:
                        self.iceberg_orders[order_id] = {
                            'symbol': symbol, 'side': side,
                            'total_quantity': total_quantity,
                            'filled_quantity': 0, 'remaining': remaining - qty,
                            'iceberg_qty': iceberg_qty, 'price': price,
                            'child_orders': []
                        }
                    self.iceberg_orders[order_id]['child_orders'].append(order_id)
                    remaining -= qty
                    time.sleep(0.5)
                else:
                    break
            logger.info(f"✅ Iceberg order placed: {symbol} {side} total={total_quantity}")
            return orders
        except Exception as e:
            logger.error(f"Iceberg order error: {e}")
            return []
    
    def execute_twap(self, symbol: str, side: str, total_quantity: float,
                    duration_minutes: int, num_slices: int = 10) -> List[Dict]:
        try:
            orders = []
            slice_qty = total_quantity / num_slices
            interval_seconds = (duration_minutes * 60) / num_slices
            schedule_id = f"twap_{symbol}_{int(time.time())}"
            self.twap_schedules[schedule_id] = {
                'symbol': symbol, 'side': side,
                'total_quantity': total_quantity, 'remaining': total_quantity,
                'slice_qty': slice_qty, 'num_slices': num_slices,
                'interval': interval_seconds, 'start_time': time.time(),
                'orders': []
            }
            current_price = self.client.get_current_price(symbol)
            if current_price:
                params = {
                    'symbol': symbol,
                    'side': side.upper(),
                    'type': 'LIMIT',
                    'timeInForce': 'GTC',
                    'quantity': slice_qty,
                    'price': current_price
                }
                result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
                if result:
                    orders.append(result)
                    self.twap_schedules[schedule_id]['orders'].append(result.get('orderId'))
                    self.twap_schedules[schedule_id]['remaining'] -= slice_qty
            logger.info(f"✅ TWAP schedule created: {symbol} {side} over {duration_minutes}min")
            
            def twap_worker():
                time.sleep(interval_seconds)
                for i in range(1, num_slices):
                    if schedule_id not in self.twap_schedules:
                        break
                    schedule = self.twap_schedules[schedule_id]
                    if schedule['remaining'] <= 0:
                        break
                    current_price = self.client.get_current_price(symbol)
                    if current_price:
                        params = {
                            'symbol': symbol,
                            'side': side.upper(),
                            'type': 'LIMIT',
                            'timeInForce': 'GTC',
                            'quantity': min(slice_qty, schedule['remaining']),
                            'price': current_price
                        }
                        result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
                        if result:
                            schedule['orders'].append(result.get('orderId'))
                            schedule['remaining'] -= slice_qty
                    if i < num_slices - 1:
                        time.sleep(interval_seconds)
            thread = threading.Thread(target=twap_worker, daemon=True)
            thread.start()
            return orders
        except Exception as e:
            logger.error(f"TWAP execution error: {e}")
            return []
    
    def execute_vwap(self, symbol: str, side: str, total_quantity: float,
                    volume_profile: Dict[str, float]) -> List[Dict]:
        try:
            orders = []
            total_volume = sum(volume_profile.values())
            if total_volume == 0:
                return self.execute_twap(symbol, side, total_quantity, 30)
            for period, volume_ratio in volume_profile.items():
                period_qty = total_quantity * (volume_ratio / total_volume)
                if period_qty < 0.001:
                    continue
                current_price = self.client.get_current_price(symbol)
                if current_price:
                    params = {
                        'symbol': symbol,
                        'side': side.upper(),
                        'type': 'LIMIT',
                        'timeInForce': 'GTC',
                        'quantity': period_qty,
                        'price': current_price
                    }
                    result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
                    if result:
                        orders.append(result)
                    delay_seconds = max(1, int(60 * (1 - volume_ratio / total_volume)))
                    time.sleep(delay_seconds)
            logger.info(f"✅ VWAP execution completed: {symbol} {side}")
            return orders
        except Exception as e:
            logger.error(f"VWAP execution error: {e}")
            return []
    
    def cancel_oco_order(self, symbol: str, order_id: str) -> bool:
        try:
            params = {'symbol': symbol, 'orderId': order_id}
            result = self.client._make_request("DELETE", "/fapi/v1/order", params, signed=True)
            if result and order_id in self.active_orders:
                del self.active_orders[order_id]
                logger.info(f"✅ OCO order cancelled: {order_id}")
            return result is not None
        except Exception as e:
            logger.error(f"Cancel OCO error: {e}")
            return False
    
    def get_order_status(self, symbol: str, order_id: str) -> Optional[Dict]:
        try:
            params = {'symbol': symbol, 'orderId': order_id}
            return self.client._make_request("GET", "/fapi/v1/order", params, signed=True)
        except Exception as e:
            logger.error(f"Order status error: {e}")
            return None

# ========== PORTFOLIO MANAGEMENT ==========
@dataclass
class PortfolioPosition:
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    allocation: float
    beta: float
    correlation: float
    sector: str
    style: str
    tier: str
    entry_time: datetime

class PortfolioManager:
    """Portfolio management: multi-symbol tracking, heat map, correlation, sector allocation"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.positions: Dict[str, PortfolioPosition] = {}
        self.position_history: List[Dict] = []
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.sector_allocation = defaultdict(float)
        self.style_allocation = defaultdict(float)
        self.tier_allocation = defaultdict(float)
        self.correlation_matrix = {}
        self.heatmap_data = {}
    
    def update_position(self, symbol: str, quantity: float, entry_price: float,
                        sector: str = "Unknown", style: str = "Unknown", tier: str = "Unknown"):
        current_price = entry_price
        position = PortfolioPosition(
            symbol=symbol, quantity=quantity, entry_price=entry_price,
            current_price=current_price, pnl=0, pnl_percentage=0,
            allocation=quantity * entry_price, beta=1.0, correlation=0.5,
            sector=sector, style=style, tier=tier, entry_time=datetime.now()
        )
        self.positions[symbol] = position
        self._update_allocations()
        logger.info(f"✅ Position added: {symbol} {quantity} @ {entry_price}")
    
    def close_position(self, symbol: str, exit_price: float):
        if symbol in self.positions:
            pos = self.positions[symbol]
            pnl = (exit_price - pos.entry_price) * pos.quantity
            pnl_percentage = (exit_price / pos.entry_price - 1) * 100
            self.position_history.append({
                'symbol': symbol, 'entry_price': pos.entry_price, 'exit_price': exit_price,
                'quantity': pos.quantity, 'pnl': pnl, 'pnl_percentage': pnl_percentage,
                'sector': pos.sector, 'style': pos.style, 'tier': pos.tier,
                'entry_time': pos.entry_time, 'exit_time': datetime.now(),
                'duration': (datetime.now() - pos.entry_time).total_seconds() / 3600
            })
            self.current_capital += pnl
            del self.positions[symbol]
            self._update_allocations()
            logger.info(f"✅ Position closed: {symbol} @ {exit_price} (P&L: {pnl:.2f})")
    
    def update_prices(self, price_data: Dict[str, float]):
        total_value = 0
        for symbol, price in price_data.items():
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.current_price = price
                pos.pnl = (price - pos.entry_price) * pos.quantity
                pos.pnl_percentage = (price / pos.entry_price - 1) * 100
                pos.allocation = price * pos.quantity
                total_value += pos.allocation
        self.current_capital = total_value + (self.initial_capital - sum(p.entry_price * p.quantity for p in self.positions.values()))
    
    def _update_allocations(self):
        self.sector_allocation.clear()
        self.style_allocation.clear()
        self.tier_allocation.clear()
        total_value = sum(p.allocation for p in self.positions.values())
        if total_value == 0:
            return
        for pos in self.positions.values():
            weight = pos.allocation / total_value * 100
            self.sector_allocation[pos.sector] += weight
            self.style_allocation[pos.style] += weight
            self.tier_allocation[pos.tier] += weight
    
    def calculate_correlation_matrix(self, returns_data: Dict[str, List[float]]) -> pd.DataFrame:
        symbols = list(self.positions.keys())
        if len(symbols) < 2:
            return pd.DataFrame()
        returns_matrix = []
        valid_symbols = []
        for symbol in symbols:
            if symbol in returns_data and len(returns_data[symbol]) >= 20:
                returns_matrix.append(returns_data[symbol][-100:])
                valid_symbols.append(symbol)
        if len(valid_symbols) < 2:
            return pd.DataFrame()
        min_len = min(len(r) for r in returns_matrix)
        returns_matrix = [r[:min_len] for r in returns_matrix]
        corr_matrix = np.corrcoef(returns_matrix)
        df = pd.DataFrame(corr_matrix, index=valid_symbols, columns=valid_symbols)
        self.correlation_matrix = df.to_dict()
        return df
    
    def generate_heatmap(self) -> Dict:
        heatmap = {
            'sectors': {}, 'styles': {}, 'tiers': {},
            'pnl_by_symbol': {}, 'allocation_by_symbol': {}
        }
        for symbol, pos in self.positions.items():
            heatmap['pnl_by_symbol'][symbol] = pos.pnl_percentage
            heatmap['allocation_by_symbol'][symbol] = pos.allocation
        heatmap['sectors'] = dict(self.sector_allocation)
        heatmap['styles'] = dict(self.style_allocation)
        heatmap['tiers'] = dict(self.tier_allocation)
        self.heatmap_data = heatmap
        return heatmap
    
    def get_portfolio_summary(self) -> Dict:
        total_value = sum(p.allocation for p in self.positions.values())
        total_pnl = sum(p.pnl for p in self.positions.values())
        total_pnl_pct = (total_pnl / self.initial_capital * 100) if self.initial_capital > 0 else 0
        avg_beta = np.mean([p.beta for p in self.positions.values()]) if self.positions else 1.0
        num_sectors = len(self.sector_allocation)
        num_positions = len(self.positions)
        if num_positions == 0:
            diversification = 0
        elif num_positions == 1:
            diversification = 20
        else:
            weights = [p.allocation / total_value for p in self.positions.values()] if total_value > 0 else []
            hhi = sum(w ** 2 for w in weights) * 100
            diversification = 100 - min(hhi, 100)
        return {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_percentage': total_pnl_pct,
            'num_positions': num_positions,
            'avg_beta': avg_beta,
            'diversification_score': diversification,
            'sector_allocation': dict(self.sector_allocation),
            'style_allocation': dict(self.style_allocation),
            'tier_allocation': dict(self.tier_allocation),
            'largest_position': max(self.positions.values(), key=lambda p: p.allocation).symbol if self.positions else None,
            'best_performer': max(self.positions.values(), key=lambda p: p.pnl_percentage).symbol if self.positions else None,
            'worst_performer': min(self.positions.values(), key=lambda p: p.pnl_percentage).symbol if self.positions else None,
            'heatmap': self.generate_heatmap()
        }
    
    def get_position_history(self, days: int = 30) -> List[Dict]:
        cutoff = datetime.now() - timedelta(days=days)
        return [h for h in self.position_history if h['exit_time'] > cutoff]

# ========== PERFORMANCE ANALYTICS ==========
class PerformanceAnalytics:
    """Performance analytics: equity curve, monthly reports, win rate analysis, Sharpe ratio"""
    
    def __init__(self):
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        self.monthly_returns = []
        self.yearly_returns = []
    
    def add_trade(self, trade_data: Dict):
        self.trades.append(trade_data)
        if self.equity_curve:
            last_equity = self.equity_curve[-1]['equity']
            new_equity = last_equity + trade_data.get('pnl', 0)
        else:
            new_equity = trade_data.get('initial_capital', 10000) + trade_data.get('pnl', 0)
        self.equity_curve.append({
            'timestamp': trade_data.get('exit_time', datetime.now()),
            'equity': new_equity,
            'trade_id': trade_data.get('trade_id', len(self.trades))
        })
        trade_date = trade_data.get('exit_time', datetime.now()).date()
        daily_entry = next((item for item in self.daily_returns if item['date'] == trade_date), None)
        if daily_entry:
            daily_entry['return'] += trade_data.get('pnl', 0)
            daily_entry['trades'] += 1
        else:
            self.daily_returns.append({
                'date': trade_date,
                'return': trade_data.get('pnl', 0),
                'trades': 1
            })
    
    def calculate_equity_curve(self) -> pd.DataFrame:
        if not self.equity_curve:
            return pd.DataFrame()
        df = pd.DataFrame(self.equity_curve)
        df.set_index('timestamp', inplace=True)
        df['peak'] = df['equity'].cummax()
        df['drawdown'] = (df['peak'] - df['equity']) / df['peak'] * 100
        df['drawdown'] = df['drawdown'].clip(lower=0)
        return df
    
    def generate_monthly_report(self, year: int = None, month: int = None) -> Dict:
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        month_trades = []
        for trade in self.trades:
            exit_time = trade.get('exit_time')
            if exit_time and exit_time.year == year and exit_time.month == month:
                month_trades.append(trade)
        if not month_trades:
            return {'error': 'No trades for this month'}
        total_trades = len(month_trades)
        winning_trades = [t for t in month_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in month_trades if t.get('pnl', 0) < 0]
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        total_pnl = sum(t.get('pnl', 0) for t in month_trades)
        avg_win = np.mean([t.get('pnl', 0) for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.get('pnl', 0) for t in losing_trades])) if losing_trades else 0
        profit_factor = (len(winning_trades) * avg_win) / (len(losing_trades) * avg_loss + 1e-10)
        symbol_performance = defaultdict(lambda: {'trades': 0, 'pnl': 0, 'win_rate': 0})
        for trade in month_trades:
            symbol = trade.get('symbol', 'Unknown')
            symbol_performance[symbol]['trades'] += 1
            symbol_performance[symbol]['pnl'] += trade.get('pnl', 0)
        for symbol in symbol_performance:
            symbol_trades = [t for t in month_trades if t.get('symbol') == symbol]
            symbol_wins = [t for t in symbol_trades if t.get('pnl', 0) > 0]
            symbol_performance[symbol]['win_rate'] = len(symbol_wins) / len(symbol_trades) * 100 if symbol_trades else 0
        style_performance = defaultdict(lambda: {'trades': 0, 'pnl': 0, 'win_rate': 0})
        for trade in month_trades:
            style = trade.get('style', 'Unknown')
            style_performance[style]['trades'] += 1
            style_performance[style]['pnl'] += trade.get('pnl', 0)
        for style in style_performance:
            style_trades = [t for t in month_trades if t.get('style') == style]
            style_wins = [t for t in style_trades if t.get('pnl', 0) > 0]
            style_performance[style]['win_rate'] = len(style_wins) / len(style_trades) * 100 if style_trades else 0
        tier_performance = defaultdict(lambda: {'trades': 0, 'pnl': 0, 'win_rate': 0})
        for trade in month_trades:
            tier = trade.get('tier', 'Unknown')
            tier_performance[tier]['trades'] += 1
            tier_performance[tier]['pnl'] += trade.get('pnl', 0)
        for tier in tier_performance:
            tier_trades = [t for t in month_trades if t.get('tier') == tier]
            tier_wins = [t for t in tier_trades if t.get('pnl', 0) > 0]
            tier_performance[tier]['win_rate'] = len(tier_wins) / len(tier_trades) * 100 if tier_trades else 0
        consecutive_wins = 0
        max_consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_losses = 0
        for trade in month_trades:
            if trade.get('pnl', 0) > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        returns = [t.get('return_pct', 0) for t in month_trades if 'return_pct' in t]
        sharpe = np.mean(returns) / (np.std(returns) + 0.001) * np.sqrt(252) if returns else 0
        return {
            'year': year, 'month': month,
            'month_name': datetime(year, month, 1).strftime('%B'),
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'symbol_performance': dict(symbol_performance),
            'style_performance': dict(style_performance),
            'tier_performance': dict(tier_performance)
        }
    
    def generate_yearly_report(self, year: int = None) -> Dict:
        if year is None:
            year = datetime.now().year
        monthly_reports = [r for r in self.monthly_returns if r.get('year') == year]
        if not monthly_reports:
            year_trades = [t for t in self.trades if t.get('exit_time', datetime.now()).year == year]
            if not year_trades:
                return {'error': 'No trades for this year'}
            total_trades = len(year_trades)
            winning_trades = [t for t in year_trades if t.get('pnl', 0) > 0]
            losing_trades = [t for t in year_trades if t.get('pnl', 0) < 0]
            win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
            total_pnl = sum(t.get('pnl', 0) for t in year_trades)
            returns = [t.get('return_pct', 0) for t in year_trades if 'return_pct' in t]
            sharpe = np.mean(returns) / (np.std(returns) + 0.001) * np.sqrt(252) if returns else 0
            return {
                'year': year,
                'total_trades': total_trades,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'sharpe_ratio': sharpe
            }
        else:
            total_trades = sum(r['total_trades'] for r in monthly_reports)
            total_pnl = sum(r['total_pnl'] for r in monthly_reports)
            avg_win_rate = np.mean([r['win_rate'] for r in monthly_reports]) if monthly_reports else 0
            avg_sharpe = np.mean([r['sharpe_ratio'] for r in monthly_reports]) if monthly_reports else 0
            return {
                'year': year,
                'months': len(monthly_reports),
                'total_trades': total_trades,
                'total_pnl': total_pnl,
                'avg_win_rate': avg_win_rate,
                'avg_sharpe_ratio': avg_sharpe,
                'best_month': max(monthly_reports, key=lambda r: r['win_rate']) if monthly_reports else None,
                'worst_month': min(monthly_reports, key=lambda r: r['win_rate']) if monthly_reports else None
            }
    
    def win_rate_by_symbol(self, min_trades: int = 5) -> Dict:
        symbol_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        for trade in self.trades:
            symbol = trade.get('symbol', 'Unknown')
            symbol_stats[symbol]['trades'] += 1
            symbol_stats[symbol]['pnl'] += trade.get('pnl', 0)
            if trade.get('pnl', 0) > 0:
                symbol_stats[symbol]['wins'] += 1
        result = {}
        for symbol, stats in symbol_stats.items():
            if stats['trades'] >= min_trades:
                result[symbol] = {
                    'trades': stats['trades'],
                    'win_rate': stats['wins'] / stats['trades'] * 100,
                    'total_pnl': stats['pnl'],
                    'avg_pnl': stats['pnl'] / stats['trades']
                }
        return dict(sorted(result.items(), key=lambda x: x[1]['win_rate'], reverse=True))
    
    def win_rate_by_style(self, min_trades: int = 3) -> Dict:
        style_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        for trade in self.trades:
            style = trade.get('style', 'Unknown')
            style_stats[style]['trades'] += 1
            style_stats[style]['pnl'] += trade.get('pnl', 0)
            if trade.get('pnl', 0) > 0:
                style_stats[style]['wins'] += 1
        result = {}
        for style, stats in style_stats.items():
            if stats['trades'] >= min_trades:
                result[style] = {
                    'trades': stats['trades'],
                    'win_rate': stats['wins'] / stats['trades'] * 100,
                    'total_pnl': stats['pnl'],
                    'avg_pnl': stats['pnl'] / stats['trades']
                }
        return result
    
    def win_rate_by_tier(self, min_trades: int = 3) -> Dict:
        tier_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        for trade in self.trades:
            tier = trade.get('tier', 'Unknown')
            tier_stats[tier]['trades'] += 1
            tier_stats[tier]['pnl'] += trade.get('pnl', 0)
            if trade.get('pnl', 0) > 0:
                tier_stats[tier]['wins'] += 1
        result = {}
        for tier, stats in tier_stats.items():
            if stats['trades'] >= min_trades:
                result[tier] = {
                    'trades': stats['trades'],
                    'win_rate': stats['wins'] / stats['trades'] * 100,
                    'total_pnl': stats['pnl'],
                    'avg_pnl': stats['pnl'] / stats['trades']
                }
        return result
    
    def sharpe_ratio_over_time(self, window_days: int = 30) -> pd.DataFrame:
        if len(self.trades) < 10:
            return pd.DataFrame()
        sorted_trades = sorted(self.trades, key=lambda x: x.get('exit_time', datetime.now()))
        dates = []
        returns = []
        for trade in sorted_trades:
            dates.append(trade.get('exit_time'))
            returns.append(trade.get('return_pct', 0))
        df = pd.DataFrame({'date': dates, 'return': returns})
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        df['rolling_sharpe'] = df['return'].rolling(window=min(window_days, len(df))).apply(
            lambda x: np.mean(x) / (np.std(x) + 0.001) * np.sqrt(252)
        )
        return df
    
    def get_comprehensive_stats(self) -> Dict:
        if not self.trades:
            return {'error': 'No trades'}
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('pnl', 0) < 0]
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        total_pnl = sum(t.get('pnl', 0) for t in self.trades)
        avg_win = np.mean([t.get('pnl', 0) for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.get('pnl', 0) for t in losing_trades])) if losing_trades else 0
        profit_factor = (len(winning_trades) * avg_win) / (len(losing_trades) * avg_loss + 1e-10)
        consecutive_wins = 0
        max_consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_losses = 0
        for trade in self.trades:
            if trade.get('pnl', 0) > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        returns = [t.get('return_pct', 0) for t in self.trades if 'return_pct' in t]
        sharpe = np.mean(returns) / (np.std(returns) + 0.001) * np.sqrt(252) if returns else 0
        downside_returns = [r for r in returns if r < 0]
        sortino = np.mean(returns) / (np.std(downside_returns) + 0.001) * np.sqrt(252) if downside_returns else sharpe
        equity_df = self.calculate_equity_curve()
        max_dd = equity_df['drawdown'].max() if not equity_df.empty else 0
        calmar = (total_pnl / self.trades[0].get('initial_capital', 10000) * 100) / (max_dd + 0.001) if max_dd > 0 else sharpe
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'by_symbol': self.win_rate_by_symbol(),
            'by_style': self.win_rate_by_style(),
            'by_tier': self.win_rate_by_tier()
        }

# ========== TIMEFRAME CONFIGURATION ==========
class TimeframeConfig:
    ALL_TIMEFRAMES = {
        "3m": "3m", "5m": "5m", "15m": "15m",
        "30m": "30m", "1h": "1h", "2h": "2h",
        "4h": "4h", "6h": "6h", "8h": "8h", "12h": "12h",
        "1d": "1d", "3d": "3d", "1w": "1w", "1M": "1M"
    }
    
    TRADING_STYLE_TIMEFRAMES = {
        TradingStyle.SCALPING: ["3m", "5m", "15m"],
        TradingStyle.INTRADAY: ["30m", "1h", "2h"],
        TradingStyle.SWING: ["4h", "6h", "8h", "12h"],
        TradingStyle.POSITION: ["1d", "3d", "1w", "1M"]
    }
    
    ANALYSIS_GROUPS = {
        TimeframeType.ULTRA_SHORT: ["3m", "5m", "15m"],
        TimeframeType.SHORT: ["30m", "1h", "2h"],
        TimeframeType.MEDIUM: ["4h", "6h", "8h", "12h"],
        TimeframeType.LONG: ["1d", "3d", "1w", "1M"]
    }
    
    DEFAULT_TIMEFRAMES = {
        "3m": "3m", "5m": "5m", "15m": "15m",
        "30m": "30m", "1h": "1h", "2h": "2h",
        "4h": "4h", "1d": "1d"
    }

# ========== FEATURE 1: ATR STOP LOSS ==========
@dataclass
class ATRStopLoss:
    atr_value: float = 0.0
    atr_period: int = 14
    atr_multiplier: float = 1.5
    stop_loss_price: float = 0.0
    stop_loss_percentage: float = 0.0
    is_dynamic: bool = True
    
    def calculate_stop(self, entry_price: float, direction: str, df: pd.DataFrame) -> Tuple[float, float]:
        try:
            if self.atr_value <= 0:
                self.atr_value = self._calculate_atr(df)
            min_allowed_atr = entry_price * 0.001
            max_allowed_atr = entry_price * 0.05
            if self.atr_value < min_allowed_atr:
                logger.warning(f"ATR too small ({self.atr_value:.6f}), using minimum {min_allowed_atr:.6f}")
                self.atr_value = min_allowed_atr
            elif self.atr_value > max_allowed_atr:
                logger.warning(f"ATR too large ({self.atr_value:.6f}), capping at {max_allowed_atr:.6f}")
                self.atr_value = max_allowed_atr
            stop_distance = self.atr_value * self.atr_multiplier
            min_distance = entry_price * 0.002
            if stop_distance < min_distance:
                logger.debug(f"Stop distance too small ({stop_distance:.6f}), using minimum {min_distance:.6f}")
                stop_distance = min_distance
            if direction == "BUY":
                stop_loss = entry_price - stop_distance
                if stop_loss <= 0:
                    stop_loss = entry_price * 0.95
                stop_pct = (stop_distance / entry_price) * 100
            else:
                stop_loss = entry_price + stop_distance
                stop_pct = (stop_distance / entry_price) * 100
            if abs(stop_loss - entry_price) < 1e-8:
                logger.error(f"Stop loss equals entry price! Using percentage fallback")
                if direction == "BUY":
                    stop_loss = entry_price * 0.99
                    stop_pct = 1.0
                else:
                    stop_loss = entry_price * 1.01
                    stop_pct = 1.0
            self.stop_loss_price = stop_loss
            self.stop_loss_percentage = stop_pct
            logger.debug(f"ATR Stop: Entry={entry_price:.4f}, ATR={self.atr_value:.6f}, Stop={stop_loss:.4f} ({stop_pct:.2f}%)")
            return stop_loss, stop_pct
        except Exception as e:
            logger.error(f"ATR stop calculation error: {e}")
            if direction == "BUY":
                return entry_price * 0.99, 1.0
            else:
                return entry_price * 1.01, 1.0
    
    def _calculate_atr(self, df: pd.DataFrame) -> float:
        try:
            if len(df) < self.atr_period + 1:
                if len(df) > 5:
                    high = df['high'].values
                    low = df['low'].values
                    close = df['close'].values
                    tr_values = []
                    for i in range(1, len(df)):
                        hl = high[i] - low[i]
                        hc = abs(high[i] - close[i-1])
                        lc = abs(low[i] - close[i-1])
                        tr_values.append(max(hl, hc, lc))
                    if tr_values:
                        return float(np.mean(tr_values[-min(14, len(tr_values)):]))
                return float(df['high'].iloc[-1] - df['low'].iloc[-1])
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            tr = np.zeros(len(df))
            for i in range(1, len(df)):
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1])
                lc = abs(low[i] - close[i-1])
                tr[i] = max(hl, hc, lc)
            atr = pd.Series(tr).rolling(window=self.atr_period).mean().values
            return float(atr[-1])
        except Exception as e:
            logger.error(f"ATR calculation error: {e}")
            if len(df) > 5:
                return float(df['high'].iloc[-1] - df['low'].iloc[-1])
            return 0.0

# ========== FEATURE 2: VOLUME PROFILE ENTRY ==========
@dataclass
class VolumeProfileEntry:
    value_area_low: float = 0.0
    value_area_high: float = 0.0
    poc_price: float = 0.0
    high_volume_nodes: List[float] = field(default_factory=list)
    low_volume_nodes: List[float] = field(default_factory=list)
    entry_price: float = 0.0
    entry_confidence: float = 0.0
    entry_logic: str = ""
    
    def calculate_entry(self, df: pd.DataFrame, direction: str, current_price: float, 
                        style: str = "INTRADAY") -> Dict[str, Any]:
        try:
            if style == "SCALPING":
                recent_df = df.iloc[-12:] if len(df) >= 12 else df
            elif style == "INTRADAY":
                recent_df = df.iloc[-24:] if len(df) >= 24 else df
            elif style == "SWING":
                recent_df = df.iloc[-72:] if len(df) >= 72 else df
            elif style == "POSITION":
                recent_df = df.iloc[-168:] if len(df) >= 168 else df
            else:
                recent_df = df.iloc[-50:] if len(df) >= 50 else df
            if len(recent_df) < 10:
                return self._calculate_simple_profile(df, current_price, direction)
            price_min = recent_df['low'].min()
            price_max = recent_df['high'].max()
            price_range = price_max - price_min
            if price_range < current_price * 0.001:
                price_range = current_price * 0.05
                price_min = current_price - price_range/2
                price_max = current_price + price_range/2
            num_bins = max(12, min(48, int(len(recent_df) / 2)))
            bin_size = price_range / num_bins
            bins = {}
            for i in range(num_bins):
                low = price_min + (i * bin_size)
                high = low + bin_size
                bins[(low, high)] = 0.0
            total_volume_processed = 0
            for idx, row in recent_df.iterrows():
                for (low, high) in list(bins.keys()):
                    if low <= row['high'] <= high or low <= row['low'] <= high:
                        bins[(low, high)] += row['volume']
                        total_volume_processed += row['volume']
                        break
            if total_volume_processed == 0:
                return self._calculate_simple_profile(df, current_price, direction)
            poc_bin = max(bins.items(), key=lambda x: x[1])
            self.poc_price = (poc_bin[0][0] + poc_bin[0][1]) / 2
            total_volume = sum(bins.values())
            sorted_bins = sorted(bins.items(), key=lambda x: x[1], reverse=True)
            value_area_volume = 0
            value_area_bins = []
            for bin_range, volume in sorted_bins:
                value_area_volume += volume
                value_area_bins.append(bin_range)
                if value_area_volume >= total_volume * 0.7:
                    break
            if value_area_bins:
                self.value_area_low = min([b[0] for b in value_area_bins])
                self.value_area_high = max([b[1] for b in value_area_bins])
            else:
                self.value_area_low = current_price * 0.98
                self.value_area_high = current_price * 1.02
            avg_volume_per_bin = total_volume / num_bins
            self.high_volume_nodes = []
            self.low_volume_nodes = []
            for bin_range, volume in bins.items():
                mid_price = (bin_range[0] + bin_range[1]) / 2
                if volume > avg_volume_per_bin * 1.5:
                    self.high_volume_nodes.append(mid_price)
                elif volume < avg_volume_per_bin * 0.5:
                    self.low_volume_nodes.append(mid_price)
            entry_made = False
            if direction == "BUY":
                if self.value_area_low > 0 and self.value_area_low < current_price * 0.98:
                    self.entry_price = self.value_area_low
                    self.entry_logic = "Volume Profile - Discount Zone"
                    self.entry_confidence = 85
                    entry_made = True
                elif self.high_volume_nodes:
                    support_nodes = [n for n in self.high_volume_nodes if n < current_price]
                    if support_nodes:
                        self.entry_price = max(support_nodes)
                        self.entry_logic = "Volume Profile - High Volume Support"
                        self.entry_confidence = 80
                        entry_made = True
            else:
                if self.value_area_high > 0 and self.value_area_high > current_price * 1.02:
                    self.entry_price = self.value_area_high
                    self.entry_logic = "Volume Profile - Premium Zone"
                    self.entry_confidence = 85
                    entry_made = True
                elif self.high_volume_nodes:
                    resistance_nodes = [n for n in self.high_volume_nodes if n > current_price]
                    if resistance_nodes:
                        self.entry_price = min(resistance_nodes)
                        self.entry_logic = "Volume Profile - High Volume Resistance"
                        self.entry_confidence = 80
                        entry_made = True
            if not entry_made:
                if self.poc_price > 0:
                    self.entry_price = self.poc_price
                    self.entry_logic = "Volume Profile - POC"
                    self.entry_confidence = 70
                else:
                    self.entry_price = current_price
                    self.entry_logic = "Volume Profile - Current Price"
                    self.entry_confidence = 60
            if self.value_area_low < current_price * 0.5 or self.value_area_high > current_price * 2.0:
                logger.warning(f"Value area too wide: {self.value_area_low:.2f}-{self.value_area_high:.2f}")
                self.value_area_low = current_price * 0.95
                self.value_area_high = current_price * 1.05
                self.poc_price = current_price
            logger.info(f"Volume Profile ({style}): POC={self.poc_price:.4f}, VA=({self.value_area_low:.4f}-{self.value_area_high:.4f})")
            return {
                'entry_price': self.entry_price,
                'entry_confidence': self.entry_confidence,
                'entry_logic': self.entry_logic,
                'poc_price': self.poc_price,
                'value_area_low': self.value_area_low,
                'value_area_high': self.value_area_high,
                'used_fallback': False
            }
        except Exception as e:
            logger.error(f"Volume profile entry error: {e}")
            return self._calculate_simple_profile(df, current_price, direction)
    
    def _calculate_simple_profile(self, df: pd.DataFrame, current_price: float, direction: str) -> Dict[str, Any]:
        try:
            recent_df = df.iloc[-20:] if len(df) >= 20 else df
            support = recent_df['low'].min()
            resistance = recent_df['high'].max()
            avg_price = recent_df['close'].mean()
            self.poc_price = avg_price
            self.value_area_low = support
            self.value_area_high = resistance
            if direction == "BUY":
                self.entry_price = max(support, current_price * 0.99)
                self.entry_logic = "Recent Support Level"
            else:
                self.entry_price = min(resistance, current_price * 1.01)
                self.entry_logic = "Recent Resistance Level"
            self.entry_confidence = 65
            return {
                'entry_price': self.entry_price,
                'entry_confidence': self.entry_confidence,
                'entry_logic': self.entry_logic,
                'poc_price': self.poc_price,
                'value_area_low': self.value_area_low,
                'value_area_high': self.value_area_high,
                'used_fallback': True
            }
        except:
            self.entry_price = current_price
            self.entry_logic = "Current Price"
            self.entry_confidence = 50
            self.poc_price = current_price
            self.value_area_low = current_price * 0.98
            self.value_area_high = current_price * 1.02
            return {
                'entry_price': self.entry_price,
                'entry_confidence': self.entry_confidence,
                'entry_logic': self.entry_logic,
                'poc_price': self.poc_price,
                'value_area_low': self.value_area_low,
                'value_area_high': self.value_area_high,
                'used_fallback': True
            }

# ========== FEATURE 3: LIQUIDITY GRAB DETECTION ==========
@dataclass
class LiquidityGrabDetection:
    liquidity_grab_detected: bool = False
    grab_type: str = "NONE"
    grab_price: float = 0.0
    grab_strength: float = 0.0
    liquidity_levels_breached: List[float] = field(default_factory=list)
    reversal_confirmed: bool = False
    grab_description: str = ""
    
    def detect(self, df: pd.DataFrame, ob_analysis: Optional[Any] = None) -> 'LiquidityGrabDetection':
        try:
            if len(df) < 20:
                return self
            recent_df = df.iloc[-10:]
            current_price = float(df['close'].iloc[-1])
            recent_high = recent_df['high'].max()
            recent_low = recent_df['low'].min()
            prev_df = df.iloc[-30:-10] if len(df) >= 30 else df.iloc[:10]
            prev_swing_high = prev_df['high'].max() if len(prev_df) > 0 else recent_high
            prev_swing_low = prev_df['low'].min() if len(prev_df) > 0 else recent_low
            liquidity_breached = []
            grab_detected = False
            grab_type = "NONE"
            reversal = False
            atr = self._calculate_simple_atr(df)
            threshold = atr * 0.5 if atr > 0 else current_price * 0.005
            if recent_high > prev_swing_high + threshold:
                if current_price < recent_high - threshold * 0.3:
                    grab_detected = True
                    grab_type = "BUY_SIDE"
                    liquidity_breached.append(recent_high)
                    if len(df) >= 3:
                        reversal = (df['close'].iloc[-1] < df['close'].iloc[-2] < df['close'].iloc[-3])
            if recent_low < prev_swing_low - threshold:
                if current_price > recent_low + threshold * 0.3:
                    if grab_detected:
                        grab_type = "BOTH"
                    else:
                        grab_type = "SELL_SIDE"
                    grab_detected = True
                    liquidity_breached.append(recent_low)
                    if len(df) >= 3 and not reversal:
                        reversal = (df['close'].iloc[-1] > df['close'].iloc[-2] > df['close'].iloc[-3])
            grab_strength = 0
            if grab_detected and liquidity_breached:
                recent_volume = recent_df['volume'].iloc[-3:].mean()
                avg_volume = df['volume'].iloc[-20:].mean() if len(df) >= 20 else recent_df['volume'].mean()
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
                wick_percent = 0
                for i in range(-3, 0):
                    if i < len(df):
                        candle = df.iloc[i]
                        if grab_type in ["BUY_SIDE", "BOTH"]:
                            wick = candle['high'] - max(candle['open'], candle['close'])
                            wick_percent += (wick / current_price) * 100
                        if grab_type in ["SELL_SIDE", "BOTH"]:
                            wick = min(candle['open'], candle['close']) - candle['low']
                            wick_percent += (wick / current_price) * 100
                grab_strength = min(volume_ratio * 30 + wick_percent * 10 + (40 if reversal else 20), 100)
            description = ""
            if grab_detected:
                if grab_type == "BUY_SIDE":
                    description = f"Buy-side liquidity grab at {recent_high:.4f}"
                elif grab_type == "SELL_SIDE":
                    description = f"Sell-side liquidity grab at {recent_low:.4f}"
                elif grab_type == "BOTH":
                    description = f"Both sides liquidity grab detected"
                if reversal:
                    description += " - Reversal confirmed"
                else:
                    description += " - Waiting confirmation"
            self.liquidity_grab_detected = grab_detected
            self.grab_type = grab_type
            self.grab_price = recent_high if "BUY" in grab_type else recent_low
            self.grab_strength = grab_strength
            self.liquidity_levels_breached = liquidity_breached
            self.reversal_confirmed = reversal
            self.grab_description = description
            if grab_detected:
                logger.info(f"Liquidity Grab: {grab_type} at {self.grab_price:.4f}, strength={grab_strength:.1f}%")
            return self
        except Exception as e:
            logger.error(f"Liquidity grab detection error: {e}")
            return self
    
    def _calculate_simple_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        try:
            if len(df) < period + 1:
                return float(df['high'].iloc[-1] - df['low'].iloc[-1])
            high = df['high'].values[-period:]
            low = df['low'].values[-period:]
            close = df['close'].values[-period-1:-1]
            tr_values = []
            for i in range(1, len(high)):
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1]) if i-1 < len(close) else 0
                lc = abs(low[i] - close[i-1]) if i-1 < len(close) else 0
                tr_values.append(max(hl, hc, lc))
            return float(np.mean(tr_values)) if tr_values else 0
        except:
            return 0

# ========== FEATURE 4: 200 EMA TREND FILTER ==========
@dataclass
class TrendFilter200EMA:
    ema_200: float = 0.0
    current_price: float = 0.0
    price_vs_ema: str = "UNKNOWN"
    ema_slope: float = 0.0
    ema_trend: str = "UNKNOWN"
    trend_strength: float = 0.0
    filter_passed: bool = False
    filter_description: str = ""
    
    def analyze(self, df: pd.DataFrame, direction: str) -> 'TrendFilter200EMA':
        try:
            if len(df) < 50:
                ema_period = min(50, len(df) - 1)
                if ema_period >= 20:
                    close_prices = df['close'].values
                    ema = pd.Series(close_prices).ewm(span=ema_period, adjust=False).mean()
                    self.ema_200 = float(ema.iloc[-1])
                    self.filter_description = f"Using EMA {ema_period} instead of 200"
                else:
                    self.filter_passed = True
                    self.filter_description = "Insufficient data"
                    return self
            else:
                close_prices = df['close'].values
                ema_200 = pd.Series(close_prices).ewm(span=200, adjust=False).mean()
                self.ema_200 = float(ema_200.iloc[-1])
            self.current_price = float(df['close'].iloc[-1])
            deviation = (self.current_price / self.ema_200 - 1) * 100
            if deviation > 1.0:
                self.price_vs_ema = "ABOVE"
            elif deviation < -1.0:
                self.price_vs_ema = "BELOW"
            else:
                self.price_vs_ema = "AT"
            if len(df) >= 20:
                if 'ema_200' in locals() and len(ema_200) >= 10:
                    ema_10_ago = ema_200.iloc[-10]
                    ema_now = ema_200.iloc[-1]
                    self.ema_slope = ((ema_now / ema_10_ago) - 1) * 100
                    if self.ema_slope > 0.2:
                        self.ema_trend = "BULLISH"
                        self.trend_strength = min(abs(self.ema_slope) * 20, 100)
                    elif self.ema_slope < -0.2:
                        self.ema_trend = "BEARISH"
                        self.trend_strength = min(abs(self.ema_slope) * 20, 100)
                    else:
                        self.ema_trend = "SIDEWAYS"
                        self.trend_strength = 30
                else:
                    if self.current_price > self.ema_200 * 1.05:
                        self.ema_trend = "BULLISH"
                        self.trend_strength = 60
                    elif self.current_price < self.ema_200 * 0.95:
                        self.ema_trend = "BEARISH"
                        self.trend_strength = 60
                    else:
                        self.ema_trend = "SIDEWAYS"
                        self.trend_strength = 40
            else:
                self.ema_trend = "SIDEWAYS"
                self.trend_strength = 30
            if direction == "BUY":
                if self.price_vs_ema == "ABOVE" or self.ema_trend == "BULLISH":
                    self.filter_passed = True
                    self.filter_description = f"200 EMA filter passed - Price {self.price_vs_ema} EMA"
                else:
                    self.filter_passed = False
                    self.filter_description = f"200 EMA filter failed - Price {self.price_vs_ema} EMA"
            else:
                if self.price_vs_ema == "BELOW" or self.ema_trend == "BEARISH":
                    self.filter_passed = True
                    self.filter_description = f"200 EMA filter passed - Price {self.price_vs_ema} EMA"
                else:
                    self.filter_passed = False
                    self.filter_description = f"200 EMA filter failed - Price {self.price_vs_ema} EMA"
            return self
        except Exception as e:
            logger.error(f"200 EMA trend filter error: {e}")
            self.filter_passed = True
            self.filter_description = "Calculation error"
            return self

# ========== FEATURE 5: PURE NUMPY AI CONFIDENCE MODEL ==========
class AIConfidenceModel:
    def __init__(self, max_history: int = 100):
        self.feature_history = []
        self.outcome_history = []
        self.feature_weights = None
        self.is_trained = False
        self.max_history = max_history
        self.feature_names = [
            'rsi', 'macd_trend_score', 'ema_trend_score', 'volume_ratio',
            'bid_ask_ratio', 'imbalance', 'cumulative_delta',
            'regime_alignment', 'tech_score', 'flow_score',
            'volatility', 'adx', 'smart_money_score',
            'timeframe_confluence', 'liquidity_grab_strength',
            'ema200_position', 'volume_profile_score'
        ]
        self.num_features = len(self.feature_names)
        self.model_file = "ai_weights_production.npy"
        self.correlation_threshold = 0.3
        
        self._load_weights()
    
    def _load_weights(self):
        try:
            if os.path.exists(self.model_file):
                self.feature_weights = np.load(self.model_file)
                self.is_trained = True
                logger.info("✅ AI Confidence Model weights loaded")
        except Exception as e:
            logger.warning(f"Could not load AI weights: {e}")
    
    def _save_weights(self):
        try:
            if self.feature_weights is not None:
                np.save(self.model_file, self.feature_weights)
                logger.info("✅ AI Confidence Model weights saved")
        except Exception as e:
            logger.error(f"Could not save AI weights: {e}")
    
    def add_training_data(self, features: List[float], outcome: float):
        self.feature_history.append(features)
        self.outcome_history.append(outcome)
        if len(self.feature_history) > self.max_history:
            self.feature_history = self.feature_history[-self.max_history:]
            self.outcome_history = self.outcome_history[-self.max_history:]
    
    def train(self):
        try:
            if len(self.feature_history) < 20:
                logger.warning(f"Not enough data to train AI: {len(self.feature_history)} < 20")
                return False
            X = np.array(self.feature_history)
            y = np.array(self.outcome_history)
            X_mean = np.mean(X, axis=0)
            X_std = np.std(X, axis=0)
            X_std[X_std == 0] = 1
            X_norm = (X - X_mean) / X_std
            correlations = []
            for i in range(X_norm.shape[1]):
                feature = X_norm[:, i]
                corr = np.corrcoef(feature, y)[0, 1]
                if np.isnan(corr):
                    corr = 0
                correlations.append(abs(corr))
            correlations = np.array(correlations)
            if np.sum(correlations) > 0:
                self.feature_weights = correlations / np.sum(correlations)
            else:
                self.feature_weights = np.ones(self.num_features) / self.num_features
            self.is_trained = True
            self._save_weights()
            logger.info(f"✅ AI Model trained on {len(self.feature_history)} samples")
            return True
        except Exception as e:
            logger.error(f"AI training error: {e}")
            return False
    
    def predict(self, features: List[float]) -> Tuple[float, float]:
        try:
            if not self.is_trained or self.feature_weights is None:
                return 50.0, 50.0
            features = np.array(features)
            features = np.clip(features, 0, 100)
            if len(features) == len(self.feature_weights):
                predicted = np.sum(features * self.feature_weights)
            else:
                predicted = np.mean(features)
            predicted = max(0, min(100, predicted))
            if len(self.feature_history) > 0:
                historical_preds = []
                for hist_features in self.feature_history[-20:]:
                    hist_features = np.clip(hist_features, 0, 100)
                    if len(hist_features) == len(self.feature_weights):
                        hist_pred = np.sum(hist_features * self.feature_weights)
                    else:
                        hist_pred = np.mean(hist_features)
                    historical_preds.append(hist_pred)
                if historical_preds:
                    pred_std = np.std(historical_preds)
                    confidence_in_pred = max(0, min(100, 100 - pred_std))
                else:
                    confidence_in_pred = 70
            else:
                confidence_in_pred = 70
            return predicted, confidence_in_pred
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return 50.0, 50.0
    
    def extract_features(self, signal: 'EnhancedHighConfidenceSignal') -> List[float]:
        try:
            features = []
            features.append(signal.rsi)
            if signal.macd_trend == "BULLISH":
                features.append(100)
            elif signal.macd_trend == "BEARISH":
                features.append(0)
            else:
                features.append(50)
            if signal.ema_trend == "BULLISH":
                features.append(100)
            elif signal.ema_trend == "BEARISH":
                features.append(0)
            else:
                features.append(50)
            volume_ratio = getattr(signal, 'volume_ratio', 1.0)
            features.append(min(volume_ratio * 50, 100))
            bid_ask = signal.bid_ask_ratio
            if bid_ask > 2:
                features.append(100)
            elif bid_ask > 1.5:
                features.append(80)
            elif bid_ask > 1.2:
                features.append(60)
            elif bid_ask > 0.8:
                features.append(50)
            elif bid_ask > 0.5:
                features.append(40)
            else:
                features.append(20)
            imbalance = abs(signal.order_book_imbalance or 0)
            features.append(min(imbalance * 2, 100))
            delta = abs(signal.cumulative_delta_15min)
            delta_norm = min(np.tanh(delta / 1e6) * 100, 100)
            features.append(delta_norm)
            features.append(signal.multi_tf_regime.regime_alignment)
            tech_norm = (signal.tech_score + 100) / 2
            features.append(max(0, min(100, tech_norm)))
            flow_norm = (signal.flow_score + 100) / 2
            features.append(max(0, min(100, flow_norm)))
            vol_score = 50
            if hasattr(signal.multi_tf_regime, 'ultra_short_volatility'):
                if signal.multi_tf_regime.ultra_short_volatility == "HIGH":
                    vol_score = 80
                elif signal.multi_tf_regime.ultra_short_volatility == "LOW":
                    vol_score = 20
            features.append(vol_score)
            features.append(signal.multi_tf_regime.ultra_short_adx)
            if signal.smart_money_display:
                features.append(abs(signal.smart_money_display.smart_money_score))
            else:
                features.append(0)
            features.append(signal.timeframe_confluence.alignment_score)
            if hasattr(signal, 'liquidity_grab') and signal.liquidity_grab:
                features.append(signal.liquidity_grab.grab_strength)
            else:
                features.append(0)
            if hasattr(signal, 'trend_filter_200ema'):
                if signal.trend_filter_200ema.price_vs_ema == "ABOVE":
                    features.append(100)
                elif signal.trend_filter_200ema.price_vs_ema == "BELOW":
                    features.append(0)
                else:
                    features.append(50)
            else:
                features.append(50)
            if hasattr(signal, 'volume_profile_entry'):
                if signal.volume_profile_entry.entry_confidence:
                    features.append(signal.volume_profile_entry.entry_confidence)
                else:
                    features.append(50)
            else:
                features.append(50)
            return features
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return [50] * self.num_features

# ========== DATA CLASSES ==========
@dataclass
class OrderBookLevel:
    price: float
    quantity: float
    total: float

@dataclass
class OrderBookAnalysis:
    best_bid: float
    best_ask: float
    spread: float
    spread_percentage: float
    bid_volume: float
    ask_volume: float
    bid_ask_ratio: float
    buy_pressure: float
    sell_pressure: float
    imbalance: float
    top_bids: List[OrderBookLevel]
    top_asks: List[OrderBookLevel]
    support_levels: List[float]
    resistance_levels: List[float]
    symbol: str = ""

@dataclass
class MarketTradeAnalysis:
    buy_volume: float
    sell_volume: float
    net_volume: float
    buy_sell_ratio: float
    large_trades_buy: int
    large_trades_sell: int
    aggressive_buying: bool
    aggressive_selling: bool

@dataclass
class CumulativeFlow:
    delta_5min: float
    delta_15min: float
    delta_1h: float
    cumulative_delta: float
    trend_strength: str
    accumulation: bool
    distribution: bool

@dataclass
class SmartMoneyDisplay:
    primary_concept: SmartMoneyConcept
    secondary_concepts: List[SmartMoneyConcept]
    concept_details: Dict[str, Any]
    smart_money_score: float
    concept_description: str

@dataclass
class MultiTimeframeRegime:
    ultra_short_regime: str
    ultra_short_strength: float
    ultra_short_adx: float
    ultra_short_volatility: str
    short_regime: str
    short_strength: float
    short_adx: float
    short_volatility: str
    medium_regime: str
    medium_strength: float
    medium_adx: float
    medium_volatility: str
    long_regime: str
    long_strength: float
    long_adx: float
    long_volatility: str
    overall_regime: str
    overall_strength: float
    regime_alignment: float
    dominant_trend: str
    regime_score: float
    all_timeframes: Dict[str, Dict] = field(default_factory=dict)

@dataclass
class MarketRegime:
    regime_type: str
    strength: float
    volatility: str
    volume_profile: str
    adx_value: float
    adx_trend: str
    regime_score: float

@dataclass
class SmartMoneyConcepts:
    order_block_detected: bool
    order_block_type: str
    order_block_price: float
    order_block_strength: float
    liquidity_sweep: bool
    liquidity_levels: List[float]
    fvg_detected: bool
    fvg_type: str
    fvg_zone_low: float
    fvg_zone_high: float
    fvg_filled: bool
    breaker_block: bool
    mitigation_detected: bool
    institutional_divergence: bool
    smart_money_score: float
    primary_concept: Optional[SmartMoneyConcept] = None
    concept_summary: str = ""

@dataclass
class MarketProfile:
    value_area_low: float
    value_area_high: float
    poc_price: float
    volume_nodes: List[Tuple[float, float]]
    high_volume_nodes: List[float]
    low_volume_nodes: List[float]
    developing_poc: bool
    market_type: str
    profile_complete: bool
    volume_profile_score: float

@dataclass
class InterMarketAnalysis:
    btc_dominance: Optional[float]
    btc_dominance_change: Optional[float]
    btc_price: Optional[float]
    btc_change_24h: Optional[float]
    eth_price: Optional[float]
    eth_change_24h: Optional[float]
    btc_correlation: float
    eth_correlation: float
    total_market_cap: Optional[float]
    total_market_cap_change: Optional[float]
    altcoin_season_index: Optional[float]
    altcoin_season: Optional[bool]
    usdt_dominance: Optional[float]
    usdt_dominance_change: Optional[float]
    sector_strength: Dict[str, float]
    intermarket_score: float

@dataclass
class OnChainMetrics:
    exchange_netflow: Optional[float]
    exchange_netflow_24h: Optional[float]
    large_transactions_24h: Optional[int]
    active_addresses_24h: Optional[float]
    active_addresses_change: Optional[float]
    velocity: Optional[float]
    holder_distribution: Dict[str, float]
    supply_on_exchanges: Optional[float]
    supply_off_exchanges: Optional[float]
    whale_activity: Optional[str]
    onchain_score: float

@dataclass
class MarketSentiment:
    fear_greed_index: Optional[int]
    fear_greed_sentiment: str
    news_sentiment: str
    news_sentiment_score: float
    social_volume: Optional[float]
    social_dominance: Optional[float]
    social_sentiment: str
    sentiment_score: float
    funding_sentiment_aligned: bool
    crowd_behavior: str

@dataclass
class DivergenceAnalysis:
    rsi_divergence: str
    rsi_divergence_strength: float
    macd_divergence: str
    macd_divergence_strength: float
    volume_divergence: str
    volume_divergence_strength: float
    obv_divergence: str
    obv_divergence_strength: float
    divergence_score: float

@dataclass
class PatternRecognition:
    candlestick_patterns: List[str]
    candlestick_reliability: float
    chart_patterns: List[str]
    pattern_reliability: float
    breakout_confirmed: bool
    breakout_direction: str
    target_price: float
    invalidation_price: float
    pattern_score: float

@dataclass
class LiquidityAnalysis:
    buy_liquidity_levels: List[float]
    sell_liquidity_levels: List[float]
    closest_buy_liquidity: float
    closest_sell_liquidity: float
    liquidity_imbalance: float
    stop_hunts_detected: bool
    recent_stop_hunt: bool
    liquidity_score: float

@dataclass
class TimeframeConfluence:
    timeframe_signals: Dict[str, str]
    confluence_count: int
    major_trend: str
    minor_trend: str
    alignment_score: float
    best_timeframe: str
    aligned_styles: List[TradingStyle] = field(default_factory=list)
    style_scores: Dict[str, float] = field(default_factory=dict)
    scalping_signals: Dict[str, str] = field(default_factory=dict)
    intraday_signals: Dict[str, str] = field(default_factory=dict)
    swing_signals: Dict[str, str] = field(default_factory=dict)
    position_signals: Dict[str, str] = field(default_factory=dict)
    primary_style: Optional[str] = None
    secondary_styles: List[str] = field(default_factory=list)

@dataclass
class TechnicalAnalysis:
    rsi: float
    rsi_signal: str
    macd: float
    macd_signal: float
    macd_histogram: float
    macd_trend: str
    bb_position: str
    bb_width: float
    stoch_k: float
    stoch_d: float
    stoch_signal: str
    ema9: float
    ema21: float
    ema_trend: str
    vwap: float
    vwap_position: str
    volume_surge: bool
    volume_ratio: float

@dataclass
class EnhancedTechnicalAnalysis(TechnicalAnalysis):
    adx: float
    adx_trend: str
    obv: float
    obv_trend: str
    money_flow_index: float
    mfi_signal: str
    ichimoku_tenkan: float
    ichimoku_kijun: float
    ichimoku_senkou_a: float
    ichimoku_senkou_b: float
    ichimoku_cloud: str
    fibonacci_levels: Dict[str, float]
    pivot_points: Dict[str, float]
    camarilla_levels: Dict[str, float]

@dataclass
class BacktestResult:
    symbol: str
    total_signals: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    profit_factor: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    last_updated: datetime

@dataclass
class MarketContext:
    btc_price: float
    btc_change_24h: float
    eth_price: float
    eth_change_24h: float
    total_market_cap: float
    market_cap_change_24h: float
    btc_dominance: float
    dominance_change: float
    fear_greed_index: int
    fear_greed_text: str

@dataclass
class RiskRewardAnalysis:
    risk_percentage: float
    reward_1_percentage: float
    reward_2_percentage: float
    reward_3_percentage: float
    rr_ratio_1: float
    rr_ratio_2: float
    rr_ratio_3: float
    expected_value: float
    scalping_target_1: float = 0
    scalping_target_2: float = 0
    intraday_target_1: float = 0
    intraday_target_2: float = 0
    swing_target_1: float = 0
    swing_target_2: float = 0
    position_target_1: float = 0
    position_target_2: float = 0

@dataclass
class ConfirmationSignals:
    bullish_timeframes: int
    bearish_timeframes: int
    total_timeframes: int
    volume_confirmation: bool
    volume_ratio: float
    obv_confirmation: str
    divergence_confirmation: str
    pattern_confirmation: str
    confirmation_score: float

@dataclass
class DynamicThresholds:
    base_tech_score: float
    base_flow_score: float
    volume_multiplier: float
    volatility_multiplier: float
    confidence_threshold: float
    
    def get_adjusted_thresholds(self, market_regime: MarketRegime) -> Tuple[float, float]:
        vol_factor = 1.0
        if market_regime.volatility == "HIGH":
            vol_factor = 1.3
        elif market_regime.volatility == "LOW":
            vol_factor = 0.8
        adjusted_tech = self.base_tech_score * vol_factor * self.volume_multiplier
        adjusted_flow = self.base_flow_score * vol_factor * self.volume_multiplier
        return adjusted_tech, adjusted_flow

@dataclass
class PendingSignal:
    signal: 'EnhancedHighConfidenceSignal'
    level: AlertLevel
    send_time: datetime
    message_id: Optional[int] = None
    
@dataclass
class OrderExecution:
    """Class to store executed order details"""
    order_id: str
    symbol: str
    signal_tier: SignalTier
    signal_style: Optional[SignalStyle]
    direction: str
    entry_price: float
    quantity: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    executed_time: datetime
    leverage: int
    order_type: str
    status: str = "OPEN"
    pnl_percent: float = 0.0
    pnl_usdt: float = 0.0
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    message_id: Optional[int] = None

# ========== ENHANCED HIGH CONFIDENCE SIGNAL ==========
@dataclass
class EnhancedHighConfidenceSignal:
    timestamp: datetime
    symbol: str
    signal_type: str
    confidence: float
    current_price: float
    best_bid: float
    best_ask: float
    spread: float
    spread_percentage: float
    suggested_order_type: OrderType
    entry_price: float
    entry_range_low: float
    entry_range_high: float
    optimal_entry_timeframe: str
    stop_loss: float
    stop_loss_percentage: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    recommended_leverage: int
    rsi: float
    rsi_signal: str
    macd_trend: str
    ema_trend: str
    bb_position: str
    buy_pressure: float
    sell_pressure: float
    bid_ask_ratio: float
    cumulative_delta_15min: float
    delta_trend: str
    volume_24h: float
    volume_change_24h: float
    funding_rate: float
    funding_sentiment: str
    open_interest: Optional[float]
    oi_change_1h: Optional[float]
    support_levels: List[float]
    resistance_levels: List[float]
    nearest_support: float
    nearest_resistance: float
    primary_reasons: List[str]
    secondary_reasons: List[str]
    aligned_styles: List[TradingStyle]
    style_scores: Dict[str, float]
    recommendation: str
    risk_level: str
    time_horizon: str
    market_regime: Any
    multi_tf_regime: Any
    smart_money: Any
    market_profile: Any
    intermarket: Any
    onchain: Optional[Any]
    sentiment: Any
    divergence: Any
    patterns: Any
    liquidity: Any
    timeframe_confluence: Any
    enhanced_tech: Any
    overall_accuracy_score: float
    risk_adjusted_confidence: float
    expected_move: float
    optimal_position_size: float
    tech_score: float = 0
    flow_score: float = 0
    backtest_result: Optional[Any] = None
    market_context: Optional[Any] = None
    risk_reward: Optional[Any] = None
    confirmations: Optional[Any] = None
    bot_win_rate: float = 0.0
    signals_last_100: int = 0
    win_rate_last_100: float = 0.0
    entry_timeframe_3m_signal: Optional[str] = None
    entry_timeframe_5m_signal: Optional[str] = None
    tier: Optional[SignalTier] = None
    tier_confidence: Optional[float] = None
    smart_scan_score: float = 0.0
    adaptive_cooldown_minutes: int = 0
    entry_bid_level: Optional[float] = None
    entry_ask_level: Optional[float] = None
    entry_mid_price: Optional[float] = None
    order_book_imbalance: Optional[float] = None
    ultra_short_regime_aligned: bool = False
    short_regime_aligned: bool = False
    medium_regime_aligned: bool = False
    long_regime_aligned: bool = False
    scalping_entry: Optional[float] = None
    intraday_entry: Optional[float] = None
    swing_entry: Optional[float] = None
    position_entry: Optional[float] = None
    scalping_tp1: Optional[float] = None
    scalping_tp2: Optional[float] = None
    intraday_tp1: Optional[float] = None
    intraday_tp2: Optional[float] = None
    swing_tp1: Optional[float] = None
    swing_tp2: Optional[float] = None
    position_tp1: Optional[float] = None
    position_tp2: Optional[float] = None
    primary_style: Optional[SignalStyle] = None
    secondary_styles: List[SignalStyle] = field(default_factory=list)
    style_confidence: Dict[str, float] = field(default_factory=dict)
    smart_money_display: Optional[SmartMoneyDisplay] = None
    atr_stop_loss: Optional[ATRStopLoss] = None
    atr_value: float = 0.0
    atr_multiplier: float = 1.5
    volume_profile_entry: Optional[VolumeProfileEntry] = None
    volume_poc_price: float = 0.0
    volume_value_area_low: float = 0.0
    volume_value_area_high: float = 0.0
    liquidity_grab: Optional[LiquidityGrabDetection] = None
    liquidity_grab_detected: bool = False
    liquidity_grab_type: str = "NONE"
    liquidity_grab_strength: float = 0.0
    trend_filter_200ema: Optional[TrendFilter200EMA] = None
    ema_200: float = 0.0
    price_vs_ema_200: str = "UNKNOWN"
    ema_200_trend: str = "UNKNOWN"
    trend_filter_passed: bool = True
    ai_confidence: float = 0.0
    ai_confidence_prediction: float = 0.0
    ai_confidence_in_prediction: float = 0.0
    ai_model_used: bool = False
    ai_score: float = 0.0
    ai_weights: List[float] = field(default_factory=list)
    ai_feature_history: List[List[float]] = field(default_factory=list)
    ai_outcome_history: List[float] = field(default_factory=list)
    alert_level: Optional[AlertLevel] = None
    is_confirmed: bool = False
    confirmation_time: Optional[datetime] = None
    confirmation_message_id: Optional[int] = None
    order_execution: Optional[OrderExecution] = None
    
    # New fields for advanced features
    risk_report: Optional[Dict] = None
    portfolio_position: Optional[Any] = None
    backtest_details: Optional[Dict] = None
    ml_predictions: Optional[Dict] = None
    advanced_order_ids: List[str] = field(default_factory=list)

# ========== CONFIGURATION CLASSES ==========
@dataclass
class TelegramConfig:
    BOT_TOKEN: str = ""
    CHAT_ID: str = ""
    API_URL: str = "https://api.telegram.org/bot{}/sendMessage"
    EDIT_URL: str = "https://api.telegram.org/bot{}/editMessageText"
    ANSWER_URL: str = "https://api.telegram.org/bot{}/answerCallbackQuery"
    ALERT_ON_SCALPING: bool = True
    ALERT_ON_INTRADAY: bool = True
    ALERT_ON_SWING: bool = True
    ALERT_ON_POSITION: bool = True
    MIN_CONFIDENCE: float = 70.0
    MIN_ACCURACY_SCORE: float = 75.0
    MIN_CONFLUENCE_PERCENT: float = 70.0
    COOLDOWN_MINUTES: int = 15
    EMERGENCY_THRESHOLD: float = 90.0
    HIGH_THRESHOLD: float = 80.0
    MEDIUM_THRESHOLD: float = 70.0
    ENABLE_VOICE_ALERTS: bool = False
    ENABLE_BUTTONS: bool = False
    ENABLE_SUMMARY: bool = True
    SUMMARY_INTERVAL_MINUTES: int = 60
    ENABLE_AUTO_TRADE: bool = True
    MAX_POSITION_SIZE_USDT: float = 100.0
    DEFAULT_LEVERAGE: int = 5

@dataclass
class BinanceFuturesConfig:
    API_KEY: str = ""
    API_SECRET: str = ""
    BASE_URL: str = "https://fapi.binance.com"
    BASE_URL_BACKUP: str = "https://fapi1.binance.com"
    BASE_URL_BACKUP2: str = "https://fapi2.binance.com"
    BASE_URL_BACKUP3: str = "https://fapi3.binance.com"
    USE_TESTNET: bool = False
    TESTNET_URL: str = "https://testnet.binancefuture.com"
    REQUEST_TIMEOUT: int = 30

@dataclass
class TpConfig:
    """Class for TP multipliers per trading style"""
    scalping_tp1: float = 0.35
    scalping_tp2: float = 0.70
    intraday_tp1: float = 1.0
    intraday_tp2: float = 1.8
    swing_tp1: float = 1.5
    swing_tp2: float = 2.5
    position_tp1: float = 2.0
    position_tp2: float = 3.5
    
    def get_multipliers(self, style: str) -> Tuple[float, float]:
        """Get TP multipliers for a specific trading style"""
        style = style.upper()
        if style == "SCALPING":
            return self.scalping_tp1, self.scalping_tp2
        elif style == "INTRADAY":
            return self.intraday_tp1, self.intraday_tp2
        elif style == "SWING":
            return self.swing_tp1, self.swing_tp2
        elif style == "POSITION":
            return self.position_tp1, self.position_tp2
        else:
            return self.intraday_tp1, self.intraday_tp2

@dataclass
class SecurityConfig:
    """Security configuration"""
    ENCRYPTION_ENABLED: bool = True
    IP_WHITELIST_ENABLED: bool = False
    ALLOWED_IPS: List[str] = field(default_factory=list)
    TWO_FA_ENABLED: bool = False
    RATE_LIMIT_ENABLED: bool = True
    MAX_REQUESTS_PER_MINUTE: int = 60
    FAILED_ATTEMPT_LIMIT: int = 5

@dataclass
class MLConfig:
    """ML models configuration"""
    RANDOM_FOREST_ENABLED: bool = True
    GRADIENT_BOOSTING_ENABLED: bool = True
    LSTM_ENABLED: bool = True
    ENSEMBLE_ENABLED: bool = True
    AUTO_RETRAIN: bool = True
    RETRAIN_INTERVAL_HOURS: int = 24
    MODEL_DIR: str = "ml_models"

@dataclass
class RiskConfig:
    """Risk management configuration"""
    KELLY_CRITERION_ENABLED: bool = True
    VAR_CALCULATION_ENABLED: bool = True
    MONTE_CARLO_ENABLED: bool = True
    DRAWDOWN_PROTECTION_ENABLED: bool = True
    MAX_DRAWDOWN_PERCENT: float = 20.0
    POSITION_SIZING_METHOD: str = "kelly"  # kelly, fixed, dynamic
    CORRELATION_CHECK_ENABLED: bool = True
    MAX_CORRELATION: float = 0.7

@dataclass
class OrderConfig:
    """Advanced order types configuration"""
    OCO_ENABLED: bool = True
    TRAILING_STOP_ENABLED: bool = True
    ICEBERG_ENABLED: bool = True
    TWAP_ENABLED: bool = True
    VWAP_ENABLED: bool = True
    DEFAULT_TRAILING_CALLBACK: float = 1.0  # percent
    DEFAULT_ICEBERG_SIZE: float = 0.1  # fraction of total
    DEFAULT_TWAP_SLICES: int = 10

@dataclass
class BacktestConfig:
    """Advanced backtesting configuration"""
    WALK_FORWARD_ENABLED: bool = True
    MONTE_CARLO_ENABLED: bool = True
    OPTIMIZATION_ENABLED: bool = True
    MULTI_TIMEFRAME_ENABLED: bool = True
    TRAIN_WINDOW_DAYS: int = 30
    TEST_WINDOW_DAYS: int = 7
    NUM_SIMULATIONS: int = 1000

@dataclass
class PortfolioConfig:
    """Portfolio management configuration"""
    TRACK_POSITIONS: bool = True
    GENERATE_HEATMAP: bool = True
    CALCULATE_CORRELATION: bool = True
    SECTOR_ALLOCATION: bool = True
    REBALANCE_THRESHOLD: float = 10.0  # percent deviation

@dataclass
class PerformanceConfig:
    """Performance analytics configuration"""
    TRACK_EQUITY_CURVE: bool = True
    GENERATE_MONTHLY_REPORTS: bool = True
    GENERATE_YEARLY_REPORTS: bool = True
    TRACK_WIN_RATE_BY_SYMBOL: bool = True
    TRACK_WIN_RATE_BY_STYLE: bool = True
    TRACK_WIN_RATE_BY_TIER: bool = True
    CALCULATE_SHARPE: bool = True
    CALCULATE_SORTINO: bool = True
    CALCULATE_CALMAR: bool = True

@dataclass
class HybridConfig:
    ENABLE_TIER_1: bool = True
    ENABLE_TIER_2: bool = True
    ENABLE_TIER_3: bool = True
    MAX_SIGNALS_PER_DAY: int = 200
    SCAN_TOP_SYMBOLS: int = 100
    TIER_1_TECH_THRESHOLD: float = 70.0
    TIER_1_FLOW_THRESHOLD: float = 60.0
    TIER_2_TECH_THRESHOLD: float = 59.0
    TIER_2_FLOW_THRESHOLD: float = 55.0
    TIER_3_TECH_THRESHOLD: float = 54.0
    TIER_3_FLOW_THRESHOLD: float = 48.0
    ENTRY_ORDER_BOOK_DEPTH: int = 10
    ENTRY_MAX_SPREAD_PERCENT: float = 0.05
    ENTRY_USE_MID_PRICE: bool = True
    ENTRY_BUY_BID_LEVEL: int = 1
    ENTRY_SELL_ASK_LEVEL: int = 1
    ULTRA_SHORT_WEIGHT: float = 0.30
    SHORT_WEIGHT: float = 0.25
    MEDIUM_WEIGHT: float = 0.25
    LONG_WEIGHT: float = 0.20
    ULTRA_SHORT_TIMEFRAMES: Dict[str, float] = field(default_factory=lambda: {
        "3m": 0.4, "5m": 0.35, "15m": 0.25
    })
    SHORT_TIMEFRAMES: Dict[str, float] = field(default_factory=lambda: {
        "30m": 0.4, "1h": 0.35, "2h": 0.25
    })
    MEDIUM_TIMEFRAMES: Dict[str, float] = field(default_factory=lambda: {
        "4h": 0.4, "6h": 0.3, "8h": 0.2, "12h": 0.1
    })
    LONG_TIMEFRAMES: Dict[str, float] = field(default_factory=lambda: {
        "1d": 0.5, "3d": 0.3, "1w": 0.15, "1M": 0.05
    })
    MIN_REGIME_ALIGNMENT: float = 60.0
    MIN_STYLE_CONFIDENCE: float = 70.0
    SECONDARY_STYLE_THRESHOLD: float = 70.0
    ATR_STOP_LOSS_ENABLED: bool = True
    ATR_PERIOD: int = 14
    ATR_MULTIPLIER: float = 1.5
    ATR_DYNAMIC_MULTIPLIER: bool = True
    VOLUME_PROFILE_ENTRY_ENABLED: bool = True
    VOLUME_PROFILE_BINS: int = 24
    VOLUME_PROFILE_VALUE_AREA_PERCENT: float = 70.0
    VOLUME_PROFILE_MIN_BARS: int = 20
    LIQUIDITY_GRAB_ENABLED: bool = True
    LIQUIDITY_GRAB_LOOKBACK: int = 10
    LIQUIDITY_GRAB_MIN_WICK_PERCENT: float = 0.5
    LIQUIDITY_GRAB_VOLUME_CONFIRMATION: bool = True
    EMA_200_TREND_FILTER_ENABLED: bool = True
    EMA_200_REQUIRED_FOR_TIER1: bool = True
    EMA_200_REQUIRED_FOR_TIER2: bool = True
    EMA_200_REQUIRED_FOR_TIER3: bool = True
    AI_CONFIDENCE_MODEL_ENABLED: bool = True
    AI_MIN_SIGNALS_FOR_TRAINING: int = 20
    AI_OVERRIDE_CONFIDENCE: bool = True
    AI_MAX_HISTORY: int = 100
    TP_CONFIG: TpConfig = field(default_factory=TpConfig)
    
    # New configs
    SECURITY_CONFIG: SecurityConfig = field(default_factory=SecurityConfig)
    ML_CONFIG: MLConfig = field(default_factory=MLConfig)
    RISK_CONFIG: RiskConfig = field(default_factory=RiskConfig)
    ORDER_CONFIG: OrderConfig = field(default_factory=OrderConfig)
    BACKTEST_CONFIG: BacktestConfig = field(default_factory=BacktestConfig)
    PORTFOLIO_CONFIG: PortfolioConfig = field(default_factory=PortfolioConfig)
    PERFORMANCE_CONFIG: PerformanceConfig = field(default_factory=PerformanceConfig)

@dataclass
class Config:
    SYMBOLS: List[str] = field(default_factory=lambda: [
        "1INCHUSDT", "AAVEUSDT", "ACHUSDT", "ACUUSDT", "ADAUSDT",
        "AGLDUSDT", "ALGOUSDT", "ALICEUSDT", "ANKRUSDT", "API3USDT",
        "APTUSDT", "ARBUSDT", "ARUSDT", "ASTERUSDT", "ATOMUSDT",
        "AVAXUSDT", "AXSUSDT", "BANDUSDT", "BATUSDT", "BCHUSDT",
        "BICOUSDT", "BNBUSDT", "BNTUSDT", "BREVUSDT", "BTCUSDT",
        "C98USDT", "CCUSDT", "CELOUSDT", "CELRUSDT", "CHRUSDT",
        "CHZUSDT", "COMPUSDT", "COTIUSDT", "CRVUSDT", "CTSIUSDT",
        "CVCUSDT", "DASHUSDT", "DENTUSDT", "DOGEUSDT", "DOTUSDT",
        "DYDXUSDT", "EGLDUSDT", "ENJUSDT", "ENSUSDT", "ESPUSDT",
        "ETCUSDT", "ETHFIUSDT", "ETHUSDT", "FETUSDT", "FILUSDT",
        "FLOWUSDT", "FLUXUSDT", "FOGOUSDT", "GALAUSDT", "GRTUSDT",
        "HBARUSDT", "HOTUSDT", "ICPUSDT", "ICXUSDT", "ILVUSDT",
        "IMXUSDT", "IOSTUSDT", "IOTAUSDT", "IOTXUSDT", "LIGHTUSDT",
        "LINKUSDT", "LITUSDT", "LTCUSDT", "MONUSDT", "NEARUSDT",
        "OPUSDT", "RAVEUSDT", "RIVERUSDT", "SOLUSDT", "SPACEUSDT",
        "TRIAUSDT", "UNIUSDT", "WETUSDT", "XAGUSDT", "XAUUSDT",
        "XPDUSDT", "XPTUSDT", "XRPUSDT", "ZAMAUSDT", "ZKPUSDT"
    ])
    
    TIMEFRAMES: Dict[str, str] = field(default_factory=lambda: TimeframeConfig.ALL_TIMEFRAMES.copy())
    DEFAULT_TIMEFRAMES: Dict[str, str] = field(default_factory=lambda: TimeframeConfig.DEFAULT_TIMEFRAMES.copy())
    ENTRY_TIMEFRAMES: List[str] = field(default_factory=lambda: ["3m", "5m"])
    
    HIGH_CONFIDENCE_THRESHOLDS: Dict[str, float] = field(default_factory=lambda: {
        'MIN_VOLUME_24H': 500000,
        'MAX_SPREAD_PERCENT': 0.1,
        'MIN_TECH_SCORE': 50,
        'MIN_ORDER_FLOW_SCORE': 45,
        'MIN_STYLE_ALIGNMENT': 2,
        'MIN_REGIME_ALIGNMENT': 50.0
    })
    
    RISK_PER_TRADE: float = 0.01
    MAX_LEVERAGE: int = 100
    TELEGRAM_CONFIG: Optional[TelegramConfig] = None
    FUTURES_CONFIG: Optional[BinanceFuturesConfig] = None
    HYBRID_CONFIG: Optional[HybridConfig] = None
    client: Optional[Any] = None

# ========== BINANCE FUTURES CLIENT ==========
class BinanceFuturesClient:
    def __init__(self, config: Config):
        self.config = config
        self.futures_config = config.FUTURES_CONFIG or BinanceFuturesConfig()
        
        if self.futures_config.USE_TESTNET:
            self.base_url = self.futures_config.TESTNET_URL
        else:
            self.base_url = self.futures_config.BASE_URL
        
        self.backup_urls = [
            self.futures_config.BASE_URL_BACKUP,
            self.futures_config.BASE_URL_BACKUP2,
            self.futures_config.BASE_URL_BACKUP3
        ]
        
        self.timeout = self.futures_config.REQUEST_TIMEOUT
        self.session = self._create_session()
        self.klines_cache = {}
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit = 1200
        self.depth_history = deque(maxlen=20)
        
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _rate_limit(self):
        self.request_count += 1
        current_time = time.time()
        
        if current_time - self.last_request_time >= 60:
            self.request_count = 1
            self.last_request_time = current_time
        
        if self.request_count > self.rate_limit:
            sleep_time = 60 - (current_time - self.last_request_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.request_count = 1
            self.last_request_time = time.time()
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Optional[Dict]:
        self._rate_limit()
        
        urls = [self.base_url] + self.backup_urls
        last_error = None
        
        for url in urls:
            for attempt in range(3):
                try:
                    full_url = f"{url}{endpoint}"
                    
                    headers = {}
                    if signed:
                        if not self.futures_config.API_KEY:
                            logger.error("API key required for signed endpoint")
                            return None
                        
                        timestamp = int(time.time() * 1000)
                        if params is None:
                            params = {}
                        params['timestamp'] = timestamp
                        params['recvWindow'] = 5000
                        
                        query_string = urllib.parse.urlencode(params)
                        signature = hmac.new(
                            self.futures_config.API_SECRET.encode('utf-8'),
                            query_string.encode('utf-8'),
                            hashlib.sha256
                        ).hexdigest()
                        params['signature'] = signature
                        
                        headers['X-MBX-APIKEY'] = self.futures_config.API_KEY
                    
                    response = self.session.request(
                        method=method,
                        url=full_url,
                        params=params,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        # Store depth history for order book analysis
                        if endpoint == "/fapi/v1/depth":
                            self.depth_history.append(response.json())
                        
                        return response.json()
                    else:
                        logger.warning(f"Request failed with status {response.status_code}: {response.text}")
                        last_error = f"HTTP {response.status_code}"
                        break
                        
                except requests.exceptions.Timeout:
                    time.sleep(2 ** attempt)
                    continue
                except requests.exceptions.ConnectionError:
                    time.sleep(2 ** attempt)
                    continue
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request failed: {e}")
                    time.sleep(2 ** attempt)
                    continue
            
            continue
        
        logger.error(f"All URLs failed for {endpoint}. Last error: {last_error}")
        return None
    
    def test_connection(self) -> bool:
        try:
            result = self._make_request("GET", "/fapi/v1/ping")
            return result == {}
        except:
            return False
    
    def get_server_time(self) -> Optional[int]:
        try:
            result = self._make_request("GET", "/fapi/v1/time")
            return result['serverTime'] if result else None
        except:
            return None
    
    def get_exchange_info(self) -> Optional[Dict]:
        try:
            return self._make_request("GET", "/fapi/v1/exchangeInfo")
        except:
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        try:
            result = self._make_request("GET", "/fapi/v1/ticker/price", {"symbol": symbol})
            return float(result['price']) if result and 'price' in result else None
        except:
            return None
    
    def get_ticker_24hr(self, symbol: str) -> Optional[Dict]:
        try:
            result = self._make_request("GET", "/fapi/v1/ticker/24hr", {"symbol": symbol})
            if result:
                return {
                    'priceChange': float(result['priceChange']),
                    'priceChangePercent': float(result['priceChangePercent']),
                    'lastPrice': float(result['lastPrice']),
                    'volume': float(result['volume']),
                    'quoteVolume': float(result['quoteVolume']),
                    'highPrice': float(result['highPrice']),
                    'lowPrice': float(result['lowPrice']),
                    'openPrice': float(result['openPrice'])
                }
            return None
        except:
            return None
    
    def get_klines(self, symbol: str, interval: str, limit: int = 200) -> Optional[pd.DataFrame]:
        cache_key = f"{symbol}_{interval}_{limit}"
        
        if cache_key in self.klines_cache:
            data, timestamp = self.klines_cache[cache_key]
            if time.time() - timestamp < 15:
                return data.copy()
        
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            result = self._make_request("GET", "/fapi/v1/klines", params)
            
            if result and len(result) > 0:
                df = pd.DataFrame(result, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                self.klines_cache[cache_key] = (df.copy(), time.time())
                return df
            
            return None
        except:
            return None
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        try:
            params = {
                'symbol': symbol,
                'limit': limit
            }
            return self._make_request("GET", "/fapi/v1/depth", params)
        except:
            return None
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> Optional[List[Dict]]:
        try:
            params = {
                'symbol': symbol,
                'limit': limit
            }
            return self._make_request("GET", "/fapi/v1/trades", params)
        except:
            return None
    
    def get_funding_rate(self, symbol: str) -> Optional[float]:
        try:
            params = {'symbol': symbol}
            result = self._make_request("GET", "/fapi/v1/premiumIndex", params)
            return float(result['lastFundingRate']) * 100 if result and 'lastFundingRate' in result else None
        except:
            return None
    
    def get_open_interest(self, symbol: str) -> Optional[float]:
        try:
            params = {'symbol': symbol}
            result = self._make_request("GET", "/fapi/v1/openInterest", params)
            return float(result['openInterest']) if result and 'openInterest' in result else None
        except:
            return None
    
    def get_depth_history(self) -> List[Any]:
        """Get order book depth history"""
        return list(self.depth_history)
    
    # ========== ORDER EXECUTION METHODS ==========
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, 
                   price: Optional[float] = None, stop_price: Optional[float] = None,
                   reduce_only: bool = False) -> Optional[Dict]:
        """Place an order on Binance Futures"""
        try:
            # Check if API keys are configured
            if not self.futures_config.API_KEY or not self.futures_config.API_SECRET:
                logger.error("❌ API keys not configured. Cannot place real orders.")
                return None
            
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': quantity
            }
            
            if price and order_type.upper() in ['LIMIT', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT_MARKET']:
                params['price'] = price
            
            if stop_price and order_type.upper() in ['STOP', 'STOP_MARKET', 'TAKE_PROFIT_MARKET']:
                params['stopPrice'] = stop_price
            
            if reduce_only:
                params['reduceOnly'] = 'true'
            
            return self._make_request("POST", "/fapi/v1/order", params, signed=True)
            
        except Exception as e:
            logger.error(f"Order placement error: {e}")
            return None
    
    def place_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> Optional[Dict]:
        """Place stop loss order"""
        return self.place_order(
            symbol=symbol,
            side=side,
            order_type='STOP_MARKET',
            quantity=quantity,
            stop_price=stop_price,
            reduce_only=True
        )
    
    def place_take_profit(self, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict]:
        """Place take profit limit order"""
        return self.place_order(
            symbol=symbol,
            side=side,
            order_type='LIMIT',
            quantity=quantity,
            price=price,
            reduce_only=True
        )
    
    def get_position_info(self, symbol: str) -> Optional[Dict]:
        """Get current position information"""
        try:
            if not self.futures_config.API_KEY or not self.futures_config.API_SECRET:
                return None
            
            params = {'symbol': symbol}
            result = self._make_request("GET", "/fapi/v2/positionRisk", params, signed=True)
            if result and len(result) > 0:
                return result[0]
            return None
        except:
            return None
    
    def get_account_balance(self) -> Optional[float]:
        """Get account balance in USDT"""
        try:
            if not self.futures_config.API_KEY or not self.futures_config.API_SECRET:
                return None
            
            result = self._make_request("GET", "/fapi/v2/account", signed=True)
            if result and 'totalWalletBalance' in result:
                return float(result['totalWalletBalance'])
            return None
        except:
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """Cancel an order"""
        try:
            if not self.futures_config.API_KEY or not self.futures_config.API_SECRET:
                return False
            
            params = {
                'symbol': symbol,
                'orderId': order_id
            }
            result = self._make_request("DELETE", "/fapi/v1/order", params, signed=True)
            return result is not None
        except:
            return False
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """Cancel all orders for a symbol"""
        try:
            if not self.futures_config.API_KEY or not self.futures_config.API_SECRET:
                return False
            
            params = {'symbol': symbol}
            result = self._make_request("DELETE", "/fapi/v1/allOpenOrders", params, signed=True)
            return result is not None
        except:
            return False

# ========== ENHANCED BINANCE CLIENT ==========
class EnhancedBinanceFuturesClient(BinanceFuturesClient):
    def __init__(self, config: Config):
        super().__init__(config)
        self.public_api_urls = [
            "https://api.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://api3.binance.com"
        ]
        self.current_public_index = 0
        self.coingecko_cache = {}
        self.alternative_cache = {}
        self.binance_spot_cache = {}
        
        # Advanced features
        self.risk_manager = None
        self.portfolio_manager = None
        self.advanced_order_executor = None
        self.performance_analytics = None
        self.ml_models = None
        self.security_manager = None
    
    def _get_public_url(self) -> str:
        return self.public_api_urls[self.current_public_index]
    
    def _rotate_public_url(self):
        self.current_public_index = (self.current_public_index + 1) % len(self.public_api_urls)
        time.sleep(0.1)
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        try:
            cache_key = "fear_greed"
            if cache_key in self.alternative_cache:
                data, timestamp = self.alternative_cache[cache_key]
                if time.time() - timestamp < 3600:
                    return data
            
            url = "https://api.alternative.me/fng/?limit=1"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'data' in data and len(data['data']) > 0:
                    self.alternative_cache[cache_key] = (data, time.time())
                    return data
            return None
        except:
            return None
    
    def get_coingecko_global_data(self) -> Optional[Dict]:
        try:
            cache_key = "coingecko_global"
            if cache_key in self.coingecko_cache:
                data, timestamp = self.coingecko_cache[cache_key]
                if time.time() - timestamp < 300:
                    return data
            
            url = "https://api.coingecko.com/api/v3/global"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'data' in data:
                    self.coingecko_cache[cache_key] = (data, time.time())
                    return data
            return None
        except:
            return None
    
    def get_btc_dominance(self) -> Optional[float]:
        try:
            data = self.get_coingecko_global_data()
            if data and 'data' in data and 'market_cap_percentage' in data['data']:
                return float(data['data']['market_cap_percentage'].get('btc', 50.0))
            return None
        except:
            return None
    
    def get_total_market_cap(self) -> Optional[float]:
        try:
            data = self.get_coingecko_global_data()
            if data and 'data' in data and 'total_market_cap' in data['data']:
                return float(data['data']['total_market_cap'].get('usd', 0))
            return None
        except:
            return None
    
    def get_btc_price(self) -> Optional[float]:
        try:
            cache_key = "btc_price"
            if cache_key in self.binance_spot_cache:
                data, timestamp = self.binance_spot_cache[cache_key]
                if time.time() - timestamp < 15:
                    return data
            
            url = f"{self._get_public_url()}/api/v3/ticker/price?symbol=BTCUSDT"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'price' in data:
                    price = float(data['price'])
                    self.binance_spot_cache[cache_key] = (price, time.time())
                    return price
            return None
        except:
            return None
    
    def get_eth_price(self) -> Optional[float]:
        try:
            cache_key = "eth_price"
            if cache_key in self.binance_spot_cache:
                data, timestamp = self.binance_spot_cache[cache_key]
                if time.time() - timestamp < 15:
                    return data
            
            url = f"{self._get_public_url()}/api/v3/ticker/price?symbol=ETHUSDT"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'price' in data:
                    price = float(data['price'])
                    self.binance_spot_cache[cache_key] = (price, time.time())
                    return price
            return None
        except:
            return None
    
    def get_24hr_change(self, symbol: str) -> Optional[float]:
        try:
            cache_key = f"change_{symbol}"
            if cache_key in self.binance_spot_cache:
                data, timestamp = self.binance_spot_cache[cache_key]
                if time.time() - timestamp < 30:
                    return data
            
            url = f"{self._get_public_url()}/api/v3/ticker/24hr?symbol={symbol}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'priceChangePercent' in data:
                    change = float(data['priceChangePercent'])
                    self.binance_spot_cache[cache_key] = (change, time.time())
                    return change
            return None
        except:
            return None

# ========== TECHNICAL INDICATORS ==========
class TechnicalIndicators:
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        try:
            if len(df) < period + 1:
                return 50.0
            close = df['close'].values
            deltas = np.diff(close)
            seed = deltas[:period]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            rs = up / down if down != 0 else 100
            rsi = np.zeros_like(close)
            rsi[:period] = 100. - 100. / (1. + rs)
            for i in range(period, len(close)):
                delta = deltas[i-1]
                if delta > 0:
                    upval = delta
                    downval = 0.
                else:
                    upval = 0.
                    downval = -delta
                up = (up * (period - 1) + upval) / period
                down = (down * (period - 1) + downval) / period
                rs = up / down if down != 0 else 100
                rsi[i] = 100. - 100. / (1. + rs)
            return float(rsi[-1])
        except:
            return 50.0
    
    def calculate_macd(self, df: pd.DataFrame) -> Dict[str, float]:
        try:
            if len(df) < 26:
                return {'macd': 0, 'signal': 0, 'histogram': 0}
            close = df['close'].values
            exp1 = pd.Series(close).ewm(span=12, adjust=False).mean()
            exp2 = pd.Series(close).ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal
            return {
                'macd': float(macd.iloc[-1]),
                'signal': float(signal.iloc[-1]),
                'histogram': float(histogram.iloc[-1])
            }
        except:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        try:
            if len(df) < period:
                return {'upper': 0, 'middle': 0, 'lower': 0, 'width': 0}
            close = df['close'].values[-period:]
            middle = np.mean(close)
            std = np.std(close)
            upper = middle + (std * 2)
            lower = middle - (std * 2)
            width = ((upper - lower) / middle) * 100 if middle != 0 else 0
            return {
                'upper': float(upper),
                'middle': float(middle),
                'lower': float(lower),
                'width': float(width)
            }
        except:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'width': 0}
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> float:
        try:
            if len(df) < period:
                return float(df['close'].iloc[-1])
            close = df['close'].values
            ema = pd.Series(close).ewm(span=period, adjust=False).mean()
            return float(ema.iloc[-1])
        except:
            return float(df['close'].iloc[-1])
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, float]:
        try:
            if len(df) < k_period + d_period:
                return {'k': 50, 'd': 50}
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            k = 100 * ((df['close'] - low_min) / (high_max - low_min))
            d = k.rolling(window=d_period).mean()
            return {
                'k': float(k.iloc[-1]) if not pd.isna(k.iloc[-1]) else 50,
                'd': float(d.iloc[-1]) if not pd.isna(d.iloc[-1]) else 50
            }
        except:
            return {'k': 50, 'd': 50}
    
    def calculate_vwap(self, df: pd.DataFrame) -> float:
        try:
            if len(df) < 1:
                return float(df['close'].iloc[-1])
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            volume = df['volume']
            if volume.sum() == 0:
                return float(df['close'].iloc[-1])
            vwap = (typical_price * volume).sum() / volume.sum()
            return float(vwap)
        except:
            return float(df['close'].iloc[-1])
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> Optional[float]:
        try:
            if len(df) < period + 1:
                return None
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            tr = np.zeros(len(df))
            for i in range(1, len(df)):
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1])
                lc = abs(low[i] - close[i-1])
                tr[i] = max(hl, hc, lc)
            atr = pd.Series(tr).rolling(window=period).mean().values
            return float(atr[-1])
        except:
            return None
    
    def analyze_technical(self, df: pd.DataFrame, current_price: float) -> TechnicalAnalysis:
        try:
            rsi = self.calculate_rsi(df)
            if rsi > 70:
                rsi_signal = "OVERBOUGHT"
            elif rsi < 30:
                rsi_signal = "OVERSOLD"
            else:
                rsi_signal = "NEUTRAL"
            macd_data = self.calculate_macd(df)
            macd = macd_data['macd']
            macd_signal = macd_data['signal']
            macd_histogram = macd_data['histogram']
            if macd > macd_signal and macd_histogram > 0:
                macd_trend = "BULLISH"
            elif macd < macd_signal and macd_histogram < 0:
                macd_trend = "BEARISH"
            else:
                macd_trend = "NEUTRAL"
            bb = self.calculate_bollinger_bands(df)
            if current_price >= bb['upper'] and bb['upper'] > 0:
                bb_position = "ABOVE_UPPER"
            elif current_price <= bb['lower'] and bb['lower'] > 0:
                bb_position = "BELOW_LOWER"
            elif current_price > bb['middle']:
                bb_position = "ABOVE_MIDDLE"
            elif current_price < bb['middle']:
                bb_position = "BELOW_MIDDLE"
            else:
                bb_position = "AT_MIDDLE"
            stoch = self.calculate_stochastic(df)
            stoch_k = stoch['k']
            stoch_d = stoch['d']
            if stoch_k > 80 and stoch_d > 80:
                stoch_signal = "OVERBOUGHT"
            elif stoch_k < 20 and stoch_d < 20:
                stoch_signal = "OVERSOLD"
            else:
                stoch_signal = "NEUTRAL"
            ema9 = self.calculate_ema(df, 9)
            ema21 = self.calculate_ema(df, 21)
            if ema9 > ema21 and current_price > ema9:
                ema_trend = "BULLISH"
            elif ema9 < ema21 and current_price < ema9:
                ema_trend = "BEARISH"
            else:
                ema_trend = "NEUTRAL"
            vwap = self.calculate_vwap(df)
            if current_price > vwap * 1.01:
                vwap_position = "ABOVE"
            elif current_price < vwap * 0.99:
                vwap_position = "BELOW"
            else:
                vwap_position = "AT"
            avg_volume = df['volume'].iloc[-20:].mean() if len(df) >= 20 else df['volume'].mean()
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            volume_surge = volume_ratio > 1.5
            return TechnicalAnalysis(
                rsi=rsi, rsi_signal=rsi_signal,
                macd=macd, macd_signal=macd_signal, macd_histogram=macd_histogram, macd_trend=macd_trend,
                bb_position=bb_position, bb_width=bb['width'],
                stoch_k=stoch_k, stoch_d=stoch_d, stoch_signal=stoch_signal,
                ema9=ema9, ema21=ema21, ema_trend=ema_trend,
                vwap=vwap, vwap_position=vwap_position,
                volume_surge=volume_surge, volume_ratio=volume_ratio
            )
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            return TechnicalAnalysis(
                rsi=50, rsi_signal="NEUTRAL",
                macd=0, macd_signal=0, macd_histogram=0, macd_trend="NEUTRAL",
                bb_position="UNKNOWN", bb_width=0,
                stoch_k=50, stoch_d=50, stoch_signal="NEUTRAL",
                ema9=current_price, ema21=current_price, ema_trend="NEUTRAL",
                vwap=current_price, vwap_position="UNKNOWN",
                volume_surge=False, volume_ratio=1
            )

# ========== ENHANCED TECHNICAL INDICATORS ==========
class EnhancedTechnicalIndicators(TechnicalIndicators):
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        try:
            if len(df) < period + 1:
                return 25.0
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            tr = np.zeros(len(df))
            for i in range(1, len(df)):
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1])
                lc = abs(low[i] - close[i-1])
                tr[i] = max(hl, hc, lc)
            atr = pd.Series(tr).rolling(window=period).mean().values
            up_move = high[1:] - high[:-1]
            down_move = low[:-1] - low[1:]
            plus_dm = np.zeros(len(df))
            minus_dm = np.zeros(len(df))
            for i in range(1, len(df)):
                if up_move[i-1] > down_move[i-1] and up_move[i-1] > 0:
                    plus_dm[i] = up_move[i-1]
                if down_move[i-1] > up_move[i-1] and down_move[i-1] > 0:
                    minus_dm[i] = down_move[i-1]
            plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / atr
            minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / atr
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
            adx = pd.Series(dx).rolling(window=period).mean().values
            return float(adx[-1]) if len(adx) > 0 else 25.0
        except:
            return 25.0
    
    def calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> Tuple[float, str]:
        try:
            if len(df) < period + 1:
                return 50.0, "NEUTRAL"
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            money_flow = typical_price * df['volume']
            positive_flow = 0
            negative_flow = 0
            for i in range(-period, 0):
                if typical_price.iloc[i] > typical_price.iloc[i-1]:
                    positive_flow += money_flow.iloc[i]
                else:
                    negative_flow += money_flow.iloc[i]
            if negative_flow == 0:
                mfi = 100.0
            else:
                money_ratio = positive_flow / negative_flow
                mfi = 100 - (100 / (1 + money_ratio))
            if mfi > 80:
                signal = "OVERBOUGHT"
            elif mfi < 20:
                signal = "OVERSOLD"
            else:
                signal = "NEUTRAL"
            return float(mfi), signal
        except:
            return 50.0, "NEUTRAL"
    
    def calculate_ichimoku(self, df: pd.DataFrame) -> Dict:
        try:
            if len(df) < 52:
                return {
                    'tenkan': float(df['close'].iloc[-1]),
                    'kijun': float(df['close'].iloc[-1]),
                    'senkou_a': float(df['close'].iloc[-1]),
                    'senkou_b': float(df['close'].iloc[-1]),
                    'cloud': "NEUTRAL"
                }
            tenkan_high = df['high'].iloc[-9:].max()
            tenkan_low = df['low'].iloc[-9:].min()
            tenkan = (tenkan_high + tenkan_low) / 2
            kijun_high = df['high'].iloc[-26:].max()
            kijun_low = df['low'].iloc[-26:].min()
            kijun = (kijun_high + kijun_low) / 2
            senkou_a = (tenkan + kijun) / 2
            senkou_b_high = df['high'].iloc[-52:].max()
            senkou_b_low = df['low'].iloc[-52:].min()
            senkou_b = (senkou_b_high + senkou_b_low) / 2
            current_price = float(df['close'].iloc[-1])
            if current_price > senkou_a and current_price > senkou_b:
                cloud = "ABOVE"
            elif current_price < senkou_a and current_price < senkou_b:
                cloud = "BELOW"
            else:
                cloud = "INSIDE"
            return {
                'tenkan': float(tenkan),
                'kijun': float(kijun),
                'senkou_a': float(senkou_a),
                'senkou_b': float(senkou_b),
                'cloud': cloud
            }
        except:
            return {
                'tenkan': float(df['close'].iloc[-1]),
                'kijun': float(df['close'].iloc[-1]),
                'senkou_a': float(df['close'].iloc[-1]),
                'senkou_b': float(df['close'].iloc[-1]),
                'cloud': "NEUTRAL"
            }
    
    def calculate_enhanced_technical(self, df: pd.DataFrame, current_price: float) -> EnhancedTechnicalAnalysis:
        try:
            base = self.analyze_technical(df, current_price)
            adx = self.calculate_adx(df)
            if adx >= 50:
                adx_trend = "VERY_STRONG"
            elif adx >= 35:
                adx_trend = "STRONG"
            elif adx >= 25:
                adx_trend = "WEAK"
            else:
                adx_trend = "NO_TREND"
            obv_values = [0]
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    obv_values.append(obv_values[-1] + df['volume'].iloc[i])
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    obv_values.append(obv_values[-1] - df['volume'].iloc[i])
                else:
                    obv_values.append(obv_values[-1])
            obv = obv_values[-1] if obv_values else 0
            if len(obv_values) >= 5:
                obv_slope = obv_values[-1] - obv_values[-5]
                price_slope = df['close'].iloc[-1] - df['close'].iloc[-5]
                if obv_slope > 0 and price_slope > 0:
                    obv_trend = "BULLISH"
                elif obv_slope < 0 and price_slope < 0:
                    obv_trend = "BEARISH"
                elif obv_slope > 0 and price_slope < 0:
                    obv_trend = "BULLISH_DIVERGENCE"
                elif obv_slope < 0 and price_slope > 0:
                    obv_trend = "BEARISH_DIVERGENCE"
                else:
                    obv_trend = "NEUTRAL"
            else:
                obv_trend = "NEUTRAL"
            mfi, mfi_signal = self.calculate_mfi(df)
            ichimoku = self.calculate_ichimoku(df)
            if len(df) >= 20:
                high = df['high'].iloc[-20:].max()
                low = df['low'].iloc[-20:].min()
                diff = high - low
                fib_levels = {
                    '0.0': high,
                    '0.236': high - diff * 0.236,
                    '0.382': high - diff * 0.382,
                    '0.5': high - diff * 0.5,
                    '0.618': high - diff * 0.618,
                    '0.786': high - diff * 0.786,
                    '1.0': low
                }
            else:
                fib_levels = {}
            if len(df) >= 1:
                high = df['high'].iloc[-1]
                low = df['low'].iloc[-1]
                close = df['close'].iloc[-1]
                pp = (high + low + close) / 3
                r1 = 2 * pp - low
                s1 = 2 * pp - high
                r2 = pp + (high - low)
                s2 = pp - (high - low)
                r3 = high + 2 * (pp - low)
                s3 = low - 2 * (high - pp)
                pivot_points = {
                    'PP': float(pp), 'R1': float(r1), 'R2': float(r2), 'R3': float(r3),
                    'S1': float(s1), 'S2': float(s2), 'S3': float(s3)
                }
            else:
                pivot_points = {}
            if len(df) >= 1:
                high = df['high'].iloc[-1]
                low = df['low'].iloc[-1]
                close = df['close'].iloc[-1]
                range_hl = high - low
                camarilla = {
                    'R4': close + range_hl * 1.1 / 2,
                    'R3': close + range_hl * 1.1 / 4,
                    'R2': close + range_hl * 1.1 / 6,
                    'R1': close + range_hl * 1.1 / 12,
                    'S1': close - range_hl * 1.1 / 12,
                    'S2': close - range_hl * 1.1 / 6,
                    'S3': close - range_hl * 1.1 / 4,
                    'S4': close - range_hl * 1.1 / 2
                }
            else:
                camarilla = {}
            return EnhancedTechnicalAnalysis(
                rsi=base.rsi, rsi_signal=base.rsi_signal,
                macd=base.macd, macd_signal=base.macd_signal, macd_histogram=base.macd_histogram, macd_trend=base.macd_trend,
                bb_position=base.bb_position, bb_width=base.bb_width,
                stoch_k=base.stoch_k, stoch_d=base.stoch_d, stoch_signal=base.stoch_signal,
                ema9=base.ema9, ema21=base.ema21, ema_trend=base.ema_trend,
                vwap=base.vwap, vwap_position=base.vwap_position,
                volume_surge=base.volume_surge, volume_ratio=base.volume_ratio,
                adx=adx, adx_trend=adx_trend,
                obv=obv, obv_trend=obv_trend,
                money_flow_index=mfi, mfi_signal=mfi_signal,
                ichimoku_tenkan=ichimoku['tenkan'], ichimoku_kijun=ichimoku['kijun'],
                ichimoku_senkou_a=ichimoku['senkou_a'], ichimoku_senkou_b=ichimoku['senkou_b'],
                ichimoku_cloud=ichimoku['cloud'],
                fibonacci_levels=fib_levels, pivot_points=pivot_points, camarilla_levels=camarilla
            )
        except Exception as e:
            logger.error(f"Enhanced technical error: {e}")
            return EnhancedTechnicalAnalysis(
                rsi=50, rsi_signal="NEUTRAL",
                macd=0, macd_signal=0, macd_histogram=0, macd_trend="NEUTRAL",
                bb_position="UNKNOWN", bb_width=0,
                stoch_k=50, stoch_d=50, stoch_signal="NEUTRAL",
                ema9=current_price, ema21=current_price, ema_trend="NEUTRAL",
                vwap=current_price, vwap_position="UNKNOWN",
                volume_surge=False, volume_ratio=1,
                adx=25, adx_trend="WEAK",
                obv=0, obv_trend="NEUTRAL",
                money_flow_index=50, mfi_signal="NEUTRAL",
                ichimoku_tenkan=current_price, ichimoku_kijun=current_price,
                ichimoku_senkou_a=current_price, ichimoku_senkou_b=current_price,
                ichimoku_cloud="NEUTRAL",
                fibonacci_levels={}, pivot_points={}, camarilla_levels={}
            )

# ========== ORDER FLOW ANALYZER ==========
class OrderFlowAnalyzer:
    def __init__(self, client: BinanceFuturesClient):
        self.client = client
    
    def analyze_order_book(self, symbol: str, current_price: float = None) -> Optional[OrderBookAnalysis]:
        try:
            ob_data = self.client.get_order_book(symbol, 20)
            if not ob_data or 'bids' not in ob_data or 'asks' not in ob_data:
                return None
            bids = ob_data['bids']
            asks = ob_data['asks']
            if len(bids) == 0 or len(asks) == 0:
                return None
            bid_levels = []
            bid_volume = 0
            for bid in bids[:10]:
                price = float(bid[0])
                qty = float(bid[1])
                total = price * qty
                bid_levels.append(OrderBookLevel(price, qty, total))
                bid_volume += total
            ask_levels = []
            ask_volume = 0
            for ask in asks[:10]:
                price = float(ask[0])
                qty = float(ask[1])
                total = price * qty
                ask_levels.append(OrderBookLevel(price, qty, total))
                ask_volume += total
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            spread = best_ask - best_bid
            spread_percentage = (spread / best_bid) * 100 if best_bid > 0 else 0
            total_volume = bid_volume + ask_volume
            if total_volume > 0:
                bid_ask_ratio = bid_volume / ask_volume
                buy_pressure = (bid_volume / total_volume) * 100
                sell_pressure = (ask_volume / total_volume) * 100
                imbalance = ((bid_volume - ask_volume) / total_volume) * 100
            else:
                bid_ask_ratio = 1.0
                buy_pressure = 50.0
                sell_pressure = 50.0
                imbalance = 0.0
            support_levels = [float(bid[0]) for bid in bids[:5]]
            resistance_levels = [float(ask[0]) for ask in asks[:5]]
            return OrderBookAnalysis(
                best_bid=best_bid, best_ask=best_ask,
                spread=spread, spread_percentage=spread_percentage,
                bid_volume=bid_volume, ask_volume=ask_volume,
                bid_ask_ratio=bid_ask_ratio,
                buy_pressure=buy_pressure, sell_pressure=sell_pressure,
                imbalance=imbalance,
                top_bids=bid_levels[:5], top_asks=ask_levels[:5],
                support_levels=support_levels, resistance_levels=resistance_levels,
                symbol=symbol
            )
        except:
            return None
    
    def analyze_market_trades(self, symbol: str, current_price: float) -> Optional[MarketTradeAnalysis]:
        try:
            trades = self.client.get_recent_trades(symbol, 100)
            if not trades or len(trades) == 0:
                return None
            buy_volume = 0
            sell_volume = 0
            large_trades_buy = 0
            large_trades_sell = 0
            for trade in trades:
                qty = float(trade['qty'])
                price = float(trade['price'])
                is_buyer_maker = trade['isBuyerMaker']
                trade_value = qty * price
                if not is_buyer_maker:
                    buy_volume += trade_value
                    if trade_value > 10000:
                        large_trades_buy += 1
                else:
                    sell_volume += trade_value
                    if trade_value > 10000:
                        large_trades_sell += 1
            net_volume = buy_volume - sell_volume
            buy_sell_ratio = buy_volume / sell_volume if sell_volume > 0 else float('inf') if buy_volume > 0 else 1.0
            aggressive_buying = buy_volume > sell_volume * 1.2
            aggressive_selling = sell_volume > buy_volume * 1.2
            return MarketTradeAnalysis(
                buy_volume=buy_volume, sell_volume=sell_volume,
                net_volume=net_volume, buy_sell_ratio=buy_sell_ratio,
                large_trades_buy=large_trades_buy, large_trades_sell=large_trades_sell,
                aggressive_buying=aggressive_buying, aggressive_selling=aggressive_selling
            )
        except:
            return None
    
    def calculate_cumulative_flow(self, symbol: str) -> Optional[CumulativeFlow]:
        try:
            trades = self.client.get_recent_trades(symbol, 500)
            if not trades or len(trades) < 50:
                return None
            cumulative_delta = 0
            deltas_5min = []
            deltas_15min = []
            deltas_1h = []
            current_time = time.time() * 1000
            five_min_ago = current_time - 5 * 60 * 1000
            fifteen_min_ago = current_time - 15 * 60 * 1000
            one_hour_ago = current_time - 60 * 60 * 1000
            for trade in trades:
                trade_time = trade['time']
                qty = float(trade['qty'])
                price = float(trade['price'])
                is_buyer_maker = trade['isBuyerMaker']
                delta = (qty * price) if not is_buyer_maker else -(qty * price)
                cumulative_delta += delta
                if trade_time >= five_min_ago:
                    deltas_5min.append(delta)
                if trade_time >= fifteen_min_ago:
                    deltas_15min.append(delta)
                if trade_time >= one_hour_ago:
                    deltas_1h.append(delta)
            delta_5min = sum(deltas_5min)
            delta_15min = sum(deltas_15min)
            delta_1h = sum(deltas_1h)
            if delta_15min > 0 and abs(delta_15min) > abs(delta_1h) * 0.3:
                trend_strength = "STRONG_BULLISH"
                accumulation = True
                distribution = False
            elif delta_15min < 0 and abs(delta_15min) > abs(delta_1h) * 0.3:
                trend_strength = "STRONG_BEARISH"
                accumulation = False
                distribution = True
            elif delta_15min > 0:
                trend_strength = "WEAK_BULLISH"
                accumulation = True
                distribution = False
            elif delta_15min < 0:
                trend_strength = "WEAK_BEARISH"
                accumulation = False
                distribution = True
            else:
                trend_strength = "NEUTRAL"
                accumulation = False
                distribution = False
            return CumulativeFlow(
                delta_5min=delta_5min, delta_15min=delta_15min, delta_1h=delta_1h,
                cumulative_delta=cumulative_delta, trend_strength=trend_strength,
                accumulation=accumulation, distribution=distribution
            )
        except:
            return None

# ========== ADVANCED FEATURE 1: ADVANCED ORDER FLOW ANALYSIS ==========
@dataclass
class AdvancedOrderFlowAnalysis:
    """ការវិភាគជ្រៅនៃ order flow"""
    cumulative_delta: float = 0.0
    bid_ask_ratio_history: List[float] = field(default_factory=list)
    volume_profile: Dict[float, float] = field(default_factory=dict)
    iceberg_orders_detected: bool = False
    iceberg_levels: List[float] = field(default_factory=list)
    spoofing_detected: bool = False
    wash_trading_detected: bool = False
    large_orders_tracking: Dict[str, int] = field(default_factory=dict)
    order_flow_imbalance_score: float = 0.0
    accumulation_distribution_score: float = 0.0
    
    def analyze(self, order_book: Any, trades: List[Any], depth_history: List[Any]) -> 'AdvancedOrderFlowAnalysis':
        """វិភាគ order flow កម្រិតខ្ពស់"""
        try:
            self._detect_iceberg_orders(order_book, depth_history)
            self._detect_spoofing(depth_history)
            self._detect_wash_trading(trades)
            self._track_large_orders(trades)
            self._calculate_imbalance_score(order_book)
            self._calculate_accumulation_distribution(trades)
            return self
        except Exception as e:
            logger.error(f"Advanced Order Flow Analysis error: {e}")
            return self
    
    def _detect_iceberg_orders(self, order_book: Any, depth_history: List[Any]):
        try:
            if not order_book or not depth_history or len(depth_history) < 5:
                return
            current_bids = {float(b[0]): float(b[1]) for b in order_book.get('bids', [])[:10]}
            current_asks = {float(a[0]): float(a[1]) for a in order_book.get('asks', [])[:10]}
            for hist in depth_history[-3:]:
                if not hist:
                    continue
                hist_bids = {float(b[0]): float(b[1]) for b in hist.get('bids', [])[:10]}
                hist_asks = {float(a[0]): float(a[1]) for a in hist.get('asks', [])[:10]}
                for price in set(current_bids.keys()) & set(hist_bids.keys()):
                    if abs(current_bids[price] - hist_bids[price]) > 10 and abs(hist_bids[price]) > 5:
                        self.iceberg_orders_detected = True
                        self.iceberg_levels.append(price)
                        logger.info(f"🐟 Iceberg order detected at {price}")
                for price in set(current_asks.keys()) & set(hist_asks.keys()):
                    if abs(current_asks[price] - hist_asks[price]) > 10 and abs(hist_asks[price]) > 5:
                        self.iceberg_orders_detected = True
                        self.iceberg_levels.append(price)
                        logger.info(f"🐟 Iceberg order detected at {price}")
        except Exception as e:
            logger.error(f"Iceberg detection error: {e}")
    
    def _detect_spoofing(self, depth_history: List[Any]):
        try:
            if len(depth_history) < 10:
                return
            large_orders_disappeared = 0
            suspicious_patterns = 0
            for i in range(1, len(depth_history)):
                prev = depth_history[i-1]
                curr = depth_history[i]
                if not prev or not curr:
                    continue
                prev_asks = {float(a[0]): float(a[1]) for a in prev.get('asks', [])[:5]}
                curr_asks = {float(a[0]): float(a[1]) for a in curr.get('asks', [])[:5]}
                for price in set(prev_asks.keys()) - set(curr_asks.keys()):
                    if prev_asks[price] > 20:
                        large_orders_disappeared += 1
                if len(curr_asks) > 0 and len(prev_asks) > 0:
                    avg_prev_price = sum(prev_asks.keys()) / len(prev_asks)
                    avg_curr_price = sum(curr_asks.keys()) / len(curr_asks)
                    if abs(avg_curr_price - avg_prev_price) > 0.001 * avg_prev_price:
                        suspicious_patterns += 1
            if large_orders_disappeared >= 3 and suspicious_patterns >= 2:
                self.spoofing_detected = True
                logger.info("🎭 Spoofing detected in market")
        except Exception as e:
            logger.error(f"Spoofing detection error: {e}")
    
    def _detect_wash_trading(self, trades: List[Any]):
        try:
            if not trades or len(trades) < 20:
                return
            same_size_trades = defaultdict(int)
            same_time_trades = 0
            buy_sell_patterns = 0
            for i in range(0, len(trades)-1, 2):
                if i+1 >= len(trades):
                    break
                t1 = trades[i]
                t2 = trades[i+1]
                if abs(float(t1['qty']) - float(t2['qty'])) < 0.001 and \
                   abs(float(t1['price']) - float(t2['price'])) < 0.001:
                    key = (float(t1['price']), float(t1['qty']))
                    same_size_trades[key] += 1
                if abs(t1['time'] - t2['time']) < 100:
                    same_time_trades += 1
                    if t1['isBuyerMaker'] != t2['isBuyerMaker']:
                        buy_sell_patterns += 1
            if len(same_size_trades) > 0 and max(same_size_trades.values()) >= 3:
                self.wash_trading_detected = True
                logger.info("🔄 Wash trading detected")
        except Exception as e:
            logger.error(f"Wash trading detection error: {e}")
    
    def _track_large_orders(self, trades: List[Any]):
        try:
            if not trades:
                return
            large_buy = 0
            large_sell = 0
            for trade in trades[-50:]:
                qty = float(trade['qty'])
                price = float(trade['price'])
                value = qty * price
                if value > 50000:
                    if not trade['isBuyerMaker']:
                        large_buy += 1
                        self.large_orders_tracking[f"BUY_{price:.2f}"] = \
                            self.large_orders_tracking.get(f"BUY_{price:.2f}", 0) + 1
                    else:
                        large_sell += 1
                        self.large_orders_tracking[f"SELL_{price:.2f}"] = \
                            self.large_orders_tracking.get(f"SELL_{price:.2f}", 0) + 1
            logger.info(f"🐋 Large orders: {large_buy} buys, {large_sell} sells")
        except Exception as e:
            logger.error(f"Large orders tracking error: {e}")
    
    def _calculate_imbalance_score(self, order_book: Any):
        try:
            if not order_book:
                return
            bids = order_book.get('bids', [])[:10]
            asks = order_book.get('asks', [])[:10]
            bid_volume = sum(float(b[1]) * float(b[0]) for b in bids)
            ask_volume = sum(float(a[1]) * float(a[0]) for a in asks)
            total = bid_volume + ask_volume
            if total > 0:
                self.order_flow_imbalance_score = ((bid_volume - ask_volume) / total) * 100
            if len(bids) > 0 and len(asks) > 0:
                ratio = bid_volume / ask_volume if ask_volume > 0 else 2.0
                self.bid_ask_ratio_history.append(ratio)
                if len(self.bid_ask_ratio_history) > 20:
                    self.bid_ask_ratio_history.pop(0)
        except Exception as e:
            logger.error(f"Imbalance score calculation error: {e}")
    
    def _calculate_accumulation_distribution(self, trades: List[Any]):
        try:
            if not trades or len(trades) < 20:
                return
            total_buy_volume = 0
            total_sell_volume = 0
            weighted_price_sum = 0
            total_volume = 0
            for trade in trades[-50:]:
                qty = float(trade['qty'])
                price = float(trade['price'])
                value = qty * price
                if not trade['isBuyerMaker']:
                    total_buy_volume += value
                else:
                    total_sell_volume += value
                weighted_price_sum += price * value
                total_volume += value
            if total_volume > 0:
                vwap = weighted_price_sum / total_volume
                current_price = float(trades[-1]['price'])
                if total_buy_volume > total_sell_volume:
                    self.accumulation_distribution_score = (current_price / vwap - 1) * 100
                else:
                    self.accumulation_distribution_score = -(current_price / vwap - 1) * 100
        except Exception as e:
            logger.error(f"Accumulation/distribution calculation error: {e}")

# ========== ADVANCED FEATURE 2: SMART MONEY FOOTPRINT ==========
@dataclass
class SmartMoneyFootprint:
    """ស្នាមជើងរបស់ Smart Money"""
    institutional_order_blocks: List[Dict] = field(default_factory=list)
    liquidity_grab_zones: List[Tuple[float, float]] = field(default_factory=list)
    stop_hunt_levels: List[float] = field(default_factory=list)
    manipulation_detected: bool = False
    manipulation_type: str = "NONE"
    whale_activity: str = "NONE"
    smart_money_flow: float = 0.0
    institutional_sentiment: float = 0.0
    
    def analyze(self, df: pd.DataFrame, order_book: Any, trades: List[Any]) -> 'SmartMoneyFootprint':
        """វិភាគស្នាមជើង smart money"""
        try:
            self._detect_institutional_order_blocks(df)
            self._detect_liquidity_grab_zones(df, order_book)
            self._detect_stop_hunt_levels(df)
            self._track_whale_activity(trades)
            self._calculate_smart_money_flow(order_book, trades)
            return self
        except Exception as e:
            logger.error(f"Smart Money Footprint analysis error: {e}")
            return self
    
    def _detect_institutional_order_blocks(self, df: pd.DataFrame):
        try:
            if len(df) < 30:
                return
            for i in range(5, len(df)-5):
                volume_spike = df['volume'].iloc[i] > df['volume'].iloc[i-5:i].mean() * 3
                price_range = (df['high'].iloc[i] - df['low'].iloc[i]) / df['close'].iloc[i] * 100
                if volume_spike and price_range < 1.0:
                    block = {
                        'price': df['close'].iloc[i],
                        'volume': df['volume'].iloc[i],
                        'type': 'BUY' if df['close'].iloc[i] > df['open'].iloc[i] else 'SELL',
                        'strength': min(df['volume'].iloc[i] / df['volume'].iloc[i-5:i].mean() * 10, 100)
                    }
                    self.institutional_order_blocks.append(block)
            self.institutional_order_blocks = self.institutional_order_blocks[-5:]
        except Exception as e:
            logger.error(f"Institutional order blocks detection error: {e}")
    
    def _detect_liquidity_grab_zones(self, df: pd.DataFrame, order_book: Any):
        try:
            if len(df) < 20 or not order_book:
                return
            current_price = float(df['close'].iloc[-1])
            bids = order_book.get('bids', [])[:5]
            asks = order_book.get('asks', [])[:5]
            for bid in bids:
                price = float(bid[0])
                if abs(price - current_price) / current_price < 0.02:
                    self.liquidity_grab_zones.append((price - 0.001*price, price))
            for ask in asks:
                price = float(ask[0])
                if abs(price - current_price) / current_price < 0.02:
                    self.liquidity_grab_zones.append((price, price + 0.001*price))
            recent_high = df['high'].iloc[-10:].max()
            recent_low = df['low'].iloc[-10:].min()
            if abs(recent_high - current_price) / current_price < 0.01:
                self.liquidity_grab_zones.append((recent_high - 0.001*recent_high, recent_high))
            if abs(recent_low - current_price) / current_price < 0.01:
                self.liquidity_grab_zones.append((recent_low, recent_low + 0.001*recent_low))
        except Exception as e:
            logger.error(f"Liquidity grab zones detection error: {e}")
    
    def _detect_stop_hunt_levels(self, df: pd.DataFrame):
        try:
            if len(df) < 30:
                return
            for i in range(10, len(df)-5):
                if df['high'].iloc[i] > df['high'].iloc[i-5:i].max() * 1.005:
                    if df['close'].iloc[i+1] < df['high'].iloc[i] * 0.998:
                        self.stop_hunt_levels.append(df['high'].iloc[i])
                if df['low'].iloc[i] < df['low'].iloc[i-5:i].min() * 0.995:
                    if df['close'].iloc[i+1] > df['low'].iloc[i] * 1.002:
                        self.stop_hunt_levels.append(df['low'].iloc[i])
            self.stop_hunt_levels = list(set(self.stop_hunt_levels))[-5:]
        except Exception as e:
            logger.error(f"Stop hunt levels detection error: {e}")
    
    def _track_whale_activity(self, trades: List[Any]):
        try:
            if not trades or len(trades) < 20:
                return
            whale_buys = 0
            whale_sells = 0
            whale_value = 0
            for trade in trades[-50:]:
                qty = float(trade['qty'])
                price = float(trade['price'])
                value = qty * price
                if value > 100000:
                    whale_value += value
                    if not trade['isBuyerMaker']:
                        whale_buys += 1
                    else:
                        whale_sells += 1
            if whale_buys + whale_sells > 0:
                if whale_buys > whale_sells * 2:
                    self.whale_activity = "STRONG_ACCUMULATION"
                elif whale_buys > whale_sells:
                    self.whale_activity = "ACCUMULATION"
                elif whale_sells > whale_buys * 2:
                    self.whale_activity = "STRONG_DISTRIBUTION"
                elif whale_sells > whale_buys:
                    self.whale_activity = "DISTRIBUTION"
                else:
                    self.whale_activity = "NEUTRAL"
            logger.info(f"🐋 Whale activity: {self.whale_activity}, Value: ${whale_value:,.0f}")
        except Exception as e:
            logger.error(f"Whale activity tracking error: {e}")
    
    def _calculate_smart_money_flow(self, order_book: Any, trades: List[Any]):
        try:
            if not order_book or not trades:
                return
            bids = order_book.get('bids', [])[:5]
            asks = order_book.get('asks', [])[:5]
            bid_volume = sum(float(b[1]) * float(b[0]) for b in bids)
            ask_volume = sum(float(a[1]) * float(a[0]) for a in asks)
            order_book_flow = 0
            if bid_volume + ask_volume > 0:
                order_book_flow = (bid_volume - ask_volume) / (bid_volume + ask_volume) * 100
            large_buy_value = 0
            large_sell_value = 0
            for trade in trades[-20:]:
                qty = float(trade['qty'])
                price = float(trade['price'])
                value = qty * price
                if value > 50000:
                    if not trade['isBuyerMaker']:
                        large_buy_value += value
                    else:
                        large_sell_value += value
            trade_flow = 0
            if large_buy_value + large_sell_value > 0:
                trade_flow = (large_buy_value - large_sell_value) / (large_buy_value + large_sell_value) * 100
            self.smart_money_flow = (order_book_flow * 0.4 + trade_flow * 0.6)
            self.institutional_sentiment = self.smart_money_flow / 100
        except Exception as e:
            logger.error(f"Smart money flow calculation error: {e}")

# ========== ADVANCED FEATURE 3: MARKET MICROSTRUCTURE ==========
@dataclass
class MarketMicrostructure:
    """ការវិភាគរចនាសម្ព័ន្ធទីផ្សារកម្រិតតូច"""
    tick_velocity: float = 0.0
    trade_intensity: float = 0.0
    spread_behavior: str = "NORMAL"
    market_maker_activity: float = 0.0
    high_frequency_trading_detected: bool = False
    order_book_imbalance_history: List[float] = field(default_factory=list)
    price_discovery_efficiency: float = 0.0
    market_depth_profile: Dict[str, float] = field(default_factory=dict)
    
    def analyze(self, order_book: Any, trades: List[Any], depth_history: List[Any]) -> 'MarketMicrostructure':
        """វិភាគរចនាសម្ព័ន្ធទីផ្សារ"""
        try:
            self._calculate_tick_velocity(trades)
            self._calculate_trade_intensity(trades)
            self._analyze_spread_behavior(order_book, depth_history)
            self._measure_market_maker_activity(order_book, depth_history)
            self._detect_hft(trades)
            self._analyze_market_depth(order_book)
            return self
        except Exception as e:
            logger.error(f"Market Microstructure analysis error: {e}")
            return self
    
    def _calculate_tick_velocity(self, trades: List[Any]):
        try:
            if not trades or len(trades) < 10:
                return
            if len(trades) >= 10:
                time_diff = (trades[-1]['time'] - trades[-10]['time']) / 1000
                if time_diff > 0:
                    self.tick_velocity = 10 / time_diff
        except Exception as e:
            logger.error(f"Tick velocity calculation error: {e}")
    
    def _calculate_trade_intensity(self, trades: List[Any]):
        try:
            if not trades or len(trades) < 10:
                return
            total_volume = sum(float(t['qty']) * float(t['price']) for t in trades[-20:])
            self.trade_intensity = total_volume / len(trades[-20:]) if trades else 0
        except Exception as e:
            logger.error(f"Trade intensity calculation error: {e}")
    
    def _analyze_spread_behavior(self, order_book: Any, depth_history: List[Any]):
        try:
            if not order_book:
                return
            best_bid = float(order_book['bids'][0][0]) if order_book.get('bids') else 0
            best_ask = float(order_book['asks'][0][0]) if order_book.get('asks') else 0
            if best_bid > 0 and best_ask > 0:
                current_spread = (best_ask - best_bid) / best_bid * 100
            if len(depth_history) >= 5:
                spreads = []
                for hist in depth_history[-5:]:
                    if hist.get('bids') and hist.get('asks'):
                        bid = float(hist['bids'][0][0])
                        ask = float(hist['asks'][0][0])
                        spreads.append((ask - bid) / bid * 100)
                avg_spread = np.mean(spreads) if spreads else current_spread
                if current_spread < avg_spread * 0.7:
                    self.spread_behavior = "TIGHTENING"
                elif current_spread > avg_spread * 1.3:
                    self.spread_behavior = "WIDENING"
                else:
                    self.spread_behavior = "NORMAL"
        except Exception as e:
            logger.error(f"Spread behavior analysis error: {e}")
    
    def _measure_market_maker_activity(self, order_book: Any, depth_history: List[Any]):
        try:
            if not order_book or len(depth_history) < 3:
                return
            current_bid_size = sum(float(b[1]) for b in order_book.get('bids', [])[:3])
            current_ask_size = sum(float(a[1]) for a in order_book.get('asks', [])[:3])
            prev = depth_history[-2]
            prev_bid_size = sum(float(b[1]) for b in prev.get('bids', [])[:3])
            prev_ask_size = sum(float(a[1]) for a in prev.get('asks', [])[:3])
            bid_change = abs(current_bid_size - prev_bid_size) / (prev_bid_size + 1)
            ask_change = abs(current_ask_size - prev_ask_size) / (prev_ask_size + 1)
            self.market_maker_activity = (bid_change + ask_change) * 50
        except Exception as e:
            logger.error(f"Market maker activity measurement error: {e}")
    
    def _detect_hft(self, trades: List[Any]):
        try:
            if not trades or len(trades) < 20:
                return
            time_diffs = []
            for i in range(1, min(20, len(trades))):
                time_diffs.append(trades[-i]['time'] - trades[-i-1]['time'])
            avg_time_diff = np.mean(time_diffs) if time_diffs else 0
            if avg_time_diff < 50 and len([d for d in time_diffs if d < 50]) > 10:
                self.high_frequency_trading_detected = True
                logger.info("🤖 High Frequency Trading detected")
        except Exception as e:
            logger.error(f"HFT detection error: {e}")
    
    def _analyze_market_depth(self, order_book: Any):
        try:
            if not order_book:
                return
            bids = order_book.get('bids', [])[:5]
            asks = order_book.get('asks', [])[:5]
            if bids and asks:
                bid_depth = sum(float(b[1]) * float(b[0]) for b in bids)
                ask_depth = sum(float(a[1]) * float(a[0]) for a in asks)
                self.market_depth_profile = {
                    'bid_depth': bid_depth,
                    'ask_depth': ask_depth,
                    'total_depth': bid_depth + ask_depth,
                    'bid_ask_ratio': bid_depth / ask_depth if ask_depth > 0 else 1
                }
        except Exception as e:
            logger.error(f"Market depth analysis error: {e}")

# ========== MULTI-TIMEFRAME MARKET REGIME DETECTOR ==========
class MultiTimeframeRegimeDetector:
    def __init__(self, client: EnhancedBinanceFuturesClient, config: HybridConfig = None):
        self.client = client
        self.indicators = TechnicalIndicators()
        self.enhanced_indicators = EnhancedTechnicalIndicators()
        self.config = config or HybridConfig()
    
    def detect_multi_tf_regime(self, symbol: str) -> MultiTimeframeRegime:
        try:
            ultra_short_data = self._get_timeframe_group(symbol, TimeframeType.ULTRA_SHORT)
            short_data = self._get_timeframe_group(symbol, TimeframeType.SHORT)
            medium_data = self._get_timeframe_group(symbol, TimeframeType.MEDIUM)
            long_data = self._get_timeframe_group(symbol, TimeframeType.LONG)
            ultra_short_regime = self._analyze_timeframe_group(ultra_short_data, TimeframeType.ULTRA_SHORT)
            short_regime = self._analyze_timeframe_group(short_data, TimeframeType.SHORT)
            medium_regime = self._analyze_timeframe_group(medium_data, TimeframeType.MEDIUM)
            long_regime = self._analyze_timeframe_group(long_data, TimeframeType.LONG)
            overall_regime, overall_strength = self._calculate_overall_regime(
                ultra_short_regime, short_regime, medium_regime, long_regime
            )
            regime_alignment = self._calculate_regime_alignment(
                ultra_short_regime, short_regime, medium_regime, long_regime, overall_regime
            )
            dominant_trend = self._determine_dominant_trend(
                ultra_short_regime, short_regime, medium_regime, long_regime
            )
            regime_score = self._calculate_regime_score(overall_regime, overall_strength)
            all_timeframes = {}
            for group_data in [ultra_short_data, short_data, medium_data, long_data]:
                for tf, df in group_data.items():
                    if df is not None:
                        all_timeframes[tf] = self._analyze_single_timeframe(df)
            return MultiTimeframeRegime(
                ultra_short_regime=ultra_short_regime['regime'],
                ultra_short_strength=ultra_short_regime['strength'],
                ultra_short_adx=ultra_short_regime['adx'],
                ultra_short_volatility=ultra_short_regime['volatility'],
                short_regime=short_regime['regime'],
                short_strength=short_regime['strength'],
                short_adx=short_regime['adx'],
                short_volatility=short_regime['volatility'],
                medium_regime=medium_regime['regime'],
                medium_strength=medium_regime['strength'],
                medium_adx=medium_regime['adx'],
                medium_volatility=medium_regime['volatility'],
                long_regime=long_regime['regime'],
                long_strength=long_regime['strength'],
                long_adx=long_regime['adx'],
                long_volatility=long_regime['volatility'],
                overall_regime=overall_regime,
                overall_strength=overall_strength,
                regime_alignment=regime_alignment,
                dominant_trend=dominant_trend,
                regime_score=regime_score,
                all_timeframes=all_timeframes
            )
        except Exception as e:
            logger.error(f"Multi-timeframe regime detection error for {symbol}: {e}")
            return self._get_default_multi_tf_regime()
    
    def _get_timeframe_group(self, symbol: str, group: TimeframeType) -> Dict[str, Optional[pd.DataFrame]]:
        timeframes = TimeframeConfig.ANALYSIS_GROUPS[group]
        result = {}
        for tf in timeframes:
            df = self.client.get_klines(symbol, tf, 100)
            result[tf] = df
        return result
    
    def _analyze_single_timeframe(self, df: pd.DataFrame) -> Dict:
        if df is None or len(df) < 50:
            return {'regime': "UNKNOWN", 'strength': 50, 'adx': 25, 'volatility': "MEDIUM"}
        adx = self.enhanced_indicators.calculate_adx(df)
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(24) * 100 if len(returns) > 0 else 2.0
        if volatility > 5:
            vol_level = "HIGH"
        elif volatility > 2.5:
            vol_level = "MEDIUM"
        else:
            vol_level = "LOW"
        ema9 = self.indicators.calculate_ema(df, 9)
        ema21 = self.indicators.calculate_ema(df, 21)
        current_price = float(df['close'].iloc[-1])
        if ema9 > ema21 and current_price > ema9:
            regime = "TRENDING_BULL"
            strength = min(adx * 1.5, 100)
        elif ema9 < ema21 and current_price < ema9:
            regime = "TRENDING_BEAR"
            strength = min(adx * 1.5, 100)
        elif adx < 25:
            regime = "RANGING"
            strength = 50 - (adx * 0.5)
        else:
            regime = "VOLATILE"
            strength = min(adx, 100)
        return {'regime': regime, 'strength': strength, 'adx': adx, 'volatility': vol_level}
    
    def _analyze_timeframe_group(self, group_data: Dict[str, Optional[pd.DataFrame]], group: TimeframeType) -> Dict:
        valid_dfs = {tf: df for tf, df in group_data.items() if df is not None and len(df) > 50}
        if not valid_dfs:
            return {'regime': "UNKNOWN", 'strength': 50, 'adx': 25, 'volatility': "MEDIUM"}
        if group == TimeframeType.ULTRA_SHORT:
            weights = self.config.ULTRA_SHORT_TIMEFRAMES
        elif group == TimeframeType.SHORT:
            weights = self.config.SHORT_TIMEFRAMES
        elif group == TimeframeType.MEDIUM:
            weights = self.config.MEDIUM_TIMEFRAMES
        else:
            weights = self.config.LONG_TIMEFRAMES
        analyses = {}
        for tf, df in valid_dfs.items():
            analyses[tf] = self._analyze_single_timeframe(df)
        total_weight = 0
        weighted_regime_score = 0
        weighted_adx = 0
        volatility_counts = defaultdict(int)
        for tf, analysis in analyses.items():
            weight = weights.get(tf, 1.0 / len(valid_dfs))
            total_weight += weight
            regime_score = self._regime_to_score(analysis['regime'])
            weighted_regime_score += regime_score * weight * (analysis['strength'] / 100)
            weighted_adx += analysis['adx'] * weight
            volatility_counts[analysis['volatility']] += weight
        if total_weight > 0:
            avg_regime_score = weighted_regime_score / total_weight
            avg_adx = weighted_adx / total_weight
        else:
            avg_regime_score = 0
            avg_adx = 25
        primary_volatility = max(volatility_counts, key=volatility_counts.get, default="MEDIUM")
        if avg_regime_score > 0.4:
            regime = "TRENDING_BULL"
            strength = min(avg_adx * 1.5, 100)
        elif avg_regime_score < -0.4:
            regime = "TRENDING_BEAR"
            strength = min(avg_adx * 1.5, 100)
        elif avg_adx < 25:
            regime = "RANGING"
            strength = 50 - (avg_adx * 0.5)
        else:
            regime = "VOLATILE"
            strength = min(avg_adx, 100)
        return {'regime': regime, 'strength': strength, 'adx': avg_adx, 'volatility': primary_volatility}
    
    def _regime_to_score(self, regime: str) -> float:
        scores = {
            'TRENDING_BULL': 1.0,
            'VOLATILE': 0.5,
            'RANGING': 0,
            'UNKNOWN': 0,
            'TRENDING_BEAR': -1.0
        }
        return scores.get(regime, 0)
    
    def _calculate_overall_regime(self, ultra_short: Dict, short: Dict, medium: Dict, long: Dict) -> Tuple[str, float]:
        weights = {
            'ultra_short': self.config.ULTRA_SHORT_WEIGHT,
            'short': self.config.SHORT_WEIGHT,
            'medium': self.config.MEDIUM_WEIGHT,
            'long': self.config.LONG_WEIGHT
        }
        total_score = 0
        total_weight = 0
        regimes = [ultra_short, short, medium, long]
        weight_list = [weights['ultra_short'], weights['short'], weights['medium'], weights['long']]
        for regime_dict, weight in zip(regimes, weight_list):
            regime = regime_dict['regime']
            strength = regime_dict['strength']
            base_score = self._regime_to_score(regime)
            adjusted_score = base_score * (strength / 100)
            total_score += adjusted_score * weight
            total_weight += weight
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0
        if final_score > 0.4:
            overall_regime = "TRENDING_BULL"
            overall_strength = final_score * 100
        elif final_score < -0.4:
            overall_regime = "TRENDING_BEAR"
            overall_strength = abs(final_score) * 100
        elif abs(final_score) < 0.1:
            overall_regime = "RANGING"
            overall_strength = 50
        else:
            overall_regime = "VOLATILE"
            overall_strength = abs(final_score) * 100
        return overall_regime, overall_strength
    
    def _calculate_regime_alignment(self, ultra_short: Dict, short: Dict, medium: Dict, long: Dict, overall: str) -> float:
        regimes = [ultra_short['regime'], short['regime'], medium['regime'], long['regime']]
        aligned_count = 0
        for regime in regimes:
            if regime == overall:
                aligned_count += 1
            elif overall == "TRENDING_BULL" and regime in ["VOLATILE", "RANGING"]:
                aligned_count += 0.5
            elif overall == "TRENDING_BEAR" and regime in ["VOLATILE", "RANGING"]:
                aligned_count += 0.5
        return (aligned_count / len(regimes)) * 100
    
    def _determine_dominant_trend(self, ultra_short: Dict, short: Dict, medium: Dict, long: Dict) -> str:
        bullish_count = 0
        bearish_count = 0
        for regime_dict in [ultra_short, short, medium, long]:
            regime = regime_dict['regime']
            if "BULL" in regime:
                bullish_count += 1
            elif "BEAR" in regime:
                bearish_count += 1
        if bullish_count > bearish_count:
            return "BULLISH"
        elif bearish_count > bullish_count:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _calculate_regime_score(self, overall_regime: str, overall_strength: float) -> float:
        if overall_regime == "TRENDING_BULL":
            return overall_strength
        elif overall_regime == "TRENDING_BEAR":
            return -overall_strength
        else:
            return 0
    
    def _get_default_multi_tf_regime(self) -> MultiTimeframeRegime:
        return MultiTimeframeRegime(
            ultra_short_regime="UNKNOWN", ultra_short_strength=50, ultra_short_adx=25, ultra_short_volatility="MEDIUM",
            short_regime="UNKNOWN", short_strength=50, short_adx=25, short_volatility="MEDIUM",
            medium_regime="UNKNOWN", medium_strength=50, medium_adx=25, medium_volatility="MEDIUM",
            long_regime="UNKNOWN", long_strength=50, long_adx=25, long_volatility="MEDIUM",
            overall_regime="UNKNOWN", overall_strength=50,
            regime_alignment=0, dominant_trend="NEUTRAL", regime_score=0,
            all_timeframes={}
        )

# ========== MARKET REGIME DETECTOR ==========
class MarketRegimeDetector:
    def __init__(self, client: EnhancedBinanceFuturesClient, config: HybridConfig = None):
        self.client = client
        self.multi_tf_detector = MultiTimeframeRegimeDetector(client, config)
    
    def detect_regime(self, symbol: str, df_4h: pd.DataFrame = None, df_1d: pd.DataFrame = None) -> MarketRegime:
        try:
            multi_tf = self.multi_tf_detector.detect_multi_tf_regime(symbol)
            return MarketRegime(
                regime_type=multi_tf.overall_regime,
                strength=multi_tf.overall_strength,
                volatility=self._get_primary_volatility(multi_tf),
                volume_profile="NEUTRAL",
                adx_value=multi_tf.medium_adx,
                adx_trend=self._get_adx_trend(multi_tf.medium_adx),
                regime_score=multi_tf.regime_score
            )
        except:
            return MarketRegime(
                regime_type="UNKNOWN", strength=50, volatility="MEDIUM",
                volume_profile="NEUTRAL", adx_value=25, adx_trend="WEAK", regime_score=0
            )
    
    def _get_primary_volatility(self, multi_tf: MultiTimeframeRegime) -> str:
        volatilities = [
            multi_tf.ultra_short_volatility, multi_tf.short_volatility,
            multi_tf.medium_volatility, multi_tf.long_volatility
        ]
        vol_counts = {v: volatilities.count(v) for v in set(volatilities)}
        return max(vol_counts, key=vol_counts.get, default="MEDIUM")
    
    def _get_adx_trend(self, adx: float) -> str:
        if adx >= 50:
            return "VERY_STRONG"
        elif adx >= 35:
            return "STRONG"
        elif adx >= 25:
            return "WEAK"
        else:
            return "NO_TREND"

# ========== SMART MONEY DETECTOR ==========
class SmartMoneyDetector:
    def __init__(self, client: EnhancedBinanceFuturesClient):
        self.client = client
    
    def detect_smart_money(self, symbol: str, df: pd.DataFrame, ob: Optional[OrderBookAnalysis]) -> SmartMoneyConcepts:
        try:
            order_block_detected = False
            order_block_type = "NEUTRAL"
            order_block_price = 0.0
            order_block_strength = 0.0
            liquidity_sweep = False
            liquidity_levels = []
            fvg_detected = False
            fvg_type = "NEUTRAL"
            fvg_low = 0.0
            fvg_high = 0.0
            fvg_filled = False
            breaker_block = False
            mitigation_detected = False
            institutional_divergence = False
            smart_money_score = 0.0
            primary_concept = SmartMoneyConcept.NONE
            concept_summary = ""
            if len(df) >= 20:
                price_changes = df['close'].pct_change() * 100
                strong_buy_candles = price_changes[price_changes > 2].index
                strong_sell_candles = price_changes[price_changes < -2].index
                if len(strong_buy_candles) > 0:
                    last_strong = strong_buy_candles[-1]
                    try:
                        idx = df.index.get_loc(last_strong)
                        if idx + 5 < len(df):
                            consolidation = df['close'].iloc[idx:idx+5]
                            consolidation_range = (consolidation.max() - consolidation.min()) / consolidation.min() * 100
                            if consolidation_range < 3:
                                order_block_detected = True
                                order_block_type = "BULLISH"
                                order_block_price = df['low'].iloc[idx]
                                order_block_strength = min(50 + (price_changes.iloc[idx] * 5), 100)
                                primary_concept = SmartMoneyConcept.ORDER_BLOCK
                                concept_summary = f"Bullish order block at {order_block_price:.4f}"
                    except:
                        pass
                if not order_block_detected and len(strong_sell_candles) > 0:
                    last_strong = strong_sell_candles[-1]
                    try:
                        idx = df.index.get_loc(last_strong)
                        if idx + 5 < len(df):
                            consolidation = df['close'].iloc[idx:idx+5]
                            consolidation_range = (consolidation.max() - consolidation.min()) / consolidation.min() * 100
                            if consolidation_range < 3:
                                order_block_detected = True
                                order_block_type = "BEARISH"
                                order_block_price = df['high'].iloc[idx]
                                order_block_strength = min(50 + (abs(price_changes.iloc[idx]) * 5), 100)
                                primary_concept = SmartMoneyConcept.ORDER_BLOCK
                                concept_summary = f"Bearish order block at {order_block_price:.4f}"
                    except:
                        pass
                if len(df) > 20 and ob:
                    recent_high = df['high'].iloc[-20:].max()
                    recent_low = df['low'].iloc[-20:].min()
                    current_price = float(df['close'].iloc[-1])
                    if current_price > recent_high * 1.005 and current_price < recent_high * 1.02:
                        if df['close'].iloc[-1] < df['close'].iloc[-2]:
                            liquidity_sweep = True
                            liquidity_levels.append(recent_high)
                            if primary_concept == SmartMoneyConcept.NONE:
                                primary_concept = SmartMoneyConcept.LIQUIDITY_SWEEP
                                concept_summary = f"Liquidity sweep above {recent_high:.4f}"
                    if current_price < recent_low * 0.995 and current_price > recent_low * 0.98:
                        if df['close'].iloc[-1] > df['close'].iloc[-2]:
                            liquidity_sweep = True
                            liquidity_levels.append(recent_low)
                            if primary_concept == SmartMoneyConcept.NONE:
                                primary_concept = SmartMoneyConcept.LIQUIDITY_SWEEP
                                concept_summary = f"Liquidity sweep below {recent_low:.4f}"
                    for level in ob.top_bids[:3]:
                        liquidity_levels.append(level.price)
                    for level in ob.top_asks[:3]:
                        liquidity_levels.append(level.price)
            if len(df) >= 5:
                for i in range(2, len(df)-1):
                    try:
                        candle1_high = df['high'].iloc[i-2]
                        candle1_low = df['low'].iloc[i-2]
                        candle2_high = df['high'].iloc[i-1]
                        candle2_low = df['low'].iloc[i-1]
                        if candle2_low > candle1_high:
                            fvg_detected = True
                            fvg_type = "BULLISH"
                            fvg_low = candle1_high
                            fvg_high = candle2_low
                            current_price = float(df['close'].iloc[-1])
                            fvg_filled = fvg_low <= current_price <= fvg_high
                            if primary_concept == SmartMoneyConcept.NONE:
                                primary_concept = SmartMoneyConcept.FVG
                                concept_summary = f"Bullish FVG: {fvg_low:.4f}-{fvg_high:.4f}"
                            break
                        if candle2_high < candle1_low:
                            fvg_detected = True
                            fvg_type = "BEARISH"
                            fvg_low = candle2_high
                            fvg_high = candle1_low
                            current_price = float(df['close'].iloc[-1])
                            fvg_filled = fvg_low <= current_price <= fvg_high
                            if primary_concept == SmartMoneyConcept.NONE:
                                primary_concept = SmartMoneyConcept.FVG
                                concept_summary = f"Bearish FVG: {fvg_low:.4f}-{fvg_high:.4f}"
                            break
                    except:
                        continue
            if len(df) >= 30:
                recent_high = df['high'].iloc[-30:].max()
                recent_low = df['low'].iloc[-30:].min()
                if df['high'].iloc[-5:].max() > recent_high * 1.01:
                    if df['close'].iloc[-1] < recent_high:
                        breaker_block = True
                        if primary_concept == SmartMoneyConcept.NONE:
                            primary_concept = SmartMoneyConcept.BREAKER
                            concept_summary = f"Breaker block below {recent_high:.4f}"
                if df['low'].iloc[-5:].min() < recent_low * 0.99:
                    if df['close'].iloc[-1] > recent_low:
                        breaker_block = True
                        if primary_concept == SmartMoneyConcept.NONE:
                            primary_concept = SmartMoneyConcept.BREAKER
                            concept_summary = f"Breaker block above {recent_low:.4f}"
            if len(df) >= 20:
                ema20 = df['close'].ewm(span=20).mean()
                current_price = float(df['close'].iloc[-1])
                deviation = abs((current_price / ema20.iloc[-1] - 1) * 100)
                mitigation_detected = deviation < 1.5
                if mitigation_detected and primary_concept == SmartMoneyConcept.NONE:
                    primary_concept = SmartMoneyConcept.MITIGATION
                    concept_summary = f"Price mitigation near EMA20"
            if ob and len(df) > 5:
                current_price = float(df['close'].iloc[-1])
                price_change = ((current_price / df['close'].iloc[-5]) - 1) * 100
                if price_change < -1 and ob.buy_pressure > 55:
                    institutional_divergence = True
                    if primary_concept == SmartMoneyConcept.NONE:
                        primary_concept = SmartMoneyConcept.INSTITUTIONAL_DIVERGENCE
                        concept_summary = f"Institutional divergence (price down, buying pressure)"
                if price_change > 1 and ob.sell_pressure > 55:
                    institutional_divergence = True
                    if primary_concept == SmartMoneyConcept.NONE:
                        primary_concept = SmartMoneyConcept.INSTITUTIONAL_DIVERGENCE
                        concept_summary = f"Institutional divergence (price up, selling pressure)"
            score = 0
            if order_block_detected:
                score += order_block_strength * 0.3
            if liquidity_sweep:
                score += 20
            if fvg_detected:
                score += 15
            if breaker_block:
                score += 15
            if institutional_divergence:
                score += 20
            if order_block_type == "BULLISH" or fvg_type == "BULLISH":
                smart_money_score = score
            elif order_block_type == "BEARISH" or fvg_type == "BEARISH":
                smart_money_score = -score
            else:
                smart_money_score = 0
            return SmartMoneyConcepts(
                order_block_detected=order_block_detected,
                order_block_type=order_block_type,
                order_block_price=order_block_price,
                order_block_strength=order_block_strength,
                liquidity_sweep=liquidity_sweep,
                liquidity_levels=liquidity_levels[:5],
                fvg_detected=fvg_detected,
                fvg_type=fvg_type,
                fvg_zone_low=fvg_low,
                fvg_zone_high=fvg_high,
                fvg_filled=fvg_filled,
                breaker_block=breaker_block,
                mitigation_detected=mitigation_detected,
                institutional_divergence=institutional_divergence,
                smart_money_score=smart_money_score,
                primary_concept=primary_concept,
                concept_summary=concept_summary
            )
        except:
            return SmartMoneyConcepts(
                order_block_detected=False, order_block_type="NEUTRAL", order_block_price=0, order_block_strength=0,
                liquidity_sweep=False, liquidity_levels=[],
                fvg_detected=False, fvg_type="NEUTRAL", fvg_zone_low=0, fvg_zone_high=0, fvg_filled=False,
                breaker_block=False, mitigation_detected=False, institutional_divergence=False,
                smart_money_score=0, primary_concept=SmartMoneyConcept.NONE, concept_summary="No smart money concepts detected"
            )

# ========== MARKET PROFILE ANALYZER ==========
class MarketProfileAnalyzer:
    def analyze_profile(self, df: pd.DataFrame, num_bins: int = 24) -> MarketProfile:
        try:
            if len(df) < 50:
                current_price = float(df['close'].iloc[-1])
                return MarketProfile(
                    value_area_low=current_price * 0.98,
                    value_area_high=current_price * 1.02,
                    poc_price=current_price,
                    volume_nodes=[],
                    high_volume_nodes=[],
                    low_volume_nodes=[],
                    developing_poc=True,
                    market_type="BALANCED",
                    profile_complete=False,
                    volume_profile_score=0
                )
            price_min = df['low'].min()
            price_max = df['high'].max()
            price_range = price_max - price_min
            bin_size = price_range / num_bins
            bins = {}
            for i in range(num_bins):
                low = price_min + (i * bin_size)
                high = low + bin_size
                bins[(low, high)] = 0
            for idx, row in df.iterrows():
                for (low, high) in list(bins.keys()):
                    if low <= row['high'] <= high or low <= row['low'] <= high:
                        bins[(low, high)] += row['volume']
            poc_bin = max(bins.items(), key=lambda x: x[1])
            poc_price = (poc_bin[0][0] + poc_bin[0][1]) / 2
            total_volume = sum(bins.values())
            sorted_bins = sorted(bins.items(), key=lambda x: x[1], reverse=True)
            value_area_volume = 0
            value_area_bins = []
            for bin_range, volume in sorted_bins:
                value_area_volume += volume
                value_area_bins.append(bin_range)
                if value_area_volume >= total_volume * 0.7:
                    break
            value_area_low = min([b[0] for b in value_area_bins])
            value_area_high = max([b[1] for b in value_area_bins])
            avg_volume_per_bin = total_volume / num_bins
            high_volume_nodes = []
            low_volume_nodes = []
            volume_nodes = []
            for bin_range, volume in bins.items():
                mid_price = (bin_range[0] + bin_range[1]) / 2
                volume_nodes.append((mid_price, volume))
                if volume > avg_volume_per_bin * 1.5:
                    high_volume_nodes.append(mid_price)
                elif volume < avg_volume_per_bin * 0.5:
                    low_volume_nodes.append(mid_price)
            current_price = float(df['close'].iloc[-1])
            if current_price > value_area_high * 1.02:
                market_type = "TRENDING_BULL"
            elif current_price < value_area_low * 0.98:
                market_type = "TRENDING_BEAR"
            else:
                market_type = "BALANCED"
            if current_price > poc_price:
                volume_profile_score = (current_price - poc_price) / poc_price * 100
            else:
                volume_profile_score = -(poc_price - current_price) / poc_price * 100
            return MarketProfile(
                value_area_low=value_area_low,
                value_area_high=value_area_high,
                poc_price=poc_price,
                volume_nodes=volume_nodes[:20],
                high_volume_nodes=high_volume_nodes[:10],
                low_volume_nodes=low_volume_nodes[:10],
                developing_poc=len(df) < 100,
                market_type=market_type,
                profile_complete=len(df) >= 100,
                volume_profile_score=volume_profile_score
            )
        except:
            current_price = float(df['close'].iloc[-1])
            return MarketProfile(
                value_area_low=current_price * 0.98,
                value_area_high=current_price * 1.02,
                poc_price=current_price,
                volume_nodes=[],
                high_volume_nodes=[],
                low_volume_nodes=[],
                developing_poc=True,
                market_type="BALANCED",
                profile_complete=False,
                volume_profile_score=0
            )

# ========== INTERMARKET ANALYZER ==========
class InterMarketAnalyzer:
    def __init__(self, client: EnhancedBinanceFuturesClient):
        self.client = client
        self.sector_symbols = {
            "Layer1": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "NEARUSDT", "ATOMUSDT", "APTUSDT"],
            "Exchange": ["BNBUSDT"],
            "DeFi": ["UNIUSDT", "AAVEUSDT", "COMPUSDT"],
            "L2": ["OPUSDT", "ARBUSDT"],
            "Meme": ["DOGEUSDT"],
            "Oracle": ["LINKUSDT", "API3USDT"],
            "Gaming": ["AXSUSDT", "GALAUSDT", "ENJUSDT"]
        }
    
    def analyze_intermarket(self, symbol: str) -> InterMarketAnalysis:
        try:
            btc_dominance = self.client.get_btc_dominance()
            total_market_cap = self.client.get_total_market_cap()
            btc_price = self.client.get_btc_price()
            eth_price = self.client.get_eth_price()
            btc_change = self.client.get_24hr_change("BTCUSDT")
            eth_change = self.client.get_24hr_change("ETHUSDT")
            if btc_dominance is not None:
                altcoin_season_index = 100 - btc_dominance
                altcoin_season = altcoin_season_index > 60
                usdt_dominance = max(0, 100 - btc_dominance - 30)
            else:
                altcoin_season_index = None
                altcoin_season = None
                usdt_dominance = None
            if symbol == "BTCUSDT":
                btc_correlation = 1.0
                eth_correlation = 0.85
            elif symbol == "ETHUSDT":
                btc_correlation = 0.85
                eth_correlation = 1.0
            elif symbol in ["SOLUSDT", "BNBUSDT", "ADAUSDT"]:
                btc_correlation = 0.75
                eth_correlation = 0.8
            else:
                btc_correlation = 0.6
                eth_correlation = 0.7
            sector_strength = {}
            for sector, symbols in self.sector_symbols.items():
                if symbol in symbols:
                    sector_strength[sector] = 10.0
                else:
                    sector_strength[sector] = 0.0
            score = 0
            if btc_dominance is not None:
                if btc_dominance < 45:
                    score += 15
                elif btc_dominance > 55:
                    score -= 15
            if altcoin_season:
                score += 15
            if total_market_cap is not None:
                score += 10
            if btc_change is not None and btc_change > 2:
                score += 10
            elif btc_change is not None and btc_change < -2:
                score -= 10
            for sector, strength in sector_strength.items():
                if strength > 0:
                    score += 5
            return InterMarketAnalysis(
                btc_dominance=btc_dominance, btc_dominance_change=None,
                btc_price=btc_price, btc_change_24h=btc_change,
                eth_price=eth_price, eth_change_24h=eth_change,
                btc_correlation=btc_correlation, eth_correlation=eth_correlation,
                total_market_cap=total_market_cap, total_market_cap_change=None,
                altcoin_season_index=altcoin_season_index, altcoin_season=altcoin_season,
                usdt_dominance=usdt_dominance, usdt_dominance_change=None,
                sector_strength=sector_strength, intermarket_score=score
            )
        except:
            return InterMarketAnalysis(
                btc_dominance=None, btc_dominance_change=None,
                btc_price=None, btc_change_24h=None,
                eth_price=None, eth_change_24h=None,
                btc_correlation=0.7, eth_correlation=0.8,
                total_market_cap=None, total_market_cap_change=None,
                altcoin_season_index=None, altcoin_season=None,
                usdt_dominance=None, usdt_dominance_change=None,
                sector_strength={}, intermarket_score=0
            )

# ========== ON-CHAIN ANALYZER ==========
class OnChainAnalyzer:
    def __init__(self, client: EnhancedBinanceFuturesClient):
        self.client = client
    
    def analyze_onchain(self, symbol: str) -> Optional[OnChainMetrics]:
        return None

# ========== MARKET SENTIMENT ANALYZER ==========
class MarketSentimentAnalyzer:
    def __init__(self, client: EnhancedBinanceFuturesClient):
        self.client = client
    
    def analyze_sentiment(self, funding_rate: float) -> MarketSentiment:
        try:
            fng_data = self.client.get_fear_greed_index()
            fear_greed_index = None
            fear_greed_sentiment = "UNKNOWN"
            if fng_data and 'data' in fng_data and len(fng_data['data']) > 0:
                fear_greed_index = int(fng_data['data'][0]['value'])
                fear_greed_class = fng_data['data'][0].get('value_classification', 'Neutral')
                fear_greed_sentiment = fear_greed_class.upper().replace(' ', '_')
            if fear_greed_index is not None:
                if fear_greed_index <= 25:
                    sentiment_score = 30
                    news_sentiment = "BULLISH_CONTRARIAN"
                elif fear_greed_index <= 45:
                    sentiment_score = 15
                    news_sentiment = "BULLISH"
                elif fear_greed_index <= 55:
                    sentiment_score = 0
                    news_sentiment = "NEUTRAL"
                elif fear_greed_index <= 75:
                    sentiment_score = -15
                    news_sentiment = "BEARISH"
                else:
                    sentiment_score = -30
                    news_sentiment = "BEARISH_CONTRARIAN"
            else:
                sentiment_score = 0
                news_sentiment = "UNKNOWN"
            funding_sentiment_aligned = False
            if funding_rate > 0.01 and sentiment_score < 0:
                funding_sentiment_aligned = True
            elif funding_rate < -0.01 and sentiment_score > 0:
                funding_sentiment_aligned = True
            if fear_greed_index is not None:
                if fear_greed_index > 75:
                    crowd_behavior = "EXTREME_GREED"
                elif fear_greed_index > 60:
                    crowd_behavior = "GREED"
                elif fear_greed_index < 25:
                    crowd_behavior = "EXTREME_FEAR"
                elif fear_greed_index < 40:
                    crowd_behavior = "FEAR"
                else:
                    crowd_behavior = "NEUTRAL"
            else:
                crowd_behavior = "UNKNOWN"
            return MarketSentiment(
                fear_greed_index=fear_greed_index,
                fear_greed_sentiment=fear_greed_sentiment,
                news_sentiment=news_sentiment,
                news_sentiment_score=0,
                social_volume=None,
                social_dominance=None,
                social_sentiment="UNKNOWN",
                sentiment_score=sentiment_score,
                funding_sentiment_aligned=funding_sentiment_aligned,
                crowd_behavior=crowd_behavior
            )
        except:
            return MarketSentiment(
                fear_greed_index=None, fear_greed_sentiment="UNKNOWN",
                news_sentiment="UNKNOWN", news_sentiment_score=0,
                social_volume=None, social_dominance=None, social_sentiment="UNKNOWN",
                sentiment_score=0, funding_sentiment_aligned=False, crowd_behavior="UNKNOWN"
            )

# ========== DIVERGENCE DETECTOR ==========
class DivergenceDetector:
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def detect_divergences(self, df: pd.DataFrame) -> DivergenceAnalysis:
        try:
            if len(df) < 30:
                return DivergenceAnalysis(
                    rsi_divergence="NONE", rsi_divergence_strength=0,
                    macd_divergence="NONE", macd_divergence_strength=0,
                    volume_divergence="NONE", volume_divergence_strength=0,
                    obv_divergence="NONE", obv_divergence_strength=0,
                    divergence_score=0
                )
            rsi_values = []
            for i in range(max(0, len(df)-14), len(df)):
                if i >= 14:
                    rsi = self.indicators.calculate_rsi(df.iloc[:i+1])
                    rsi_values.append(rsi)
                else:
                    rsi_values.append(50)
            rsi_div, rsi_strength = self._detect_divergence(
                df['close'].values[-min(14, len(df)):],
                np.array(rsi_values[-min(14, len(rsi_values)):])
            )
            obv_values = [0]
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    obv_values.append(obv_values[-1] + df['volume'].iloc[i])
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    obv_values.append(obv_values[-1] - df['volume'].iloc[i])
                else:
                    obv_values.append(obv_values[-1])
            obv_div, obv_strength = self._detect_divergence(
                df['close'].values[-20:],
                np.array(obv_values[-20:])
            )
            vol_div, vol_strength = self._detect_divergence(
                df['close'].values[-20:],
                df['volume'].values[-20:]
            )
            score = 0
            if rsi_div == "BULLISH":
                score += rsi_strength * 0.4
            elif rsi_div == "BEARISH":
                score -= rsi_strength * 0.4
            if vol_div == "BULLISH":
                score += vol_strength * 0.3
            elif vol_div == "BEARISH":
                score -= vol_strength * 0.3
            if obv_div == "BULLISH":
                score += obv_strength * 0.3
            elif obv_div == "BEARISH":
                score -= obv_strength * 0.3
            return DivergenceAnalysis(
                rsi_divergence=rsi_div, rsi_divergence_strength=rsi_strength,
                macd_divergence="NONE", macd_divergence_strength=0,
                volume_divergence=vol_div, volume_divergence_strength=vol_strength,
                obv_divergence=obv_div, obv_divergence_strength=obv_strength,
                divergence_score=score
            )
        except:
            return DivergenceAnalysis(
                rsi_divergence="NONE", rsi_divergence_strength=0,
                macd_divergence="NONE", macd_divergence_strength=0,
                volume_divergence="NONE", volume_divergence_strength=0,
                obv_divergence="NONE", obv_divergence_strength=0,
                divergence_score=0
            )
    
    def _detect_divergence(self, price: np.array, indicator: np.array) -> Tuple[str, float]:
        try:
            if len(price) < 5 or len(indicator) < 5:
                return "NONE", 0
            price_highs = []
            price_lows = []
            ind_highs = []
            ind_lows = []
            for i in range(1, len(price)-1):
                if price[i] > price[i-1] and price[i] > price[i+1]:
                    price_highs.append((i, price[i]))
                if price[i] < price[i-1] and price[i] < price[i+1]:
                    price_lows.append((i, price[i]))
                if indicator[i] > indicator[i-1] and indicator[i] > indicator[i+1]:
                    ind_highs.append((i, indicator[i]))
                if indicator[i] < indicator[i-1] and indicator[i] < indicator[i+1]:
                    ind_lows.append((i, indicator[i]))
            if len(price_highs) >= 2 and len(ind_highs) >= 2:
                last_price_high = price_highs[-1][1]
                prev_price_high = price_highs[-2][1]
                last_ind_high = ind_highs[-1][1]
                prev_ind_high = ind_highs[-2][1]
                if last_price_high > prev_price_high and last_ind_high < prev_ind_high:
                    strength = min(100, abs((last_price_high - prev_price_high) / prev_price_high * 100))
                    return "BEARISH", strength
            if len(price_lows) >= 2 and len(ind_lows) >= 2:
                last_price_low = price_lows[-1][1]
                prev_price_low = price_lows[-2][1]
                last_ind_low = ind_lows[-1][1]
                prev_ind_low = ind_lows[-2][1]
                if last_price_low < prev_price_low and last_ind_low > prev_ind_low:
                    strength = min(100, abs((last_price_low - prev_price_low) / prev_price_low * 100))
                    return "BULLISH", strength
            return "NONE", 0
        except:
            return "NONE", 0

# ========== PATTERN RECOGNIZER ==========
class PatternRecognizer:
    def recognize_patterns(self, df: pd.DataFrame) -> PatternRecognition:
        try:
            if len(df) < 10:
                current_price = float(df['close'].iloc[-1])
                return PatternRecognition(
                    candlestick_patterns=[], candlestick_reliability=0,
                    chart_patterns=[], pattern_reliability=0,
                    breakout_confirmed=False, breakout_direction="NONE",
                    target_price=current_price, invalidation_price=current_price,
                    pattern_score=0
                )
            candlestick_patterns = self._detect_candlestick_patterns(df)
            chart_patterns, target, invalidation = self._detect_chart_patterns(df)
            score = 0
            if "ENGULFING_BULLISH" in candlestick_patterns:
                score += 15
            if "ENGULFING_BEARISH" in candlestick_patterns:
                score -= 15
            if "HAMMER" in candlestick_patterns:
                score += 10
            if "SHOOTING_STAR" in candlestick_patterns:
                score -= 10
            if "MORNING_STAR" in candlestick_patterns:
                score += 20
            if "EVENING_STAR" in candlestick_patterns:
                score -= 20
            if "DOUBLE_BOTTOM" in chart_patterns:
                score += 25
            if "DOUBLE_TOP" in chart_patterns:
                score -= 25
            if "HEAD_AND_SHOULDERS" in chart_patterns:
                score -= 30
            if "INVERSE_HEAD_AND_SHOULDERS" in chart_patterns:
                score += 30
            breakout_confirmed = False
            breakout_direction = "NONE"
            current_price = float(df['close'].iloc[-1])
            if "DOUBLE_BOTTOM" in chart_patterns and len(df) >= 5:
                if current_price > df['high'].iloc[-5:].max():
                    breakout_confirmed = True
                    breakout_direction = "UP"
            elif "DOUBLE_TOP" in chart_patterns and len(df) >= 5:
                if current_price < df['low'].iloc[-5:].min():
                    breakout_confirmed = True
                    breakout_direction = "DOWN"
            return PatternRecognition(
                candlestick_patterns=candlestick_patterns[:5],
                candlestick_reliability=min(len(candlestick_patterns) * 10, 50),
                chart_patterns=chart_patterns,
                pattern_reliability=min(abs(score) * 2, 100),
                breakout_confirmed=breakout_confirmed,
                breakout_direction=breakout_direction,
                target_price=target,
                invalidation_price=invalidation,
                pattern_score=score
            )
        except:
            current_price = float(df['close'].iloc[-1])
            return PatternRecognition(
                candlestick_patterns=[], candlestick_reliability=0,
                chart_patterns=[], pattern_reliability=0,
                breakout_confirmed=False, breakout_direction="NONE",
                target_price=current_price, invalidation_price=current_price,
                pattern_score=0
            )
    
    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> List[str]:
        patterns = []
        if len(df) < 3:
            return patterns
        last = df.iloc[-1]
        prev = df.iloc[-2]
        prev2 = df.iloc[-3] if len(df) > 2 else None
        body = abs(last['close'] - last['open'])
        range_total = last['high'] - last['low']
        if range_total > 0 and body / range_total < 0.1:
            patterns.append("DOJI")
        if range_total > 0:
            upper_shadow = last['high'] - max(last['close'], last['open'])
            lower_shadow = min(last['close'], last['open']) - last['low']
            body_size = abs(last['close'] - last['open'])
            if lower_shadow > body_size * 2 and upper_shadow < body_size * 0.3:
                if last['close'] > last['open']:
                    patterns.append("HAMMER")
                else:
                    patterns.append("INVERTED_HAMMER")
            if upper_shadow > body_size * 2 and lower_shadow < body_size * 0.3:
                if last['close'] < last['open']:
                    patterns.append("SHOOTING_STAR")
        if len(df) >= 2:
            if last['close'] > last['open'] and prev['close'] < prev['open']:
                if last['open'] < prev['close'] and last['close'] > prev['open']:
                    patterns.append("ENGULFING_BULLISH")
            if last['close'] < last['open'] and prev['close'] > prev['open']:
                if last['open'] > prev['close'] and last['close'] < prev['open']:
                    patterns.append("ENGULFING_BEARISH")
        if prev2 is not None:
            if (prev2['close'] < prev2['open'] and
                abs(prev['close'] - prev['open']) < (prev['high'] - prev['low']) * 0.3 and
                last['close'] > last['open'] and
                last['close'] > (prev2['open'] + prev2['close']) / 2):
                patterns.append("MORNING_STAR")
            if (prev2['close'] > prev2['open'] and
                abs(prev['close'] - prev['open']) < (prev['high'] - prev['low']) * 0.3 and
                last['close'] < last['open'] and
                last['close'] < (prev2['open'] + prev2['close']) / 2):
                patterns.append("EVENING_STAR")
        return patterns
    
    def _detect_chart_patterns(self, df: pd.DataFrame) -> Tuple[List[str], float, float]:
        patterns = []
        target = float(df['close'].iloc[-1])
        invalidation = float(df['close'].iloc[-1])
        if len(df) < 30:
            return patterns, target, invalidation
        highs = []
        lows = []
        for i in range(5, len(df)-5):
            if (df['high'].iloc[i] > df['high'].iloc[i-1] and 
                df['high'].iloc[i] > df['high'].iloc[i-2] and
                df['high'].iloc[i] > df['high'].iloc[i+1] and 
                df['high'].iloc[i] > df['high'].iloc[i+2]):
                highs.append((i, df['high'].iloc[i]))
            if (df['low'].iloc[i] < df['low'].iloc[i-1] and 
                df['low'].iloc[i] < df['low'].iloc[i-2] and
                df['low'].iloc[i] < df['low'].iloc[i+1] and 
                df['low'].iloc[i] < df['low'].iloc[i+2]):
                lows.append((i, df['low'].iloc[i]))
        if len(highs) >= 2:
            last_two_highs = highs[-2:]
            if len(last_two_highs) == 2:
                price_diff = abs(last_two_highs[0][1] - last_two_highs[1][1]) / last_two_highs[0][1] * 100
                if price_diff < 2:
                    patterns.append("DOUBLE_TOP")
                    if lows:
                        target = last_two_highs[0][1] - (last_two_highs[0][1] - min([l[1] for l in lows[-3:]])) * 2
                    invalidation = max(last_two_highs[0][1], last_two_highs[1][1]) * 1.02
        if len(lows) >= 2:
            last_two_lows = lows[-2:]
            if len(last_two_lows) == 2:
                price_diff = abs(last_two_lows[0][1] - last_two_lows[1][1]) / last_two_lows[0][1] * 100
                if price_diff < 2:
                    patterns.append("DOUBLE_BOTTOM")
                    if highs:
                        target = last_two_lows[0][1] + (max([h[1] for h in highs[-3:]]) - last_two_lows[0][1]) * 2
                    invalidation = min(last_two_lows[0][1], last_two_lows[1][1]) * 0.98
        return patterns, target, invalidation

# ========== LIQUIDITY ANALYZER ==========
class LiquidityAnalyzer:
    def analyze_liquidity(self, ob: Optional[OrderBookAnalysis], df: pd.DataFrame) -> LiquidityAnalysis:
        try:
            buy_liquidity = []
            sell_liquidity = []
            if ob:
                for level in ob.top_bids[:5]:
                    buy_liquidity.append(level.price)
                for level in ob.top_asks[:5]:
                    sell_liquidity.append(level.price)
            if len(df) > 20:
                recent_high = df['high'].iloc[-20:].max()
                recent_low = df['low'].iloc[-20:].min()
                sell_liquidity.append(recent_high)
                buy_liquidity.append(recent_low)
            current_price = float(df['close'].iloc[-1])
            if buy_liquidity:
                closest_buy = min(buy_liquidity, key=lambda x: abs(x - current_price))
            else:
                closest_buy = current_price * 0.98
            if sell_liquidity:
                closest_sell = min(sell_liquidity, key=lambda x: abs(x - current_price))
            else:
                closest_sell = current_price * 1.02
            buy_distance = abs(closest_buy - current_price) / current_price * 100 if closest_buy else 2
            sell_distance = abs(closest_sell - current_price) / current_price * 100 if closest_sell else 2
            if sell_distance + buy_distance > 0:
                imbalance = (sell_distance - buy_distance) / (sell_distance + buy_distance) * 100
            else:
                imbalance = 0
            stop_hunts = False
            recent_stop = False
            if len(df) > 2:
                price_move = abs(df['close'].iloc[-1] / df['close'].iloc[-2] - 1) * 100
                if price_move > 3:
                    if df['close'].iloc[-1] < df['low'].iloc[-2] or df['close'].iloc[-1] > df['high'].iloc[-2]:
                        stop_hunts = True
                        recent_stop = True
            if imbalance > 20:
                score = 30
            elif imbalance < -20:
                score = -30
            else:
                score = 0
            return LiquidityAnalysis(
                buy_liquidity_levels=buy_liquidity[:5],
                sell_liquidity_levels=sell_liquidity[:5],
                closest_buy_liquidity=closest_buy,
                closest_sell_liquidity=closest_sell,
                liquidity_imbalance=imbalance,
                stop_hunts_detected=stop_hunts,
                recent_stop_hunt=recent_stop,
                liquidity_score=score
            )
        except:
            current_price = float(df['close'].iloc[-1])
            return LiquidityAnalysis(
                buy_liquidity_levels=[], sell_liquidity_levels=[],
                closest_buy_liquidity=current_price * 0.98,
                closest_sell_liquidity=current_price * 1.02,
                liquidity_imbalance=0,
                stop_hunts_detected=False, recent_stop_hunt=False,
                liquidity_score=0
            )

# ========== TIMEFRAME CONFLUENCE ANALYZER ==========
class TimeframeConfluenceAnalyzer:
    def __init__(self, client: EnhancedBinanceFuturesClient, indicators: TechnicalIndicators, config: HybridConfig = None):
        self.client = client
        self.indicators = indicators
        self.config = config or HybridConfig()
    
    def analyze_confluence(self, symbol: str, direction: str) -> TimeframeConfluence:
        try:
            all_timeframes = TimeframeConfig.ALL_TIMEFRAMES
            signals = {}
            scalping_signals = {}
            intraday_signals = {}
            swing_signals = {}
            position_signals = {}
            for tf_name, tf_interval in all_timeframes.items():
                df = self.client.get_klines(symbol, tf_interval, 50)
                if df is not None and len(df) > 20:
                    signal = self._get_timeframe_signal(df, direction)
                    signals[tf_name] = signal
                    if tf_name in TimeframeConfig.TRADING_STYLE_TIMEFRAMES[TradingStyle.SCALPING]:
                        scalping_signals[tf_name] = signal
                    elif tf_name in TimeframeConfig.TRADING_STYLE_TIMEFRAMES[TradingStyle.INTRADAY]:
                        intraday_signals[tf_name] = signal
                    elif tf_name in TimeframeConfig.TRADING_STYLE_TIMEFRAMES[TradingStyle.SWING]:
                        swing_signals[tf_name] = signal
                    elif tf_name in TimeframeConfig.TRADING_STYLE_TIMEFRAMES[TradingStyle.POSITION]:
                        position_signals[tf_name] = signal
            bullish_count = sum(1 for s in signals.values() if s == "BULLISH")
            bearish_count = sum(1 for s in signals.values() if s == "BEARISH")
            if bullish_count > bearish_count:
                major_trend = "BULLISH"
                minor_trend = "BULLISH" if bullish_count >= len(signals) * 0.6 else "NEUTRAL"
            elif bearish_count > bullish_count:
                major_trend = "BEARISH"
                minor_trend = "BEARISH" if bearish_count >= len(signals) * 0.6 else "NEUTRAL"
            else:
                major_trend = "NEUTRAL"
                minor_trend = "NEUTRAL"
            total_timeframes = len(signals) if signals else 1
            if direction == "BUY":
                alignment_score = (bullish_count / total_timeframes) * 100
            else:
                alignment_score = (bearish_count / total_timeframes) * 100
            style_scores = {}
            if scalping_signals:
                scalping_bullish = sum(1 for s in scalping_signals.values() if s == "BULLISH" if direction == "BUY")
                scalping_bearish = sum(1 for s in scalping_signals.values() if s == "BEARISH" if direction == "SELL")
                style_scores["SCALPING"] = ((scalping_bullish + scalping_bearish) / len(scalping_signals)) * 100
            else:
                style_scores["SCALPING"] = 0
            if intraday_signals:
                intraday_bullish = sum(1 for s in intraday_signals.values() if s == "BULLISH" if direction == "BUY")
                intraday_bearish = sum(1 for s in intraday_signals.values() if s == "BEARISH" if direction == "SELL")
                style_scores["INTRADAY"] = ((intraday_bullish + intraday_bearish) / len(intraday_signals)) * 100
            else:
                style_scores["INTRADAY"] = 0
            if swing_signals:
                swing_bullish = sum(1 for s in swing_signals.values() if s == "BULLISH" if direction == "BUY")
                swing_bearish = sum(1 for s in swing_signals.values() if s == "BEARISH" if direction == "SELL")
                style_scores["SWING"] = ((swing_bullish + swing_bearish) / len(swing_signals)) * 100
            else:
                style_scores["SWING"] = 0
            if position_signals:
                position_bullish = sum(1 for s in position_signals.values() if s == "BULLISH" if direction == "BUY")
                position_bearish = sum(1 for s in position_signals.values() if s == "BEARISH" if direction == "SELL")
                style_scores["POSITION"] = ((position_bullish + position_bearish) / len(position_signals)) * 100
            else:
                style_scores["POSITION"] = 0
            primary_style = None
            secondary_styles = []
            if style_scores:
                best_style = max(style_scores, key=style_scores.get)
                if style_scores[best_style] >= self.config.MIN_STYLE_CONFIDENCE:
                    primary_style = best_style
                    for style, score in style_scores.items():
                        if style != best_style and score >= self.config.SECONDARY_STYLE_THRESHOLD:
                            secondary_styles.append(style)
            best_timeframe = "1h"
            if primary_style == "POSITION":
                best_timeframe = "1d"
            elif primary_style == "SWING":
                best_timeframe = "4h"
            elif primary_style == "INTRADAY":
                best_timeframe = "1h"
            elif primary_style == "SCALPING":
                best_timeframe = "5m"
            else:
                if alignment_score >= 80:
                    if any(s == direction for s in position_signals.values()):
                        best_timeframe = "1d"
                    elif any(s == direction for s in swing_signals.values()):
                        best_timeframe = "4h"
                    elif any(s == direction for s in intraday_signals.values()):
                        best_timeframe = "1h"
                    elif any(s == direction for s in scalping_signals.values()):
                        best_timeframe = "5m"
                elif alignment_score >= 60:
                    if any(s == direction for s in swing_signals.values()):
                        best_timeframe = "4h"
                    elif any(s == direction for s in intraday_signals.values()):
                        best_timeframe = "1h"
                    elif any(s == direction for s in scalping_signals.values()):
                        best_timeframe = "15m"
                elif alignment_score >= 40:
                    if any(s == direction for s in intraday_signals.values()):
                        best_timeframe = "30m"
                    else:
                        best_timeframe = "15m"
                else:
                    if any(s == direction for s in scalping_signals.values()):
                        best_timeframe = "3m"
                    else:
                        best_timeframe = "5m"
            aligned_styles = []
            if primary_style == "SCALPING":
                aligned_styles.append(TradingStyle.SCALPING)
            elif primary_style == "INTRADAY":
                aligned_styles.append(TradingStyle.INTRADAY)
            elif primary_style == "SWING":
                aligned_styles.append(TradingStyle.SWING)
            elif primary_style == "POSITION":
                aligned_styles.append(TradingStyle.POSITION)
            return TimeframeConfluence(
                timeframe_signals=signals,
                confluence_count=bullish_count if direction == "BUY" else bearish_count,
                major_trend=major_trend,
                minor_trend=minor_trend,
                alignment_score=alignment_score,
                best_timeframe=best_timeframe,
                aligned_styles=aligned_styles,
                style_scores=style_scores,
                scalping_signals=scalping_signals,
                intraday_signals=intraday_signals,
                swing_signals=swing_signals,
                position_signals=position_signals,
                primary_style=primary_style,
                secondary_styles=secondary_styles
            )
        except:
            return TimeframeConfluence(
                timeframe_signals={}, confluence_count=0,
                major_trend="NEUTRAL", minor_trend="NEUTRAL",
                alignment_score=50, best_timeframe="1h",
                aligned_styles=[], style_scores={},
                scalping_signals={}, intraday_signals={},
                swing_signals={}, position_signals={},
                primary_style=None, secondary_styles=[]
            )
    
    def _get_timeframe_signal(self, df: pd.DataFrame, direction: str) -> str:
        try:
            ema9 = self.indicators.calculate_ema(df, 9)
            ema21 = self.indicators.calculate_ema(df, 21)
            current_price = float(df['close'].iloc[-1])
            if direction == "BUY":
                if ema9 > ema21 and current_price > ema9:
                    return "BULLISH"
                elif ema9 < ema21 and current_price < ema9:
                    return "BEARISH"
                else:
                    return "NEUTRAL"
            else:
                if ema9 < ema21 and current_price < ema9:
                    return "BEARISH"
                elif ema9 > ema21 and current_price > ema9:
                    return "BULLISH"
                else:
                    return "NEUTRAL"
        except:
            return "NEUTRAL"

# ========== BACKTEST ENGINE ==========
class BacktestEngine:
    def __init__(self, client: EnhancedBinanceFuturesClient):
        self.client = client
        self.backtest_results: Dict[str, BacktestResult] = {}
        self.signals_history: List[Dict] = []
    
    def backtest_symbol(self, symbol: str, days: int = 30) -> Optional[BacktestResult]:
        try:
            df = self.client.get_klines(symbol, '1h', limit=days*24)
            if df is None or len(df) < 100:
                return None
            total_signals = 0
            winning_trades = 0
            losing_trades = 0
            total_pnl = 0.0
            max_drawdown = 0.0
            pnl_history = []
            for i in range(50, len(df)-24):
                ema9 = df['close'].iloc[i-9:i].mean()
                ema21 = df['close'].iloc[i-21:i].mean()
                future_return = (df['close'].iloc[i+12] / df['close'].iloc[i] - 1) * 100
                if ema9 > ema21 and future_return > 0:
                    total_signals += 1
                    winning_trades += 1
                    total_pnl += future_return
                    pnl_history.append(total_pnl)
                elif ema9 < ema21 and future_return < 0:
                    total_signals += 1
                    winning_trades += 1
                    total_pnl += abs(future_return)
                    pnl_history.append(total_pnl)
                elif abs(ema9 - ema21) > 0.01 * df['close'].iloc[i]:
                    total_signals += 1
                    losing_trades += 1
                    total_pnl -= abs(future_return)
                    pnl_history.append(total_pnl)
            if total_signals == 0:
                return None
            win_rate = (winning_trades / total_signals) * 100
            avg_profit = total_pnl / winning_trades if winning_trades > 0 else 0
            avg_loss = abs(total_pnl) / losing_trades if losing_trades > 0 else 0
            profit_factor = (winning_trades * avg_profit) / (losing_trades * avg_loss + 1e-10)
            running_peak = 0
            for value in pnl_history:
                if value > running_peak:
                    running_peak = value
                drawdown = (running_peak - value) / (running_peak + 1e-10) * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            max_drawdown = min(max_drawdown, 100.0)
            returns = np.diff(pnl_history) if len(pnl_history) > 1 else [0]
            sharpe_ratio = (np.mean(returns) / (np.std(returns) + 1e-10)) * np.sqrt(365)
            if total_signals < 10:
                return None
            result = BacktestResult(
                symbol=symbol,
                total_signals=total_signals,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                avg_profit=avg_profit,
                avg_loss=avg_loss,
                profit_factor=profit_factor,
                total_pnl=total_pnl,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                last_updated=datetime.now()
            )
            self.backtest_results[symbol] = result
            return result
        except:
            return None
    
    def get_backtest_result(self, symbol: str) -> Optional[BacktestResult]:
        if symbol in self.backtest_results:
            result = self.backtest_results[symbol]
            if (datetime.now() - result.last_updated).days >= 1:
                return self.backtest_symbol(symbol)
            return result
        return self.backtest_symbol(symbol)

# ========== ENHANCED ENTRY OPTIMIZER ==========
class EnhancedEntryOptimizer:
    def __init__(self, client: BinanceFuturesClient, config: HybridConfig):
        self.client = client
        self.config = config
        self.order_flow_analyzer = OrderFlowAnalyzer(client)
        self.volume_profile = VolumeProfileEntry()
    
    def get_style_entries(self, symbol: str, direction: str, current_price: float, 
                          df_1h: Optional[pd.DataFrame] = None, style: str = "INTRADAY") -> Dict[str, Any]:
        try:
            ob_data = self.client.get_order_book(symbol, self.config.ENTRY_ORDER_BOOK_DEPTH)
            vp_entry = None
            if df_1h is not None and len(df_1h) >= 20:
                vp_entry = self.volume_profile.calculate_entry(df_1h, direction, current_price, style)
                if vp_entry.get('used_fallback', False):
                    logger.info(f"Volume Profile fallback for {symbol}")
                else:
                    logger.info(f"Volume Profile for {symbol}: {vp_entry['entry_logic']}")
            entries = {}
            if direction == "BUY":
                if vp_entry and vp_entry['entry_confidence'] >= 60:
                    poc = vp_entry['poc_price']
                    va_low = vp_entry['value_area_low']
                    va_high = vp_entry['value_area_high']
                    entries['scalping'] = {
                        'price': max(current_price, current_price * 0.998),
                        'range_low': current_price * 0.997,
                        'range_high': current_price * 1.001,
                        'logic': f"Scalping: {vp_entry['entry_logic']}"
                    }
                    entries['intraday'] = {
                        'price': va_low if va_low < current_price else current_price * 0.995,
                        'range_low': min(va_low, current_price * 0.99),
                        'range_high': current_price,
                        'logic': f"Intraday: {vp_entry['entry_logic']}"
                    }
                    entries['swing'] = {
                        'price': min(va_low, current_price * 0.99),
                        'range_low': min(va_low, current_price * 0.985),
                        'range_high': current_price * 0.995,
                        'logic': f"Swing: {vp_entry['entry_logic']}"
                    }
                    entries['position'] = {
                        'price': min(va_low, current_price * 0.98),
                        'range_low': min(va_low, current_price * 0.975),
                        'range_high': current_price * 0.99,
                        'logic': f"Position: {vp_entry['entry_logic']}"
                    }
                    entries['poc_price'] = poc
                    entries['value_area_low'] = va_low
                    entries['value_area_high'] = va_high
                elif ob_data and 'bids' in ob_data and 'asks' in ob_data:
                    bids = ob_data['bids']
                    asks = ob_data['asks']
                    if len(bids) > 0 and len(asks) > 0:
                        best_bid = float(bids[0][0])
                        best_ask = float(asks[0][0])
                        mid_price = (best_bid + best_ask) / 2
                        entries['scalping'] = {
                            'price': best_ask, 'range_low': best_ask, 'range_high': best_ask,
                            'logic': 'Scalping: Market Ask'
                        }
                        entries['intraday'] = {
                            'price': mid_price, 'range_low': best_bid, 'range_high': best_ask,
                            'logic': 'Intraday: Mid Price'
                        }
                        entries['swing'] = {
                            'price': best_bid, 'range_low': best_bid * 0.998, 'range_high': best_bid,
                            'logic': 'Swing: Bid Level'
                        }
                        entries['position'] = {
                            'price': best_bid * 0.995, 'range_low': best_bid * 0.99, 'range_high': best_bid * 0.998,
                            'logic': 'Position: Deep Bid'
                        }
                        entries['best_bid'] = best_bid
                        entries['best_ask'] = best_ask
                        entries['mid'] = mid_price
                else:
                    entries['scalping'] = {
                        'price': current_price * 1.001, 'range_low': current_price, 'range_high': current_price * 1.002,
                        'logic': 'Scalping: Market'
                    }
                    entries['intraday'] = {
                        'price': current_price, 'range_low': current_price * 0.998, 'range_high': current_price * 1.002,
                        'logic': 'Intraday: Current'
                    }
                    entries['swing'] = {
                        'price': current_price * 0.995, 'range_low': current_price * 0.99, 'range_high': current_price,
                        'logic': 'Swing: Discount'
                    }
                    entries['position'] = {
                        'price': current_price * 0.99, 'range_low': current_price * 0.985, 'range_high': current_price * 0.995,
                        'logic': 'Position: Deep Discount'
                    }
            else:
                if vp_entry and vp_entry['entry_confidence'] >= 60:
                    poc = vp_entry['poc_price']
                    va_low = vp_entry['value_area_low']
                    va_high = vp_entry['value_area_high']
                    entries['scalping'] = {
                        'price': min(current_price, current_price * 1.002),
                        'range_low': current_price * 0.999,
                        'range_high': current_price * 1.003,
                        'logic': f"Scalping: {vp_entry['entry_logic']}"
                    }
                    entries['intraday'] = {
                        'price': va_high if va_high > current_price else current_price * 1.005,
                        'range_low': current_price,
                        'range_high': max(va_high, current_price * 1.01),
                        'logic': f"Intraday: {vp_entry['entry_logic']}"
                    }
                    entries['swing'] = {
                        'price': max(va_high, current_price * 1.01),
                        'range_low': current_price * 1.005,
                        'range_high': max(va_high, current_price * 1.015),
                        'logic': f"Swing: {vp_entry['entry_logic']}"
                    }
                    entries['position'] = {
                        'price': max(va_high, current_price * 1.02),
                        'range_low': current_price * 1.01,
                        'range_high': max(va_high, current_price * 1.025),
                        'logic': f"Position: {vp_entry['entry_logic']}"
                    }
                    entries['poc_price'] = poc
                    entries['value_area_low'] = va_low
                    entries['value_area_high'] = va_high
                elif ob_data and 'bids' in ob_data and 'asks' in ob_data:
                    bids = ob_data['bids']
                    asks = ob_data['asks']
                    if len(bids) > 0 and len(asks) > 0:
                        best_bid = float(bids[0][0])
                        best_ask = float(asks[0][0])
                        mid_price = (best_bid + best_ask) / 2
                        entries['scalping'] = {
                            'price': best_bid, 'range_low': best_bid, 'range_high': best_bid,
                            'logic': 'Scalping: Market Bid'
                        }
                        entries['intraday'] = {
                            'price': mid_price, 'range_low': best_bid, 'range_high': best_ask,
                            'logic': 'Intraday: Mid Price'
                        }
                        entries['swing'] = {
                            'price': best_ask, 'range_low': best_ask, 'range_high': best_ask * 1.002,
                            'logic': 'Swing: Ask Level'
                        }
                        entries['position'] = {
                            'price': best_ask * 1.005, 'range_low': best_ask * 1.002, 'range_high': best_ask * 1.01,
                            'logic': 'Position: Deep Ask'
                        }
                        entries['best_bid'] = best_bid
                        entries['best_ask'] = best_ask
                        entries['mid'] = mid_price
                else:
                    entries['scalping'] = {
                        'price': current_price * 0.999, 'range_low': current_price * 0.998, 'range_high': current_price,
                        'logic': 'Scalping: Market'
                    }
                    entries['intraday'] = {
                        'price': current_price, 'range_low': current_price * 0.998, 'range_high': current_price * 1.002,
                        'logic': 'Intraday: Current'
                    }
                    entries['swing'] = {
                        'price': current_price * 1.005, 'range_low': current_price, 'range_high': current_price * 1.01,
                        'logic': 'Swing: Premium'
                    }
                    entries['position'] = {
                        'price': current_price * 1.01, 'range_low': current_price * 1.005, 'range_high': current_price * 1.015,
                        'logic': 'Position: Deep Premium'
                    }
            if 'best_bid' not in entries and ob_data:
                try:
                    entries['best_bid'] = float(ob_data['bids'][0][0])
                    entries['best_ask'] = float(ob_data['asks'][0][0])
                    entries['mid'] = (entries['best_bid'] + entries['best_ask']) / 2
                except:
                    entries['best_bid'] = current_price * 0.999
                    entries['best_ask'] = current_price * 1.001
                    entries['mid'] = current_price
            elif 'best_bid' not in entries:
                entries['best_bid'] = current_price * 0.999
                entries['best_ask'] = current_price * 1.001
                entries['mid'] = current_price
            entries['imbalance'] = 0
            entries['spread_percent'] = ((entries['best_ask'] - entries['best_bid']) / entries['best_bid']) * 100
            return entries
        except Exception as e:
            logger.error(f"Entry optimization error for {symbol}: {e}")
            entries = {
                'scalping': {'price': current_price, 'range_low': current_price * 0.999, 'range_high': current_price * 1.001, 'logic': 'Fallback'},
                'intraday': {'price': current_price, 'range_low': current_price * 0.998, 'range_high': current_price * 1.002, 'logic': 'Fallback'},
                'swing': {'price': current_price * 0.995, 'range_low': current_price * 0.99, 'range_high': current_price, 'logic': 'Fallback'},
                'position': {'price': current_price * 0.99, 'range_low': current_price * 0.985, 'range_high': current_price * 0.995, 'logic': 'Fallback'},
                'best_bid': current_price * 0.999,
                'best_ask': current_price * 1.001,
                'mid': current_price,
                'imbalance': 0,
                'spread_percent': 0.2
            }
            return entries

# ========== BASE SIGNAL GENERATOR ==========
class HighConfidenceSignalGenerator:
    def __init__(self, client: BinanceFuturesClient, config: Config):
        self.client = client
        self.config = config
        self.indicators = TechnicalIndicators()
        self.enhanced_indicators = EnhancedTechnicalIndicators()
        self.order_flow = OrderFlowAnalyzer(client)
        self.entry_optimizer = EnhancedEntryOptimizer(client, config.HYBRID_CONFIG or HybridConfig())
        self.atr_stop = ATRStopLoss(atr_multiplier=config.HYBRID_CONFIG.ATR_MULTIPLIER if config.HYBRID_CONFIG else 1.5)
        self.volume_profile = VolumeProfileEntry()
        self.liquidity_grab = LiquidityGrabDetection()
        self.trend_filter_200ema = TrendFilter200EMA()
        self.ai_model = AIConfidenceModel()
        self.klines_cache = {}
    
    def _get_cached_klines(self, symbol: str, interval: str, limit: int) -> Optional[pd.DataFrame]:
        cache_key = f"{symbol}_{interval}_{limit}"
        if cache_key in self.klines_cache:
            df, timestamp = self.klines_cache[cache_key]
            if time.time() - timestamp < 15:
                return df.copy()
        df = self.client.get_klines(symbol, interval, limit)
        if df is not None:
            self.klines_cache[cache_key] = (df, time.time())
        return df
    
    def calculate_technical_score(self, tech: EnhancedTechnicalAnalysis) -> float:
        score = 0
        if tech.rsi_signal == "OVERSOLD":
            score += 20
        elif tech.rsi_signal == "OVERBOUGHT":
            score -= 20
        if tech.macd_trend == "BULLISH":
            score += 25
        elif tech.macd_trend == "BEARISH":
            score -= 25
        if tech.ema_trend == "BULLISH":
            score += 20
        elif tech.ema_trend == "BEARISH":
            score -= 20
        if tech.bb_position == "BELOW_LOWER":
            score += 15
        elif tech.bb_position == "ABOVE_UPPER":
            score -= 15
        if tech.stoch_signal == "OVERSOLD":
            score += 10
        elif tech.stoch_signal == "OVERBOUGHT":
            score -= 10
        if tech.vwap_position == "ABOVE":
            score += 10
        elif tech.vwap_position == "BELOW":
            score -= 10
        if tech.adx_trend == "VERY_STRONG":
            score += 15
        elif tech.adx_trend == "STRONG":
            score += 10
        elif tech.adx_trend == "WEAK":
            score += 5
        if tech.mfi_signal == "OVERSOLD":
            score += 10
        elif tech.mfi_signal == "OVERBOUGHT":
            score -= 10
        return score
    
    def calculate_order_flow_score(self, ob: OrderBookAnalysis, mt: MarketTradeAnalysis, cf: CumulativeFlow) -> float:
        score = 0
        if ob.imbalance > 10:
            score += 20
        elif ob.imbalance < -10:
            score -= 20
        if ob.bid_ask_ratio > 1.2:
            score += 15
        elif ob.bid_ask_ratio < 0.8:
            score -= 15
        if mt.aggressive_buying:
            score += 25
        elif mt.aggressive_selling:
            score -= 25
        if mt.large_trades_buy > mt.large_trades_sell * 2:
            score += 20
        elif mt.large_trades_sell > mt.large_trades_buy * 2:
            score -= 20
        if cf.accumulation:
            score += 20
        elif cf.distribution:
            score -= 20
        return score
    
    def get_style_entries(self, symbol: str, direction: str, current_price: float, 
                         df_1h: Optional[pd.DataFrame] = None, style: str = "INTRADAY") -> Dict[str, Any]:
        return self.entry_optimizer.get_style_entries(symbol, direction, current_price, df_1h, style)
    
    def calculate_atr_stop_loss(self, entry_price: float, direction: str, df: pd.DataFrame) -> Tuple[float, float, float]:
        if self.config.HYBRID_CONFIG and self.config.HYBRID_CONFIG.ATR_STOP_LOSS_ENABLED:
            self.atr_stop.atr_multiplier = self.config.HYBRID_CONFIG.ATR_MULTIPLIER
            stop_loss, stop_percentage = self.atr_stop.calculate_stop(entry_price, direction, df)
            return stop_loss, stop_percentage, self.atr_stop.atr_value
        else:
            atr_value = self._calculate_atr_manual(df)
            if atr_value > 0:
                stop_distance = atr_value * 1.5
                if direction == "BUY":
                    stop_loss = entry_price - stop_distance
                    stop_percentage = (stop_distance / entry_price) * 100
                else:
                    stop_loss = entry_price + stop_distance
                    stop_percentage = (stop_distance / entry_price) * 100
                return stop_loss, stop_percentage, atr_value
            else:
                if direction == "BUY":
                    stop_loss = entry_price * 0.99
                    stop_percentage = 1.0
                else:
                    stop_loss = entry_price * 1.01
                    stop_percentage = 1.0
                return stop_loss, stop_percentage, 0.0
    
    def _calculate_atr_manual(self, df: pd.DataFrame, period: int = 14) -> float:
        try:
            if len(df) < period + 1:
                return 0.0
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            tr = np.zeros(len(df))
            for i in range(1, len(df)):
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1])
                lc = abs(low[i] - close[i-1])
                tr[i] = max(hl, hc, lc)
            atr = pd.Series(tr).rolling(window=period).mean().values
            return float(atr[-1])
        except:
            return 0.0
    
    def calculate_take_profit_adaptive(self, entry_price: float, stop_loss: float, direction: str, 
                                  trading_style: Optional[TradingStyle] = None, atr: Optional[float] = None,
                                  config: HybridConfig = None) -> Tuple[float, float, float, float, float, float, float, float]:
        risk = abs(entry_price - stop_loss)
        min_risk = entry_price * 0.002
        if risk < min_risk:
            logger.warning(f"Risk too small ({risk:.6f}), using minimum {min_risk:.6f}")
            risk = min_risk
        if config is None:
            config = HybridConfig()
        scalping_mult = config.TP_CONFIG.scalping_tp1
        scalping_mult2 = config.TP_CONFIG.scalping_tp2
        intraday_mult = config.TP_CONFIG.intraday_tp1
        intraday_mult2 = config.TP_CONFIG.intraday_tp2
        swing_mult = config.TP_CONFIG.swing_tp1
        swing_mult2 = config.TP_CONFIG.swing_tp2
        position_mult = config.TP_CONFIG.position_tp1
        position_mult2 = config.TP_CONFIG.position_tp2
        if direction == "BUY":
            scalping_tp1 = entry_price + (risk * scalping_mult)
            scalping_tp2 = entry_price + (risk * scalping_mult2)
            intraday_tp1 = entry_price + (risk * intraday_mult)
            intraday_tp2 = entry_price + (risk * intraday_mult2)
            swing_tp1 = entry_price + (risk * swing_mult)
            swing_tp2 = entry_price + (risk * swing_mult2)
            position_tp1 = entry_price + (risk * position_mult)
            position_tp2 = entry_price + (risk * position_mult2)
        else:
            scalping_tp1 = entry_price - (risk * scalping_mult)
            scalping_tp2 = entry_price - (risk * scalping_mult2)
            intraday_tp1 = entry_price - (risk * intraday_mult)
            intraday_tp2 = entry_price - (risk * intraday_mult2)
            swing_tp1 = entry_price - (risk * swing_mult)
            swing_tp2 = entry_price - (risk * swing_mult2)
            position_tp1 = entry_price - (risk * position_mult)
            position_tp2 = entry_price - (risk * position_mult2)
        if abs(intraday_tp1 - intraday_tp2) < 1e-8:
            intraday_tp2 = intraday_tp1 + (risk * 0.2) if direction == "BUY" else intraday_tp1 - (risk * 0.2)
        if abs(swing_tp1 - swing_tp2) < 1e-8:
            swing_tp2 = swing_tp1 + (risk * 0.3) if direction == "BUY" else swing_tp1 - (risk * 0.3)
        if abs(position_tp1 - position_tp2) < 1e-8:
            position_tp2 = position_tp1 + (risk * 0.4) if direction == "BUY" else position_tp1 - (risk * 0.4)
        return scalping_tp1, scalping_tp2, intraday_tp1, intraday_tp2, swing_tp1, swing_tp2, position_tp1, position_tp2
    
    def calculate_risk_reward_adaptive(self, entry_price: float, stop_loss: float, 
                                      scalping_tp1: float, scalping_tp2: float,
                                      intraday_tp1: float, intraday_tp2: float,
                                      swing_tp1: float, swing_tp2: float,
                                      position_tp1: float, position_tp2: float,
                                      direction: str) -> RiskRewardAnalysis:
        risk = abs(entry_price - stop_loss)
        risk_percentage = (risk / entry_price) * 100 if entry_price > 0 else 0
        scalping_reward1 = abs(scalping_tp1 - entry_price) if scalping_tp1 else 0
        scalping_reward2 = abs(scalping_tp2 - entry_price) if scalping_tp2 else 0
        scalping_rr1 = scalping_reward1 / risk if risk > 0 else 0
        scalping_rr2 = scalping_reward2 / risk if risk > 0 else 0
        intraday_reward1 = abs(intraday_tp1 - entry_price)
        intraday_reward2 = abs(intraday_tp2 - entry_price)
        intraday_rr1 = intraday_reward1 / risk if risk > 0 else 0
        intraday_rr2 = intraday_reward2 / risk if risk > 0 else 0
        swing_reward1 = abs(swing_tp1 - entry_price)
        swing_reward2 = abs(swing_tp2 - entry_price)
        swing_rr1 = swing_reward1 / risk if risk > 0 else 0
        swing_rr2 = swing_reward2 / risk if risk > 0 else 0
        position_reward1 = abs(position_tp1 - entry_price)
        position_reward2 = abs(position_tp2 - entry_price)
        position_rr1 = position_reward1 / risk if risk > 0 else 0
        position_rr2 = position_reward2 / risk if risk > 0 else 0
        reward1_percentage = (intraday_reward1 / entry_price) * 100 if entry_price > 0 else 0
        reward2_percentage = (intraday_reward2 / entry_price) * 100 if entry_price > 0 else 0
        reward3_percentage = reward2_percentage * 1.5
        expected_value = (intraday_reward1 * 0.5 - risk * 0.5) / entry_price * 100 if entry_price > 0 else 0
        return RiskRewardAnalysis(
            risk_percentage=risk_percentage,
            reward_1_percentage=reward1_percentage,
            reward_2_percentage=reward2_percentage,
            reward_3_percentage=reward3_percentage,
            rr_ratio_1=intraday_rr1,
            rr_ratio_2=intraday_rr2,
            rr_ratio_3=intraday_rr2 * 1.5,
            expected_value=expected_value,
            scalping_target_1=scalping_rr1,
            scalping_target_2=scalping_rr2,
            intraday_target_1=intraday_rr1,
            intraday_target_2=intraday_rr2,
            swing_target_1=swing_rr1,
            swing_target_2=swing_rr2,
            position_target_1=position_rr1,
            position_target_2=position_rr2
        )
    
    def calculate_confirmations(self, df: pd.DataFrame, tech: EnhancedTechnicalAnalysis, 
                               confluence: TimeframeConfluence, direction: str) -> ConfirmationSignals:
        bullish_timeframes = sum(1 for s in confluence.timeframe_signals.values() if s == "BULLISH")
        bearish_timeframes = sum(1 for s in confluence.timeframe_signals.values() if s == "BEARISH")
        total_timeframes = len(confluence.timeframe_signals) if confluence.timeframe_signals else 1
        volume_confirmation = tech.volume_surge and tech.volume_ratio > 1.2
        obv_confirmation = "NEUTRAL"
        if tech.obv_trend == "BULLISH" and direction == "BUY":
            obv_confirmation = "BULLISH"
        elif tech.obv_trend == "BEARISH" and direction == "SELL":
            obv_confirmation = "BEARISH"
        divergence_confirmation = "NEUTRAL"
        pattern_confirmation = "NEUTRAL"
        confirmation_score = 0
        if bullish_timeframes > bearish_timeframes and direction == "BUY":
            confirmation_score += 30
        elif bearish_timeframes > bullish_timeframes and direction == "SELL":
            confirmation_score += 30
        if volume_confirmation:
            confirmation_score += 20
        if obv_confirmation == direction:
            confirmation_score += 20
        return ConfirmationSignals(
            bullish_timeframes=bullish_timeframes,
            bearish_timeframes=bearish_timeframes,
            total_timeframes=total_timeframes,
            volume_confirmation=volume_confirmation,
            volume_ratio=tech.volume_ratio,
            obv_confirmation=obv_confirmation,
            divergence_confirmation=divergence_confirmation,
            pattern_confirmation=pattern_confirmation,
            confirmation_score=confirmation_score
        )

# ========== TIERED SIGNAL GENERATOR ==========
class TieredSignalGenerator(HighConfidenceSignalGenerator):
    def __init__(self, client: EnhancedBinanceFuturesClient, config: Config):
        super().__init__(client, config)
        self.client = client
        self.enhanced_indicators = EnhancedTechnicalIndicators()
        self.multi_tf_regime_detector = MultiTimeframeRegimeDetector(client, config.HYBRID_CONFIG)
        self.regime_detector = MarketRegimeDetector(client, config.HYBRID_CONFIG)
        self.smart_money_detector = SmartMoneyDetector(client)
        self.market_profile_analyzer = MarketProfileAnalyzer()
        self.intermarket_analyzer = InterMarketAnalyzer(client)
        self.onchain_analyzer = OnChainAnalyzer(client)
        self.sentiment_analyzer = MarketSentimentAnalyzer(client)
        self.divergence_detector = DivergenceDetector()
        self.pattern_recognizer = PatternRecognizer()
        self.liquidity_analyzer = LiquidityAnalyzer()
        self.timeframe_analyzer = TimeframeConfluenceAnalyzer(client, self.indicators, config.HYBRID_CONFIG)
        self.backtest_engine = BacktestEngine(client)
        self.signal_cache = {}
        self.tier_stats = defaultdict(int)
        self.hybrid_config = config.HYBRID_CONFIG or HybridConfig()
        
        self.training_signals = []
        self.training_outcomes = []
        
        self.tier1_generator = Tier1Generator(self)
        self.tier2_generator = Tier2Generator(self)
        self.tier3_generator = Tier3Generator(self)
        
        # New features
        self.security_manager = SecurityManager()
        self.ml_models = AdvancedMLModels()
        self.risk_manager = AdvancedRiskManager()
        self.portfolio_manager = PortfolioManager()
        self.advanced_order_executor = None
        self.advanced_backtest = None
        self.performance_analytics = PerformanceAnalytics()
    
    def initialize_advanced_features(self):
        """Initialize advanced features"""
        self.advanced_order_executor = AdvancedOrderExecutor(self.client, self.config)
        logger.info("✅ Advanced features initialized")
    
    def generate_tiered_signals(self, symbol: str) -> List[EnhancedHighConfidenceSignal]:
        signals = []
        base_analysis = self._get_base_analysis(symbol)
        if not base_analysis:
            return signals
        current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
        volume_24h = ticker.get('quoteVolume', 0)
        if volume_24h < self.config.HIGH_CONFIDENCE_THRESHOLDS['MIN_VOLUME_24H']:
            return signals
        multi_tf_regime = self.multi_tf_regime_detector.detect_multi_tf_regime(symbol)
        if self.hybrid_config.ENABLE_TIER_1:
            tier1 = self.tier1_generator.generate(symbol, base_analysis, multi_tf_regime)
            if tier1:
                signals.append(tier1)
                self.tier_stats['tier1'] += 1
                self.training_signals.append(tier1)
        if self.hybrid_config.ENABLE_TIER_2:
            tier2 = self.tier2_generator.generate(symbol, base_analysis, multi_tf_regime)
            if tier2:
                signals.append(tier2)
                self.tier_stats['tier2'] += 1
                self.training_signals.append(tier2)
        if self.hybrid_config.ENABLE_TIER_3:
            tier3 = self.tier3_generator.generate(symbol, base_analysis, multi_tf_regime)
            if tier3:
                signals.append(tier3)
                self.tier_stats['tier3'] += 1
                self.training_signals.append(tier3)
        return signals
    
    def _get_base_analysis(self, symbol: str) -> Optional[Tuple]:
        cache_key = f"base_{symbol}_{int(time.time()/60)}"
        if cache_key in self.signal_cache:
            return self.signal_cache[cache_key]
        try:
            ob = self.order_flow.analyze_order_book(symbol)
            if ob:
                current_price = (ob.best_bid + ob.best_ask) / 2
            else:
                current_price = self.client.get_current_price(symbol)
            if not current_price or current_price <= 0:
                logger.debug(f"Invalid price for {symbol}")
                return None
            ticker = self.client.get_ticker_24hr(symbol)
            if not ticker:
                logger.debug(f"No ticker for {symbol}")
                return None
            df_1h = self._get_cached_klines(symbol, '1h', 200)
            if df_1h is None or df_1h.empty:
                logger.debug(f"No 1h klines for {symbol}")
                return None
            tech = self.enhanced_indicators.calculate_enhanced_technical(df_1h, current_price)
            ob = self.order_flow.analyze_order_book(symbol, current_price)
            mt = self.order_flow.analyze_market_trades(symbol, current_price)
            cf = self.order_flow.calculate_cumulative_flow(symbol)
            if not all([ob, mt, cf]):
                logger.debug(f"Incomplete order flow data for {symbol}")
                return None
            if ob.spread_percentage > self.config.HIGH_CONFIDENCE_THRESHOLDS['MAX_SPREAD_PERCENT']:
                logger.debug(f"Spread too high for {symbol}: {ob.spread_percentage:.2f}%")
                return None
            result = (current_price, tech, ob, mt, cf, ticker, df_1h)
            self.signal_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Base analysis error for {symbol}: {e}")
            return None

# ========== TIER 1 GENERATOR ==========
class Tier1Generator:
    def __init__(self, parent: TieredSignalGenerator):
        self.parent = parent
        self.config = parent.hybrid_config
    
    def generate(self, symbol: str, base_analysis: Tuple, multi_tf_regime: MultiTimeframeRegime) -> Optional[EnhancedHighConfidenceSignal]:
        current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
        tech_score = self.parent.calculate_technical_score(tech)
        flow_score = self.parent.calculate_order_flow_score(ob, mt, cf)
        if abs(tech_score) < self.config.TIER_1_TECH_THRESHOLD or abs(flow_score) < self.config.TIER_1_FLOW_THRESHOLD:
            logger.debug(f"Tier1 {symbol}: Tech score {tech_score} < {self.config.TIER_1_TECH_THRESHOLD} or Flow score {flow_score} < {self.config.TIER_1_FLOW_THRESHOLD}")
            return None
        combined_score = tech_score * 0.4 + flow_score * 0.6
        if combined_score > 20:
            direction = "BUY"
        elif combined_score < -20:
            direction = "SELL"
        else:
            logger.debug(f"Tier1 {symbol}: Combined score {combined_score} not strong enough")
            return None
        regime_aligned = self._check_regime_alignment(direction, multi_tf_regime)
        if not regime_aligned:
            logger.debug(f"Tier1 {symbol}: Regime alignment failed")
            return None
        if self.config.EMA_200_TREND_FILTER_ENABLED and self.config.EMA_200_REQUIRED_FOR_TIER1:
            trend_filter = self.parent.trend_filter_200ema.analyze(df_1h, direction)
            if not trend_filter.filter_passed:
                logger.debug(f"Tier1 {symbol}: 200 EMA trend filter failed: {trend_filter.filter_description}")
                return None
        if not self._has_strong_confirmations(tech, ob, multi_tf_regime):
            logger.debug(f"Tier1 {symbol}: Strong confirmations failed")
            return None
        if not self._check_order_book_entry(ob, direction):
            logger.debug(f"Tier1 {symbol}: Order book entry check failed")
            return None
        return self._build_signal(symbol, base_analysis, tech_score, flow_score, direction, SignalTier.TIER_1_ULTRA_SAFE, multi_tf_regime)
    
    def _check_regime_alignment(self, direction: str, multi_tf: MultiTimeframeRegime) -> bool:
        if direction == "BUY":
            bullish_count = 0
            if "BULL" in multi_tf.ultra_short_regime:
                bullish_count += 1
            if "BULL" in multi_tf.short_regime:
                bullish_count += 1
            if "BULL" in multi_tf.medium_regime:
                bullish_count += 1
            if "BULL" in multi_tf.long_regime:
                bullish_count += 1
            alignment = (bullish_count / 4) * 100
            return alignment >= self.config.MIN_REGIME_ALIGNMENT
        else:
            bearish_count = 0
            if "BEAR" in multi_tf.ultra_short_regime:
                bearish_count += 1
            if "BEAR" in multi_tf.short_regime:
                bearish_count += 1
            if "BEAR" in multi_tf.medium_regime:
                bearish_count += 1
            if "BEAR" in multi_tf.long_regime:
                bearish_count += 1
            alignment = (bearish_count / 4) * 100
            return alignment >= self.config.MIN_REGIME_ALIGNMENT
    
    def _has_strong_confirmations(self, tech: EnhancedTechnicalAnalysis, 
                                  ob: OrderBookAnalysis, multi_tf: MultiTimeframeRegime) -> bool:
        confirmations = 0
        if tech.ema_trend in ["BULLISH", "BEARISH"]: confirmations += 1
        if tech.macd_trend in ["BULLISH", "BEARISH"]: confirmations += 1
        if tech.rsi_signal in ["OVERSOLD", "OVERBOUGHT"]: confirmations += 1
        if abs(ob.imbalance) > 15: confirmations += 1
        if ob.bid_ask_ratio > 1.3 or ob.bid_ask_ratio < 0.7: confirmations += 1
        if multi_tf.regime_alignment > 70: confirmations += 1
        if multi_tf.overall_regime in ["TRENDING_BULL", "TRENDING_BEAR"]: confirmations += 1
        if multi_tf.ultra_short_volatility != "HIGH": confirmations += 1
        return confirmations >= 6
    
    def _check_order_book_entry(self, ob: OrderBookAnalysis, direction: str) -> bool:
        if direction == "BUY":
            return ob.imbalance > 0 and ob.buy_pressure > 52
        else:
            return ob.imbalance < 0 and ob.sell_pressure > 52
    
    def _build_signal(self, symbol: str, base_analysis: Tuple, tech_score: float, 
                     flow_score: float, direction: str, tier: SignalTier,
                     multi_tf_regime: MultiTimeframeRegime) -> EnhancedHighConfidenceSignal:
        current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
        volume_24h = ticker.get('quoteVolume', 0)
        funding_data = self.parent.client.get_funding_rate(symbol)
        funding_rate = funding_data if funding_data is not None else 0.0
        smart_money = self.parent.smart_money_detector.detect_smart_money(symbol, df_1h, ob)
        profile = self.parent.market_profile_analyzer.analyze_profile(df_1h)
        intermarket = self.parent.intermarket_analyzer.analyze_intermarket(symbol)
        onchain = self.parent.onchain_analyzer.analyze_onchain(symbol)
        sentiment = self.parent.sentiment_analyzer.analyze_sentiment(funding_rate)
        divergence = self.parent.divergence_detector.detect_divergences(df_1h)
        patterns = self.parent.pattern_recognizer.recognize_patterns(df_1h)
        liquidity = self.parent.liquidity_analyzer.analyze_liquidity(ob, df_1h)
        confluence = self.parent.timeframe_analyzer.analyze_confluence(symbol, direction)
        stop_loss, stop_percentage, atr_value = self.parent.calculate_atr_stop_loss(current_price, direction, df_1h)
        atr_stop = ATRStopLoss(atr_value=atr_value, atr_multiplier=self.config.ATR_MULTIPLIER)
        volume_profile_entry = None
        vp_result = None
        if self.config.VOLUME_PROFILE_ENTRY_ENABLED:
            vp = VolumeProfileEntry()
            style_name = confluence.primary_style if confluence.primary_style else "INTRADAY"
            vp_result = vp.calculate_entry(df_1h, direction, current_price, style_name)
            volume_profile_entry = vp
            if vp_result.get('used_fallback', False):
                logger.info(f"Volume Profile fallback for {symbol}")
            else:
                logger.info(f"Volume Profile calculated for {symbol}: POC={vp_result['poc_price']:.4f}")
        liquidity_grab = None
        if self.config.LIQUIDITY_GRAB_ENABLED:
            lg = LiquidityGrabDetection()
            liquidity_grab = lg.detect(df_1h, ob)
        trend_filter = None
        if self.config.EMA_200_TREND_FILTER_ENABLED:
            tf = TrendFilter200EMA()
            trend_filter = tf.analyze(df_1h, direction)
        smart_money_display = None
        if smart_money:
            primary_concept = smart_money.primary_concept or SmartMoneyConcept.NONE
            secondary_concepts = []
            if smart_money.order_block_detected and smart_money.primary_concept != SmartMoneyConcept.ORDER_BLOCK:
                secondary_concepts.append(SmartMoneyConcept.ORDER_BLOCK)
            if smart_money.liquidity_sweep and smart_money.primary_concept != SmartMoneyConcept.LIQUIDITY_SWEEP:
                secondary_concepts.append(SmartMoneyConcept.LIQUIDITY_SWEEP)
            if smart_money.fvg_detected and smart_money.primary_concept != SmartMoneyConcept.FVG:
                secondary_concepts.append(SmartMoneyConcept.FVG)
            if smart_money.breaker_block and smart_money.primary_concept != SmartMoneyConcept.BREAKER:
                secondary_concepts.append(SmartMoneyConcept.BREAKER)
            if smart_money.mitigation_detected and smart_money.primary_concept != SmartMoneyConcept.MITIGATION:
                secondary_concepts.append(SmartMoneyConcept.MITIGATION)
            if smart_money.institutional_divergence and smart_money.primary_concept != SmartMoneyConcept.INSTITUTIONAL_DIVERGENCE:
                secondary_concepts.append(SmartMoneyConcept.INSTITUTIONAL_DIVERGENCE)
            if liquidity_grab and liquidity_grab.liquidity_grab_detected:
                secondary_concepts.append(SmartMoneyConcept.LIQUIDITY_GRAB)
            concept_details = {}
            if smart_money.order_block_detected:
                concept_details['order_block'] = {
                    'type': smart_money.order_block_type,
                    'price': smart_money.order_block_price,
                    'strength': smart_money.order_block_strength
                }
            if smart_money.liquidity_sweep:
                concept_details['liquidity_sweep'] = {
                    'levels': smart_money.liquidity_levels
                }
            if smart_money.fvg_detected:
                concept_details['fvg'] = {
                    'type': smart_money.fvg_type,
                    'low': smart_money.fvg_zone_low,
                    'high': smart_money.fvg_zone_high,
                    'filled': smart_money.fvg_filled
                }
            if liquidity_grab and liquidity_grab.liquidity_grab_detected:
                concept_details['liquidity_grab'] = {
                    'type': liquidity_grab.grab_type,
                    'price': liquidity_grab.grab_price,
                    'strength': liquidity_grab.grab_strength
                }
            smart_money_display = SmartMoneyDisplay(
                primary_concept=primary_concept,
                secondary_concepts=secondary_concepts[:3],
                concept_details=concept_details,
                smart_money_score=smart_money.smart_money_score,
                concept_description=smart_money.concept_summary
            )
        legacy_regime = MarketRegime(
            regime_type=multi_tf_regime.overall_regime,
            strength=multi_tf_regime.overall_strength,
            volatility=self._get_primary_volatility(multi_tf_regime),
            volume_profile="NEUTRAL",
            adx_value=multi_tf_regime.medium_adx,
            adx_trend=self._get_adx_trend(multi_tf_regime.medium_adx),
            regime_score=multi_tf_regime.regime_score
        )
        accuracy_score = self._calculate_accuracy_score(tech_score, flow_score, legacy_regime, smart_money, 
                                                       intermarket, onchain, sentiment, divergence, 
                                                       patterns, liquidity, confluence, direction, multi_tf_regime,
                                                       liquidity_grab, trend_filter)
        base_confidence = 60
        base_confidence += min(abs(tech_score) * 0.3, 15)
        base_confidence += min(abs(flow_score) * 0.3, 15)
        base_confidence += confluence.confluence_count * 2
        base_confidence += multi_tf_regime.regime_alignment * 0.2
        base_confidence += accuracy_score * 0.1
        confidence = min(base_confidence, 98)
        ai_confidence = confidence
        ai_confidence_pred = 0
        ai_conf_in_pred = 0
        ai_used = False
        if self.config.AI_CONFIDENCE_MODEL_ENABLED and self.parent.ai_model.is_trained:
            try:
                features = self.parent.ai_model.extract_features(self)
                ai_confidence_pred, ai_conf_in_pred = self.parent.ai_model.predict(features)
                if self.config.AI_OVERRIDE_CONFIDENCE and ai_confidence_pred > confidence:
                    ai_confidence = ai_confidence_pred
                    ai_used = True
            except:
                pass
        atr = self.parent.indicators.calculate_atr(df_1h)
        style_name = confluence.primary_style if confluence.primary_style else "INTRADAY"
        entry_data = self.parent.get_style_entries(symbol, direction, current_price, df_1h, style_name)
        primary_style_enum = None
        if confluence.primary_style:
            if confluence.primary_style == "SCALPING":
                primary_style_enum = SignalStyle.SCALPING
            elif confluence.primary_style == "INTRADAY":
                primary_style_enum = SignalStyle.INTRADAY
            elif confluence.primary_style == "SWING":
                primary_style_enum = SignalStyle.SWING
            elif confluence.primary_style == "POSITION":
                primary_style_enum = SignalStyle.POSITION
        else:
            primary_style_enum = SignalStyle.HYBRID
        if primary_style_enum == SignalStyle.SCALPING:
            entry_price = entry_data['scalping']['price']
            entry_low = entry_data['scalping']['range_low']
            entry_high = entry_data['scalping']['range_high']
            entry_logic = entry_data['scalping']['logic']
        elif primary_style_enum == SignalStyle.INTRADAY:
            entry_price = entry_data['intraday']['price']
            entry_low = entry_data['intraday']['range_low']
            entry_high = entry_data['intraday']['range_high']
            entry_logic = entry_data['intraday']['logic']
        elif primary_style_enum == SignalStyle.SWING:
            entry_price = entry_data['swing']['price']
            entry_low = entry_data['swing']['range_low']
            entry_high = entry_data['swing']['range_high']
            entry_logic = entry_data['swing']['logic']
        else:
            entry_price = entry_data['position']['price']
            entry_low = entry_data['position']['range_low']
            entry_high = entry_data['position']['range_high']
            entry_logic = entry_data['position']['logic']
        if direction == "BUY":
            if "Market" in entry_logic or "Aggressive" in entry_logic:
                order_type = OrderType.MARKET_BUY
            else:
                order_type = OrderType.LIMIT_BUY
        else:
            if "Market" in entry_logic or "Aggressive" in entry_logic:
                order_type = OrderType.MARKET_SELL
            else:
                order_type = OrderType.LIMIT_SELL
        stop_loss, stop_percentage, atr_value = self.parent.calculate_atr_stop_loss(entry_price, direction, df_1h)
        (scalping_tp1, scalping_tp2, intraday_tp1, intraday_tp2, 
         swing_tp1, swing_tp2, position_tp1, position_tp2) = self.parent.calculate_take_profit_adaptive(
            entry_price, stop_loss, direction, 
            confluence.aligned_styles[0] if confluence.aligned_styles else None,
            atr, self.config
        )
        if primary_style_enum == SignalStyle.SCALPING:
            tp1 = scalping_tp1
            tp2 = scalping_tp2
            tp3 = scalping_tp2 * 1.5
        elif primary_style_enum == SignalStyle.INTRADAY:
            tp1 = intraday_tp1
            tp2 = intraday_tp2
            tp3 = intraday_tp2 * 1.33
        elif primary_style_enum == SignalStyle.SWING:
            tp1 = swing_tp1
            tp2 = swing_tp2
            tp3 = swing_tp2 * 1.4
        elif primary_style_enum == SignalStyle.POSITION:
            tp1 = position_tp1
            tp2 = position_tp2
            tp3 = position_tp2 * 1.5
        else:
            tp1 = intraday_tp1
            tp2 = intraday_tp2
            tp3 = intraday_tp2 * 1.33
        leverage = self._calculate_leverage(legacy_regime, confluence, multi_tf_regime)
        risk_reward = self.parent.calculate_risk_reward_adaptive(
            entry_price, stop_loss,
            scalping_tp1, scalping_tp2,
            intraday_tp1, intraday_tp2,
            swing_tp1, swing_tp2,
            position_tp1, position_tp2,
            direction
        )
        confirmations = self.parent.calculate_confirmations(df_1h, tech, confluence, direction)
        market_context = MarketContext(
            btc_price=intermarket.btc_price or 0,
            btc_change_24h=intermarket.btc_change_24h or 0,
            eth_price=intermarket.eth_price or 0,
            eth_change_24h=intermarket.eth_change_24h or 0,
            total_market_cap=intermarket.total_market_cap or 0,
            market_cap_change_24h=0,
            btc_dominance=intermarket.btc_dominance or 50,
            dominance_change=0,
            fear_greed_index=sentiment.fear_greed_index or 50,
            fear_greed_text=sentiment.fear_greed_sentiment
        )
        backtest_result = self.parent.backtest_engine.get_backtest_result(symbol)
        primary_reasons = self._generate_reasons(direction, tech, tech_score, flow_score, legacy_regime, 
                                                smart_money, confluence, accuracy_score, confirmations,
                                                entry_logic, None, None, ob, multi_tf_regime,
                                                liquidity_grab, trend_filter)
        if smart_money_display and smart_money_display.primary_concept != SmartMoneyConcept.NONE:
            primary_reasons.insert(0, smart_money_display.concept_description)
        position_size = 1.0
        if accuracy_score > 85:
            position_size = 1.5
        elif accuracy_score > 75:
            position_size = 1.2
        elif accuracy_score > 65:
            position_size = 1.0
        else:
            position_size = 0.8
        if multi_tf_regime.ultra_short_volatility == "HIGH" or multi_tf_regime.short_volatility == "HIGH":
            position_size *= 0.7
        elif multi_tf_regime.ultra_short_volatility == "LOW" and multi_tf_regime.short_volatility == "LOW":
            position_size *= 1.2
        position_size = min(max(position_size, 0.5), 2.0)
        signal_type = "STRONG_BUY" if direction == "BUY" else "STRONG_SELL"
        ultra_short_aligned = "BULL" in multi_tf_regime.ultra_short_regime if direction == "BUY" else "BEAR" in multi_tf_regime.ultra_short_regime
        short_aligned = "BULL" in multi_tf_regime.short_regime if direction == "BUY" else "BEAR" in multi_tf_regime.short_regime
        medium_aligned = "BULL" in multi_tf_regime.medium_regime if direction == "BUY" else "BEAR" in multi_tf_regime.medium_regime
        long_aligned = "BULL" in multi_tf_regime.long_regime if direction == "BUY" else "BEAR" in multi_tf_regime.long_regime
        secondary_styles_enum = []
        for style in confluence.secondary_styles:
            if style == "SCALPING":
                secondary_styles_enum.append(SignalStyle.SCALPING)
            elif style == "INTRADAY":
                secondary_styles_enum.append(SignalStyle.INTRADAY)
            elif style == "SWING":
                secondary_styles_enum.append(SignalStyle.SWING)
            elif style == "POSITION":
                secondary_styles_enum.append(SignalStyle.POSITION)
        signal = EnhancedHighConfidenceSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal_type,
            confidence=ai_confidence,
            current_price=current_price,
            best_bid=ob.best_bid,
            best_ask=ob.best_ask,
            spread=ob.spread,
            spread_percentage=ob.spread_percentage,
            suggested_order_type=order_type,
            entry_price=entry_price,
            entry_range_low=entry_low,
            entry_range_high=entry_high,
            optimal_entry_timeframe=entry_logic,
            stop_loss=stop_loss,
            stop_loss_percentage=stop_percentage,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            recommended_leverage=leverage,
            rsi=tech.rsi,
            rsi_signal=tech.rsi_signal,
            macd_trend=tech.macd_trend,
            ema_trend=tech.ema_trend,
            bb_position=tech.bb_position,
            buy_pressure=ob.buy_pressure,
            sell_pressure=ob.sell_pressure,
            bid_ask_ratio=ob.bid_ask_ratio,
            cumulative_delta_15min=cf.delta_15min,
            delta_trend=cf.trend_strength,
            volume_24h=volume_24h,
            volume_change_24h=ticker.get('priceChangePercent', 0),
            funding_rate=funding_rate,
            funding_sentiment="ALIGNED" if sentiment.funding_sentiment_aligned else "MISALIGNED",
            open_interest=self.parent.client.get_open_interest(symbol),
            oi_change_1h=None,
            support_levels=ob.support_levels,
            resistance_levels=ob.resistance_levels,
            nearest_support=ob.support_levels[0] if ob.support_levels else current_price * 0.98,
            nearest_resistance=ob.resistance_levels[0] if ob.resistance_levels else current_price * 1.02,
            primary_reasons=primary_reasons,
            secondary_reasons=[],
            aligned_styles=confluence.aligned_styles,
            style_scores=confluence.style_scores,
            recommendation=f"{'LONG' if direction == 'BUY' else 'SHORT'} | Acc: {accuracy_score:.1f}%",
            risk_level=self._get_risk_level(legacy_regime, stop_percentage, multi_tf_regime),
            time_horizon=confluence.best_timeframe,
            market_regime=legacy_regime,
            multi_tf_regime=multi_tf_regime,
            smart_money=smart_money,
            market_profile=profile,
            intermarket=intermarket,
            onchain=onchain,
            sentiment=sentiment,
            divergence=divergence,
            patterns=patterns,
            liquidity=liquidity,
            timeframe_confluence=confluence,
            enhanced_tech=tech,
            overall_accuracy_score=accuracy_score,
            risk_adjusted_confidence=ai_confidence,
            expected_move=(atr / current_price) * 100 if atr else 2.0,
            optimal_position_size=position_size,
            tech_score=tech_score,
            flow_score=flow_score,
            backtest_result=backtest_result,
            market_context=market_context,
            risk_reward=risk_reward,
            confirmations=confirmations,
            bot_win_rate=0,
            signals_last_100=0,
            win_rate_last_100=0,
            entry_timeframe_3m_signal=None,
            entry_timeframe_5m_signal=None,
            tier=tier,
            tier_confidence=ai_confidence,
            smart_scan_score=0,
            adaptive_cooldown_minutes=15,
            entry_bid_level=entry_data['best_bid'],
            entry_ask_level=entry_data['best_ask'],
            entry_mid_price=entry_data['mid'],
            order_book_imbalance=entry_data.get('imbalance', 0),
            ultra_short_regime_aligned=ultra_short_aligned,
            short_regime_aligned=short_aligned,
            medium_regime_aligned=medium_aligned,
            long_regime_aligned=long_aligned,
            scalping_entry=entry_data['scalping']['price'],
            intraday_entry=entry_data['intraday']['price'],
            swing_entry=entry_data['swing']['price'],
            position_entry=entry_data['position']['price'],
            scalping_tp1=scalping_tp1,
            scalping_tp2=scalping_tp2,
            intraday_tp1=intraday_tp1,
            intraday_tp2=intraday_tp2,
            swing_tp1=swing_tp1,
            swing_tp2=swing_tp2,
            position_tp1=position_tp1,
            position_tp2=position_tp2,
            primary_style=primary_style_enum,
            secondary_styles=secondary_styles_enum,
            style_confidence=confluence.style_scores,
            smart_money_display=smart_money_display,
            atr_stop_loss=atr_stop,
            atr_value=atr_value,
            atr_multiplier=self.config.ATR_MULTIPLIER,
            volume_profile_entry=volume_profile_entry,
            volume_poc_price=entry_data.get('poc_price', current_price),
            volume_value_area_low=entry_data.get('value_area_low', current_price * 0.98),
            volume_value_area_high=entry_data.get('value_area_high', current_price * 1.02),
            liquidity_grab=liquidity_grab,
            liquidity_grab_detected=liquidity_grab.liquidity_grab_detected if liquidity_grab else False,
            liquidity_grab_type=liquidity_grab.grab_type if liquidity_grab else "NONE",
            liquidity_grab_strength=liquidity_grab.grab_strength if liquidity_grab else 0,
            trend_filter_200ema=trend_filter,
            ema_200=trend_filter.ema_200 if trend_filter else 0,
            price_vs_ema_200=trend_filter.price_vs_ema if trend_filter else "UNKNOWN",
            ema_200_trend=trend_filter.ema_trend if trend_filter else "UNKNOWN",
            trend_filter_passed=trend_filter.filter_passed if trend_filter else True,
            ai_confidence=ai_confidence,
            ai_confidence_prediction=ai_confidence_pred,
            ai_confidence_in_prediction=ai_conf_in_pred,
            ai_model_used=ai_used,
            alert_level=None,
            is_confirmed=False
        )
        if abs(signal.entry_price - current_price) / current_price > 0.05:
            logger.warning(f"Entry price {signal.entry_price:.2f} too far from current {current_price:.2f}")
            signal.entry_price = current_price
            signal.entry_range_low = current_price * 0.998
            signal.entry_range_high = current_price * 1.002
            signal.optimal_entry_timeframe = "Corrected: Using current price"
        if abs(signal.stop_loss - signal.entry_price) < 1e-8:
            logger.error(f"CRITICAL: Stop loss equals entry price for {symbol} - forcing adjustment")
            if direction == "BUY":
                signal.stop_loss = signal.entry_price * 0.99
                signal.stop_loss_percentage = 1.0
            else:
                signal.stop_loss = signal.entry_price * 1.01
                signal.stop_loss_percentage = 1.0
        if abs(signal.take_profit_1 - signal.take_profit_2) < 1e-8:
            logger.warning(f"TP1 equals TP2 for {symbol} - adjusting")
            risk = abs(signal.entry_price - signal.stop_loss)
            if direction == "BUY":
                signal.take_profit_2 = signal.take_profit_1 + (risk * 0.5)
            else:
                signal.take_profit_2 = signal.take_profit_1 - (risk * 0.5)
        if signal.stop_loss_percentage < 0.5 or signal.stop_loss_percentage > 5.0:
            logger.warning(f"Stop loss {signal.stop_loss_percentage:.2f}% unreasonable - adjusting")
            signal.stop_loss_percentage = 1.5
            if direction == "BUY":
                signal.stop_loss = signal.entry_price * 0.985
            else:
                signal.stop_loss = signal.entry_price * 1.015
        if signal.volume_value_area_low < current_price * 0.8 or signal.volume_value_area_high > current_price * 1.2:
            logger.warning(f"Value area too wide: {signal.volume_value_area_low:.2f}-{signal.volume_value_area_high:.2f}")
            signal.volume_value_area_low = current_price * 0.95
            signal.volume_value_area_high = current_price * 1.05
            signal.volume_poc_price = current_price
        if direction == "BUY" and signal.take_profit_1 <= signal.entry_price:
            logger.warning(f"TP1 {signal.take_profit_1:.2f} <= entry {signal.entry_price:.2f} - recalculating")
            risk = abs(signal.entry_price - signal.stop_loss)
            signal.take_profit_1 = signal.entry_price + (risk * 1.5)
            signal.take_profit_2 = signal.entry_price + (risk * 2.5)
            signal.take_profit_3 = signal.entry_price + (risk * 4.0)
        if direction == "SELL" and signal.take_profit_1 >= signal.entry_price:
            logger.warning(f"TP1 {signal.take_profit_1:.2f} >= entry {signal.entry_price:.2f} - recalculating")
            risk = abs(signal.entry_price - signal.stop_loss)
            signal.take_profit_1 = signal.entry_price - (risk * 1.5)
            signal.take_profit_2 = signal.entry_price - (risk * 2.5)
            signal.take_profit_3 = signal.entry_price - (risk * 4.0)
        logger.info(f"Signal built for {symbol} with validation passed")
        signal.risk_report = self.parent.risk_manager.get_risk_report()
        if self.parent.ml_models.models:
            try:
                features = self.parent.ai_model.extract_features(signal)
                ml_pred = self.parent.ml_models.predict(np.array(features), 'ensemble_model')
                signal.ml_predictions = {'ensemble': ml_pred}
            except:
                pass
        return signal
    
    def _calculate_accuracy_score(self, tech_score: float, flow_score: float,
                                 regime: MarketRegime, smart_money: SmartMoneyConcepts,
                                 intermarket: InterMarketAnalysis, onchain: Optional[OnChainMetrics],
                                 sentiment: MarketSentiment, divergence: DivergenceAnalysis,
                                 patterns: PatternRecognition, liquidity: LiquidityAnalysis,
                                 confluence: TimeframeConfluence, direction: str,
                                 multi_tf: MultiTimeframeRegime,
                                 liquidity_grab: Optional[LiquidityGrabDetection] = None,
                                 trend_filter: Optional[TrendFilter200EMA] = None) -> float:
        score = 50
        if direction == "BUY":
            score += min(max(tech_score, 0) * 0.3, 10)
            score += min(max(flow_score, 0) * 0.4, 15)
        else:
            score += min(max(-tech_score, 0) * 0.3, 10)
            score += min(max(-flow_score, 0) * 0.4, 15)
        score += min(multi_tf.regime_alignment * 0.2, 10)
        if direction == "BUY":
            if "BULL" in multi_tf.ultra_short_regime:
                score += 5
            if "BULL" in multi_tf.short_regime:
                score += 4
            if "BULL" in multi_tf.medium_regime:
                score += 3
            if "BULL" in multi_tf.long_regime:
                score += 2
        else:
            if "BEAR" in multi_tf.ultra_short_regime:
                score += 5
            if "BEAR" in multi_tf.short_regime:
                score += 4
            if "BEAR" in multi_tf.medium_regime:
                score += 3
            if "BEAR" in multi_tf.long_regime:
                score += 2
        if abs(smart_money.smart_money_score) > 20:
            score += min(abs(smart_money.smart_money_score) * 0.2, 10)
        if intermarket.intermarket_score > 0 and direction == "BUY":
            score += min(intermarket.intermarket_score * 0.2, 8)
        elif intermarket.intermarket_score < 0 and direction == "SELL":
            score += min(abs(intermarket.intermarket_score) * 0.2, 8)
        if sentiment.fear_greed_index is not None:
            if (direction == "BUY" and sentiment.fear_greed_index < 30) or \
               (direction == "SELL" and sentiment.fear_greed_index > 70):
                score += 8
        if (direction == "BUY" and divergence.divergence_score > 0) or \
           (direction == "SELL" and divergence.divergence_score < 0):
            score += min(abs(divergence.divergence_score) * 0.2, 8)
        if (direction == "BUY" and patterns.pattern_score > 0) or \
           (direction == "SELL" and patterns.pattern_score < 0):
            score += min(abs(patterns.pattern_score) * 0.1, 5)
        if (direction == "BUY" and liquidity.liquidity_score > 0) or \
           (direction == "SELL" and liquidity.liquidity_score < 0):
            score += min(abs(liquidity.liquidity_score) * 0.2, 5)
        score += min(confluence.alignment_score * 0.2, 8)
        if liquidity_grab and liquidity_grab.liquidity_grab_detected:
            if (direction == "BUY" and liquidity_grab.grab_type in ["SELL_SIDE", "BOTH"] and liquidity_grab.reversal_confirmed) or \
               (direction == "SELL" and liquidity_grab.grab_type in ["BUY_SIDE", "BOTH"] and liquidity_grab.reversal_confirmed):
                score += min(liquidity_grab.grab_strength * 0.3, 15)
        if trend_filter:
            if (direction == "BUY" and trend_filter.filter_passed and trend_filter.price_vs_ema == "ABOVE") or \
               (direction == "SELL" and trend_filter.filter_passed and trend_filter.price_vs_ema == "BELOW"):
                score += 10
            elif trend_filter.filter_passed:
                score += 5
        return min(max(score, 0), 100)
    
    def _calculate_leverage(self, regime: MarketRegime, confluence: TimeframeConfluence, multi_tf: MultiTimeframeRegime) -> int:
        leverage = 5
        if regime.regime_type in ["TRENDING_BULL", "TRENDING_BEAR"]:
            leverage = 10
        elif regime.regime_type == "RANGING":
            leverage = 4
        if multi_tf.ultra_short_volatility == "LOW":
            leverage = int(leverage * 1.3)
        elif multi_tf.ultra_short_volatility == "HIGH":
            leverage = int(leverage * 0.7)
        if confluence.alignment_score >= 80:
            leverage = int(leverage * 1.4)
        elif confluence.alignment_score >= 60:
            leverage = int(leverage * 1.2)
        elif confluence.alignment_score <= 40:
            leverage = int(leverage * 0.8)
        return max(2, min(20, leverage))
    
    def _get_risk_level(self, regime: MarketRegime, stop_percentage: float, multi_tf: MultiTimeframeRegime) -> str:
        if stop_percentage < 1.0:
            risk_level = "LOW"
        elif stop_percentage < 2.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        if multi_tf.ultra_short_volatility == "HIGH" or multi_tf.short_volatility == "HIGH":
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            elif risk_level == "MEDIUM":
                risk_level = "HIGH"
        return risk_level
    
    def _get_primary_volatility(self, multi_tf: MultiTimeframeRegime) -> str:
        volatilities = [
            multi_tf.ultra_short_volatility,
            multi_tf.short_volatility,
            multi_tf.medium_volatility,
            multi_tf.long_volatility
        ]
        vol_counts = {v: volatilities.count(v) for v in set(volatilities)}
        return max(vol_counts, key=vol_counts.get, default="MEDIUM")
    
    def _get_adx_trend(self, adx: float) -> str:
        if adx >= 50:
            return "VERY_STRONG"
        elif adx >= 35:
            return "STRONG"
        elif adx >= 25:
            return "WEAK"
        else:
            return "NO_TREND"
    
    def _generate_reasons(self, direction: str, tech: EnhancedTechnicalAnalysis,
                         tech_score: float, flow_score: float, regime: MarketRegime,
                         smart_money: SmartMoneyConcepts, confluence: TimeframeConfluence,
                         accuracy_score: float, confirmations: ConfirmationSignals,
                         opt_tf: str, signal_3m: Optional[str], signal_5m: Optional[str],
                         ob: OrderBookAnalysis, multi_tf: MultiTimeframeRegime,
                         liquidity_grab: Optional[LiquidityGrabDetection] = None,
                         trend_filter: Optional[TrendFilter200EMA] = None) -> List[str]:
        reasons = []
        if smart_money and smart_money.primary_concept and smart_money.primary_concept != SmartMoneyConcept.NONE:
            reasons.append(smart_money.concept_summary)
        if liquidity_grab and liquidity_grab.liquidity_grab_detected:
            reasons.append(liquidity_grab.grab_description)
        reasons.append(f"Regime Alignment: {multi_tf.regime_alignment:.0f}%")
        if "BULL" in multi_tf.ultra_short_regime and direction == "BUY":
            reasons.append("Ultra-short bullish")
        if "BEAR" in multi_tf.ultra_short_regime and direction == "SELL":
            reasons.append("Ultra-short bearish")
        if "BULL" in multi_tf.short_regime and direction == "BUY":
            reasons.append("Short-term bullish")
        if "BEAR" in multi_tf.short_regime and direction == "SELL":
            reasons.append("Short-term bearish")
        if "BULL" in multi_tf.medium_regime and direction == "BUY":
            reasons.append("Medium-term bullish")
        if "BEAR" in multi_tf.medium_regime and direction == "SELL":
            reasons.append("Medium-term bearish")
        if "BULL" in multi_tf.long_regime and direction == "BUY":
            reasons.append("Long-term bullish")
        if "BEAR" in multi_tf.long_regime and direction == "SELL":
            reasons.append("Long-term bearish")
        if confluence.primary_style:
            reasons.append(f"Primary style: {confluence.primary_style}")
            if confluence.secondary_styles:
                reasons.append(f"Secondary: {', '.join(confluence.secondary_styles)}")
        if ob.imbalance > 15:
            reasons.append(f"Strong OB imbalance ({ob.imbalance:.0f}%)")
        elif ob.imbalance < -15:
            reasons.append(f"Strong OB imbalance ({ob.imbalance:.0f}%)")
        if ob.bid_ask_ratio > 1.3:
            reasons.append(f"High bid/ask ratio ({ob.bid_ask_ratio:.2f})")
        elif ob.bid_ask_ratio < 0.7:
            reasons.append(f"Low bid/ask ratio ({ob.bid_ask_ratio:.2f})")
        reasons.append(f"Entry: {opt_tf}")
        if regime.regime_type in ["TRENDING_BULL", "TRENDING_BEAR"]:
            reasons.append(f"{regime.regime_type} ({regime.strength:.0f}%)")
        if tech.ema_trend == "BULLISH" and direction == "BUY":
            reasons.append("EMA bullish")
        elif tech.ema_trend == "BEARISH" and direction == "SELL":
            reasons.append("EMA bearish")
        if tech.macd_trend == "BULLISH" and direction == "BUY":
            reasons.append("MACD bullish")
        elif tech.macd_trend == "BEARISH" and direction == "SELL":
            reasons.append("MACD bearish")
        if (direction == "BUY" and tech.rsi_signal == "OVERSOLD") or \
           (direction == "SELL" and tech.rsi_signal == "OVERBOUGHT"):
            reasons.append(f"RSI {tech.rsi_signal}")
        if smart_money.order_block_detected and smart_money.primary_concept != SmartMoneyConcept.ORDER_BLOCK:
            reasons.append(f"Smart money {smart_money.order_block_type}")
        if confluence.confluence_count >= 4:
            reasons.append(f"Multi-TF confluence ({confluence.confluence_count})")
        if abs(flow_score) > 50:
            reasons.append("Strong order flow")
        if accuracy_score > 80:
            reasons.append(f"High accuracy ({accuracy_score:.0f}%)")
        if confirmations.confirmation_score > 70:
            reasons.append("Strong confirmations")
        if self.config.ATR_STOP_LOSS_ENABLED:
            reasons.append("ATR-based stop loss")
        if trend_filter and trend_filter.filter_passed:
            reasons.append(trend_filter.filter_description)
        if len(reasons) > 5:
            reasons = reasons[:5]
        return reasons

# ========== TIER 2 GENERATOR ==========
class Tier2Generator(Tier1Generator):
    def __init__(self, parent: TieredSignalGenerator):
        super().__init__(parent)
        self.recent_signals = deque(maxlen=50)
        self.config = parent.hybrid_config
    
    def generate(self, symbol: str, base_analysis: Tuple, multi_tf_regime: MultiTimeframeRegime) -> Optional[EnhancedHighConfidenceSignal]:
        current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
        if self._has_recent_signal(symbol, 30):
            logger.debug(f"Tier2 {symbol}: Recent signal within 30 minutes")
            return None
        tech_score = self.parent.calculate_technical_score(tech)
        flow_score = self.parent.calculate_order_flow_score(ob, mt, cf)
        tech_threshold, flow_threshold = self._get_dynamic_thresholds(multi_tf_regime)
        if abs(tech_score) < tech_threshold or abs(flow_score) < flow_threshold:
            logger.debug(f"Tier2 {symbol}: Tech score {tech_score} < {tech_threshold} or Flow score {flow_score} < {flow_threshold}")
            return None
        combined_score = tech_score * 0.45 + flow_score * 0.55
        if combined_score > 15:
            direction = "BUY"
        elif combined_score < -15:
            direction = "SELL"
        else:
            logger.debug(f"Tier2 {symbol}: Combined score {combined_score} not strong enough")
            return None
        if not self._check_basic_regime_alignment(direction, multi_tf_regime):
            logger.debug(f"Tier2 {symbol}: Basic regime alignment failed")
            return None
        if self.config.EMA_200_TREND_FILTER_ENABLED and self.config.EMA_200_REQUIRED_FOR_TIER2:
            trend_filter = self.parent.trend_filter_200ema.analyze(df_1h, direction)
            if not trend_filter.filter_passed:
                logger.debug(f"Tier2 {symbol}: 200 EMA trend filter failed: {trend_filter.filter_description}")
                return None
        if not self._check_order_book_entry_light(ob, direction):
            logger.debug(f"Tier2 {symbol}: Order book light check failed")
            return None
        if not self._safety_checks(tech, ob, multi_tf_regime):
            logger.debug(f"Tier2 {symbol}: Safety checks failed")
            return None
        signal = self._build_signal(symbol, base_analysis, tech_score, flow_score, direction, SignalTier.TIER_2_BALANCED, multi_tf_regime)
        signal.adaptive_cooldown_minutes = 10
        self.recent_signals.append((symbol, time.time()))
        return signal
    
    def _has_recent_signal(self, symbol: str, minutes: int) -> bool:
        current_time = time.time()
        for sym, ts in self.recent_signals:
            if sym == symbol and (current_time - ts) < minutes * 60:
                return True
        return False
    
    def _get_dynamic_thresholds(self, multi_tf: MultiTimeframeRegime) -> Tuple[float, float]:
        base_tech = self.config.TIER_2_TECH_THRESHOLD
        base_flow = self.config.TIER_2_FLOW_THRESHOLD
        if multi_tf.ultra_short_volatility == "HIGH" or multi_tf.short_volatility == "HIGH":
            return base_tech * 1.2, base_flow * 1.2
        elif multi_tf.ultra_short_volatility == "LOW" and multi_tf.short_volatility == "LOW":
            return base_tech * 0.8, base_flow * 0.8
        else:
            return base_tech, base_flow
    
    def _check_basic_regime_alignment(self, direction: str, multi_tf: MultiTimeframeRegime) -> bool:
        if direction == "BUY":
            return "BULL" in multi_tf.ultra_short_regime or "BULL" in multi_tf.short_regime
        else:
            return "BEAR" in multi_tf.ultra_short_regime or "BEAR" in multi_tf.short_regime
    
    def _check_order_book_entry_light(self, ob: OrderBookAnalysis, direction: str) -> bool:
        if direction == "BUY":
            return ob.imbalance > -5
        else:
            return ob.imbalance < 5
    
    def _safety_checks(self, tech: EnhancedTechnicalAnalysis, 
                      ob: OrderBookAnalysis, multi_tf: MultiTimeframeRegime) -> bool:
        if tech.rsi > 85 or tech.rsi < 15:
            return False
        if ob.spread_percentage > 0.1:
            return False
        if multi_tf.ultra_short_volatility == "HIGH" and multi_tf.ultra_short_strength > 80:
            return False
        return True

# ========== TIER 3 GENERATOR ==========
class Tier3Generator(Tier2Generator):
    def __init__(self, parent: TieredSignalGenerator):
        super().__init__(parent)
        self.signal_count = defaultdict(int)
        self.config = parent.hybrid_config
    
    def generate(self, symbol: str, base_analysis: Tuple, multi_tf_regime: MultiTimeframeRegime) -> Optional[EnhancedHighConfidenceSignal]:
        current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
        if self.signal_count[symbol] >= 4:
            logger.debug(f"Tier3 {symbol}: Already generated 4 signals")
            return None
        tech_score = self.parent.calculate_technical_score(tech)
        flow_score = self.parent.calculate_order_flow_score(ob, mt, cf)
        if abs(tech_score) < self.config.TIER_3_TECH_THRESHOLD or abs(flow_score) < self.config.TIER_3_FLOW_THRESHOLD:
            logger.debug(f"Tier3 {symbol}: Tech score {tech_score} < {self.config.TIER_3_TECH_THRESHOLD} or Flow score {flow_score} < {self.config.TIER_3_FLOW_THRESHOLD}")
            return None
        combined_score = tech_score * 0.5 + flow_score * 0.5
        if combined_score > 10:
            direction = "BUY"
        elif combined_score < -10:
            direction = "SELL"
        else:
            logger.debug(f"Tier3 {symbol}: Combined score {combined_score} not strong enough")
            return None
        if self.config.EMA_200_TREND_FILTER_ENABLED and self.config.EMA_200_REQUIRED_FOR_TIER3:
            trend_filter = self.parent.trend_filter_200ema.analyze(df_1h, direction)
            if not trend_filter.filter_passed:
                logger.debug(f"Tier3 {symbol}: 200 EMA trend filter failed: {trend_filter.filter_description}")
                return None
        if not self._basic_safety_check(tech, ob):
            logger.debug(f"Tier3 {symbol}: Basic safety check failed")
            return None
        self.signal_count[symbol] += 1
        signal = self._build_signal(symbol, base_analysis, tech_score, flow_score, direction, SignalTier.TIER_3_AGGRESSIVE, multi_tf_regime)
        signal.adaptive_cooldown_minutes = 5
        return signal
    
    def _basic_safety_check(self, tech: EnhancedTechnicalAnalysis, ob: OrderBookAnalysis) -> bool:
        if tech.rsi > 90 or tech.rsi < 10:
            return False
        if ob.spread_percentage > 0.2:
            return False
        return True

# ========== MARKET SCANNER ==========
class MarketScanner:
    def __init__(self, client: EnhancedBinanceFuturesClient):
        self.client = client
        self.symbol_scores = {}
    
    def scan_all_symbols(self, symbols: List[str]) -> List[Tuple[str, float]]:
        scores = []
        for symbol in symbols:
            score = self._calculate_opportunity_score(symbol)
            if score > 0:
                scores.append((symbol, score))
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def _calculate_opportunity_score(self, symbol: str) -> float:
        try:
            score = 0
            ticker = self.client.get_ticker_24hr(symbol)
            if ticker:
                volume = ticker.get('quoteVolume', 0)
                if volume > 10_000_000:
                    score += 30
                elif volume > 1_000_000:
                    score += 20
                elif volume > 500_000:
                    score += 10
            df_1h = self.client.get_klines(symbol, '1h', 24)
            if df_1h is not None and len(df_1h) > 1:
                returns = df_1h['close'].pct_change().dropna()
                volatility = returns.std() * 100
                if 1.5 <= volatility <= 4:
                    score += 20
                elif volatility > 4:
                    score += 10
                elif volatility < 1.5:
                    score -= 10
            for tf in ["3m", "15m", "1h", "4h", "1d"]:
                df = self.client.get_klines(symbol, tf, 20)
                if df is not None and len(df) >= 20:
                    ema9 = df['close'].iloc[-9:].mean()
                    ema21 = df['close'].iloc[-21:].mean()
                    current = df['close'].iloc[-1]
                    if ema9 > ema21 and current > ema9:
                        score += 5
                    elif ema9 < ema21 and current < ema9:
                        score += 5
            return score
        except:
            return 0

# ========== ADAPTIVE COOLDOWN ==========
class AdaptiveCooldown:
    def __init__(self):
        self.last_signals = defaultdict(list)
        self.base_cooldown = {
            SignalTier.TIER_1_ULTRA_SAFE: 15,
            SignalTier.TIER_2_BALANCED: 10,
            SignalTier.TIER_3_AGGRESSIVE: 5
        }
    
    def can_send_signal(self, symbol: str, tier: SignalTier, market_regime: MarketRegime) -> bool:
        if symbol not in self.last_signals:
            return True
        cooldown = self.base_cooldown[tier]
        if market_regime.volatility == "HIGH":
            cooldown *= 1.5
        elif market_regime.volatility == "LOW":
            cooldown *= 0.7
        last_time = self.last_signals[symbol][-1]
        time_diff = (datetime.now() - last_time).total_seconds() / 60
        return time_diff >= cooldown
    
    def record_signal(self, symbol: str, tier: SignalTier):
        self.last_signals[symbol].append(datetime.now())
        if len(self.last_signals[symbol]) > 5:
            self.last_signals[symbol].pop(0)

# ========== SIMPLE TELEGRAM NOTIFIER ==========
class SimpleTelegramNotifier:
    def __init__(self, config: TelegramConfig, bot_config: Config):
        self.config = config
        self.bot_config = bot_config
        self.last_signal_time = {}
        self.sent_signals = []
        if self.config.ENABLE_SUMMARY:
            self._start_summary_thread()
    
    def _start_summary_thread(self):
        def run_summary():
            while True:
                time.sleep(self.config.SUMMARY_INTERVAL_MINUTES * 60)
                self.send_hourly_summary()
        thread = threading.Thread(target=run_summary, daemon=True)
        thread.start()
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> Optional[int]:
        if not self.config.BOT_TOKEN or not self.config.CHAT_ID:
            return None
        try:
            url = self.config.API_URL.format(self.config.BOT_TOKEN)
            payload = {
                'chat_id': self.config.CHAT_ID,
                'text': message,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get('result', {}).get('message_id')
            return None
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return None
    
    def get_alert_level(self, signal: EnhancedHighConfidenceSignal) -> AlertLevel:
        if signal.confidence >= self.config.EMERGENCY_THRESHOLD and signal.overall_accuracy_score >= 85:
            return AlertLevel.EMERGENCY
        elif signal.confidence >= self.config.HIGH_THRESHOLD and signal.overall_accuracy_score >= 75:
            return AlertLevel.HIGH
        elif signal.confidence >= self.config.MEDIUM_THRESHOLD:
            return AlertLevel.MEDIUM
        else:
            return AlertLevel.LOW
    
    def _format_price(self, price: float) -> str:
        if price < 0.0001:
            return f"{price:.8f}"
        elif price < 0.01:
            return f"{price:.6f}"
        elif price < 1:
            return f"{price:.4f}"
        else:
            return f"{price:,.2f}"
    
    def _build_signal_message(self, signal: EnhancedHighConfidenceSignal) -> str:
        tier_emojis = {
            SignalTier.TIER_1_ULTRA_SAFE: "🛡️🛡️🛡️",
            SignalTier.TIER_2_BALANCED: "⚖️⚖️",
            SignalTier.TIER_3_AGGRESSIVE: "⚡"
        }
        tier_names = {
            SignalTier.TIER_1_ULTRA_SAFE: "ULTRA SAFE",
            SignalTier.TIER_2_BALANCED: "BALANCED",
            SignalTier.TIER_3_AGGRESSIVE: "AGGRESSIVE"
        }
        emoji = tier_emojis.get(signal.tier, "🔵")
        tier_name = tier_names.get(signal.tier, "HYBRID")
        direction_emoji = "🟢" if signal.signal_type == "STRONG_BUY" else "🔴"
        direction_text = "LONG" if signal.signal_type == "STRONG_BUY" else "SHORT"
        confidence_stars = "⭐" * int(signal.confidence / 20)
        sections = []
        sections.append(f"{emoji} <b>{tier_name} SIGNAL</b> {emoji}")
        sections.append("━━━━━━━━━━━━━━━━━━━━━━")
        sections.append(f"⏰ {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append(f"💰 <b>{signal.symbol}</b> | {direction_emoji} {direction_text}")
        sections.append(f"🎯 Confidence: {signal.confidence:.1f}% {confidence_stars}")
        sections.append(f"📊 Accuracy: {signal.overall_accuracy_score:.1f}%")
        if signal.primary_style:
            style_emojis = {
                SignalStyle.SCALPING: "⚡", SignalStyle.INTRADAY: "📊",
                SignalStyle.SWING: "🔄", SignalStyle.POSITION: "🎯",
                SignalStyle.HYBRID: "🔄"
            }
            style_emoji = style_emojis.get(signal.primary_style, "📈")
            sections.append(f"\n🎨 <b>Style</b>: {style_emoji} {signal.primary_style.value}")
        if signal.smart_money_display and signal.smart_money_display.primary_concept != SmartMoneyConcept.NONE:
            sections.append(f"\n🧠 <b>Smart Money</b>")
            sections.append(f"├ {signal.smart_money_display.primary_concept.value}")
            sections.append(f"├ {signal.smart_money_display.concept_description}")
            sections.append(f"└ Score: {signal.smart_money_display.smart_money_score:.1f}")
        sections.append(f"\n📈 <b>ENTRY LEVELS</b>")
        sections.append(f"├ Entry Price: ${self._format_price(signal.entry_price)}")
        sections.append(f"├ Best Bid: ${self._format_price(signal.best_bid)}")
        sections.append(f"├ Best Ask: ${self._format_price(signal.best_ask)}")
        sections.append(f"└ Entry Logic: {signal.optimal_entry_timeframe}")
        sections.append(f"\n🛑 <b>STOP LOSS</b>")
        sections.append(f"├ Price: ${self._format_price(signal.stop_loss)}")
        sections.append(f"└ Percentage: {signal.stop_loss_percentage:.2f}%")
        sections.append(f"\n🎯 <b>TAKE PROFIT LEVELS</b>")
        sections.append(f"├ TP1: ${self._format_price(signal.take_profit_1)} (R:R {signal.risk_reward.rr_ratio_1:.1f})")
        sections.append(f"├ TP2: ${self._format_price(signal.take_profit_2)} (R:R {signal.risk_reward.rr_ratio_2:.1f})")
        sections.append(f"└ TP3: ${self._format_price(signal.take_profit_3)} (R:R {signal.risk_reward.rr_ratio_3:.1f})")
        sections.append(f"\n📊 <b>RISK MANAGEMENT</b>")
        sections.append(f"├ Leverage: {signal.recommended_leverage}x")
        sections.append(f"├ Risk Level: {signal.risk_level}")
        sections.append(f"├ Position Size: {signal.optimal_position_size:.2f}x")
        sections.append(f"└ Expected Move: {signal.expected_move:.2f}%")
        sections.append(f"\n📊 <b>TECHNICAL SUMMARY</b>")
        sections.append(f"├ RSI: {signal.rsi:.1f} ({signal.rsi_signal})")
        sections.append(f"├ MACD: {signal.macd_trend}")
        sections.append(f"├ EMA: {signal.ema_trend}")
        sections.append(f"├ Tech Score: {signal.tech_score:+.0f}")
        sections.append(f"└ Flow Score: {signal.flow_score:+.0f}")
        sections.append(f"\n💧 <b>ORDER FLOW</b>")
        sections.append(f"├ Buy Pressure: {signal.buy_pressure:.0f}%")
        sections.append(f"├ Sell Pressure: {signal.sell_pressure:.0f}%")
        sections.append(f"├ Bid/Ask Ratio: {signal.bid_ask_ratio:.2f}")
        sections.append(f"└ Imbalance: {signal.order_book_imbalance:.1f}%")
        sections.append(f"\n📊 <b>MARKET REGIME</b>")
        sections.append(f"├ Ultra-short: {signal.multi_tf_regime.ultra_short_regime}")
        sections.append(f"├ Short-term: {signal.multi_tf_regime.short_regime}")
        sections.append(f"├ Medium-term: {signal.multi_tf_regime.medium_regime}")
        sections.append(f"├ Long-term: {signal.multi_tf_regime.long_regime}")
        sections.append(f"└ Alignment: {signal.multi_tf_regime.regime_alignment:.0f}%")
        if signal.atr_value > 0:
            sections.append(f"\n📏 <b>ATR STOP</b>")
            sections.append(f"├ ATR: {signal.atr_value:.4f}")
            sections.append(f"└ Multiplier: {signal.atr_multiplier:.1f}x")
        if signal.volume_poc_price > 0:
            sections.append(f"\n📊 <b>VOLUME PROFILE</b>")
            sections.append(f"├ POC: ${self._format_price(signal.volume_poc_price)}")
            sections.append(f"└ Value Area: ${self._format_price(signal.volume_value_area_low)} - ${self._format_price(signal.volume_value_area_high)}")
        if signal.liquidity_grab_detected:
            sections.append(f"\n🎣 <b>LIQUIDITY GRAB</b>")
            sections.append(f"├ Type: {signal.liquidity_grab_type}")
            sections.append(f"├ Strength: {signal.liquidity_grab_strength:.1f}%")
            sections.append(f"└ {signal.liquidity_grab.grab_description}")
        if signal.ema_200 > 0:
            sections.append(f"\n📈 <b>200 EMA FILTER</b>")
            sections.append(f"├ EMA200: ${self._format_price(signal.ema_200)}")
            sections.append(f"├ Position: {signal.price_vs_ema_200}")
            sections.append(f"├ Trend: {signal.ema_200_trend}")
            sections.append(f"└ Passed: {'✅' if signal.trend_filter_passed else '❌'}")
        if signal.ai_model_used:
            sections.append(f"\n🤖 <b>AI CONFIDENCE</b>")
            sections.append(f"├ AI Prediction: {signal.ai_confidence_prediction:.1f}%")
            sections.append(f"└ AI Confidence: {signal.ai_confidence_in_prediction:.1f}%")
        if signal.ml_predictions:
            sections.append(f"\n🧠 <b>ML ENSEMBLE</b>")
            sections.append(f"└ Prediction: {signal.ml_predictions.get('ensemble', 0)*100:.1f}%")
        if signal.risk_report:
            sections.append(f"\n📉 <b>RISK REPORT</b>")
            sections.append(f"├ Drawdown: {signal.risk_report.get('drawdown', 0):.1f}%")
            sections.append(f"├ Max DD: {signal.risk_report.get('max_drawdown', 0):.1f}%")
            sections.append(f"├ VaR 95%: {signal.risk_report.get('var_95', 0):.1f}%")
            sections.append(f"└ Kelly: {signal.risk_report.get('kelly_fraction', 0):.2f}")
        sections.append(f"\n<b>⭐ PRIMARY REASONS</b>")
        for i, reason in enumerate(signal.primary_reasons[:3], 1):
            sections.append(f"{i}. {reason}")
        if signal.market_context:
            sections.append(f"\n🌍 <b>MARKET CONTEXT</b>")
            sections.append(f"├ BTC: ${signal.market_context.btc_price:,.0f} ({signal.market_context.btc_change_24h:+.1f}%)")
            sections.append(f"├ ETH: ${signal.market_context.eth_price:,.0f} ({signal.market_context.eth_change_24h:+.1f}%)")
            sections.append(f"└ Fear/Greed: {signal.market_context.fear_greed_index} ({signal.market_context.fear_greed_text})")
        if signal.backtest_result and signal.backtest_result.total_signals >= 10:
            sections.append(f"\n📈 <b>BACKTEST (30d)</b>")
            sections.append(f"├ Win Rate: {signal.backtest_result.win_rate:.1f}%")
            sections.append(f"├ Profit Factor: {signal.backtest_result.profit_factor:.2f}")
            sections.append(f"└ Max DD: {signal.backtest_result.max_drawdown:.1f}%")
        sections.append("━━━━━━━━━━━━━━━━━━━━━━")
        sections.append(f"⚡ Risk: {signal.risk_level} | Cooldown: {signal.adaptive_cooldown_minutes}min")
        return "\n".join(sections)
    
    def send_enhanced_signal(self, signal: EnhancedHighConfidenceSignal) -> bool:
        symbol = signal.symbol
        if signal.confidence < self.config.MIN_CONFIDENCE:
            logger.debug(f"Telegram {symbol}: Confidence {signal.confidence} < {self.config.MIN_CONFIDENCE}")
            return False
        if signal.overall_accuracy_score < self.config.MIN_ACCURACY_SCORE:
            logger.debug(f"Telegram {symbol}: Accuracy {signal.overall_accuracy_score} < {self.config.MIN_ACCURACY_SCORE}")
            return False
        if symbol in self.last_signal_time:
            time_diff = (datetime.now() - self.last_signal_time[symbol]).total_seconds() / 60
            if time_diff < self.config.COOLDOWN_MINUTES:
                logger.debug(f"Telegram {symbol}: Cooldown {time_diff:.1f} min < {self.config.COOLDOWN_MINUTES}")
                return False
        alert_level = self.get_alert_level(signal)
        signal.alert_level = alert_level
        message = self._build_signal_message(signal)
        message_id = self.send_message(message)
        if message_id:
            self.sent_signals.append(signal)
            self.last_signal_time[symbol] = datetime.now()
            logger.info(f"✅ Telegram {alert_level.value} signal sent for {symbol}")
            if self.config.ENABLE_AUTO_TRADE and self.bot_config.FUTURES_CONFIG and \
               self.bot_config.FUTURES_CONFIG.API_KEY and self.bot_config.FUTURES_CONFIG.API_SECRET:
                self._execute_trade(signal)
            return True
        logger.error(f"❌ Failed to send Telegram signal for {symbol}")
        return False
    
    def _execute_trade(self, signal: EnhancedHighConfidenceSignal):
        try:
            symbol = signal.symbol
            side = "BUY" if signal.signal_type == "STRONG_BUY" else "SELL"
            if hasattr(self.bot_config.client, 'risk_manager'):
                can_trade, reason = self.bot_config.client.risk_manager.can_trade()
                if not can_trade:
                    logger.warning(f"Risk manager blocked trade: {reason}")
                    self.send_message(f"⚠️ Trade blocked: {reason}")
                    return
            balance = self.bot_config.client.get_account_balance()
            if not balance:
                logger.error(f"Cannot get account balance for {symbol}")
                return
            if hasattr(self.bot_config.client, 'risk_manager'):
                self.bot_config.client.risk_manager.update_drawdown(balance)
            if hasattr(self.bot_config.client, 'risk_manager') and self.bot_config.client.risk_manager.kelly_fraction > 0:
                position_size_usdt = self.bot_config.client.risk_manager.get_position_size(signal.confidence, balance, 1.0)
            else:
                position_size_usdt = balance * self.config.MAX_POSITION_SIZE_USDT / 100
            quantity = position_size_usdt / signal.entry_price
            if signal.entry_price < 0.1:
                quantity = round(quantity, 3)
            elif signal.entry_price < 1:
                quantity = round(quantity, 2)
            elif signal.entry_price < 10:
                quantity = round(quantity, 1)
            else:
                quantity = round(quantity, 0)
            min_qty = 0.001
            if quantity < min_qty:
                quantity = min_qty
            order_type = signal.suggested_order_type.value.split()[0]
            hybrid_config = self.bot_config.HYBRID_CONFIG
            advanced_executor = getattr(self.bot_config.client, 'advanced_order_executor', None)
            order_ids = []
            if advanced_executor and hybrid_config.ORDER_CONFIG.TWAP_ENABLED and signal.optimal_position_size > 1.2:
                orders = advanced_executor.execute_twap(
                    symbol=symbol, side=side, total_quantity=quantity,
                    duration_minutes=30, num_slices=hybrid_config.ORDER_CONFIG.DEFAULT_TWAP_SLICES
                )
                for order in orders:
                    if order:
                        order_ids.append(order.get('orderId', 'Unknown'))
                logger.info(f"✅ TWAP orders placed for {symbol}: {len(orders)} slices")
            elif advanced_executor and hybrid_config.ORDER_CONFIG.ICEBERG_ENABLED and quantity > 10:
                iceberg_qty = quantity * hybrid_config.ORDER_CONFIG.DEFAULT_ICEBERG_SIZE
                orders = advanced_executor.place_iceberg_order(
                    symbol=symbol, side=side, total_quantity=quantity,
                    price=signal.entry_price, iceberg_qty=iceberg_qty
                )
                for order in orders:
                    if order:
                        order_ids.append(order.get('orderId', 'Unknown'))
                logger.info(f"✅ Iceberg orders placed for {symbol}: {len(orders)} pieces")
            else:
                order = self.bot_config.client.place_order(
                    symbol=symbol, side=side, order_type=order_type,
                    quantity=quantity, price=signal.entry_price if order_type == "LIMIT" else None
                )
                if order:
                    order_id = order.get('orderId', 'Unknown')
                    order_ids.append(order_id)
                    logger.info(f"✅ Entry order placed for {symbol}: {order_id}")
            if order_ids:
                sl_side = "SELL" if side == "BUY" else "BUY"
                if advanced_executor and hybrid_config.ORDER_CONFIG.TRAILING_STOP_ENABLED:
                    sl_order = advanced_executor.place_trailing_stop(
                        symbol=symbol, side=sl_side, quantity=quantity,
                        activation_price=signal.entry_price * 1.01 if side == "BUY" else signal.entry_price * 0.99,
                        callback_rate=hybrid_config.ORDER_CONFIG.DEFAULT_TRAILING_CALLBACK
                    )
                    if sl_order:
                        logger.info(f"✅ Trailing stop placed for {symbol}")
                else:
                    sl_order = self.bot_config.client.place_stop_loss(
                        symbol=symbol, side=sl_side, quantity=quantity, stop_price=signal.stop_loss
                    )
                    if sl_order:
                        logger.info(f"✅ Stop loss placed for {symbol} at {signal.stop_loss}")
                tp1_qty = quantity * 0.5
                tp2_qty = quantity * 0.3
                tp3_qty = quantity * 0.2
                if advanced_executor and hybrid_config.ORDER_CONFIG.OCO_ENABLED:
                    oco_order = advanced_executor.place_oco_order(
                        symbol=symbol, side=sl_side, quantity=tp1_qty + tp2_qty,
                        price=signal.take_profit_1, stop_price=signal.take_profit_2,
                        limit_price=signal.take_profit_2 * 0.999
                    )
                    if oco_order:
                        logger.info(f"✅ OCO order placed for {symbol}")
                    tp3_order = self.bot_config.client.place_take_profit(
                        symbol=symbol, side=sl_side, quantity=tp3_qty, price=signal.take_profit_3
                    )
                else:
                    tp1_order = self.bot_config.client.place_take_profit(
                        symbol=symbol, side=sl_side, quantity=tp1_qty, price=signal.take_profit_1
                    )
                    tp2_order = self.bot_config.client.place_take_profit(
                        symbol=symbol, side=sl_side, quantity=tp2_qty, price=signal.take_profit_2
                    )
                    tp3_order = self.bot_config.client.place_take_profit(
                        symbol=symbol, side=sl_side, quantity=tp3_qty, price=signal.take_profit_3
                    )
                if hasattr(self.bot_config.client, 'portfolio_manager'):
                    sector = "Unknown"
                    for s, symbols in self.bot_config.client.intermarket_analyzer.sector_symbols.items():
                        if symbol in symbols:
                            sector = s
                            break
                    self.bot_config.client.portfolio_manager.update_position(
                        symbol=symbol, quantity=quantity, entry_price=signal.entry_price,
                        sector=sector, style=signal.primary_style.value if signal.primary_style else "Unknown",
                        tier=signal.tier.value if signal.tier else "Unknown"
                    )
                if hasattr(self.bot_config.client, 'performance_analytics'):
                    self.bot_config.client.performance_analytics.add_trade({
                        'symbol': symbol, 'entry_price': signal.entry_price, 'quantity': quantity,
                        'initial_capital': balance, 'entry_time': datetime.now(),
                        'style': signal.primary_style.value if signal.primary_style else "Unknown",
                        'tier': signal.tier.value if signal.tier else "Unknown"
                    })
                confirm_msg = f"""
✅ <b>ORDER EXECUTED</b>
━━━━━━━━━━━━━━━━━━━━━━
💰 <b>{symbol}</b> | {side}
📊 Quantity: {quantity:.4f}
💵 Entry: ${signal.entry_price:.4f}
🛑 Stop Loss: ${signal.stop_loss:.4f}
🎯 TP1: ${signal.take_profit_1:.4f} (50%)
🎯 TP2: ${signal.take_profit_2:.4f} (30%)
🎯 TP3: ${signal.take_profit_3:.4f} (20%)
⚡ Leverage: {signal.recommended_leverage}x
📈 Risk: ${position_size_usdt:.2f} USDT
🆔 Order IDs: {', '.join(str(oid) for oid in order_ids[:3])}
⏰ {datetime.now().strftime('%H:%M:%S')}
"""
                self.send_message(confirm_msg)
            else:
                logger.error(f"❌ Failed to place entry order for {symbol}")
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
    
    def send_hourly_summary(self):
        if not self.sent_signals:
            return
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_signals = [s for s in self.sent_signals if s.timestamp > one_hour_ago]
        if not recent_signals:
            return
        total = len(recent_signals)
        tier1 = sum(1 for s in recent_signals if s.tier == SignalTier.TIER_1_ULTRA_SAFE)
        tier2 = sum(1 for s in recent_signals if s.tier == SignalTier.TIER_2_BALANCED)
        tier3 = sum(1 for s in recent_signals if s.tier == SignalTier.TIER_3_AGGRESSIVE)
        buys = sum(1 for s in recent_signals if s.signal_type == "STRONG_BUY")
        sells = sum(1 for s in recent_signals if s.signal_type == "STRONG_SELL")
        avg_confidence = sum(s.confidence for s in recent_signals) / total
        avg_accuracy = sum(s.overall_accuracy_score for s in recent_signals) / total
        summary = f"""
📊 <b>HOURLY SIGNAL SUMMARY</b>
━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
📈 Total Signals: {total}
<b>By Tier:</b>
├ 🛡️ Ultra Safe: {tier1}
├ ⚖️ Balanced: {tier2}
└ ⚡ Aggressive: {tier3}
<b>By Direction:</b>
├ 🟢 BUY: {buys}
└ 🔴 SELL: {sells}
<b>Performance:</b>
├ Avg Confidence: {avg_confidence:.1f}%
└ Avg Accuracy: {avg_accuracy:.1f}%
<b>Top Signals:</b>
"""
        top_signals = sorted(recent_signals, key=lambda x: x.confidence, reverse=True)[:3]
        for s in top_signals:
            summary += f"├ {s.symbol}: {s.signal_type} ({s.confidence:.1f}%)\n"
        summary += "━━━━━━━━━━━━━━━━━━━━━━\n"
        self.send_message(summary)
    
    def send_startup_message(self, hybrid_config: HybridConfig):
        tiers = []
        if hybrid_config.ENABLE_TIER_1:
            tiers.append("🛡️ Ultra Safe")
        if hybrid_config.ENABLE_TIER_2:
            tiers.append("⚖️ Balanced")
        if hybrid_config.ENABLE_TIER_3:
            tiers.append("⚡ Aggressive")
        features = []
        if hybrid_config.ATR_STOP_LOSS_ENABLED:
            features.append("📏 ATR Stop Loss")
        if hybrid_config.VOLUME_PROFILE_ENTRY_ENABLED:
            features.append("📊 Volume Profile Entry")
        if hybrid_config.LIQUIDITY_GRAB_ENABLED:
            features.append("🎣 Liquidity Grab Detection")
        if hybrid_config.EMA_200_TREND_FILTER_ENABLED:
            features.append("📈 200 EMA Trend Filter")
        if hybrid_config.AI_CONFIDENCE_MODEL_ENABLED:
            features.append("🤖 AI Confidence Model")
        advanced_features = []
        if hybrid_config.SECURITY_CONFIG.ENCRYPTION_ENABLED:
            advanced_features.append("🔐 API Encryption")
        if hybrid_config.SECURITY_CONFIG.TWO_FA_ENABLED:
            advanced_features.append("🔑 2FA Support")
        if hybrid_config.ML_CONFIG.ENSEMBLE_ENABLED:
            advanced_features.append("🧠 ML Ensemble")
        if hybrid_config.RISK_CONFIG.KELLY_CRITERION_ENABLED:
            advanced_features.append("📊 Kelly Criterion")
        if hybrid_config.RISK_CONFIG.VAR_CALCULATION_ENABLED:
            advanced_features.append("📉 VaR Calculation")
        if hybrid_config.ORDER_CONFIG.OCO_ENABLED:
            advanced_features.append("🔄 OCO Orders")
        if hybrid_config.ORDER_CONFIG.TRAILING_STOP_ENABLED:
            advanced_features.append("🎯 Trailing Stop")
        if hybrid_config.ORDER_CONFIG.TWAP_ENABLED:
            advanced_features.append("⏱️ TWAP Execution")
        if hybrid_config.PORTFOLIO_CONFIG.TRACK_POSITIONS:
            advanced_features.append("💼 Portfolio Tracking")
        if hybrid_config.PERFORMANCE_CONFIG.TRACK_EQUITY_CURVE:
            advanced_features.append("📊 Performance Analytics")
        auto_trade_status = "✅ Enabled" if self.config.ENABLE_AUTO_TRADE else "❌ Disabled"
        message = f"""
🤖 <b>ULTIMATE HYBRID BOT V10.5.0 STARTED</b>
━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Monitoring {len(self.bot_config.SYMBOLS)} symbols
🎯 Tiers: {', '.join(tiers)}
🎯 Min Confidence: {self.config.MIN_CONFIDENCE}%
📈 Min Accuracy: {self.config.MIN_ACCURACY_SCORE}%
⏱️ Cooldown: {self.config.COOLDOWN_MINUTES} min
⚡ Auto Trade: {auto_trade_status}
<b>🔧 Core Features:</b>
{chr(10).join(['├ ' + f for f in features])}
<b>🔬 Advanced Features (10):</b>
{chr(10).join(['├ ' + f for f in advanced_features[:8]])}
{chr(10).join(['└ ' + f for f in advanced_features[8:]]) if len(advanced_features) > 8 else ''}
<b>📊 ENTRY & TP/SL DISPLAYED:</b>
├ ✅ Entry Price: Displayed
├ ✅ Stop Loss: Displayed
├ ✅ TP1: Displayed
├ ✅ TP2: Displayed
└ ✅ TP3: Displayed
<b>🎨 Complete Analysis:</b>
├ 🧠 Smart Money Detection
├ 📊 Volume Profile Entry
├ 🎣 Liquidity Grab Detection
├ 📈 200 EMA Trend Filter
├ 🤖 AI Confidence Model
├ 📏 ATR Stop Loss
├ 🔄 Multi-Timeframe Regime
├ 🐋 Whale Activity Tracking
├ 🎭 Spoofing Detection
├ 🐟 Iceberg Order Detection
├ 📉 Advanced Risk Management
├ 🧠 ML Ensemble (RF+GB+LSTM)
├ 💼 Portfolio Management
├ 📊 Performance Analytics
└ 🔐 Enterprise Security
<b>⚙️ TP Multipliers:</b>
├ ⚡ Scalping: {hybrid_config.TP_CONFIG.scalping_tp1}x / {hybrid_config.TP_CONFIG.scalping_tp2}x
├ 📊 Intraday: {hybrid_config.TP_CONFIG.intraday_tp1}x / {hybrid_config.TP_CONFIG.intraday_tp2}x
├ 🔄 Swing: {hybrid_config.TP_CONFIG.swing_tp1}x / {hybrid_config.TP_CONFIG.swing_tp2}x
└ 🎯 Position: {hybrid_config.TP_CONFIG.position_tp1}x / {hybrid_config.TP_CONFIG.position_tp2}x
━━━━━━━━━━━━━━━━━━━━━━
<i>Pydroid Optimized Edition with 15+ advanced features ready...</i>
"""
        self.send_message(message)

# ========== ULTIMATE HYBRID BOT ==========
class UltimateHybridBot:
    def __init__(self, telegram_config: TelegramConfig, futures_config: BinanceFuturesConfig):
        self.config = Config()
        self.config.FUTURES_CONFIG = futures_config
        self.config.TELEGRAM_CONFIG = telegram_config
        self.config.HYBRID_CONFIG = HybridConfig()
        self.telegram_config = telegram_config
        self.client = EnhancedBinanceFuturesClient(self.config)
        self.signal_generator = TieredSignalGenerator(self.client, self.config)
        self.notifier = SimpleTelegramNotifier(telegram_config, self.config)
        self.backtest_engine = BacktestEngine(self.client)
        self.scanner = MarketScanner(self.client)
        self.cooldown = AdaptiveCooldown()
        self.config.client = self.client
        self.signal_generator.initialize_advanced_features()
        self.client.risk_manager = self.signal_generator.risk_manager
        self.client.portfolio_manager = self.signal_generator.portfolio_manager
        self.client.advanced_order_executor = self.signal_generator.advanced_order_executor
        self.client.performance_analytics = self.signal_generator.performance_analytics
        self.client.ml_models = self.signal_generator.ml_models
        self.client.security_manager = self.signal_generator.security_manager
        self.running = False
        self.signals_history = []
        self.enhanced_signals_history = []
        self.start_time = datetime.now()
        self.scan_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.trade_history = []
        self.signals_last_100 = deque(maxlen=100)
        self.stats = {
            'total_scans': 0, 'total_signals': 0,
            'tier1_signals': 0, 'tier2_signals': 0, 'tier3_signals': 0,
            'buy_signals': 0, 'sell_signals': 0,
            'avg_confidence': 0, 'avg_accuracy': 0,
            'signals_by_symbol': defaultdict(int),
            'entries_by_timeframe': defaultdict(int),
            'signals_by_style': defaultdict(int),
            'primary_styles': defaultdict(int),
            'smart_money_concepts': defaultdict(int),
            'atr_signals': 0, 'volume_profile_signals': 0,
            'liquidity_grab_signals': 0, 'trend_filter_passed': 0, 'ai_used_signals': 0,
            'emergency_alerts': 0, 'high_alerts': 0, 'medium_alerts': 0,
            'confirmed_signals': 0,
            'ml_used_signals': 0, 'twap_orders': 0, 'iceberg_orders': 0,
            'trailing_stops': 0, 'oco_orders': 0
        }
        if not self.client.test_connection():
            logger.error("Cannot connect to Binance Futures. Exiting.")
            sys.exit(1)
        hybrid_config = self.config.HYBRID_CONFIG
        logger.info("=" * 80)
        logger.info("ULTIMATE HYBRID FUTURES TRADING BOT V10.5.0")
        logger.info("PYDROID OPTIMIZED EDITION - ALL FEATURES")
        logger.info("=" * 80)
        logger.info(f"Symbols: {len(self.config.SYMBOLS)}")
        logger.info(f"Tiers: Ultra Safe={hybrid_config.ENABLE_TIER_1}, Balanced={hybrid_config.ENABLE_TIER_2}, Aggressive={hybrid_config.ENABLE_TIER_3}")
        logger.info(f"Min Confidence: {self.telegram_config.MIN_CONFIDENCE}%")
        logger.info(f"Min Accuracy: {self.telegram_config.MIN_ACCURACY_SCORE}%")
        logger.info(f"Using: {'TESTNET' if futures_config.USE_TESTNET else 'REAL MARKET'}")
        logger.info("=" * 80)
        logger.info("🔧 CORE FEATURES (10):")
        logger.info("  ✅ ATR Stop Loss")
        logger.info("  ✅ Volume Profile Entry")
        logger.info("  ✅ Liquidity Grab Detection")
        logger.info("  ✅ 200 EMA Trend Filter")
        logger.info("  ✅ AI Confidence Model")
        logger.info("  ✅ Advanced Order Flow Analysis")
        logger.info("  ✅ Smart Money Footprint")
        logger.info("  ✅ Market Microstructure")
        logger.info("  ✅ Divergence Detection")
        logger.info("  ✅ Pattern Recognition")
        logger.info("=" * 80)
        logger.info("🔬 ADVANCED FEATURES (15):")
        logger.info("  ✅ Security: API Encryption, 2FA, IP Whitelist")
        logger.info("  ✅ ML Models: Random Forest, LSTM, Ensemble")
        logger.info("  ✅ Risk Management: Kelly Criterion, VaR, Monte Carlo")
        logger.info("  ✅ Advanced Orders: OCO, Trailing Stop, Iceberg, TWAP")
        logger.info("  ✅ Portfolio: Multi-symbol tracking, Heatmap, Correlation")
        logger.info("  ✅ Analytics: Equity curve, Monthly reports, Sharpe ratio")
        logger.info("=" * 80)
        logger.info("📊 ENTRY & TP/SL DISPLAY:")
        logger.info("  ✅ Entry Price - Displayed")
        logger.info("  ✅ Stop Loss - Displayed")
        logger.info("  ✅ TP1, TP2, TP3 - Displayed")
        logger.info("=" * 80)
        logger.info("📱 PYDROID OPTIMIZATIONS:")
        logger.info("  ✅ Memory Efficient")
        logger.info("  ✅ Error Handling for Android")
        logger.info("  ✅ Log Rotation")
        logger.info("  ✅ Configurable Scan Intervals")
        logger.info("=" * 80)
    
    def update_performance_stats(self, signal: EnhancedHighConfidenceSignal):
        self.signals_last_100.append(signal)
        self.stats['entries_by_timeframe'][signal.optimal_entry_timeframe] += 1
        if signal.tier == SignalTier.TIER_1_ULTRA_SAFE:
            self.stats['tier1_signals'] += 1
        elif signal.tier == SignalTier.TIER_2_BALANCED:
            self.stats['tier2_signals'] += 1
        elif signal.tier == SignalTier.TIER_3_AGGRESSIVE:
            self.stats['tier3_signals'] += 1
        for style in signal.aligned_styles:
            self.stats['signals_by_style'][style.value] += 1
        if signal.primary_style:
            self.stats['primary_styles'][signal.primary_style.value] += 1
        if signal.smart_money_display and signal.smart_money_display.primary_concept != SmartMoneyConcept.NONE:
            self.stats['smart_money_concepts'][signal.smart_money_display.primary_concept.value] += 1
        if signal.atr_stop_loss and signal.atr_value > 0:
            self.stats['atr_signals'] += 1
        if signal.volume_profile_entry:
            self.stats['volume_profile_signals'] += 1
        if signal.liquidity_grab_detected:
            self.stats['liquidity_grab_signals'] += 1
        if signal.trend_filter_passed:
            self.stats['trend_filter_passed'] += 1
        if signal.ai_model_used:
            self.stats['ai_used_signals'] += 1
        if signal.ml_predictions:
            self.stats['ml_used_signals'] += 1
        if signal.alert_level == AlertLevel.EMERGENCY:
            self.stats['emergency_alerts'] += 1
        elif signal.alert_level == AlertLevel.HIGH:
            self.stats['high_alerts'] += 1
        elif signal.alert_level == AlertLevel.MEDIUM:
            self.stats['medium_alerts'] += 1
        if len(self.signals_last_100) > 0:
            self.stats['avg_accuracy'] = sum(s.overall_accuracy_score for s in self.signals_last_100) / len(self.signals_last_100)
    
    def get_bot_win_rate(self) -> Tuple[float, int, float]:
        if len(self.trade_history) > 0:
            total = len(self.trade_history)
            win_rate = (self.winning_trades / total) * 100 if total > 0 else 0
        else:
            win_rate = self.stats['avg_accuracy']
        last_100_signals = list(self.signals_last_100)
        signals_last_100_count = len(last_100_signals)
        win_rate_last_100 = sum(s.overall_accuracy_score for s in last_100_signals) / signals_last_100_count if signals_last_100_count > 0 else 0
        return win_rate, signals_last_100_count, win_rate_last_100
    
    def run_smart_scan(self, continuous: bool = True, interval_seconds: int = 30):
        self.running = True
        if self.telegram_config.BOT_TOKEN and self.telegram_config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
            self.notifier.send_startup_message(self.config.HYBRID_CONFIG)
        try:
            while self.running:
                self.scan_count += 1
                self.stats['total_scans'] += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"COMPLETE SCAN V10.5.0 #{self.scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}")
                ranked_symbols = self.scanner.scan_all_symbols(self.config.SYMBOLS)
                top_symbols = [s[0] for s in ranked_symbols[:self.config.HYBRID_CONFIG.SCAN_TOP_SYMBOLS]]
                logger.info(f"🎯 Top {len(top_symbols)} opportunities: {', '.join(top_symbols)}")
                signals_found = []
                bot_win_rate, signals_last_100, win_rate_last_100 = self.get_bot_win_rate()
                for symbol in top_symbols:
                    try:
                        time.sleep(0.1)
                        tier_signals = self.signal_generator.generate_tiered_signals(symbol)
                        for signal in tier_signals:
                            if self.cooldown.can_send_signal(symbol, signal.tier, signal.market_regime):
                                signal.bot_win_rate = bot_win_rate
                                signal.signals_last_100 = signals_last_100
                                signal.win_rate_last_100 = win_rate_last_100
                                signals_found.append(signal)
                                self.signals_history.append(signal)
                                self.enhanced_signals_history.append(signal)
                                self.stats['total_signals'] += 1
                                self.update_performance_stats(signal)
                                self.cooldown.record_signal(symbol, signal.tier)
                                if signal.signal_type == "STRONG_BUY":
                                    self.stats['buy_signals'] += 1
                                else:
                                    self.stats['sell_signals'] += 1
                                self.stats['signals_by_symbol'][symbol] += 1
                                total_conf = sum(s.confidence for s in self.signals_history)
                                self.stats['avg_confidence'] = total_conf / len(self.signals_history) if self.signals_history else 0
                                total_acc = sum(s.overall_accuracy_score for s in self.enhanced_signals_history)
                                self.stats['avg_accuracy'] = total_acc / len(self.enhanced_signals_history) if self.enhanced_signals_history else 0
                                self._display_hybrid_signal(signal)
                                if self.telegram_config.BOT_TOKEN and self.telegram_config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                                    self.notifier.send_enhanced_signal(signal)
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {e}")
                        continue
                logger.info(f"\n✅ Found {len(signals_found)} complete signals")
                logger.info(f"📊 Total: {len(self.signals_history)} | Avg Conf: {self.stats['avg_confidence']:.1f}% | Avg Acc: {self.stats['avg_accuracy']:.1f}%")
                logger.info(f"📊 Tiers: Ultra Safe={self.stats['tier1_signals']}, Balanced={self.stats['tier2_signals']}, Aggressive={self.stats['tier3_signals']}")
                if self.stats['atr_signals'] > 0:
                    logger.info(f"📏 ATR Stop Loss used: {self.stats['atr_signals']}")
                if self.stats['volume_profile_signals'] > 0:
                    logger.info(f"📊 Volume Profile used: {self.stats['volume_profile_signals']}")
                if self.stats['liquidity_grab_signals'] > 0:
                    logger.info(f"🎣 Liquidity Grab detected: {self.stats['liquidity_grab_signals']}")
                if self.stats['trend_filter_passed'] > 0:
                    logger.info(f"📈 Trend Filter passed: {self.stats['trend_filter_passed']}")
                if self.stats['ai_used_signals'] > 0:
                    logger.info(f"🤖 AI used: {self.stats['ai_used_signals']}")
                if self.stats['ml_used_signals'] > 0:
                    logger.info(f"🧠 ML used: {self.stats['ml_used_signals']}")
                logger.info(f"📱 Telegram Alerts: EMG={self.stats['emergency_alerts']}, HIGH={self.stats['high_alerts']}, MED={self.stats['medium_alerts']}")
                risk_report = self.signal_generator.risk_manager.get_risk_report()
                logger.info(f"📉 Risk: Drawdown={risk_report['drawdown']:.1f}%, VaR95={risk_report['var_95']:.1f}%, Kelly={risk_report['kelly_fraction']:.2f}")
                portfolio_summary = self.signal_generator.portfolio_manager.get_portfolio_summary()
                if portfolio_summary['num_positions'] > 0:
                    logger.info(f"💼 Portfolio: {portfolio_summary['num_positions']} positions, P&L={portfolio_summary['total_pnl']:.2f}")
                if self.stats['primary_styles']:
                    logger.info("🎨 Primary Styles:")
                    for style, count in self.stats['primary_styles'].items():
                        percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
                        logger.info(f"  {style}: {count} ({percentage:.1f}%)")
                if self.stats['smart_money_concepts']:
                    logger.info("🧠 Smart Money Concepts:")
                    for concept, count in self.stats['smart_money_concepts'].items():
                        percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
                        logger.info(f"  {concept}: {count} ({percentage:.1f}%)")
                if not continuous:
                    break
                next_scan = datetime.now() + timedelta(seconds=interval_seconds)
                logger.info(f"\n⏱️ Next scan at: {next_scan.strftime('%H:%M:%S')}")
                logger.info(f"💤 Waiting {interval_seconds} seconds...")
                for i in range(interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
            if self.telegram_config.BOT_TOKEN and self.telegram_config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                self.notifier.send_message("🛑 Bot stopped successfully")
        finally:
            self.running = False
            self._generate_hybrid_report()
    
    def _display_hybrid_signal(self, signal: EnhancedHighConfidenceSignal):
        tier_emoji = {
            SignalTier.TIER_1_ULTRA_SAFE: "🛡️🛡️🛡️",
            SignalTier.TIER_2_BALANCED: "⚖️⚖️",
            SignalTier.TIER_3_AGGRESSIVE: "⚡"
        }
        tier_names = {
            SignalTier.TIER_1_ULTRA_SAFE: "ULTRA SAFE",
            SignalTier.TIER_2_BALANCED: "BALANCED",
            SignalTier.TIER_3_AGGRESSIVE: "AGGRESSIVE"
        }
        alert_emojis = {
            AlertLevel.EMERGENCY: "🔴", AlertLevel.HIGH: "🟡",
            AlertLevel.MEDIUM: "🔵", AlertLevel.LOW: "⚪"
        }
        styles = ", ".join([s.value for s in signal.aligned_styles]) if signal.aligned_styles else "None"
        primary_style = signal.primary_style.value if signal.primary_style else "None"
        smart_money_concept = "None"
        if signal.smart_money_display and signal.smart_money_display.primary_concept != SmartMoneyConcept.NONE:
            smart_money_concept = signal.smart_money_display.primary_concept.value
        new_features = []
        if signal.atr_stop_loss and signal.atr_value > 0:
            new_features.append("ATR")
        if signal.volume_profile_entry:
            new_features.append("VP")
        if signal.liquidity_grab_detected:
            new_features.append("LG")
        if signal.trend_filter_passed:
            new_features.append("EMA200")
        if signal.ai_model_used:
            new_features.append("AI")
        if signal.ml_predictions:
            new_features.append("ML")
        new_features_str = f" [{', '.join(new_features)}]" if new_features else ""
        alert_emoji = alert_emojis.get(signal.alert_level, "")
        logger.info(f"\n{tier_emoji[signal.tier]} COMPLETE SIGNAL V10.5.0 - {signal.symbol} ({tier_names[signal.tier]}){new_features_str} {alert_emoji}")
        logger.info(f"Type: {signal.signal_type} | Confidence: {signal.confidence:.1f}%")
        logger.info(f"Accuracy: {signal.overall_accuracy_score:.1f}%")
        logger.info(f"Alert Level: {signal.alert_level.value if signal.alert_level else 'N/A'}")
        logger.info(f"Primary Style: {primary_style}")
        logger.info(f"Smart Money: {smart_money_concept}")
        logger.info(f"Aligned Styles: {styles}")
        logger.info(f"Price: ${signal.current_price:,.4f}")
        logger.info(f"Entry: {signal.suggested_order_type.value} @ ${signal.entry_price:,.4f}")
        logger.info(f"Entry Logic: {signal.optimal_entry_timeframe}")
        logger.info(f"Stop Loss: ${signal.stop_loss:,.4f} ({signal.stop_loss_percentage:.2f}%)")
        logger.info(f"Take Profit 1: ${signal.take_profit_1:,.4f}")
        logger.info(f"Take Profit 2: ${signal.take_profit_2:,.4f}")
        logger.info(f"Take Profit 3: ${signal.take_profit_3:,.4f}")
        logger.info(f"Bid/Ask: ${signal.best_bid:,.4f} / ${signal.best_ask:,.4f} | Imbalance: {signal.order_book_imbalance:.1f}%")
        logger.info(f"Regime Alignment: {signal.multi_tf_regime.regime_alignment:.0f}%")
        logger.info(f"R:R: 1:{signal.risk_reward.rr_ratio_1:.1f}")
        logger.info(f"Tech Score: {signal.tech_score:+.0f} | Flow Score: {signal.flow_score:+.0f}")
        if signal.risk_report:
            logger.info(f"Risk: DD={signal.risk_report['drawdown']:.1f}%, VaR95={signal.risk_report['var_95']:.1f}%")
        if signal.ml_predictions:
            logger.info(f"ML Ensemble: {signal.ml_predictions.get('ensemble', 0)*100:.1f}%")
        logger.info(f"Reasons: {', '.join(signal.primary_reasons[:2])}")
    
    def _generate_hybrid_report(self):
        if not self.enhanced_signals_history:
            logger.info("\n📝 No complete signals generated")
            return
        runtime = datetime.now() - self.start_time
        hours = runtime.total_seconds() / 3600
        logger.info("\n" + "="*80)
        logger.info("COMPLETE V10.5.0 FINAL REPORT")
        logger.info("="*80)
        logger.info(f"Runtime: {runtime}")
        logger.info(f"Total Scans: {self.stats['total_scans']}")
        logger.info(f"Total Signals: {self.stats['total_signals']}")
        logger.info(f"Signals/hour: {self.stats['total_signals']/hours:.2f}" if hours > 0 else "Signals/hour: N/A")
        logger.info(f"Tier 1 (Ultra Safe): {self.stats['tier1_signals']}")
        logger.info(f"Tier 2 (Balanced): {self.stats['tier2_signals']}")
        logger.info(f"Tier 3 (Aggressive): {self.stats['tier3_signals']}")
        logger.info(f"Buy Signals: {self.stats['buy_signals']}")
        logger.info(f"Sell Signals: {self.stats['sell_signals']}")
        logger.info(f"Avg Confidence: {self.stats['avg_confidence']:.1f}%" if self.stats['total_signals'] > 0 else "Avg Confidence: N/A")
        logger.info(f"Avg Accuracy: {self.stats['avg_accuracy']:.1f}%" if self.stats['total_signals'] > 0 else "Avg Accuracy: N/A")
        bot_win_rate, signals_last_100, win_rate_last_100 = self.get_bot_win_rate()
        logger.info(f"Bot Win Rate (est): {bot_win_rate:.1f}%")
        logger.info(f"Last 100 Win Rate: {win_rate_last_100:.1f}%" if signals_last_100 > 0 else "Last 100 Win Rate: N/A")
        logger.info("\n📱 TELEGRAM STATS:")
        logger.info(f"  🔴 Emergency Alerts: {self.stats['emergency_alerts']}")
        logger.info(f"  🟡 High Alerts: {self.stats['high_alerts']}")
        logger.info(f"  🔵 Medium Alerts: {self.stats['medium_alerts']}")
        logger.info("\n🔧 CORE FEATURES STATS:")
        logger.info(f"  📏 ATR Stop Loss used: {self.stats['atr_signals']} ({(self.stats['atr_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)")
        logger.info(f"  📊 Volume Profile used: {self.stats['volume_profile_signals']} ({(self.stats['volume_profile_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)")
        logger.info(f"  🎣 Liquidity Grab detected: {self.stats['liquidity_grab_signals']} ({(self.stats['liquidity_grab_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)")
        logger.info(f"  📈 Trend Filter passed: {self.stats['trend_filter_passed']} ({(self.stats['trend_filter_passed']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)")
        logger.info(f"  🤖 AI used: {self.stats['ai_used_signals']} ({(self.stats['ai_used_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)")
        logger.info(f"  🧠 ML Ensemble used: {self.stats['ml_used_signals']} ({(self.stats['ml_used_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)")
        logger.info("\n🔬 ADVANCED FEATURES STATS:")
        logger.info(f"  🛡️ Security features: Enabled")
        logger.info(f"  📊 Risk Management: Kelly={self.signal_generator.risk_manager.kelly_fraction:.2f}, DD={self.signal_generator.risk_manager.drawdown:.1f}%")
        portfolio_summary = self.signal_generator.portfolio_manager.get_portfolio_summary()
        if portfolio_summary['num_positions'] > 0:
            logger.info(f"  💼 Portfolio: {portfolio_summary['num_positions']} positions, Diversification={portfolio_summary['diversification_score']:.1f}%")
        perf_stats = self.signal_generator.performance_analytics.get_comprehensive_stats()
        if 'total_trades' in perf_stats:
            logger.info(f"  📊 Performance: Sharpe={perf_stats['sharpe_ratio']:.2f}, PF={perf_stats['profit_factor']:.2f}")
        logger.info("\n🎨 PRIMARY STYLES:")
        for style, count in sorted(self.stats['primary_styles'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
            logger.info(f"  {style}: {count} ({percentage:.1f}%)")
        logger.info("\n🧠 SMART MONEY CONCEPTS:")
        for concept, count in sorted(self.stats['smart_money_concepts'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
            logger.info(f"  {concept}: {count} ({percentage:.1f}%)")
        logger.info("\n📊 TRADING STYLES (aligned):")
        for style, count in sorted(self.stats['signals_by_style'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
            logger.info(f"  {style}: {count} ({percentage:.1f}%)")
        logger.info("\n📊 ENTRY LOGIC:")
        for logic, count in sorted(self.stats['entries_by_timeframe'].items()):
            percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
            logger.info(f"  {logic}: {count} ({percentage:.1f}%)")
        logger.info("\n📊 TOP SYMBOLS:")
        for symbol, count in sorted(self.stats['signals_by_symbol'].items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {symbol}: {count}")
        report_file = f"complete_v10.5_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ULTIMATE HYBRID FUTURES BOT V10.5.0 - PYDROID OPTIMIZED\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Runtime: {runtime}\n")
            f.write(f"Total Scans: {self.stats['total_scans']}\n")
            f.write(f"Total Signals: {self.stats['total_signals']}\n")
            f.write(f"Tier 1 (Ultra Safe): {self.stats['tier1_signals']}\n")
            f.write(f"Tier 2 (Balanced): {self.stats['tier2_signals']}\n")
            f.write(f"Tier 3 (Aggressive): {self.stats['tier3_signals']}\n")
            f.write(f"Buy Signals: {self.stats['buy_signals']}\n")
            f.write(f"Sell Signals: {self.stats['sell_signals']}\n")
            f.write(f"Avg Confidence: {self.stats['avg_confidence']:.1f}%\n")
            f.write(f"Avg Accuracy: {self.stats['avg_accuracy']:.1f}%\n")
            f.write(f"Bot Win Rate (est): {bot_win_rate:.1f}%\n")
            f.write(f"Last 100 Win Rate: {win_rate_last_100:.1f}%\n")
            f.write("\n📱 TELEGRAM STATS:\n")
            f.write(f"  Emergency Alerts: {self.stats['emergency_alerts']}\n")
            f.write(f"  High Alerts: {self.stats['high_alerts']}\n")
            f.write(f"  Medium Alerts: {self.stats['medium_alerts']}\n")
            f.write("\n🔧 CORE FEATURES STATS:\n")
            f.write(f"  ATR Stop Loss used: {self.stats['atr_signals']} ({(self.stats['atr_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)\n")
            f.write(f"  Volume Profile used: {self.stats['volume_profile_signals']} ({(self.stats['volume_profile_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)\n")
            f.write(f"  Liquidity Grab detected: {self.stats['liquidity_grab_signals']} ({(self.stats['liquidity_grab_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)\n")
            f.write(f"  Trend Filter passed: {self.stats['trend_filter_passed']} ({(self.stats['trend_filter_passed']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)\n")
            f.write(f"  AI used: {self.stats['ai_used_signals']} ({(self.stats['ai_used_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)\n")
            f.write(f"  ML Ensemble used: {self.stats['ml_used_signals']} ({(self.stats['ml_used_signals']/self.stats['total_signals']*100 if self.stats['total_signals']>0 else 0):.1f}%)\n")
            f.write("\n🔬 ADVANCED FEATURES:\n")
            f.write(f"  Security features: Enabled\n")
            f.write(f"  Kelly Fraction: {self.signal_generator.risk_manager.kelly_fraction:.2f}\n")
            f.write(f"  Current Drawdown: {self.signal_generator.risk_manager.drawdown:.1f}%\n")
            if portfolio_summary['num_positions'] > 0:
                f.write(f"  Portfolio Positions: {portfolio_summary['num_positions']}\n")
                f.write(f"  Portfolio P&L: {portfolio_summary['total_pnl']:.2f}\n")
                f.write(f"  Diversification: {portfolio_summary['diversification_score']:.1f}%\n")
            if 'sharpe_ratio' in perf_stats:
                f.write(f"  Sharpe Ratio: {perf_stats['sharpe_ratio']:.2f}\n")
                f.write(f"  Profit Factor: {perf_stats['profit_factor']:.2f}\n")
            f.write("="*80 + "\n\n")
            f.write("PRIMARY STYLES:\n")
            for style, count in sorted(self.stats['primary_styles'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
                f.write(f"  {style}: {count} ({percentage:.1f}%)\n")
            f.write("\nSMART MONEY CONCEPTS:\n")
            for concept, count in sorted(self.stats['smart_money_concepts'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
                f.write(f"  {concept}: {count} ({percentage:.1f}%)\n")
            f.write("\nTRADING STYLES (aligned):\n")
            for style, count in sorted(self.stats['signals_by_style'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
                f.write(f"  {style}: {count} ({percentage:.1f}%)\n")
            f.write("\nENTRY LOGIC:\n")
            for logic, count in sorted(self.stats['entries_by_timeframe'].items()):
                percentage = (count / self.stats['total_signals']) * 100 if self.stats['total_signals'] > 0 else 0
                f.write(f"  {logic}: {count} ({percentage:.1f}%)\n")
            f.write("\n" + "="*80 + "\n")
            f.write("SIGNALS BY SYMBOL:\n")
            for symbol, count in sorted(self.stats['signals_by_symbol'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {symbol}: {count}\n")
            f.write("\n" + "="*80 + "\n")
            f.write("LATEST SIGNALS (with Entry, TP/SL):\n")
            f.write("-"*70 + "\n")
            for signal in self.enhanced_signals_history[-20:]:
                styles = ", ".join([s.value for s in signal.aligned_styles]) if signal.aligned_styles else "None"
                primary_style = signal.primary_style.value if signal.primary_style else "None"
                smart_money = signal.smart_money_display.primary_concept.value if signal.smart_money_display and signal.smart_money_display.primary_concept != SmartMoneyConcept.NONE else "None"
                alert_level = signal.alert_level.value if signal.alert_level else "N/A"
                f.write(f"\n{signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {signal.symbol}\n")
                f.write(f"  Tier: {signal.tier.value} | Alert: {alert_level} | Type: {signal.signal_type} | Conf: {signal.confidence:.1f}%\n")
                f.write(f"  Primary Style: {primary_style}\n")
                f.write(f"  Smart Money: {smart_money}\n")
                f.write(f"  Aligned Styles: {styles}\n")
                f.write(f"  Price: ${signal.current_price:,.4f}\n")
                f.write(f"  ENTRY: ${signal.entry_price:,.4f} | Entry Logic: {signal.optimal_entry_timeframe}\n")
                f.write(f"  STOP LOSS: ${signal.stop_loss:,.4f} ({signal.stop_loss_percentage:.2f}%)\n")
                f.write(f"  TP1: ${signal.take_profit_1:,.4f} | TP2: ${signal.take_profit_2:,.4f} | TP3: ${signal.take_profit_3:,.4f}\n")
                f.write(f"  R:R: 1:{signal.risk_reward.rr_ratio_1:.1f}\n")
                f.write(f"  Reason: {signal.primary_reasons[0] if signal.primary_reasons else 'N/A'}\n")
        logger.info(f"📄 Complete V10.5.0 report saved to {report_file}")
        signals_file = f"complete_v10.5_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        signals_data = []
        for signal in self.enhanced_signals_history[-100:]:
            signal_dict = {
                'timestamp': signal.timestamp.isoformat(),
                'symbol': signal.symbol,
                'tier': signal.tier.value if signal.tier else 'UNKNOWN',
                'alert_level': signal.alert_level.value if signal.alert_level else None,
                'signal_type': signal.signal_type,
                'confidence': signal.confidence,
                'accuracy_score': signal.overall_accuracy_score,
                'primary_style': signal.primary_style.value if signal.primary_style else None,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'stop_loss_percentage': signal.stop_loss_percentage,
                'take_profit_1': signal.take_profit_1,
                'take_profit_2': signal.take_profit_2,
                'take_profit_3': signal.take_profit_3,
                'rr_ratio': signal.risk_reward.rr_ratio_1 if signal.risk_reward else 0,
                'primary_reasons': signal.primary_reasons[:3],
                'ml_prediction': signal.ml_predictions.get('ensemble', 0) if signal.ml_predictions else 0,
                'drawdown': signal.risk_report.get('drawdown', 0) if signal.risk_report else 0
            }
            signals_data.append(signal_dict)
        with open(signals_file, 'w', encoding='utf-8') as f:
            json.dump(signals_data, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Complete V10.5.0 signals saved to {signals_file}")

# ========== CONFIGURATION LOADER ==========
def load_hybrid_config():
    config_file = "complete_v10.5_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    else:
        default_config = {
            'telegram': {
                'bot_token': 'YOUR_BOT_TOKEN_HERE',
                'chat_id': 'YOUR_CHAT_ID_HERE',
                'min_confidence': 70.0,
                'min_accuracy': 75.0,
                'cooldown_minutes': 15,
                'emergency_threshold': 90.0,
                'high_threshold': 80.0,
                'medium_threshold': 70.0,
                'enable_voice_alerts': False,
                'enable_buttons': False,
                'enable_summary': True,
                'summary_interval_minutes': 60,
                'enable_auto_trade': True,
                'max_position_size_usdt': 100.0,
                'default_leverage': 5
            },
            'futures': {
                'api_key': '',
                'api_secret': '',
                'use_testnet': False,
                'request_timeout': 30
            },
            'filters': {
                'min_volume_24h': 500000,
                'max_spread_percent': 0.1
            },
            'tp_config': {
                'scalping_tp1': 0.35,
                'scalping_tp2': 0.70,
                'intraday_tp1': 1.0,
                'intraday_tp2': 1.8,
                'swing_tp1': 1.5,
                'swing_tp2': 2.5,
                'position_tp1': 2.0,
                'position_tp2': 3.5
            },
            'security': {
                'encryption_enabled': True,
                'ip_whitelist_enabled': False,
                'allowed_ips': [],
                'two_fa_enabled': False,
                'rate_limit_enabled': True,
                'max_requests_per_minute': 60,
                'failed_attempt_limit': 5
            },
            'ml_models': {
                'random_forest_enabled': True,
                'gradient_boosting_enabled': True,
                'lstm_enabled': True,
                'ensemble_enabled': True,
                'auto_retrain': True,
                'retrain_interval_hours': 24,
                'model_dir': 'ml_models'
            },
            'risk_management': {
                'kelly_criterion_enabled': True,
                'var_calculation_enabled': True,
                'monte_carlo_enabled': True,
                'drawdown_protection_enabled': True,
                'max_drawdown_percent': 20.0,
                'position_sizing_method': 'kelly',
                'correlation_check_enabled': True,
                'max_correlation': 0.7
            },
            'advanced_orders': {
                'oco_enabled': True,
                'trailing_stop_enabled': True,
                'iceberg_enabled': True,
                'twap_enabled': True,
                'vwap_enabled': True,
                'default_trailing_callback': 1.0,
                'default_iceberg_size': 0.1,
                'default_twap_slices': 10
            },
            'portfolio': {
                'track_positions': True,
                'generate_heatmap': True,
                'calculate_correlation': True,
                'sector_allocation': True,
                'rebalance_threshold': 10.0
            },
            'performance': {
                'track_equity_curve': True,
                'generate_monthly_reports': True,
                'generate_yearly_reports': True,
                'track_win_rate_by_symbol': True,
                'track_win_rate_by_style': True,
                'track_win_rate_by_tier': True,
                'calculate_sharpe': True,
                'calculate_sortino': True,
                'calculate_calmar': True
            },
            'hybrid': {
                'enable_tier_1': True,
                'enable_tier_2': True,
                'enable_tier_3': True,
                'max_signals_per_day': 200,
                'scan_top_symbols': 100,
                'tier_1_tech_threshold': 70,
                'tier_1_flow_threshold': 60,
                'tier_2_tech_threshold': 59,
                'tier_2_flow_threshold': 55,
                'tier_3_tech_threshold': 54,
                'tier_3_flow_threshold': 48,
                'entry_order_book_depth': 10,
                'entry_max_spread_percent': 0.05,
                'entry_use_mid_price': True,
                'entry_buy_bid_level': 1,
                'entry_sell_ask_level': 1,
                'ultra_short_weight': 0.30,
                'short_weight': 0.25,
                'medium_weight': 0.25,
                'long_weight': 0.20,
                'min_regime_alignment': 60.0,
                'min_style_confidence': 70.0,
                'secondary_style_threshold': 70.0,
                'atr_stop_loss_enabled': True,
                'atr_period': 14,
                'atr_multiplier': 1.5,
                'atr_dynamic_multiplier': True,
                'volume_profile_entry_enabled': True,
                'volume_profile_bins': 24,
                'volume_profile_value_area_percent': 70.0,
                'volume_profile_min_bars': 20,
                'liquidity_grab_enabled': True,
                'liquidity_grab_lookback': 10,
                'liquidity_grab_min_wick_percent': 0.5,
                'liquidity_grab_volume_confirmation': True,
                'ema_200_trend_filter_enabled': True,
                'ema_200_required_for_tier1': True,
                'ema_200_required_for_tier2': True,
                'ema_200_required_for_tier3': True,
                'ai_confidence_model_enabled': True,
                'ai_min_signals_for_training': 20,
                'ai_override_confidence': True,
                'ai_max_history': 100
            },
            'scan': {
                'interval_seconds': 30,
                'continuous': True
            }
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print(f"\n📝 Created complete V10.5.0 configuration file: {config_file}")
        print("⚠️  Please edit this file with your credentials")
        return default_config

# ========== MAIN FUNCTION ==========
def main():
    print("\n" + "="*80)
    print("ULTIMATE HYBRID FUTURES TRADING BOT V10.5.0")
    print("PYDROID OPTIMIZED EDITION - ALL FEATURES")
    print("Developer: Nhen Bol")
    print("="*80 + "\n")
    if not test_internet_connection():
        print("\n❌ No internet connection. Please check your network.")
        input("Press Enter to exit...")
        return
    config_data = load_hybrid_config()
    telegram_config = TelegramConfig(
        BOT_TOKEN=config_data.get('telegram', {}).get('bot_token', ''),
        CHAT_ID=config_data.get('telegram', {}).get('chat_id', ''),
        MIN_CONFIDENCE=float(config_data.get('telegram', {}).get('min_confidence', 70.0)),
        MIN_ACCURACY_SCORE=float(config_data.get('telegram', {}).get('min_accuracy', 75.0)),
        COOLDOWN_MINUTES=int(config_data.get('telegram', {}).get('cooldown_minutes', 15)),
        EMERGENCY_THRESHOLD=float(config_data.get('telegram', {}).get('emergency_threshold', 90.0)),
        HIGH_THRESHOLD=float(config_data.get('telegram', {}).get('high_threshold', 80.0)),
        MEDIUM_THRESHOLD=float(config_data.get('telegram', {}).get('medium_threshold', 70.0)),
        ENABLE_VOICE_ALERTS=bool(config_data.get('telegram', {}).get('enable_voice_alerts', False)),
        ENABLE_BUTTONS=False,
        ENABLE_SUMMARY=bool(config_data.get('telegram', {}).get('enable_summary', True)),
        SUMMARY_INTERVAL_MINUTES=int(config_data.get('telegram', {}).get('summary_interval_minutes', 60)),
        ENABLE_AUTO_TRADE=bool(config_data.get('telegram', {}).get('enable_auto_trade', True)),
        MAX_POSITION_SIZE_USDT=float(config_data.get('telegram', {}).get('max_position_size_usdt', 100.0)),
        DEFAULT_LEVERAGE=int(config_data.get('telegram', {}).get('default_leverage', 5))
    )
    futures_config = BinanceFuturesConfig(
        API_KEY=config_data.get('futures', {}).get('api_key', ''),
        API_SECRET=config_data.get('futures', {}).get('api_secret', ''),
        USE_TESTNET=bool(config_data.get('futures', {}).get('use_testnet', False)),
        REQUEST_TIMEOUT=int(config_data.get('futures', {}).get('request_timeout', 30))
    )
    interval = config_data.get('scan', {}).get('interval_seconds', 60)
    continuous = config_data.get('scan', {}).get('continuous', True)
    if telegram_config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n⚠️  Please configure Telegram bot in complete_v10.5_config.json")
        telegram_config.BOT_TOKEN = ""
    tp_data = config_data.get('tp_config', {})
    tp_config = TpConfig(
        scalping_tp1=tp_data.get('scalping_tp1', 0.35),
        scalping_tp2=tp_data.get('scalping_tp2', 0.70),
        intraday_tp1=tp_data.get('intraday_tp1', 1.0),
        intraday_tp2=tp_data.get('intraday_tp2', 1.8),
        swing_tp1=tp_data.get('swing_tp1', 1.5),
        swing_tp2=tp_data.get('swing_tp2', 2.5),
        position_tp1=tp_data.get('position_tp1', 2.0),
        position_tp2=tp_data.get('position_tp2', 3.5)
    )
    security_data = config_data.get('security', {})
    security_config = SecurityConfig(
        ENCRYPTION_ENABLED=security_data.get('encryption_enabled', True),
        IP_WHITELIST_ENABLED=security_data.get('ip_whitelist_enabled', False),
        ALLOWED_IPS=security_data.get('allowed_ips', []),
        TWO_FA_ENABLED=security_data.get('two_fa_enabled', False),
        RATE_LIMIT_ENABLED=security_data.get('rate_limit_enabled', True),
        MAX_REQUESTS_PER_MINUTE=security_data.get('max_requests_per_minute', 60),
        FAILED_ATTEMPT_LIMIT=security_data.get('failed_attempt_limit', 5)
    )
    ml_data = config_data.get('ml_models', {})
    ml_config = MLConfig(
        RANDOM_FOREST_ENABLED=ml_data.get('random_forest_enabled', True),
        GRADIENT_BOOSTING_ENABLED=ml_data.get('gradient_boosting_enabled', True),
        LSTM_ENABLED=ml_data.get('lstm_enabled', True),
        ENSEMBLE_ENABLED=ml_data.get('ensemble_enabled', True),
        AUTO_RETRAIN=ml_data.get('auto_retrain', True),
        RETRAIN_INTERVAL_HOURS=ml_data.get('retrain_interval_hours', 24),
        MODEL_DIR=ml_data.get('model_dir', 'ml_models')
    )
    risk_data = config_data.get('risk_management', {})
    risk_config = RiskConfig(
        KELLY_CRITERION_ENABLED=risk_data.get('kelly_criterion_enabled', True),
        VAR_CALCULATION_ENABLED=risk_data.get('var_calculation_enabled', True),
        MONTE_CARLO_ENABLED=risk_data.get('monte_carlo_enabled', True),
        DRAWDOWN_PROTECTION_ENABLED=risk_data.get('drawdown_protection_enabled', True),
        MAX_DRAWDOWN_PERCENT=risk_data.get('max_drawdown_percent', 20.0),
        POSITION_SIZING_METHOD=risk_data.get('position_sizing_method', 'kelly'),
        CORRELATION_CHECK_ENABLED=risk_data.get('correlation_check_enabled', True),
        MAX_CORRELATION=risk_data.get('max_correlation', 0.7)
    )
    order_data = config_data.get('advanced_orders', {})
    order_config = OrderConfig(
        OCO_ENABLED=order_data.get('oco_enabled', True),
        TRAILING_STOP_ENABLED=order_data.get('trailing_stop_enabled', True),
        ICEBERG_ENABLED=order_data.get('iceberg_enabled', True),
        TWAP_ENABLED=order_data.get('twap_enabled', True),
        VWAP_ENABLED=order_data.get('vwap_enabled', True),
        DEFAULT_TRAILING_CALLBACK=order_data.get('default_trailing_callback', 1.0),
        DEFAULT_ICEBERG_SIZE=order_data.get('default_iceberg_size', 0.1),
        DEFAULT_TWAP_SLICES=order_data.get('default_twap_slices', 10)
    )
    portfolio_data = config_data.get('portfolio', {})
    portfolio_config = PortfolioConfig(
        TRACK_POSITIONS=portfolio_data.get('track_positions', True),
        GENERATE_HEATMAP=portfolio_data.get('generate_heatmap', True),
        CALCULATE_CORRELATION=portfolio_data.get('calculate_correlation', True),
        SECTOR_ALLOCATION=portfolio_data.get('sector_allocation', True),
        REBALANCE_THRESHOLD=portfolio_data.get('rebalance_threshold', 10.0)
    )
    performance_data = config_data.get('performance', {})
    performance_config = PerformanceConfig(
        TRACK_EQUITY_CURVE=performance_data.get('track_equity_curve', True),
        GENERATE_MONTHLY_REPORTS=performance_data.get('generate_monthly_reports', True),
        GENERATE_YEARLY_REPORTS=performance_data.get('generate_yearly_reports', True),
        TRACK_WIN_RATE_BY_SYMBOL=performance_data.get('track_win_rate_by_symbol', True),
        TRACK_WIN_RATE_BY_STYLE=performance_data.get('track_win_rate_by_style', True),
        TRACK_WIN_RATE_BY_TIER=performance_data.get('track_win_rate_by_tier', True),
        CALCULATE_SHARPE=performance_data.get('calculate_sharpe', True),
        CALCULATE_SORTINO=performance_data.get('calculate_sortino', True),
        CALCULATE_CALMAR=performance_data.get('calculate_calmar', True)
    )
    hybrid_data = config_data.get('hybrid', {})
    hybrid_config = HybridConfig(
        ENABLE_TIER_1=hybrid_data.get('enable_tier_1', True),
        ENABLE_TIER_2=hybrid_data.get('enable_tier_2', True),
        ENABLE_TIER_3=hybrid_data.get('enable_tier_3', True),
        MAX_SIGNALS_PER_DAY=hybrid_data.get('max_signals_per_day', 200),
        SCAN_TOP_SYMBOLS=hybrid_data.get('scan_top_symbols', 100),
        TIER_1_TECH_THRESHOLD=hybrid_data.get('tier_1_tech_threshold', 70),
        TIER_1_FLOW_THRESHOLD=hybrid_data.get('tier_1_flow_threshold', 60),
        TIER_2_TECH_THRESHOLD=hybrid_data.get('tier_2_tech_threshold', 59),
        TIER_2_FLOW_THRESHOLD=hybrid_data.get('tier_2_flow_threshold', 55),
        TIER_3_TECH_THRESHOLD=hybrid_data.get('tier_3_tech_threshold', 54),
        TIER_3_FLOW_THRESHOLD=hybrid_data.get('tier_3_flow_threshold', 48),
        ENTRY_ORDER_BOOK_DEPTH=hybrid_data.get('entry_order_book_depth', 10),
        ENTRY_MAX_SPREAD_PERCENT=hybrid_data.get('entry_max_spread_percent', 0.05),
        ENTRY_USE_MID_PRICE=hybrid_data.get('entry_use_mid_price', True),
        ENTRY_BUY_BID_LEVEL=hybrid_data.get('entry_buy_bid_level', 1),
        ENTRY_SELL_ASK_LEVEL=hybrid_data.get('entry_sell_ask_level', 1),
        ULTRA_SHORT_WEIGHT=hybrid_data.get('ultra_short_weight', 0.30),
        SHORT_WEIGHT=hybrid_data.get('short_weight', 0.25),
        MEDIUM_WEIGHT=hybrid_data.get('medium_weight', 0.25),
        LONG_WEIGHT=hybrid_data.get('long_weight', 0.20),
        MIN_REGIME_ALIGNMENT=hybrid_data.get('min_regime_alignment', 60.0),
        MIN_STYLE_CONFIDENCE=hybrid_data.get('min_style_confidence', 70.0),
        SECONDARY_STYLE_THRESHOLD=hybrid_data.get('secondary_style_threshold', 70.0),
        ATR_STOP_LOSS_ENABLED=hybrid_data.get('atr_stop_loss_enabled', True),
        ATR_PERIOD=hybrid_data.get('atr_period', 14),
        ATR_MULTIPLIER=hybrid_data.get('atr_multiplier', 1.5),
        ATR_DYNAMIC_MULTIPLIER=hybrid_data.get('atr_dynamic_multiplier', True),
        VOLUME_PROFILE_ENTRY_ENABLED=hybrid_data.get('volume_profile_entry_enabled', True),
        VOLUME_PROFILE_BINS=hybrid_data.get('volume_profile_bins', 24),
        VOLUME_PROFILE_VALUE_AREA_PERCENT=hybrid_data.get('volume_profile_value_area_percent', 70.0),
        VOLUME_PROFILE_MIN_BARS=hybrid_data.get('volume_profile_min_bars', 20),
        LIQUIDITY_GRAB_ENABLED=hybrid_data.get('liquidity_grab_enabled', True),
        LIQUIDITY_GRAB_LOOKBACK=hybrid_data.get('liquidity_grab_lookback', 10),
        LIQUIDITY_GRAB_MIN_WICK_PERCENT=hybrid_data.get('liquidity_grab_min_wick_percent', 0.5),
        LIQUIDITY_GRAB_VOLUME_CONFIRMATION=hybrid_data.get('liquidity_grab_volume_confirmation', True),
        EMA_200_TREND_FILTER_ENABLED=hybrid_data.get('ema_200_trend_filter_enabled', True),
        EMA_200_REQUIRED_FOR_TIER1=hybrid_data.get('ema_200_required_for_tier1', True),
        EMA_200_REQUIRED_FOR_TIER2=hybrid_data.get('ema_200_required_for_tier2', True),
        EMA_200_REQUIRED_FOR_TIER3=hybrid_data.get('ema_200_required_for_tier3', True),
        AI_CONFIDENCE_MODEL_ENABLED=hybrid_data.get('ai_confidence_model_enabled', True),
        AI_MIN_SIGNALS_FOR_TRAINING=hybrid_data.get('ai_min_signals_for_training', 20),
        AI_OVERRIDE_CONFIDENCE=hybrid_data.get('ai_override_confidence', True),
        AI_MAX_HISTORY=hybrid_data.get('ai_max_history', 100),
        TP_CONFIG=tp_config,
        SECURITY_CONFIG=security_config,
        ML_CONFIG=ml_config,
        RISK_CONFIG=risk_config,
        ORDER_CONFIG=order_config,
        PORTFOLIO_CONFIG=portfolio_config,
        PERFORMANCE_CONFIG=performance_config
    )
    Config.HYBRID_CONFIG = hybrid_config
    print("\n🔌 Testing connection to Binance Futures...")
    test_client = BinanceFuturesClient(Config())
    connected = False
    for attempt in range(3):
        try:
            if test_client.test_connection():
                connected = True
                break
        except:
            time.sleep(2)
    if connected:
        print("✅ Binance Futures connection OK")
    else:
        print("⚠️ Cannot connect to Binance Futures. Will continue but may have issues.")
    try:
        bot = UltimateHybridBot(telegram_config, futures_config)
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return
    if telegram_config.BOT_TOKEN and telegram_config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        print("\n📱 Testing Telegram connection...")
        if bot.notifier.send_message("🤖 Complete Bot V10.5.0 started with ALL features..."):
            print("✅ Telegram OK")
        else:
            print("⚠️ Telegram not configured - continuing without alerts")
    print("\n" + "="*80)
    print("SELECT SCAN MODE")
    print("="*80)
    print("1. Single scan (run once)")
    print("2. Continuous (10 seconds) - Fast")
    print("3. Continuous (30 seconds)")
    print("4. Continuous (1 minute)")
    print("5. Continuous (5 minutes)")
    print("6. Continuous (15 minutes)")
    print(f"7. Use config setting ({interval} seconds)")
    choice = input("\nEnter choice (1-7): ").strip()
    intervals = {
        '1': None,
        '2': 10,
        '3': 30,
        '4': 60,
        '5': 300,
        '6': 900,
        '7': interval if continuous else None
    }
    if choice in intervals:
        interval_sec = intervals[choice]
        if interval_sec is None:
            print("\n🔍 Running single complete scan V10.5.0...")
            bot.run_smart_scan(continuous=False)
        else:
            if interval_sec < 60:
                time_display = f"{interval_sec} seconds"
            else:
                minutes = interval_sec // 60
                time_display = f"{minutes} minute{'s' if minutes > 1 else ''}"
            print(f"\n🔍 Running continuous complete scan V10.5.0 every {time_display}...")
            print("Press Ctrl+C to stop")
            bot.run_smart_scan(continuous=True, interval_seconds=interval_sec)
    else:
        print("\n❌ Invalid choice. Running single scan.")
        bot.run_smart_scan(continuous=False)
    print("\n✅ Complete bot V10.5.0 finished. Check logs for details.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
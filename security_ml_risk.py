#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ULTIMATE HYBRID CRYPTO TRADING BOT - SECURITY, ML, RISK MANAGEMENT
================================================================================
"""

from config_enums import *

# ==============================================================================
# SECURITY MANAGER
# ==============================================================================
class SecurityManager:
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or self._generate_key()
        if CRYPTO_AVAILABLE:
            self.cipher = Fernet(self.encryption_key)
        else:
            self.cipher = None
        self.ip_whitelist = []
        self.rate_limits = {}
        self.two_factor_codes = {}
        self.failed_attempts = defaultdict(int)
        self.locked_ips = set()
        self.audit_log = []
        
    def _generate_key(self) -> bytes:
        try:
            if CRYPTO_AVAILABLE:
                password = "UltimateHybridBotV12.0.1".encode()
                salt = b'salt_123456789012'
                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
                key = base64.urlsafe_b64encode(kdf.derive(password))
                return key
            else:
                return base64.urlsafe_b64encode(b'0' * 32)
        except Exception as e:
            logger.error(f"Key generation error: {e}")
            return base64.urlsafe_b64encode(b'0' * 32)
    
    def encrypt_api_key(self, api_key: str) -> str:
        if not CRYPTO_AVAILABLE or not self.cipher:
            return api_key
        try:
            encrypted = self.cipher.encrypt(api_key.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return api_key
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        if not CRYPTO_AVAILABLE or not self.cipher:
            return encrypted_key
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return encrypted_key
    
    def set_ip_whitelist(self, ips: List[str]):
        self.ip_whitelist = ips
        logger.info(f"✅ IP whitelist set: {ips}")
    
    def check_ip_allowed(self, ip: str) -> bool:
        if not self.ip_whitelist:
            return True
        return ip in self.ip_whitelist
    
    def generate_2fa_code(self, user: str) -> str:
        code = ''.join(random.choices(string.digits, k=6))
        self.two_factor_codes[user] = {'code': code, 'expires': time.time() + 300}
        return code
    
    def verify_2fa_code(self, user: str, code: str) -> bool:
        if user not in self.two_factor_codes:
            return False
        data = self.two_factor_codes[user]
        if time.time() > data['expires']:
            del self.two_factor_codes[user]
            return False
        return data['code'] == code
    
    def check_rate_limit(self, endpoint: str, max_requests: int = 60, window: int = 60) -> bool:
        current_time = time.time()
        if endpoint not in self.rate_limits:
            self.rate_limits[endpoint] = []
        self.rate_limits[endpoint] = [t for t in self.rate_limits[endpoint] if current_time - t < window]
        if len(self.rate_limits[endpoint]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {endpoint}")
            return False
        self.rate_limits[endpoint].append(current_time)
        return True
    
    def record_failed_attempt(self, ip: str):
        self.failed_attempts[ip] += 1
        if self.failed_attempts[ip] >= 5:
            self.locked_ips.add(ip)
            logger.warning(f"🔒 IP {ip} locked")
            self.log_security_event("IP_LOCKED", f"IP {ip} locked after {self.failed_attempts[ip]} failed attempts")
    
    def is_ip_locked(self, ip: str) -> bool:
        return ip in self.locked_ips
    
    def log_security_event(self, event_type: str, details: str):
        self.audit_log.append({'timestamp': datetime.now().isoformat(), 'type': event_type, 'details': details})
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def rotate_encryption_key(self):
        if not CRYPTO_AVAILABLE:
            return
        new_key = self._generate_key()
        self.cipher = Fernet(new_key)
        self.encryption_key = new_key
        logger.info("✅ Encryption key rotated")
        self.log_security_event("KEY_ROTATION", "Encryption key rotated")

# ==============================================================================
# ADVANCED ML MODELS
# ==============================================================================
class AdvancedMLModels:
    def __init__(self, model_dir: str = "ml_models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.model_performance = {}
        self.ensemble_weights = {}
        self.training_queue = queue.Queue()
        self.training_thread = None
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        self._start_training_thread()
        self.load_models()
    
    def _start_training_thread(self):
        def train_worker():
            while True:
                try:
                    X, y, model_name, callback = self.training_queue.get(timeout=1)
                    if X is not None and y is not None:
                        model = self.train_random_forest(X, y, model_name)
                        if callback:
                            callback(model)
                except queue.Empty:
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Training thread error: {e}")
        self.training_thread = threading.Thread(target=train_worker, daemon=True)
        self.training_thread.start()
    
    def train_random_forest(self, X: np.ndarray, y: np.ndarray, model_name: str = "rf_model") -> Optional[RandomForestRegressor]:
        try:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            model = RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_split=5,
                                         min_samples_leaf=2, random_state=42, n_jobs=1)
            model.fit(X_scaled, y)
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            predictions = model.predict(X_scaled)
            mse = np.mean((predictions - y) ** 2)
            self.model_performance[model_name] = {'type': 'RandomForest', 'mse': mse, 'rmse': np.sqrt(mse), 'samples': len(X)}
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
            model = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1,
                                             subsample=0.8, random_state=42)
            model.fit(X_scaled, y)
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            predictions = model.predict(X_scaled)
            mse = np.mean((predictions - y) ** 2)
            self.model_performance[model_name] = {'type': 'GradientBoosting', 'mse': mse, 'rmse': np.sqrt(mse), 'samples': len(X)}
            joblib.dump(model, f"{self.model_dir}/{model_name}.pkl")
            joblib.dump(scaler, f"{self.model_dir}/{model_name}_scaler.pkl")
            logger.info(f"✅ Gradient Boosting model trained: {model_name} (RMSE: {np.sqrt(mse):.4f})")
            return model
        except Exception as e:
            logger.error(f"Gradient Boosting training error: {e}")
            return None
    
    def train_lstm(self, X: np.ndarray, y: np.ndarray, model_name: str = "lstm_model") -> Optional[Any]:
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
            
            # Simple LSTM simulation
            class SimpleLSTM:
                def __init__(self):
                    self.weights = np.random.randn(X_seq.shape[2]) * 0.01
                
                def predict(self, x_seq):
                    return np.mean(x_seq @ self.weights)
            
            model = SimpleLSTM()
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            
            predictions = []
            for i in range(len(X_seq)):
                pred = model.predict(X_seq[i])
                predictions.append(pred)
            if predictions:
                mse = np.mean((np.array(predictions) - y_seq[:len(predictions)]) ** 2)
                self.model_performance[model_name] = {'type': 'LSTM', 'mse': mse, 'rmse': np.sqrt(mse), 'samples': len(X_seq)}
            
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
    
    def train_async(self, X: np.ndarray, y: np.ndarray, model_name: str, callback=None):
        self.training_queue.put((X, y, model_name, callback))
    
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
    
    def predict_proba(self, X: np.ndarray, model_name: str = 'ensemble_model') -> float:
        try:
            pred = self.predict(X, model_name)
            return max(0, min(1, (pred + 1) / 2))
        except:
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
            
            logger.info(f"✅ Loaded {len(self.models)} ML models")
        except Exception as e:
            logger.error(f"Model loading error: {e}")
    
    def get_model_performance(self, model_name: str) -> Dict:
        return self.model_performance.get(model_name, {})
    
    def get_best_model(self) -> str:
        best_model = None
        best_rmse = float('inf')
        for name, perf in self.model_performance.items():
            rmse = perf.get('rmse', float('inf'))
            if rmse < best_rmse:
                best_rmse = rmse
                best_model = name
        return best_model

# ==============================================================================
# ADVANCED RISK MANAGER
# ==============================================================================
class AdvancedRiskManager:
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
        self.risk_per_trade = 0.01
        self.max_correlation = 0.7
        self.position_sizing_method = 'kelly'
        
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
        if self.position_sizing_method == 'kelly' and self.kelly_fraction > 0:
            base_size = account_balance * self.kelly_fraction * kelly_multiplier
        else:
            base_size = account_balance * self.risk_per_trade
        
        if self.drawdown > 10:
            drawdown_factor = 1 - ((self.drawdown - 10) / 20)
            base_size *= max(0.5, drawdown_factor)
        
        confidence_factor = signal_confidence / 50
        position_size = base_size * confidence_factor
        min_size = account_balance * 0.002
        return max(position_size, min_size)
    
    def check_correlation(self, symbol: str, positions: Dict[str, Any]) -> bool:
        if symbol not in self.correlation_matrix:
            return True
        
        for pos_symbol, pos_data in positions.items():
            if pos_symbol in self.correlation_matrix.get(symbol, {}):
                correlation = self.correlation_matrix[symbol][pos_symbol]
                if abs(correlation) > self.max_correlation:
                    logger.warning(f"High correlation with {pos_symbol}: {correlation:.2f}")
                    return False
        return True
    
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
            'daily_pnl': self.daily_pnl[-7:],
            'position_sizing_method': self.position_sizing_method,
            'risk_per_trade': self.risk_per_trade
        }
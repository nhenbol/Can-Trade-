#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ULTIMATE HYBRID CRYPTO TRADING BOT - MAIN BOT PART 1
Multi-Timeframe, Advanced Features, ATR, Volume Profile
================================================================================
"""

from config_enums import *
from security_ml_risk import *
from advanced_orders_portfolio import *

# ==============================================================================
# TECHNICAL INDICATORS - បន្ថែមនៅទីនេះ
# ==============================================================================
class TechnicalIndicators:
    """Technical Indicators Calculator"""
    
    def __init__(self):
        pass
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> float:
        """Calculate Exponential Moving Average"""
        try:
            if len(df) < period:
                return float(df['close'].iloc[-1])
            ema = df['close'].ewm(span=period, adjust=False).mean()
            return float(ema.iloc[-1])
        except Exception as e:
            logger.error(f"EMA calculation error: {e}")
            return float(df['close'].iloc[-1]) if len(df) > 0 else 0
    
    def calculate_sma(self, df: pd.DataFrame, period: int) -> float:
        """Calculate Simple Moving Average"""
        try:
            if len(df) < period:
                return float(df['close'].mean())
            return float(df['close'].iloc[-period:].mean())
        except Exception as e:
            logger.error(f"SMA calculation error: {e}")
            return float(df['close'].iloc[-1]) if len(df) > 0 else 0
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        try:
            if len(df) < period + 1:
                return 50.0
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except Exception as e:
            logger.error(f"RSI calculation error: {e}")
            return 50.0
    
    def calculate_macd(self, df: pd.DataFrame) -> Tuple[float, float, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            if len(df) < 26:
                return 0, 0, 0
            
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal
            
            return float(macd.iloc[-1]), float(signal.iloc[-1]), float(histogram.iloc[-1])
        except Exception as e:
            logger.error(f"MACD calculation error: {e}")
            return 0, 0, 0
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        try:
            if len(df) < period:
                close = float(df['close'].iloc[-1])
                return close, close * 1.02, close * 0.98
            
            sma = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            middle_band = sma
            lower_band = sma - (std * std_dev)
            
            return float(upper_band.iloc[-1]), float(middle_band.iloc[-1]), float(lower_band.iloc[-1])
        except Exception as e:
            logger.error(f"Bollinger Bands calculation error: {e}")
            close = float(df['close'].iloc[-1])
            return close * 1.02, close, close * 0.98
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            if len(df) < period + 1:
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
            
            atr = pd.Series(tr).rolling(window=period).mean()
            return float(atr.iloc[-1])
        except Exception as e:
            logger.error(f"ATR calculation error: {e}")
            return float(df['high'].iloc[-1] - df['low'].iloc[-1]) if len(df) > 0 else 0
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average Directional Index"""
        try:
            if len(df) < period + 1:
                return 25.0
            
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            
            plus_dm = np.zeros(len(df))
            minus_dm = np.zeros(len(df))
            tr = np.zeros(len(df))
            
            for i in range(1, len(df)):
                high_diff = high[i] - high[i-1]
                low_diff = low[i-1] - low[i]
                
                if high_diff > low_diff and high_diff > 0:
                    plus_dm[i] = high_diff
                else:
                    plus_dm[i] = 0
                
                if low_diff > high_diff and low_diff > 0:
                    minus_dm[i] = low_diff
                else:
                    minus_dm[i] = 0
                
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1])
                lc = abs(low[i] - close[i-1])
                tr[i] = max(hl, hc, lc)
            
            atr = pd.Series(tr).rolling(window=period).mean()
            plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)
            minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean()
            
            return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 25.0
        except Exception as e:
            logger.error(f"ADX calculation error: {e}")
            return 25.0
    
    def calculate_obv(self, df: pd.DataFrame) -> float:
        """Calculate On-Balance Volume"""
        try:
            if len(df) < 2:
                return 0
            
            obv = 0
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    obv += df['volume'].iloc[i]
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    obv -= df['volume'].iloc[i]
            
            return float(obv)
        except Exception as e:
            logger.error(f"OBV calculation error: {e}")
            return 0
    
    def calculate_vwap(self, df: pd.DataFrame) -> float:
        """Calculate Volume-Weighted Average Price"""
        try:
            if len(df) == 0:
                return 0
            
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).sum() / df['volume'].sum()
            return float(vwap)
        except Exception as e:
            logger.error(f"VWAP calculation error: {e}")
            return float(df['close'].iloc[-1]) if len(df) > 0 else 0
    
    def calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Money Flow Index"""
        try:
            if len(df) < period + 1:
                return 50.0
            
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            raw_money_flow = typical_price * df['volume']
            
            positive_flow = []
            negative_flow = []
            
            for i in range(1, len(typical_price)):
                if typical_price.iloc[i] > typical_price.iloc[i-1]:
                    positive_flow.append(raw_money_flow.iloc[i])
                else:
                    negative_flow.append(raw_money_flow.iloc[i])
            
            positive_sum = sum(positive_flow[-period:]) if positive_flow else 0
            negative_sum = sum(negative_flow[-period:]) if negative_flow else 1
            
            money_ratio = positive_sum / negative_sum if negative_sum > 0 else 1
            mfi = 100 - (100 / (1 + money_ratio))
            
            return float(mfi)
        except Exception as e:
            logger.error(f"MFI calculation error: {e}")
            return 50.0
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[float, float]:
        """Calculate Stochastic Oscillator"""
        try:
            if len(df) < k_period:
                return 50.0, 50.0
            
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            
            k = 100 * ((df['close'] - low_min) / (high_max - low_min))
            d = k.rolling(window=d_period).mean()
            
            return float(k.iloc[-1]), float(d.iloc[-1])
        except Exception as e:
            logger.error(f"Stochastic calculation error: {e}")
            return 50.0, 50.0
    
    def calculate_cci(self, df: pd.DataFrame, period: int = 20) -> float:
        """Calculate Commodity Channel Index"""
        try:
            if len(df) < period:
                return 0
            
            tp = (df['high'] + df['low'] + df['close']) / 3
            sma_tp = tp.rolling(window=period).mean()
            mad = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
            
            cci = (tp - sma_tp) / (0.015 * mad)
            return float(cci.iloc[-1])
        except Exception as e:
            logger.error(f"CCI calculation error: {e}")
            return 0
    
    def calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Williams %R"""
        try:
            if len(df) < period:
                return -50.0
            
            highest_high = df['high'].rolling(window=period).max()
            lowest_low = df['low'].rolling(window=period).min()
            
            williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
            return float(williams_r.iloc[-1])
        except Exception as e:
            logger.error(f"Williams %R calculation error: {e}")
            return -50.0


class EnhancedTechnicalIndicators(TechnicalIndicators):
    """Enhanced Technical Indicators with additional features"""
    
    def __init__(self):
        super().__init__()
    
    def calculate_all(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate all technical indicators"""
        result = {}
        
        try:
            result['rsi'] = self.calculate_rsi(df)
            result['ema_9'] = self.calculate_ema(df, 9)
            result['ema_21'] = self.calculate_ema(df, 21)
            result['ema_50'] = self.calculate_ema(df, 50)
            result['ema_200'] = self.calculate_ema(df, 200) if len(df) >= 200 else result['ema_50']
            result['sma_20'] = self.calculate_sma(df, 20)
            result['sma_50'] = self.calculate_sma(df, 50)
            result['sma_200'] = self.calculate_sma(df, 200) if len(df) >= 200 else result['sma_50']
            
            macd, signal, hist = self.calculate_macd(df)
            result['macd'] = macd
            result['macd_signal'] = signal
            result['macd_histogram'] = hist
            
            upper, middle, lower = self.calculate_bollinger_bands(df)
            result['bb_upper'] = upper
            result['bb_middle'] = middle
            result['bb_lower'] = lower
            
            result['atr'] = self.calculate_atr(df)
            result['adx'] = self.calculate_adx(df)
            result['obv'] = self.calculate_obv(df)
            result['vwap'] = self.calculate_vwap(df)
            result['mfi'] = self.calculate_mfi(df)
            
            k, d = self.calculate_stochastic(df)
            result['stoch_k'] = k
            result['stoch_d'] = d
            
            result['cci'] = self.calculate_cci(df)
            result['williams_r'] = self.calculate_williams_r(df)
            
        except Exception as e:
            logger.error(f"Error calculating all indicators: {e}")
        
        return result
    
    def get_trend_signal(self, df: pd.DataFrame) -> str:
        """Get trend signal based on EMAs"""
        try:
            ema_9 = self.calculate_ema(df, 9)
            ema_21 = self.calculate_ema(df, 21)
            ema_50 = self.calculate_ema(df, 50)
            current_price = float(df['close'].iloc[-1])
            
            if current_price > ema_9 > ema_21 > ema_50:
                return "STRONG_BULL"
            elif current_price < ema_9 < ema_21 < ema_50:
                return "STRONG_BEAR"
            elif current_price > ema_9 and ema_9 > ema_21:
                return "BULL"
            elif current_price < ema_9 and ema_9 < ema_21:
                return "BEAR"
            else:
                return "NEUTRAL"
        except:
            return "NEUTRAL"
    
    def get_momentum_signal(self, df: pd.DataFrame) -> str:
        """Get momentum signal based on RSI and MACD"""
        try:
            rsi = self.calculate_rsi(df)
            macd, signal, hist = self.calculate_macd(df)
            
            if rsi > 70 and hist > 0:
                return "OVERBOUGHT"
            elif rsi < 30 and hist < 0:
                return "OVERSOLD"
            elif hist > 0 and macd > signal:
                return "BULLISH"
            elif hist < 0 and macd < signal:
                return "BEARISH"
            else:
                return "NEUTRAL"
        except:
            return "NEUTRAL"
    
    def get_volatility_signal(self, df: pd.DataFrame) -> str:
        """Get volatility signal based on Bollinger Bands"""
        try:
            upper, middle, lower = self.calculate_bollinger_bands(df)
            current_price = float(df['close'].iloc[-1])
            
            bandwidth = (upper - lower) / middle
            
            if bandwidth > 0.1:
                return "HIGH"
            elif bandwidth < 0.05:
                return "LOW"
            else:
                return "MEDIUM"
        except:
            return "MEDIUM"

# ==============================================================================
# បន្តកូដដើមរបស់ bot_main_part1.py
# ==============================================================================

# ==============================================================================
# TIMEFRAME CONFIGURATION
# ==============================================================================
class TimeframeConfig:
    ALL_TIMEFRAMES = {"3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h",
                     "2h": "2h", "4h": "4h", "6h": "6h", "8h": "8h", "12h": "12h",
                     "1d": "1d", "3d": "3d", "1w": "1w", "1M": "1M"}
    
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
    
    DEFAULT_TIMEFRAMES = {"3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h",
                         "2h": "2h", "4h": "4h", "1d": "1d"}

# ==============================================================================
# MARKET REGIME MAPPING
# ==============================================================================
class MarketRegimeMapper:
    @staticmethod
    def get_display_name(regime_str: str) -> str:
        if not regime_str or regime_str == "UNKNOWN" or regime_str == "":
            return "RANGING"
        mapping = {
            "STRONG_BULL": "STRONG BULL", "WEAK_BULL": "WEAK BULL",
            "STRONG_BEAR": "STRONG BEAR", "WEAK_BEAR": "WEAK BEAR",
            "TRENDING_BULL": "TRENDING BULL", "TRENDING_BEAR": "TRENDING BEAR",
            "BULL": "BULL", "BEAR": "BEAR", "RANGING": "RANGING", "VOLATILE": "VOLATILE"
        }
        for key, value in mapping.items():
            if key in regime_str:
                return value
        return "RANGING"
    
    @staticmethod
    def get_display_name_with_emoji(regime_str: str) -> str:
        display = MarketRegimeMapper.get_display_name(regime_str)
        emoji_mapping = {
            "STRONG BULL": "🐂", "TRENDING BULL": "🐂", "BULL": "🐂",
            "STRONG BEAR": "🐻", "TRENDING BEAR": "🐻", "BEAR": "🐻",
            "WEAK BULL": "📈", "WEAK BEAR": "📉", "RANGING": "📊", "VOLATILE": "🌪️"
        }
        for key, emoji in emoji_mapping.items():
            if key in display:
                return f"{emoji} {display}"
        return f"📊 {display}"
    
    @staticmethod
    def get_regime_type(regime_str: str) -> str:
        display = MarketRegimeMapper.get_display_name(regime_str)
        if "BULL" in display:
            return "BULL"
        elif "BEAR" in display:
            return "BEAR"
        elif "VOLATILE" in display:
            return "VOLATILE"
        else:
            return "RANGING"
    
    @staticmethod
    def get_regime_strength(regime_str: str) -> float:
        if "STRONG" in regime_str:
            return 80.0
        elif "TRENDING" in regime_str:
            return 70.0
        elif "WEAK" in regime_str:
            return 40.0
        elif "RANGING" in regime_str:
            return 50.0
        elif "VOLATILE" in regime_str:
            return 60.0
        elif "BULL" in regime_str:
            return 65.0
        elif "BEAR" in regime_str:
            return 65.0
        else:
            return 50.0

class MarketRegimeDetector:
    def __init__(self, client: 'EnhancedBinanceFuturesClient', config: HybridConfig = None):
        self.client = client
        self.config = config or HybridConfig()
    
    def detect_regime(self, symbol: str, df_4h: pd.DataFrame = None, df_1d: pd.DataFrame = None) -> 'MarketRegime':
        try:
            regime_type = "RANGING"
            strength = 50.0
            volatility = "MEDIUM"
            adx = 25.0
            if df_4h is not None and len(df_4h) > 50:
                ema9 = df_4h['close'].ewm(span=9).mean().iloc[-1]
                ema21 = df_4h['close'].ewm(span=21).mean().iloc[-1]
                ema50 = df_4h['close'].ewm(span=50).mean().iloc[-1]
                current = df_4h['close'].iloc[-1]
                returns = df_4h['close'].pct_change().dropna()
                vol = returns.std() * np.sqrt(24) * 100 if len(returns) > 0 else 2.0
                if vol > 5:
                    volatility = "HIGH"
                elif vol > 2.5:
                    volatility = "MEDIUM"
                else:
                    volatility = "LOW"
                if current > ema9 > ema21 > ema50:
                    regime_type = "STRONG BULL"
                    strength = 80.0
                elif current < ema9 < ema21 < ema50:
                    regime_type = "STRONG BEAR"
                    strength = 80.0
                elif current > ema9 and ema9 > ema21:
                    regime_type = "BULL"
                    strength = 65.0
                elif current < ema9 and ema9 < ema21:
                    regime_type = "BEAR"
                    strength = 65.0
                elif abs(current - ema21) / ema21 < 0.02:
                    regime_type = "RANGING"
                    strength = 50.0
                else:
                    regime_type = "VOLATILE"
                    strength = 60.0
                high_low = (df_4h['high'].max() - df_4h['low'].min()) / df_4h['close'].mean() * 100
                if high_low > 15:
                    volatility = "HIGH"
            return MarketRegime(regime_type=regime_type, strength=strength, volatility=volatility,
                               volume_profile="NEUTRAL", adx_value=adx, adx_trend="WEAK",
                               regime_score=strength * (1 if "BULL" in regime_type else -1 if "BEAR" in regime_type else 0))
        except Exception as e:
            logger.error(f"Regime detection error: {e}")
            return MarketRegime(regime_type="RANGING", strength=50.0, volatility="MEDIUM",
                               volume_profile="NEUTRAL", adx_value=25.0, adx_trend="WEAK", regime_score=0.0)

@dataclass
class MarketRegime:
    regime_type: str
    strength: float
    volatility: str
    volume_profile: str
    adx_value: float
    adx_trend: str
    regime_score: float
    
    def __post_init__(self):
        self.regime_type = MarketRegimeMapper.get_display_name(self.regime_type)

# ==============================================================================
# MULTI-TIMEFRAME REGIME DETECTOR
# ==============================================================================
class MultiTimeframeRegimeDetector:
    def __init__(self, client: 'EnhancedBinanceFuturesClient', config: HybridConfig = None):
        self.client = client
        self.indicators = TechnicalIndicators()
        self.enhanced_indicators = EnhancedTechnicalIndicators()
        self.config = config or HybridConfig()
    
    def detect_multi_tf_regime(self, symbol: str) -> 'MultiTimeframeRegime':
        try:
            ultra_short_data = self._get_timeframe_group(symbol, TimeframeType.ULTRA_SHORT)
            short_data = self._get_timeframe_group(symbol, TimeframeType.SHORT)
            medium_data = self._get_timeframe_group(symbol, TimeframeType.MEDIUM)
            long_data = self._get_timeframe_group(symbol, TimeframeType.LONG)
            ultra_short_regime = self._analyze_timeframe_group(ultra_short_data, TimeframeType.ULTRA_SHORT)
            short_regime = self._analyze_timeframe_group(short_data, TimeframeType.SHORT)
            medium_regime = self._analyze_timeframe_group(medium_data, TimeframeType.MEDIUM)
            long_regime = self._analyze_timeframe_group(long_data, TimeframeType.LONG)
            overall_regime, overall_strength = self._calculate_overall_regime(ultra_short_regime, short_regime, medium_regime, long_regime)
            regime_alignment = self._calculate_regime_alignment(ultra_short_regime, short_regime, medium_regime, long_regime, overall_regime)
            dominant_trend = self._determine_dominant_trend(ultra_short_regime, short_regime, medium_regime, long_regime)
            regime_score = self._calculate_regime_score(overall_regime, overall_strength)
            all_timeframes = {}
            for group_data in [ultra_short_data, short_data, medium_data, long_data]:
                for tf, df in group_data.items():
                    if df is not None:
                        all_timeframes[tf] = self._analyze_single_timeframe(df)
            return MultiTimeframeRegime(
                ultra_short_regime=MarketRegimeMapper.get_display_name(ultra_short_regime['regime']),
                ultra_short_strength=ultra_short_regime['strength'],
                ultra_short_adx=ultra_short_regime['adx'],
                ultra_short_volatility=ultra_short_regime['volatility'],
                short_regime=MarketRegimeMapper.get_display_name(short_regime['regime']),
                short_strength=short_regime['strength'],
                short_adx=short_regime['adx'],
                short_volatility=short_regime['volatility'],
                medium_regime=MarketRegimeMapper.get_display_name(medium_regime['regime']),
                medium_strength=medium_regime['strength'],
                medium_adx=medium_regime['adx'],
                medium_volatility=medium_regime['volatility'],
                long_regime=MarketRegimeMapper.get_display_name(long_regime['regime']),
                long_strength=long_regime['strength'],
                long_adx=long_regime['adx'],
                long_volatility=long_regime['volatility'],
                overall_regime=MarketRegimeMapper.get_display_name(overall_regime),
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
            return {'regime': "RANGING", 'strength': 50, 'adx': 25, 'volatility': "MEDIUM"}
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
            regime = "BULL"
            strength = min(adx * 1.5, 100)
        elif ema9 < ema21 and current_price < ema9:
            regime = "BEAR"
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
            return {'regime': "RANGING", 'strength': 50, 'adx': 25, 'volatility': "MEDIUM"}
        if group == TimeframeType.ULTRA_SHORT:
            weights = {"3m": 0.4, "5m": 0.35, "15m": 0.25}
        elif group == TimeframeType.SHORT:
            weights = {"30m": 0.4, "1h": 0.35, "2h": 0.25}
        elif group == TimeframeType.MEDIUM:
            weights = {"4h": 0.4, "6h": 0.3, "8h": 0.2, "12h": 0.1}
        else:
            weights = {"1d": 0.5, "3d": 0.3, "1w": 0.2}
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
            regime = "BULL"
            strength = min(avg_adx * 1.5, 100)
        elif avg_regime_score < -0.4:
            regime = "BEAR"
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
            'BULL': 1.0, 'STRONG BULL': 1.0, 'WEAK BULL': 0.5,
            'VOLATILE': 0.5, 'RANGING': 0,
            'BEAR': -1.0, 'STRONG BEAR': -1.0, 'WEAK BEAR': -0.5
        }
        for key, value in scores.items():
            if key in regime:
                return value
        return 0
    
    def _calculate_overall_regime(self, ultra_short: Dict, short: Dict, medium: Dict, long: Dict) -> Tuple[str, float]:
        weights = {'ultra_short': self.config.ULTRA_SHORT_WEIGHT, 'short': self.config.SHORT_WEIGHT,
                  'medium': self.config.MEDIUM_WEIGHT, 'long': self.config.LONG_WEIGHT}
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
            overall_regime = "BULL"
            overall_strength = final_score * 100
        elif final_score < -0.4:
            overall_regime = "BEAR"
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
        regime_type = MarketRegimeMapper.get_regime_type(overall)
        for regime in regimes:
            regime_type2 = MarketRegimeMapper.get_regime_type(regime)
            if regime_type2 == regime_type:
                aligned_count += 1
            elif (regime_type == "BULL" and regime_type2 == "RANGING") or \
                 (regime_type == "BEAR" and regime_type2 == "RANGING") or \
                 (regime_type == "VOLATILE"):
                aligned_count += 0.5
        return (aligned_count / len(regimes)) * 100
    
    def _determine_dominant_trend(self, ultra_short: Dict, short: Dict, medium: Dict, long: Dict) -> str:
        bullish_count = 0
        bearish_count = 0
        for regime_dict in [ultra_short, short, medium, long]:
            regime = regime_dict['regime']
            regime_type = MarketRegimeMapper.get_regime_type(regime)
            if regime_type == "BULL":
                bullish_count += 1
            elif regime_type == "BEAR":
                bearish_count += 1
        if bullish_count > bearish_count:
            return "BULLISH"
        elif bearish_count > bullish_count:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _calculate_regime_score(self, overall_regime: str, overall_strength: float) -> float:
        regime_type = MarketRegimeMapper.get_regime_type(overall_regime)
        if regime_type == "BULL":
            return overall_strength
        elif regime_type == "BEAR":
            return -overall_strength
        else:
            return 0
    
    def _get_default_multi_tf_regime(self) -> 'MultiTimeframeRegime':
        return MultiTimeframeRegime(
            ultra_short_regime="RANGING", ultra_short_strength=50, ultra_short_adx=25, ultra_short_volatility="MEDIUM",
            short_regime="RANGING", short_strength=50, short_adx=25, short_volatility="MEDIUM",
            medium_regime="RANGING", medium_strength=50, medium_adx=25, medium_volatility="MEDIUM",
            long_regime="RANGING", long_strength=50, long_adx=25, long_volatility="MEDIUM",
            overall_regime="RANGING", overall_strength=50,
            regime_alignment=100, dominant_trend="NEUTRAL", regime_score=0,
            all_timeframes={}
        )

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
    
    def __post_init__(self):
        self.ultra_short_regime = MarketRegimeMapper.get_display_name(self.ultra_short_regime)
        self.short_regime = MarketRegimeMapper.get_display_name(self.short_regime)
        self.medium_regime = MarketRegimeMapper.get_display_name(self.medium_regime)
        self.long_regime = MarketRegimeMapper.get_display_name(self.long_regime)
        self.overall_regime = MarketRegimeMapper.get_display_name(self.overall_regime)

# ==============================================================================
# ATR STOP LOSS
# ==============================================================================
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
                self.atr_value = min_allowed_atr
            elif self.atr_value > max_allowed_atr:
                self.atr_value = max_allowed_atr
            stop_distance = self.atr_value * self.atr_multiplier
            min_distance = entry_price * 0.002
            if stop_distance < min_distance:
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
                if direction == "BUY":
                    stop_loss = entry_price * 0.99
                    stop_pct = 1.0
                else:
                    stop_loss = entry_price * 1.01
                    stop_pct = 1.0
            self.stop_loss_price = stop_loss
            self.stop_loss_percentage = stop_pct
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

# ==============================================================================
# VOLUME PROFILE ENTRY
# ==============================================================================
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
                self.value_area_low = current_price * 0.95
                self.value_area_high = current_price * 1.05
                self.poc_price = current_price
            return {'entry_price': self.entry_price, 'entry_confidence': self.entry_confidence,
                    'entry_logic': self.entry_logic, 'poc_price': self.poc_price,
                    'value_area_low': self.value_area_low, 'value_area_high': self.value_area_high,
                    'used_fallback': False}
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
            return {'entry_price': self.entry_price, 'entry_confidence': self.entry_confidence,
                    'entry_logic': self.entry_logic, 'poc_price': self.poc_price,
                    'value_area_low': self.value_area_low, 'value_area_high': self.value_area_high,
                    'used_fallback': True}
        except:
            self.entry_price = current_price
            self.entry_logic = "Current Price"
            self.entry_confidence = 50
            self.poc_price = current_price
            self.value_area_low = current_price * 0.98
            self.value_area_high = current_price * 1.02
            return {'entry_price': self.entry_price, 'entry_confidence': self.entry_confidence,
                    'entry_logic': self.entry_logic, 'poc_price': self.poc_price,
                    'value_area_low': self.value_area_low, 'value_area_high': self.value_area_high,
                    'used_fallback': True}

# ==============================================================================
# LIQUIDITY GRAB DETECTION
# ==============================================================================
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

# ==============================================================================
# TREND FILTER 200 EMA
# ==============================================================================
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

# ==============================================================================
# AI CONFIDENCE MODEL
# ==============================================================================
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
        self.training_count = 0
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
        self.training_count += 1
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
            features.append(signal.multi_tf_regime.regime_alignment if signal.multi_tf_regime else 50)
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
            features.append(signal.multi_tf_regime.ultra_short_adx if signal.multi_tf_regime else 25)
            if signal.smart_money_display:
                features.append(abs(signal.smart_money_display.smart_money_score))
            else:
                features.append(0)
            features.append(signal.timeframe_confluence.alignment_score if signal.timeframe_confluence else 50)
            if hasattr(signal, 'liquidity_grab') and signal.liquidity_grab:
                features.append(signal.liquidity_grab.grab_strength)
            else:
                features.append(0)
            if hasattr(signal, 'trend_filter_200ema') and signal.trend_filter_200ema:
                if signal.trend_filter_200ema.price_vs_ema == "ABOVE":
                    features.append(100)
                elif signal.trend_filter_200ema.price_vs_ema == "BELOW":
                    features.append(0)
                else:
                    features.append(50)
            else:
                features.append(50)
            if hasattr(signal, 'volume_profile_entry') and signal.volume_profile_entry:
                features.append(signal.volume_profile_entry.entry_confidence)
            else:
                features.append(50)
            return features
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return [50] * self.num_features
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ULTIMATE HYBRID CRYPTO TRADING BOT - MAIN BOT PART 3
Enhanced High Confidence Signal, Tiered Signal Generator, and Advanced Analyzers
================================================================================
Developer: Nhen Bol
Version: 12.0.1
================================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================
from config_enums import *
from security_ml_risk import *
from advanced_orders_portfolio import *
from bot_main_part1 import *
from bot_main_part2 import *
from advanced_analyzers import *
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from collections import defaultdict, deque
import numpy as np
import pandas as pd

# ==============================================================================
# ENHANCED HIGH CONFIDENCE SIGNAL
# ==============================================================================

@dataclass
class EnhancedHighConfidenceSignal:
    """Enhanced high confidence signal with all features"""
    
    # Required fields (no defaults)
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
    tech_score: float
    flow_score: float
    backtest_result: Optional[Any]
    market_context: Optional[Any]
    risk_reward: Optional[Any]
    confirmations: Optional[Any]
    bot_win_rate: float
    signals_last_100: int
    win_rate_last_100: float
    entry_timeframe_3m_signal: Optional[str]
    entry_timeframe_5m_signal: Optional[str]
    tier: Optional[SignalTier]
    tier_confidence: Optional[float]
    smart_scan_score: float
    adaptive_cooldown_minutes: int
    entry_bid_level: Optional[float]
    entry_ask_level: Optional[float]
    entry_mid_price: Optional[float]
    order_book_imbalance: Optional[float]
    ultra_short_regime_aligned: bool
    short_regime_aligned: bool
    medium_regime_aligned: bool
    long_regime_aligned: bool
    scalping_entry: Optional[float]
    intraday_entry: Optional[float]
    swing_entry: Optional[float]
    position_entry: Optional[float]
    scalping_tp1: Optional[float]
    scalping_tp2: Optional[float]
    scalping_tp3: Optional[float]
    intraday_tp1: Optional[float]
    intraday_tp2: Optional[float]
    intraday_tp3: Optional[float]
    swing_tp1: Optional[float]
    swing_tp2: Optional[float]
    swing_tp3: Optional[float]
    position_tp1: Optional[float]
    position_tp2: Optional[float]
    position_tp3: Optional[float]
    primary_style: Optional[SignalStyle]
    secondary_styles: List[SignalStyle]
    style_confidence: Dict[str, float]
    smart_money_display: Optional[Any]
    atr_stop_loss: Optional[Any]
    atr_value: float
    atr_multiplier: float
    volume_profile_entry: Optional[Any]
    volume_poc_price: float
    volume_value_area_low: float
    volume_value_area_high: float
    liquidity_grab: Optional[Any]
    liquidity_grab_detected: bool
    liquidity_grab_type: str
    liquidity_grab_strength: float
    trend_filter_200ema: Optional[Any]
    ema_200: float
    price_vs_ema_200: str
    ema_200_trend: str
    trend_filter_passed: bool
    ai_confidence: float
    ai_confidence_prediction: float
    ai_confidence_in_prediction: float
    ai_model_used: bool
    alert_level: Optional[AlertLevel]
    is_confirmed: bool
    calculated_imbalance: float
    volume_ratio_24h: float
    avg_volume_24h: float
    ultimate_direction_confidence: float
    ultimate_analysis: Optional[Dict]
    whale_activity: Optional[Any]
    whale_signal: bool
    whale_confidence: float
    whale_description: Optional[str]
    key_zones: List[Any]
    active_key_zone: Optional[Any]
    key_zone_entry: bool
    key_zone_confidence: float
    pullback_detected: bool
    pullback_percent: Optional[float]
    pullback_entry_price: Optional[float]
    dome_detected: bool
    dome_type: Optional[str]
    dome_height: Optional[float]
    tp_levels: Optional[Dict[str, Any]]
    tp_description: Optional[str]
    ml_predictions: Optional[Dict[str, float]]
    
    # Advanced analysis fields (with default values)
    candle_patterns: Optional[Dict] = None
    support_resistance: Optional[List] = None
    market_profile_analysis: Optional[Any] = None
    order_flow_analysis: Optional[Any] = None
    smart_money_analysis: Optional[Any] = None
    
    # Fields with default values
    order_recommendation: Optional[OrderRecommendation] = None
    order_recommendation_reason: Optional[str] = None


# ==============================================================================
# ENHANCED TIERED SIGNAL GENERATOR
# ==============================================================================

class EnhancedTieredSignalGenerator:
    """Enhanced signal generator with complete advanced features"""
    
    def __init__(self, client: Any, config: Config):
        self.client = client
        self.config = config
        self.indicators = TechnicalIndicators()
        self.enhanced_indicators = EnhancedTechnicalIndicators()
        
        self.hybrid_config = config.HYBRID_CONFIG or HybridConfig()
        
        self.entry_optimizer = EnhancedEntryOptimizer(client, self.hybrid_config)
        self.ai_model = AIConfidenceModel()
        self.klines_cache = {}
        self.cache_lock = threading.Lock()
        
        self.multi_tf_regime_detector = MultiTimeframeRegimeDetector(client, self.hybrid_config)
        self.regime_detector = MarketRegimeDetector(client, self.hybrid_config)
        
        self.training_signals = []
        self.training_outcomes = []
        
        self.tier1_generator = Tier1Generator(self)
        self.tier2_generator = Tier2Generator(self)
        self.tier3_generator = Tier3Generator(self)
        
        self.security_manager = SecurityManager()
        self.ml_models = AdvancedMLModels()
        self.risk_manager = AdvancedRiskManager()
        self.portfolio_manager = PortfolioManager()
        self.advanced_order_executor = None
        self.performance_analytics = PerformanceAnalytics()
        self.ultimate_analyzer = None
        
        # Initialize advanced analyzers
        self.candle_recognizer = AdvancedCandlePatternRecognizer()
        self.sr_detector = SupportResistanceDetector()
        self.market_profile_analyzer = MarketProfileAnalyzer()
        self.order_flow_analyzer = CompleteOrderFlowAnalyzer(client)
        self.smart_money_detector = CompleteSmartMoneyDetector()
        
        if hasattr(self.hybrid_config, 'LANGUAGE'):
            lang.current_language = Language(self.hybrid_config.LANGUAGE)
        
        logger.info("✅ Advanced analyzers initialized")
    
    def initialize_advanced_features(self):
        """Initialize advanced features"""
        self.advanced_order_executor = AdvancedOrderExecutor(self.client, self.config)
        logger.info("✅ Advanced features initialized")
    
    def get_complete_analysis(self, symbol: str, df_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Get complete analysis from all advanced analyzers with safe error handling"""
        
        analysis = {
            'candle_patterns': {},
            'support_resistance': [],
            'market_profile': None,
            'order_flow': None,
            'smart_money': None,
            'trading_opportunities': {},
            'nearest_support': [],
            'nearest_resistance': []
        }
        
        try:
            # Candle pattern analysis across timeframes
            if self.candle_recognizer:
                try:
                    analysis['candle_patterns'] = self.candle_recognizer.analyze_multiple_timeframes(df_dict)
                except Exception as e:
                    logger.debug(f"Candle pattern analysis error: {e}")
            
            # Support/Resistance levels (using 1h as primary)
            if '1h' in df_dict and df_dict['1h'] is not None and len(df_dict['1h']) > 30:
                try:
                    if self.sr_detector:
                        analysis['support_resistance'] = self.sr_detector.detect_levels(df_dict['1h'], '1h')
                        
                        # Get nearest levels for current price
                        current_price = float(df_dict['1h']['close'].iloc[-1]) if len(df_dict['1h']) > 0 else 0
                        if current_price > 0:
                            supports, resistances = self.sr_detector.get_nearest_levels(current_price)
                            analysis['nearest_support'] = supports
                            analysis['nearest_resistance'] = resistances
                except Exception as e:
                    logger.debug(f"Support/Resistance analysis error: {e}")
            
            # Market Profile
            if '4h' in df_dict and df_dict['4h'] is not None and len(df_dict['4h']) > 20:
                try:
                    if self.market_profile_analyzer:
                        analysis['market_profile'] = self.market_profile_analyzer.analyze_profile(df_dict['4h'])
                        if analysis['market_profile']:
                            current_price = float(df_dict['4h']['close'].iloc[-1]) if len(df_dict['4h']) > 0 else 0
                            if current_price > 0:
                                analysis['trading_opportunities'] = self.market_profile_analyzer.get_trading_opportunities(
                                    analysis['market_profile'], current_price
                                )
                except Exception as e:
                    logger.debug(f"Market Profile analysis error: {e}")
            
            # Order Flow
            ob_data = None
            trades = []
            try:
                if hasattr(self.client, 'get_order_book'):
                    ob_data = self.client.get_order_book(symbol, 10)
                if hasattr(self.client, 'get_recent_trades'):
                    trades = self.client.get_recent_trades(symbol, 50) or []
            except Exception as e:
                logger.debug(f"Order flow data error: {e}")
            
            if self.order_flow_analyzer:
                try:
                    analysis['order_flow'] = self.order_flow_analyzer.analyze_order_flow(symbol, ob_data, trades)
                except Exception as e:
                    logger.debug(f"Order flow analysis error: {e}")
            
            # Smart Money
            if '1h' in df_dict and df_dict['1h'] is not None and self.smart_money_detector:
                try:
                    analysis['smart_money'] = self.smart_money_detector.analyze(df_dict['1h'], ob_data)
                except Exception as e:
                    logger.debug(f"Smart Money analysis error: {e}")
        
        except Exception as e:
            logger.error(f"Complete analysis error for {symbol}: {e}")
        
        return analysis
    
    def generate_tiered_signals(self, symbol: str) -> List[EnhancedHighConfidenceSignal]:
        """Generate tiered signals for a symbol"""
        signals = []
        
        try:
            base_analysis = self._get_base_analysis(symbol)
            if not base_analysis:
                return signals
            
            current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
            
            # Check volume
            volume_24h = 0
            if ticker and isinstance(ticker, dict):
                try:
                    volume_24h = float(ticker.get('quoteVolume', 0))
                except (TypeError, ValueError):
                    volume_24h = 0
            
            min_volume = self.config.HIGH_CONFIDENCE_THRESHOLDS.get('MIN_VOLUME_24H', 500000)
            if volume_24h < min_volume:
                return signals
            
            # Detect multi-timeframe regime
            multi_tf_regime = self.multi_tf_regime_detector.detect_multi_tf_regime(symbol)
            
            # Get complete analysis for advanced features
            df_dict = {
                '1h': self._get_cached_klines(symbol, '1h', 100),
                '4h': self._get_cached_klines(symbol, '4h', 50),
                '1d': self._get_cached_klines(symbol, '1d', 30)
            }
            
            complete_analysis = self.get_complete_analysis(symbol, df_dict)
            
            # Generate tier 1 signals (Ultra Safe)
            if self.hybrid_config.ENABLE_TIER_1:
                try:
                    tier1 = self.tier1_generator.generate(symbol, base_analysis, multi_tf_regime)
                    if tier1:
                        tier1 = self._enhance_signal_with_analysis(tier1, complete_analysis)
                        signals.append(tier1)
                        self.training_signals.append(tier1)
                except Exception as e:
                    logger.error(f"Tier1 generation error for {symbol}: {e}")
            
            # Generate tier 2 signals (Balanced)
            if self.hybrid_config.ENABLE_TIER_2:
                try:
                    tier2 = self.tier2_generator.generate(symbol, base_analysis, multi_tf_regime)
                    if tier2:
                        tier2 = self._enhance_signal_with_analysis(tier2, complete_analysis)
                        signals.append(tier2)
                        self.training_signals.append(tier2)
                except Exception as e:
                    logger.error(f"Tier2 generation error for {symbol}: {e}")
            
            # Generate tier 3 signals (Aggressive)
            if self.hybrid_config.ENABLE_TIER_3:
                try:
                    tier3 = self.tier3_generator.generate(symbol, base_analysis, multi_tf_regime)
                    if tier3:
                        tier3 = self._enhance_signal_with_analysis(tier3, complete_analysis)
                        signals.append(tier3)
                        self.training_signals.append(tier3)
                except Exception as e:
                    logger.error(f"Tier3 generation error for {symbol}: {e}")
            
        except Exception as e:
            logger.error(f"Signal generation error for {symbol}: {e}")
        
        return signals
    
    def _enhance_signal_with_analysis(self, signal: EnhancedHighConfidenceSignal, 
                                      analysis: Dict[str, Any]) -> EnhancedHighConfidenceSignal:
        """Enhance signal with advanced analysis"""
        
        # Add analysis data
        signal.candle_patterns = analysis.get('candle_patterns')
        signal.support_resistance = analysis.get('support_resistance')
        signal.market_profile_analysis = analysis.get('market_profile')
        signal.order_flow_analysis = analysis.get('order_flow')
        signal.smart_money_analysis = analysis.get('smart_money')
        
        # Add reasons from order flow
        if analysis.get('order_flow') and analysis['order_flow'].order_flow_strength > 65:
            signal.primary_reasons.append(f"📊 Order Flow: {analysis['order_flow'].description}")
        
        # Add reasons from smart money
        if analysis.get('smart_money') and analysis['smart_money'].smart_money_score > 65:
            signal.primary_reasons.append(f"🧠 Smart Money: {analysis['smart_money'].description}")
        
        # Add candle patterns
        strong_patterns = []
        if analysis.get('candle_patterns'):
            for tf, patterns in analysis['candle_patterns'].items():
                if patterns:
                    for p in patterns[:1]:
                        if p['pattern'].strength > 75:
                            strong_patterns.append(f"{tf}: {p['pattern'].name}")
        
        if strong_patterns:
            signal.primary_reasons.append(f"🕯️ Candle Patterns: {', '.join(strong_patterns[:2])}")
        
        # Add support/resistance info
        if analysis.get('nearest_support') and analysis['nearest_support']:
            signal.nearest_support = analysis['nearest_support'][0].price
        if analysis.get('nearest_resistance') and analysis['nearest_resistance']:
            signal.nearest_resistance = analysis['nearest_resistance'][0].price
        
        # Add trading opportunities
        if analysis.get('trading_opportunities'):
            opp = analysis['trading_opportunities']
            for zone in opp.get('buy_zones', [])[:1]:
                signal.primary_reasons.append(f"🎯 {zone['reason']}")
            for zone in opp.get('sell_zones', [])[:1]:
                signal.primary_reasons.append(f"🎯 {zone['reason']}")
        
        return signal
    
    def generate_signal_with_advanced_features(self, symbol: str) -> Optional[EnhancedHighConfidenceSignal]:
        """Generate signal with all advanced features"""
        signals = self.generate_tiered_signals(symbol)
        if not signals:
            return None
        return max(signals, key=lambda s: s.confidence)
    
    def _get_base_analysis(self, symbol: str) -> Optional[Tuple]:
        """Get base analysis data for a symbol"""
        cache_key = f"base_{symbol}_{int(time.time()/60)}"
        
        if cache_key in self.klines_cache:
            return self.klines_cache[cache_key]
        
        try:
            # Get current price
            current_price = None
            if hasattr(self.client, 'get_current_price'):
                current_price = self.client.get_current_price(symbol)
            
            if not current_price or current_price <= 0:
                return None
            
            # Get ticker
            ticker = None
            if hasattr(self.client, 'get_ticker_24hr'):
                ticker = self.client.get_ticker_24hr(symbol)
            
            if not ticker:
                ticker = {}
            
            # Get klines
            df_1h = self._get_cached_klines(symbol, '1h', 100)
            if df_1h is None or df_1h.empty:
                return None
            
            # Create technical analysis with calculated indicators
            tech = EnhancedTechnicalAnalysis(
                rsi=50.0, rsi_signal="NEUTRAL",
                macd_trend="NEUTRAL", ema_trend="NEUTRAL",
                bb_position="MIDDLE", adx=25.0, adx_trend="WEAK",
                volume_surge=False, volume_ratio=1.0,
                obv_trend="NEUTRAL", stoch_signal="NEUTRAL",
                vwap_position="MIDDLE", mfi_signal="NEUTRAL"
            )
            
            # Try to calculate real indicators
            try:
                if len(df_1h) > 50:
                    # RSI
                    tech.rsi = self.indicators.calculate_rsi(df_1h)
                    if tech.rsi > 70:
                        tech.rsi_signal = "OVERBOUGHT"
                    elif tech.rsi < 30:
                        tech.rsi_signal = "OVERSOLD"
                    
                    # MACD
                    macd, signal, hist = self.indicators.calculate_macd(df_1h)
                    if macd > signal:
                        tech.macd_trend = "BULLISH"
                    elif macd < signal:
                        tech.macd_trend = "BEARISH"
                    
                    # EMA Trend
                    ema9 = self.indicators.calculate_ema(df_1h, 9)
                    ema21 = self.indicators.calculate_ema(df_1h, 21)
                    current = df_1h['close'].iloc[-1]
                    if current > ema9 > ema21:
                        tech.ema_trend = "BULLISH"
                    elif current < ema9 < ema21:
                        tech.ema_trend = "BEARISH"
                    
                    # ADX
                    tech.adx = self.indicators.calculate_adx(df_1h)
                    if tech.adx > 50:
                        tech.adx_trend = "VERY_STRONG"
                    elif tech.adx > 35:
                        tech.adx_trend = "STRONG"
                    elif tech.adx > 25:
                        tech.adx_trend = "WEAK"
            except Exception as e:
                logger.debug(f"Indicator calculation error for {symbol}: {e}")
            
            # Create order book analysis
            ob = OrderBookAnalysis(
                best_bid=current_price * 0.999, best_ask=current_price * 1.001,
                spread=current_price * 0.002, spread_percentage=0.2,
                imbalance=0.0, bid_ask_ratio=1.0, buy_pressure=50.0, sell_pressure=50.0,
                top_bids=[], top_asks=[], support_levels=[current_price * 0.99],
                resistance_levels=[current_price * 1.01]
            )
            
            # Get real order book if available
            if hasattr(self.client, 'get_order_book'):
                ob_data = self.client.get_order_book(symbol, 10)
                if ob_data and 'bids' in ob_data and 'asks' in ob_data:
                    try:
                        bids = ob_data.get('bids', [])
                        asks = ob_data.get('asks', [])
                        if len(bids) > 0 and len(asks) > 0:
                            best_bid = float(bids[0][0])
                            best_ask = float(asks[0][0])
                            spread = best_ask - best_bid
                            spread_pct = (spread / best_bid) * 100 if best_bid > 0 else 0
                            
                            bid_vol = sum(float(b[1]) * float(b[0]) for b in bids[:5])
                            ask_vol = sum(float(a[1]) * float(a[0]) for a in asks[:5])
                            total = bid_vol + ask_vol
                            imbalance = ((bid_vol - ask_vol) / total * 100) if total > 0 else 0
                            
                            ob.best_bid = best_bid
                            ob.best_ask = best_ask
                            ob.spread = spread
                            ob.spread_percentage = spread_pct
                            ob.imbalance = imbalance
                            ob.bid_ask_ratio = bid_vol / ask_vol if ask_vol > 0 else 1.0
                            ob.buy_pressure = 50 + imbalance / 2
                            ob.sell_pressure = 50 - imbalance / 2
                    except Exception as e:
                        logger.debug(f"Order book parse error for {symbol}: {e}")
            
            # Create market trade analysis
            mt = MarketTradeAnalysis(
                aggressive_buying=False, aggressive_selling=False,
                large_trades_buy=0, large_trades_sell=0
            )
            
            # Create cumulative flow
            cf = CumulativeFlow(delta_15min=0.0, trend_strength="NEUTRAL")
            
            result = (current_price, tech, ob, mt, cf, ticker, df_1h)
            self.klines_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Base analysis error for {symbol}: {e}")
            return None
    
    def _get_cached_klines(self, symbol: str, interval: str, limit: int) -> Optional[pd.DataFrame]:
        """Get cached klines data"""
        cache_key = f"{symbol}_{interval}_{limit}"
        
        with self.cache_lock:
            if cache_key in self.klines_cache:
                cached = self.klines_cache[cache_key]
                if isinstance(cached, tuple) and len(cached) == 2:
                    df, timestamp = cached
                    if time.time() - timestamp < 15:
                        return df.copy() if df is not None else None
        
        df = None
        if hasattr(self.client, 'get_klines'):
            df = self.client.get_klines(symbol, interval, limit)
        
        with self.cache_lock:
            if df is not None:
                self.klines_cache[cache_key] = (df, time.time())
        
        return df
    
    def calculate_technical_score(self, tech: Any) -> float:
        """Calculate technical score"""
        score = 0
        
        if hasattr(tech, 'rsi_signal'):
            if tech.rsi_signal == "OVERSOLD":
                score += 20
            elif tech.rsi_signal == "OVERBOUGHT":
                score -= 20
        
        if hasattr(tech, 'macd_trend'):
            if tech.macd_trend == "BULLISH":
                score += 25
            elif tech.macd_trend == "BEARISH":
                score -= 25
        
        if hasattr(tech, 'ema_trend'):
            if tech.ema_trend == "BULLISH":
                score += 20
            elif tech.ema_trend == "BEARISH":
                score -= 20
        
        if hasattr(tech, 'bb_position'):
            if tech.bb_position == "BELOW_LOWER":
                score += 15
            elif tech.bb_position == "ABOVE_UPPER":
                score -= 15
        
        if hasattr(tech, 'adx_trend'):
            if tech.adx_trend == "VERY_STRONG":
                score += 15
            elif tech.adx_trend == "STRONG":
                score += 10
            elif tech.adx_trend == "WEAK":
                score += 5
        
        return score
    
    def calculate_order_flow_score(self, ob: Any, mt: Any, cf: Any) -> float:
        """Calculate order flow score"""
        score = 0
        
        if ob and hasattr(ob, 'imbalance'):
            try:
                imbalance = float(ob.imbalance)
                if imbalance > 10:
                    score += 20
                elif imbalance < -10:
                    score -= 20
            except:
                pass
        
        if ob and hasattr(ob, 'bid_ask_ratio'):
            try:
                ratio = float(ob.bid_ask_ratio)
                if ratio > 1.2:
                    score += 15
                elif ratio < 0.8:
                    score -= 15
            except:
                pass
        
        if mt:
            if getattr(mt, 'aggressive_buying', False):
                score += 25
            if getattr(mt, 'aggressive_selling', False):
                score -= 25
        
        return score
    
    def calculate_atr_stop_loss(self, entry_price: float, direction: str, 
                                df: pd.DataFrame) -> Tuple[float, float, float]:
        """Calculate ATR-based stop loss"""
        if self.hybrid_config.ATR_STOP_LOSS_ENABLED:
            atr_stop = ATRStopLoss(atr_multiplier=self.hybrid_config.ATR_MULTIPLIER)
            stop_loss, stop_percentage = atr_stop.calculate_stop(entry_price, direction, df)
            return stop_loss, stop_percentage, atr_stop.atr_value
        else:
            if direction == "BUY":
                return entry_price * 0.99, 1.0, 0.0
            else:
                return entry_price * 1.01, 1.0, 0.0
    
    def get_style_entries(self, symbol: str, direction: str, current_price: float,
                         df_1h: Optional[pd.DataFrame] = None,
                         style: str = "INTRADAY") -> Dict[str, Any]:
        """Get style-based entries"""
        return self.entry_optimizer.get_style_entries(symbol, direction, current_price, df_1h, style)
    
    def calculate_risk_reward_adaptive(self, entry_price: float, stop_loss: float,
                                      scalping_tp1: float, scalping_tp2: float,
                                      intraday_tp1: float, intraday_tp2: float,
                                      swing_tp1: float, swing_tp2: float,
                                      position_tp1: float, position_tp2: float,
                                      direction: str) -> RiskRewardAnalysis:
        """Calculate adaptive risk/reward ratios"""
        risk = abs(entry_price - stop_loss)
        risk_percentage = (risk / entry_price) * 100 if entry_price > 0 else 0
        
        intraday_reward1 = abs(intraday_tp1 - entry_price)
        intraday_reward2 = abs(intraday_tp2 - entry_price)
        intraday_rr1 = intraday_reward1 / risk if risk > 0 else 0
        intraday_rr2 = intraday_reward2 / risk if risk > 0 else 0
        
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
            scalping_target_1=0, scalping_target_2=0,
            intraday_target_1=intraday_rr1, intraday_target_2=intraday_rr2,
            swing_target_1=0, swing_target_2=0,
            position_target_1=0, position_target_2=0
        )
    
    def calculate_confirmations(self, df: pd.DataFrame, tech: Any,
                               confluence: Any, direction: str) -> ConfirmationSignals:
        """Calculate confirmation signals"""
        return ConfirmationSignals(
            bullish_timeframes=2, bearish_timeframes=1, total_timeframes=5,
            volume_confirmation=False, volume_ratio=1.0, obv_confirmation="NEUTRAL",
            divergence_confirmation="NEUTRAL", pattern_confirmation="NEUTRAL",
            confirmation_score=50
        )


# ==============================================================================
# TIER 1 GENERATOR
# ==============================================================================

class Tier1Generator:
    """Tier 1 Ultra Safe signal generator"""
    
    def __init__(self, parent: EnhancedTieredSignalGenerator):
        self.parent = parent
        self.config = parent.hybrid_config
        self.order_type_analyzer = OrderTypeAnalyzer()
        self.keyzone_detector = KeyZoneDetector(self.config)
        self.tpsl_manager = TPSLManager(self.config)
        
        if hasattr(self.config, 'LANGUAGE'):
            lang.current_language = Language(self.config.LANGUAGE)
    
    def generate(self, symbol: str, base_analysis: Tuple, 
                 multi_tf_regime: 'MultiTimeframeRegime') -> Optional[EnhancedHighConfidenceSignal]:
        """Generate Tier 1 signal"""
        try:
            current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
            
            # Get additional timeframes
            df_4h = self.parent._get_cached_klines(symbol, '4h', 100)
            df_15m = self.parent._get_cached_klines(symbol, '15m', 100)
            
            if df_4h is None or df_15m is None:
                logger.debug(f"Tier1 {symbol}: Missing timeframe data")
                return None
            
            # Calculate scores
            tech_score = self.parent.calculate_technical_score(tech)
            flow_score = self.parent.calculate_order_flow_score(ob, mt, cf)
            
            # Get direction
            direction, direction_confidence, ultimate_result = self._get_ultimate_direction(
                symbol, df_4h, df_1h, df_15m, multi_tf_regime, None, ob, tech, 0.0
            )
            
            # Check thresholds
            if abs(tech_score) < self.config.TIER_1_TECH_THRESHOLD:
                logger.debug(f"Tier1 {symbol}: Tech score {tech_score} too low")
                return None
            
            if abs(flow_score) < self.config.TIER_1_FLOW_THRESHOLD:
                logger.debug(f"Tier1 {symbol}: Flow score {flow_score} too low")
                return None
            
            # Check regime alignment
            if not self._check_regime_alignment(direction, multi_tf_regime):
                logger.debug(f"Tier1 {symbol}: Regime alignment failed")
                return None
            
            # Check confirmations
            if not self._has_strong_confirmations(tech, ob, multi_tf_regime, direction_confidence):
                logger.debug(f"Tier1 {symbol}: Strong confirmations failed")
                return None
            
            # Check order book
            if not self._check_order_book_entry(ob, direction):
                logger.debug(f"Tier1 {symbol}: Order book entry check failed")
                return None
            
            # Get key zones
            key_zones = self.keyzone_detector.detect_zones(df_1h, current_price)
            active_key_zone = self.keyzone_detector.get_best_entry_zone(direction, current_price)
            key_zone_entry = active_key_zone is not None
            key_zone_confidence = active_key_zone.zone_strength if active_key_zone else 0
            
            # Build signal
            signal = self._build_signal(
                symbol, base_analysis, tech_score, flow_score, direction,
                SignalTier.TIER_1_ULTRA_SAFE, multi_tf_regime, ultimate_result,
                direction_confidence, None, False, 0, None,
                key_zones, active_key_zone, key_zone_entry, key_zone_confidence
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Tier1 generation error for {symbol}: {e}")
            return None
    
    def _get_ultimate_direction(self, symbol, df_4h, df_1h, df_15m, multi_tf_regime,
                                 smart_money, ob, tech, funding_rate, **kwargs):
        """Get ultimate direction analysis"""
        direction = "NEUTRAL"
        direction_confidence = 50
        ultimate_result = {'reasons': []}
        
        # EMA trend
        if hasattr(tech, 'ema_trend'):
            if tech.ema_trend == "BULLISH":
                direction = "BUY"
                direction_confidence = 65
            elif tech.ema_trend == "BEARISH":
                direction = "SELL"
                direction_confidence = 65
        
        # Multi-timeframe regime
        if hasattr(multi_tf_regime, 'overall_regime'):
            if "BULL" in multi_tf_regime.overall_regime:
                direction = "BUY"
                direction_confidence = 70
            elif "BEAR" in multi_tf_regime.overall_regime:
                direction = "SELL"
                direction_confidence = 70
        
        # Order book
        if ob and hasattr(ob, 'imbalance'):
            try:
                imbalance = float(ob.imbalance)
                if imbalance > 20:
                    direction = "BUY"
                    direction_confidence = 75
                elif imbalance < -20:
                    direction = "SELL"
                    direction_confidence = 75
            except:
                pass
        
        return direction, direction_confidence, ultimate_result
    
    def _has_strong_confirmations(self, tech: Any, ob: Any, multi_tf: MultiTimeframeRegime,
                                   direction_confidence: float, whale_signal: bool = False,
                                   key_zone_entry: bool = False) -> bool:
        """Check confirmations"""
        confirmations = 0
        
        if hasattr(tech, 'ema_trend') and tech.ema_trend in ["BULLISH", "BEARISH"]:
            confirmations += 1
        if hasattr(tech, 'macd_trend') and tech.macd_trend in ["BULLISH", "BEARISH"]:
            confirmations += 1
        if hasattr(tech, 'rsi_signal') and tech.rsi_signal in ["OVERSOLD", "OVERBOUGHT"]:
            confirmations += 1.5
        if hasattr(tech, 'adx') and isinstance(tech.adx, (int, float)) and tech.adx > 35:
            confirmations += 1
        
        if ob and hasattr(ob, 'imbalance'):
            try:
                imbalance = float(ob.imbalance)
                if abs(imbalance) > 20:
                    confirmations += 1.5
                elif abs(imbalance) > 10:
                    confirmations += 1
            except:
                pass
        
        if ob and hasattr(ob, 'bid_ask_ratio'):
            try:
                ratio = float(ob.bid_ask_ratio)
                if ratio > 1.3 or ratio < 0.7:
                    confirmations += 1
            except:
                pass
        
        if hasattr(multi_tf, 'regime_alignment'):
            try:
                alignment = float(multi_tf.regime_alignment)
                if alignment > 70:
                    confirmations += 1.5
            except:
                pass
        
        confirmations += 2 if whale_signal else 0
        confirmations += 2 if key_zone_entry else 0
        
        if isinstance(direction_confidence, (int, float)):
            if direction_confidence > 80:
                confirmations += 2
            elif direction_confidence > 70:
                confirmations += 1.5
            elif direction_confidence > 60:
                confirmations += 1
        
        return confirmations >= 6
    
    def _build_signal(self, symbol: str, base_analysis: Tuple, tech_score: float,
                      flow_score: float, direction: str, tier: SignalTier,
                      multi_tf_regime: MultiTimeframeRegime, ultimate_result: Optional[Dict],
                      direction_confidence: float, whale_activity: Any = None,
                      whale_signal: bool = False, whale_confidence: float = 0.0,
                      whale_description: Optional[str] = None,
                      key_zones: List[KeyZone] = None,
                      active_key_zone: Optional[KeyZone] = None,
                      key_zone_entry: bool = False, key_zone_confidence: float = 0.0,
                      pullback_detected: bool = False, pullback_percent: Optional[float] = None,
                      pullback_entry_price: Optional[float] = None,
                      dome_detected: bool = False, dome_type: Optional[str] = None,
                      dome_height: Optional[float] = None) -> EnhancedHighConfidenceSignal:
        """Build enhanced signal"""
        from datetime import datetime
        
        current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
        
        # Volume
        volume_24h = 0
        if ticker and isinstance(ticker, dict):
            try:
                volume_24h = float(ticker.get('quoteVolume', 0))
            except:
                volume_24h = 0
        
        # Stop loss
        stop_loss, stop_percentage, atr_value = self.parent.calculate_atr_stop_loss(current_price, direction, df_1h)
        
        # Entry data
        entry_data = self.parent.get_style_entries(symbol, direction, current_price, df_1h, "INTRADAY")
        
        # Entry price
        if direction == "BUY":
            if active_key_zone and key_zone_entry:
                entry_price = active_key_zone.zone_high
                entry_logic = f"Key zone support at {active_key_zone.zone_high:.4f}"
            elif entry_data and 'intraday' in entry_data:
                entry_price = float(entry_data['intraday']['price'])
                entry_logic = str(entry_data['intraday'].get('logic', 'Intraday entry'))
            else:
                entry_price = current_price * 0.995
                entry_logic = "Default entry"
        else:
            if active_key_zone and key_zone_entry:
                entry_price = active_key_zone.zone_low
                entry_logic = f"Key zone resistance at {active_key_zone.zone_low:.4f}"
            elif entry_data and 'intraday' in entry_data:
                entry_price = float(entry_data['intraday']['price'])
                entry_logic = str(entry_data['intraday'].get('logic', 'Intraday entry'))
            else:
                entry_price = current_price * 1.005
                entry_logic = "Default entry"
        
        entry_low = entry_price * 0.998
        entry_high = entry_price * 1.002
        
        # Recalculate stop loss
        stop_loss, stop_percentage, atr_value = self.parent.calculate_atr_stop_loss(entry_price, direction, df_1h)
        
        # TP levels
        if direction == "BUY":
            tp1 = entry_price + (entry_price - stop_loss) * 1.5
            tp2 = entry_price + (entry_price - stop_loss) * 2.5
            tp3 = entry_price + (entry_price - stop_loss) * 4.0
        else:
            tp1 = entry_price - (stop_loss - entry_price) * 1.5
            tp2 = entry_price - (stop_loss - entry_price) * 2.5
            tp3 = entry_price - (stop_loss - entry_price) * 4.0
        
        # Leverage
        leverage = self._calculate_leverage(multi_tf_regime, key_zone_entry)
        
        # Risk reward
        risk_reward = RiskRewardAnalysis(
            risk_percentage=stop_percentage,
            reward_1_percentage=abs(tp1 - entry_price) / entry_price * 100,
            reward_2_percentage=abs(tp2 - entry_price) / entry_price * 100,
            reward_3_percentage=abs(tp3 - entry_price) / entry_price * 100,
            rr_ratio_1=abs(tp1 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            rr_ratio_2=abs(tp2 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            rr_ratio_3=abs(tp3 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            expected_value=(abs(tp1 - entry_price) * 0.5 - abs(stop_loss - entry_price) * 0.5) / entry_price * 100,
            scalping_target_1=0, scalping_target_2=0,
            intraday_target_1=abs(tp1 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            intraday_target_2=abs(tp2 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            swing_target_1=0, swing_target_2=0,
            position_target_1=0, position_target_2=0
        )
        
        # Primary reasons
        primary_reasons = [
            f"Direction: {direction} with {direction_confidence:.1f}% confidence",
            f"Tech score: {tech_score:+.0f}, Flow score: {flow_score:+.0f}",
            f"Regime: {multi_tf_regime.overall_regime} ({multi_tf_regime.regime_alignment:.0f}% aligned)"
        ]
        
        if key_zone_entry and active_key_zone:
            primary_reasons.insert(0, f"🎯 Key zone: {active_key_zone.zone_type} (strength: {active_key_zone.zone_strength:.0f}%)")
        
        signal_type = "STRONG_BUY" if direction == "BUY" else "STRONG_SELL"
        risk_level = self._get_risk_level(multi_tf_regime, stop_percentage)
        primary_style = SignalStyle.INTRADAY
        
        # Create signal
        signal = EnhancedHighConfidenceSignal(
            timestamp=datetime.now(), symbol=symbol, signal_type=signal_type, confidence=85.0,
            current_price=current_price,
            best_bid=entry_data.get('best_bid', current_price * 0.999),
            best_ask=entry_data.get('best_ask', current_price * 1.001),
            spread=entry_data.get('best_ask', current_price * 1.001) - entry_data.get('best_bid', current_price * 0.999),
            spread_percentage=entry_data.get('spread_percent', 0.2),
            suggested_order_type=OrderType.LIMIT_BUY if direction == "BUY" else OrderType.LIMIT_SELL,
            entry_price=entry_price, entry_range_low=entry_low, entry_range_high=entry_high,
            optimal_entry_timeframe=entry_logic,
            stop_loss=stop_loss, stop_loss_percentage=stop_percentage,
            take_profit_1=tp1, take_profit_2=tp2, take_profit_3=tp3,
            recommended_leverage=leverage,
            rsi=tech.rsi if hasattr(tech, 'rsi') else 50.0,
            rsi_signal=tech.rsi_signal if hasattr(tech, 'rsi_signal') else "NEUTRAL",
            macd_trend=tech.macd_trend if hasattr(tech, 'macd_trend') else "NEUTRAL",
            ema_trend=tech.ema_trend if hasattr(tech, 'ema_trend') else "NEUTRAL",
            bb_position=tech.bb_position if hasattr(tech, 'bb_position') else "MIDDLE",
            buy_pressure=ob.buy_pressure if hasattr(ob, 'buy_pressure') else 50.0,
            sell_pressure=ob.sell_pressure if hasattr(ob, 'sell_pressure') else 50.0,
            bid_ask_ratio=ob.bid_ask_ratio if hasattr(ob, 'bid_ask_ratio') else 1.0,
            cumulative_delta_15min=cf.delta_15min if hasattr(cf, 'delta_15min') else 0.0,
            delta_trend=cf.trend_strength if hasattr(cf, 'trend_strength') else "NEUTRAL",
            volume_24h=volume_24h,
            volume_change_24h=float(ticker.get('priceChangePercent', 0)) if ticker else 0.0,
            funding_rate=0.0, funding_sentiment="NEUTRAL",
            open_interest=None, oi_change_1h=None,
            support_levels=ob.support_levels if hasattr(ob, 'support_levels') else [],
            resistance_levels=ob.resistance_levels if hasattr(ob, 'resistance_levels') else [],
            nearest_support=ob.support_levels[0] if ob.support_levels else current_price * 0.98,
            nearest_resistance=ob.resistance_levels[0] if ob.resistance_levels else current_price * 1.02,
            primary_reasons=primary_reasons, secondary_reasons=[],
            aligned_styles=[], style_scores={}, recommendation="", risk_level=risk_level,
            time_horizon="INTRADAY", market_regime=None, multi_tf_regime=multi_tf_regime,
            smart_money=None, market_profile=None, intermarket=None, onchain=None,
            sentiment=None, divergence=None, patterns=None, liquidity=None, timeframe_confluence=None,
            enhanced_tech=tech, overall_accuracy_score=85.0, risk_adjusted_confidence=85.0,
            expected_move=abs(tp1 - entry_price) / entry_price * 100, optimal_position_size=1.0,
            tech_score=tech_score, flow_score=flow_score,
            backtest_result=None, market_context=None, risk_reward=risk_reward, confirmations=None,
            bot_win_rate=0.0, signals_last_100=0, win_rate_last_100=0.0,
            entry_timeframe_3m_signal=None, entry_timeframe_5m_signal=None,
            tier=tier, tier_confidence=direction_confidence, smart_scan_score=0.0,
            adaptive_cooldown_minutes=15,
            entry_bid_level=entry_data.get('best_bid'), entry_ask_level=entry_data.get('best_ask'),
            entry_mid_price=entry_data.get('mid'), order_book_imbalance=entry_data.get('imbalance', 0.0),
            ultra_short_regime_aligned="BULL" in multi_tf_regime.ultra_short_regime if direction == "BUY" else "BEAR" in multi_tf_regime.ultra_short_regime,
            short_regime_aligned="BULL" in multi_tf_regime.short_regime if direction == "BUY" else "BEAR" in multi_tf_regime.short_regime,
            medium_regime_aligned="BULL" in multi_tf_regime.medium_regime if direction == "BUY" else "BEAR" in multi_tf_regime.medium_regime,
            long_regime_aligned="BULL" in multi_tf_regime.long_regime if direction == "BUY" else "BEAR" in multi_tf_regime.long_regime,
            scalping_entry=None, intraday_entry=None, swing_entry=None, position_entry=None,
            scalping_tp1=None, scalping_tp2=None, scalping_tp3=None,
            intraday_tp1=None, intraday_tp2=None, intraday_tp3=None,
            swing_tp1=None, swing_tp2=None, swing_tp3=None,
            position_tp1=None, position_tp2=None, position_tp3=None,
            primary_style=primary_style, secondary_styles=[], style_confidence={},
            smart_money_display=None, atr_stop_loss=None, atr_value=atr_value,
            atr_multiplier=self.config.ATR_MULTIPLIER,
            volume_profile_entry=None,
            volume_poc_price=entry_data.get('poc_price', current_price) if entry_data else current_price,
            volume_value_area_low=entry_data.get('value_area_low', current_price * 0.98) if entry_data else current_price * 0.98,
            volume_value_area_high=entry_data.get('value_area_high', current_price * 1.02) if entry_data else current_price * 1.02,
            liquidity_grab=None, liquidity_grab_detected=False, liquidity_grab_type="NONE", liquidity_grab_strength=0.0,
            trend_filter_200ema=None, ema_200=0.0, price_vs_ema_200="UNKNOWN", ema_200_trend="UNKNOWN", trend_filter_passed=True,
            ai_confidence=85.0, ai_confidence_prediction=0.0, ai_confidence_in_prediction=0.0, ai_model_used=False,
            alert_level=None, is_confirmed=True,
            calculated_imbalance=entry_data.get('imbalance', 0.0), volume_ratio_24h=1.0, avg_volume_24h=volume_24h,
            ultimate_direction_confidence=direction_confidence, ultimate_analysis=ultimate_result,
            whale_activity=whale_activity, whale_signal=whale_signal, whale_confidence=whale_confidence,
            whale_description=whale_description,
            key_zones=key_zones or [], active_key_zone=active_key_zone,
            key_zone_entry=key_zone_entry, key_zone_confidence=key_zone_confidence,
            pullback_detected=pullback_detected, pullback_percent=pullback_percent, pullback_entry_price=pullback_entry_price,
            dome_detected=dome_detected, dome_type=dome_type, dome_height=dome_height,
            tp_levels={'tp1': tp1, 'tp2': tp2, 'tp3': tp3},
            tp_description=f"TP1: {abs(tp1-entry_price)/entry_price*100:.1f}%, TP2: {abs(tp2-entry_price)/entry_price*100:.1f}%, TP3: {abs(tp3-entry_price)/entry_price*100:.1f}%",
            ml_predictions=None,
            candle_patterns=None, support_resistance=None, market_profile_analysis=None,
            order_flow_analysis=None, smart_money_analysis=None
        )
        
        return self._validate_signal(signal, direction, current_price)
    
    def _calculate_leverage(self, multi_tf: MultiTimeframeRegime, key_zone_entry: bool = False) -> int:
        """Calculate leverage"""
        leverage = 5
        
        if hasattr(multi_tf, 'overall_regime'):
            if "STRONG" in multi_tf.overall_regime:
                leverage = 10
            elif "WEAK" in multi_tf.overall_regime:
                leverage = 3
        
        if hasattr(multi_tf, 'ultra_short_volatility'):
            if multi_tf.ultra_short_volatility == "LOW":
                leverage = int(leverage * 1.3)
            elif multi_tf.ultra_short_volatility == "HIGH":
                leverage = int(leverage * 0.7)
        
        if key_zone_entry:
            leverage = int(leverage * 1.15)
        
        return max(2, min(25, leverage))
    
    def _check_regime_alignment(self, direction: str, multi_tf: MultiTimeframeRegime) -> bool:
        """Check regime alignment"""
        if direction == "BUY":
            count = 0
            if "BULL" in multi_tf.ultra_short_regime: count += 1
            if "BULL" in multi_tf.short_regime: count += 2
            if "BULL" in multi_tf.medium_regime: count += 2
            if "BULL" in multi_tf.long_regime: count += 1
            return count >= 3
        else:
            count = 0
            if "BEAR" in multi_tf.ultra_short_regime: count += 1
            if "BEAR" in multi_tf.short_regime: count += 2
            if "BEAR" in multi_tf.medium_regime: count += 2
            if "BEAR" in multi_tf.long_regime: count += 1
            return count >= 3
    
    def _check_order_book_entry(self, ob: Any, direction: str) -> bool:
        """Check order book entry"""
        if not ob:
            return True
        try:
            imbalance = float(getattr(ob, 'imbalance', 0))
            buy_pressure = float(getattr(ob, 'buy_pressure', 50))
            sell_pressure = float(getattr(ob, 'sell_pressure', 50))
            if direction == "BUY":
                return imbalance > 5 and buy_pressure > 51
            else:
                return imbalance < -5 and sell_pressure > 51
        except:
            return True
    
    def _get_risk_level(self, multi_tf: MultiTimeframeRegime, stop_percentage: float) -> str:
        """Get risk level"""
        risk = "LOW" if stop_percentage < 1.0 else "MEDIUM" if stop_percentage < 2.0 else "HIGH"
        if hasattr(multi_tf, 'ultra_short_volatility') and multi_tf.ultra_short_volatility == "HIGH":
            risk = "MEDIUM" if risk == "LOW" else "HIGH" if risk == "MEDIUM" else risk
        return risk
    
    def _validate_signal(self, signal: EnhancedHighConfidenceSignal, 
                         direction: str, current_price: float) -> EnhancedHighConfidenceSignal:
        """Validate signal"""
        try:
            if abs(signal.entry_price - current_price) / current_price > 0.05:
                signal.entry_price = current_price
                signal.entry_range_low = current_price * 0.998
                signal.entry_range_high = current_price * 1.002
                signal.optimal_entry_timeframe = "Corrected: Using current price"
            
            if abs(signal.stop_loss - signal.entry_price) < 1e-8:
                if direction == "BUY":
                    signal.stop_loss = signal.entry_price * 0.99
                    signal.stop_loss_percentage = 1.0
                else:
                    signal.stop_loss = signal.entry_price * 1.01
                    signal.stop_loss_percentage = 1.0
            
            if direction == "BUY" and signal.take_profit_1 <= signal.entry_price:
                risk = abs(signal.entry_price - signal.stop_loss)
                signal.take_profit_1 = signal.entry_price + risk * 1.5
                signal.take_profit_2 = signal.entry_price + risk * 2.5
                signal.take_profit_3 = signal.entry_price + risk * 4.0
            
            if direction == "SELL" and signal.take_profit_1 >= signal.entry_price:
                risk = abs(signal.entry_price - signal.stop_loss)
                signal.take_profit_1 = signal.entry_price - risk * 1.5
                signal.take_profit_2 = signal.entry_price - risk * 2.5
                signal.take_profit_3 = signal.entry_price - risk * 4.0
        except Exception as e:
            logger.error(f"Validation error: {e}")
        
        return signal


# ==============================================================================
# TIER 2 GENERATOR
# ==============================================================================

class Tier2Generator(Tier1Generator):
    """Tier 2 Balanced signal generator"""
    
    def __init__(self, parent: EnhancedTieredSignalGenerator):
        super().__init__(parent)
        self.recent_signals = deque(maxlen=50)
    
    def generate(self, symbol: str, base_analysis: Tuple, 
                 multi_tf_regime: 'MultiTimeframeRegime') -> Optional[EnhancedHighConfidenceSignal]:
        """Generate Tier 2 signal"""
        try:
            if self._has_recent_signal(symbol, 30):
                return None
            
            current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
            
            tech_score = self.parent.calculate_technical_score(tech)
            flow_score = self.parent.calculate_order_flow_score(ob, mt, cf)
            
            tech_threshold, flow_threshold = self._get_dynamic_thresholds(multi_tf_regime)
            
            if abs(tech_score) < tech_threshold or abs(flow_score) < flow_threshold:
                return None
            
            combined = tech_score * 0.45 + flow_score * 0.55
            direction = "BUY" if combined > 15 else "SELL" if combined < -15 else None
            if not direction:
                return None
            
            if not self._check_basic_regime_alignment(direction, multi_tf_regime):
                return None
            
            if not self._safety_checks(tech, ob, multi_tf_regime):
                return None
            
            key_zones = self.keyzone_detector.detect_zones(df_1h, current_price)
            active_zone = self.keyzone_detector.get_best_entry_zone(direction, current_price)
            
            signal = self._build_signal(
                symbol, base_analysis, tech_score, flow_score, direction,
                SignalTier.TIER_2_BALANCED, multi_tf_regime, None, 70,
                None, False, 0, None, key_zones, active_zone,
                active_zone is not None, active_zone.zone_strength if active_zone else 0
            )
            signal.adaptive_cooldown_minutes = 10
            self.recent_signals.append((symbol, time.time()))
            return signal
            
        except Exception as e:
            logger.error(f"Tier2 error for {symbol}: {e}")
            return None
    
    def _has_recent_signal(self, symbol: str, minutes: int) -> bool:
        current_time = time.time()
        for sym, ts in self.recent_signals:
            if sym == symbol and (current_time - ts) < minutes * 60:
                return True
        return False
    
    def _get_dynamic_thresholds(self, multi_tf: MultiTimeframeRegime) -> Tuple[float, float]:
        base_tech = self.config.TIER_2_TECH_THRESHOLD
        base_flow = self.config.TIER_2_FLOW_THRESHOLD
        if hasattr(multi_tf, 'ultra_short_volatility'):
            if multi_tf.ultra_short_volatility == "HIGH":
                return base_tech * 1.2, base_flow * 1.2
            elif multi_tf.ultra_short_volatility == "LOW":
                return base_tech * 0.8, base_flow * 0.8
        return base_tech, base_flow
    
    def _check_basic_regime_alignment(self, direction: str, multi_tf: MultiTimeframeRegime) -> bool:
        if direction == "BUY":
            return "BULL" in multi_tf.ultra_short_regime or "BULL" in multi_tf.short_regime
        else:
            return "BEAR" in multi_tf.ultra_short_regime or "BEAR" in multi_tf.short_regime
    
    def _safety_checks(self, tech: Any, ob: Any, multi_tf: MultiTimeframeRegime) -> bool:
        if hasattr(tech, 'rsi'):
            try:
                rsi = float(tech.rsi)
                if rsi > 85 or rsi < 15:
                    return False
            except:
                pass
        if ob and hasattr(ob, 'spread_percentage'):
            try:
                if float(ob.spread_percentage) > 0.1:
                    return False
            except:
                pass
        return True


# ==============================================================================
# TIER 3 GENERATOR
# ==============================================================================

class Tier3Generator(Tier2Generator):
    """Tier 3 Aggressive signal generator"""
    
    def __init__(self, parent: EnhancedTieredSignalGenerator):
        super().__init__(parent)
        self.signal_count = defaultdict(int)
    
    def generate(self, symbol: str, base_analysis: Tuple, 
                 multi_tf_regime: 'MultiTimeframeRegime') -> Optional[EnhancedHighConfidenceSignal]:
        """Generate Tier 3 signal"""
        try:
            if self.signal_count[symbol] >= 4:
                return None
            
            current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
            
            tech_score = self.parent.calculate_technical_score(tech)
            flow_score = self.parent.calculate_order_flow_score(ob, mt, cf)
            
            if abs(tech_score) < self.config.TIER_3_TECH_THRESHOLD:
                return None
            if abs(flow_score) < self.config.TIER_3_FLOW_THRESHOLD:
                return None
            
            combined = tech_score * 0.5 + flow_score * 0.5
            direction = "BUY" if combined > 10 else "SELL" if combined < -10 else None
            if not direction:
                return None
            
            if not self._basic_safety_check(tech, ob):
                return None
            
            self.signal_count[symbol] += 1
            
            signal = self._build_signal(
                symbol, base_analysis, tech_score, flow_score, direction,
                SignalTier.TIER_3_AGGRESSIVE, multi_tf_regime, None, 60
            )
            signal.adaptive_cooldown_minutes = 5
            return signal
            
        except Exception as e:
            logger.error(f"Tier3 error for {symbol}: {e}")
            return None
    
    def _basic_safety_check(self, tech: Any, ob: Any) -> bool:
        if hasattr(tech, 'rsi'):
            try:
                rsi = float(tech.rsi)
                if rsi > 90 or rsi < 10:
                    return False
            except:
                pass
        if ob and hasattr(ob, 'spread_percentage'):
            try:
                if float(ob.spread_percentage) > 0.2:
                    return False
            except:
                pass
        return True
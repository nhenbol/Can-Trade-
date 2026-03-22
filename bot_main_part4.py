#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ULTIMATE HYBRID CRYPTO TRADING BOT - MAIN BOT PART 4
Ultimate Analyzers, Market Scanner, Backtest Engine, Documentation Generator,
Telegram Notifier, Binance Client, Main Bot Class, and Pro Trader Mode
================================================================================
Developer: Nhen Bol
Version: 12.0.1
================================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================
from bot_main_part3 import *
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from collections import defaultdict, deque
import threading
import logging
import numpy as np
import pandas as pd

# ==============================================================================
# ULTIMATE DIRECTION ANALYZER
# ==============================================================================
class UltimateDirectionAnalyzer:
    """Ultimate direction analyzer combining multiple factors for high accuracy predictions"""
    
    def __init__(self, client):
        self.client = client
        self.weights = {
            'regime': 0.20,
            'correlation': 0.15,
            'volume': 0.20,
            'sentiment': 0.15,
            'divergence': 0.15,
            'smart_money': 0.15
        }
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    def analyze(self, symbol: str, df_4h: pd.DataFrame, df_1h: pd.DataFrame, df_15m: pd.DataFrame,
                multi_tf_regime: Any, smart_money: Any,
                ob: Any, tech: Any,
                funding_rate: float) -> Tuple[str, float, Dict]:
        """
        Analyze market direction using multiple factors
        
        Args:
            symbol: Trading symbol
            df_4h: 4-hour dataframe
            df_1h: 1-hour dataframe
            df_15m: 15-minute dataframe
            multi_tf_regime: Multi-timeframe regime analysis
            smart_money: Smart money analysis
            ob: Order book analysis
            tech: Technical analysis
            funding_rate: Current funding rate
            
        Returns:
            Tuple of (direction, confidence, detailed_results)
        """
        try:
            cache_key = f"{symbol}_{int(time.time()/300)}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            all_reasons = []
            detailed_scores = {}
            total_score = {'BUY': 0.0, 'SELL': 0.0}
            
            # 1. Regime analysis
            regime_score = self._analyze_regime(multi_tf_regime)
            detailed_scores['regime'] = regime_score
            total_score['BUY'] += regime_score['BUY'] * self.weights['regime']
            total_score['SELL'] += regime_score['SELL'] * self.weights['regime']
            if regime_score['BUY'] > 0.5:
                all_reasons.append(f"📊 Bullish regime")
            elif regime_score['SELL'] > 0.5:
                all_reasons.append(f"📊 Bearish regime")
            
            # 2. Correlation analysis
            correlation_score = self._analyze_correlation(symbol)
            detailed_scores['correlation'] = correlation_score
            total_score['BUY'] += correlation_score['BUY'] * self.weights['correlation']
            total_score['SELL'] += correlation_score['SELL'] * self.weights['correlation']
            if correlation_score['BUY'] > 0.3:
                all_reasons.append(f"🔄 Positive correlation")
            elif correlation_score['SELL'] > 0.3:
                all_reasons.append(f"🔄 Negative correlation")
            
            # 3. Volume profile analysis
            volume_score = self._analyze_volume(df_1h, ob)
            detailed_scores['volume'] = volume_score
            total_score['BUY'] += volume_score['BUY'] * self.weights['volume']
            total_score['SELL'] += volume_score['SELL'] * self.weights['volume']
            if volume_score['BUY'] > 0.4:
                all_reasons.append(f"📊 Strong buying volume")
            elif volume_score['SELL'] > 0.4:
                all_reasons.append(f"📊 Strong selling volume")
            
            # 4. Sentiment analysis
            sentiment_score = self._analyze_sentiment(funding_rate, tech)
            detailed_scores['sentiment'] = sentiment_score
            total_score['BUY'] += sentiment_score['BUY'] * self.weights['sentiment']
            total_score['SELL'] += sentiment_score['SELL'] * self.weights['sentiment']
            if sentiment_score['BUY'] > 0.3:
                all_reasons.append(f"😊 Positive sentiment")
            elif sentiment_score['SELL'] > 0.3:
                all_reasons.append(f"😔 Negative sentiment")
            
            # 5. Divergence analysis
            divergence_score = self._analyze_divergence(tech, df_1h)
            detailed_scores['divergence'] = divergence_score
            total_score['BUY'] += divergence_score['BUY'] * self.weights['divergence']
            total_score['SELL'] += divergence_score['SELL'] * self.weights['divergence']
            if divergence_score['BUY'] > 0.2:
                all_reasons.append(f"📈 Bullish divergence")
            elif divergence_score['SELL'] > 0.2:
                all_reasons.append(f"📉 Bearish divergence")
            
            # 6. Smart money analysis
            smart_money_score = self._analyze_smart_money(smart_money, ob)
            detailed_scores['smart_money'] = smart_money_score
            total_score['BUY'] += smart_money_score['BUY'] * self.weights['smart_money']
            total_score['SELL'] += smart_money_score['SELL'] * self.weights['smart_money']
            if smart_money_score['BUY'] > 0.3:
                all_reasons.append(f"🧠 Smart money buying")
            elif smart_money_score['SELL'] > 0.3:
                all_reasons.append(f"🧠 Smart money selling")
            
            # Calculate final scores
            total_possible = sum(self.weights.values())
            buy_final = (total_score['BUY'] / total_possible) * 100
            sell_final = (total_score['SELL'] / total_possible) * 100
            
            # Determine direction
            if buy_final > sell_final + 15:
                direction = "BUY"
                confidence = min(buy_final, 95)
                all_reasons.append(f"✅ FINAL: BUY ({confidence:.1f}%)")
            elif sell_final > buy_final + 15:
                direction = "SELL"
                confidence = min(sell_final, 95)
                all_reasons.append(f"✅ FINAL: SELL ({confidence:.1f}%)")
            else:
                # Use longer timeframe as tiebreaker
                if hasattr(multi_tf_regime, 'long_regime') and "BULL" in multi_tf_regime.long_regime:
                    direction = "BUY"
                    confidence = 55
                    all_reasons.append(f"⚠️ Neutral - leaning BULL")
                elif hasattr(multi_tf_regime, 'long_regime') and "BEAR" in multi_tf_regime.long_regime:
                    direction = "SELL"
                    confidence = 55
                    all_reasons.append(f"⚠️ Neutral - leaning BEAR")
                else:
                    direction = "NEUTRAL"
                    confidence = 50
                    all_reasons.append(f"⚠️ No clear direction")
            
            result = {
                'direction': direction,
                'confidence': confidence,
                'reasons': all_reasons[:5],
                'scores': detailed_scores,
                'buy_score': buy_final,
                'sell_score': sell_final
            }
            
            # Cache result
            self.cache[cache_key] = (direction, confidence, result)
            
            return direction, confidence, result
            
        except Exception as e:
            logger.error(f"Ultimate direction analysis error for {symbol}: {e}")
            return "NEUTRAL", 50, {'reasons': ['Analysis error']}
    
    def _analyze_regime(self, multi_tf_regime: Any) -> Dict[str, float]:
        """Analyze market regime contribution"""
        score = {'BUY': 0.0, 'SELL': 0.0}
        
        if not multi_tf_regime:
            return score
        
        # Overall regime
        if hasattr(multi_tf_regime, 'overall_regime'):
            if "BULL" in str(multi_tf_regime.overall_regime).upper():
                score['BUY'] += 0.8
            elif "BEAR" in str(multi_tf_regime.overall_regime).upper():
                score['SELL'] += 0.8
        
        # Alignment
        if hasattr(multi_tf_regime, 'regime_alignment'):
            try:
                alignment = float(multi_tf_regime.regime_alignment)
                if alignment > 80:
                    if score['BUY'] > 0:
                        score['BUY'] += 0.4
                    elif score['SELL'] > 0:
                        score['SELL'] += 0.4
            except (TypeError, ValueError):
                pass
        
        # Strength
        if hasattr(multi_tf_regime, 'overall_strength'):
            try:
                strength = float(multi_tf_regime.overall_strength)
                if strength > 70:
                    if score['BUY'] > 0:
                        score['BUY'] += 0.3
                    elif score['SELL'] > 0:
                        score['SELL'] += 0.3
            except (TypeError, ValueError):
                pass
        
        return score
    
    def _analyze_correlation(self, symbol: str) -> Dict[str, float]:
        """Analyze correlation with major assets"""
        score = {'BUY': 0.0, 'SELL': 0.0}
        
        try:
            # Simple correlation based on symbol type
            symbol_upper = symbol.upper()
            if "BTC" in symbol_upper:
                score['BUY'] += 0.2
                score['SELL'] += 0.2
            elif "ETH" in symbol_upper:
                score['BUY'] += 0.15
                score['SELL'] += 0.15
            else:
                score['BUY'] += 0.1
                score['SELL'] += 0.1
        except Exception:
            pass
        
        return score
    
    def _analyze_volume(self, df: pd.DataFrame, ob: Any) -> Dict[str, float]:
        """Analyze volume profile and order flow"""
        score = {'BUY': 0.0, 'SELL': 0.0}
        
        try:
            if df is not None and len(df) > 20:
                # Volume trend
                recent_volume = float(df['volume'].iloc[-5:].mean())
                avg_volume = float(df['volume'].iloc[-20:].mean())
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
                
                if volume_ratio > 1.5:
                    score['BUY'] += 0.3
                    score['SELL'] += 0.3
                elif volume_ratio > 1.2:
                    score['BUY'] += 0.2
                    score['SELL'] += 0.2
                
                # Price action
                current = float(df['close'].iloc[-1])
                prev = float(df['close'].iloc[-2])
                if current > prev:
                    score['BUY'] += 0.2
                else:
                    score['SELL'] += 0.2
            
            # Order book imbalance
            if ob and hasattr(ob, 'imbalance'):
                try:
                    imbalance = float(ob.imbalance)
                    if imbalance > 20:
                        score['BUY'] += 0.4
                    elif imbalance < -20:
                        score['SELL'] += 0.4
                    elif imbalance > 10:
                        score['BUY'] += 0.2
                    elif imbalance < -10:
                        score['SELL'] += 0.2
                except (TypeError, ValueError):
                    pass
                    
        except Exception as e:
            logger.error(f"Volume analysis error: {e}")
        
        return score
    
    def _analyze_sentiment(self, funding_rate: float, tech: Any) -> Dict[str, float]:
        """Analyze market sentiment from funding rate and technicals"""
        score = {'BUY': 0.0, 'SELL': 0.0}
        
        try:
            # Funding rate sentiment
            if funding_rate > 0.01:
                score['SELL'] += 0.3  # Too bullish, potential reversal
            elif funding_rate < -0.01:
                score['BUY'] += 0.3   # Too bearish, potential reversal
            elif funding_rate > 0.005:
                score['BUY'] += 0.2    # Mildly bullish
            elif funding_rate < -0.005:
                score['SELL'] += 0.2   # Mildly bearish
            
            # RSI sentiment
            if tech and hasattr(tech, 'rsi'):
                try:
                    rsi = float(tech.rsi)
                    if rsi > 70:
                        score['SELL'] += 0.3  # Overbought
                    elif rsi < 30:
                        score['BUY'] += 0.3   # Oversold
                    elif rsi > 60:
                        score['BUY'] += 0.2   # Bullish
                    elif rsi < 40:
                        score['SELL'] += 0.2  # Bearish
                except (TypeError, ValueError):
                    pass
                    
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
        
        return score
    
    def _analyze_divergence(self, tech: Any, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze price/indicator divergences"""
        score = {'BUY': 0.0, 'SELL': 0.0}
        
        try:
            if df is not None and len(df) > 30 and tech and hasattr(tech, 'rsi'):
                prices = df['close'].iloc[-10:].values
                try:
                    rsi = float(tech.rsi)
                    # Simplified divergence check
                    if len(prices) >= 5:
                        if prices[-1] > prices[-5] and rsi < 50:
                            score['SELL'] += 0.3  # Bearish divergence
                        elif prices[-1] < prices[-5] and rsi > 50:
                            score['BUY'] += 0.3   # Bullish divergence
                except (TypeError, ValueError, IndexError):
                    pass
        except Exception:
            pass
        
        return score
    
    def _analyze_smart_money(self, smart_money: Any, ob: Any) -> Dict[str, float]:
        """Analyze smart money concepts and order flow"""
        score = {'BUY': 0.0, 'SELL': 0.0}
        
        try:
            if smart_money and hasattr(smart_money, 'smart_money_score'):
                try:
                    sm_score = float(smart_money.smart_money_score)
                    if sm_score > 50:
                        score['BUY'] += 0.4
                    elif sm_score < -50:
                        score['SELL'] += 0.4
                except (TypeError, ValueError):
                    pass
            
            # Order book pressure
            if ob and hasattr(ob, 'buy_pressure') and hasattr(ob, 'sell_pressure'):
                try:
                    buy = float(ob.buy_pressure)
                    sell = float(ob.sell_pressure)
                    if buy > 60:
                        score['BUY'] += 0.3
                    elif sell > 60:
                        score['SELL'] += 0.3
                except (TypeError, ValueError):
                    pass
                    
        except Exception as e:
            logger.error(f"Smart money analysis error: {e}")
        
        return score


# ==============================================================================
# MARKET SCANNER
# ==============================================================================
class MarketScanner:
    """Market scanner to find best trading opportunities based on multiple factors"""
    
    def __init__(self, client: Any):
        self.client = client
        self.symbol_scores = {}
        self.cache = {}
        self.cache_timeout = 60  # 1 minute cache
        
    def scan_all_symbols(self, symbols: List[str]) -> List[Tuple[str, float]]:
        """
        Scan all symbols and return ranked list by opportunity score
        
        Args:
            symbols: List of symbols to scan
            
        Returns:
            List of tuples (symbol, score) sorted by score descending
        """
        scores = []
        current_time = time.time()
        
        logger.info(f"Scanning {len(symbols)} symbols for opportunities...")
        
        for i, symbol in enumerate(symbols):
            # Check cache first
            if symbol in self.cache:
                score, timestamp = self.cache[symbol]
                if current_time - timestamp < self.cache_timeout:
                    if score > 0:
                        scores.append((symbol, score))
                    continue
            
            # Calculate new score
            score = self._calculate_opportunity_score(symbol)
            self.cache[symbol] = (score, current_time)
            
            if score > 0:
                scores.append((symbol, score))
            
            # Show progress every 10 symbols
            if (i + 1) % 10 == 0:
                logger.info(f"  Scanned {i + 1}/{len(symbols)} symbols...")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        # Sort by score descending
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        
        # Log top symbols
        if sorted_scores:
            top_10 = [f"{s[0]}({s[1]:.0f})" for s in sorted_scores[:10]]
            logger.info(f"🎯 Top 10 opportunities: {', '.join(top_10)}")
        else:
            logger.info("🎯 No opportunities found in this scan")
        
        return sorted_scores
    
    def _calculate_opportunity_score(self, symbol: str) -> float:
        """
        Calculate opportunity score for a symbol (0-100)
        
        Factors considered:
        - 24h volume (0-30 points)
        - Price change (0-25 points)
        - Volatility (0-20 points)
        - Trend strength (0-15 points)
        - Momentum (0-10 points)
        """
        try:
            score = 0
            reasons = []
            
            # Get 24hr ticker data
            ticker = self.client.get_ticker_24hr(symbol)
            if not ticker or not isinstance(ticker, dict):
                return 0
            
            # 1. Volume score (0-30 points)
            try:
                volume = float(ticker.get('quoteVolume', 0))
                if volume > 100_000_000:
                    score += 30
                    reasons.append(f"Vol:{volume/1e6:.0f}M")
                elif volume > 50_000_000:
                    score += 28
                    reasons.append(f"Vol:{volume/1e6:.0f}M")
                elif volume > 20_000_000:
                    score += 25
                    reasons.append(f"Vol:{volume/1e6:.0f}M")
                elif volume > 10_000_000:
                    score += 22
                    reasons.append(f"Vol:{volume/1e6:.0f}M")
                elif volume > 5_000_000:
                    score += 20
                    reasons.append(f"Vol:{volume/1e6:.0f}M")
                elif volume > 2_000_000:
                    score += 15
                    reasons.append(f"Vol:{volume/1e6:.1f}M")
                elif volume > 1_000_000:
                    score += 12
                    reasons.append(f"Vol:{volume/1e6:.1f}M")
                elif volume > 500_000:
                    score += 10
                    reasons.append(f"Vol:{volume/1e6:.1f}M")
                elif volume > 250_000:
                    score += 5
                    reasons.append(f"Vol:{volume/1e6:.1f}M")
            except (TypeError, ValueError):
                pass
            
            # 2. Price change score (0-25 points)
            try:
                price_change = float(ticker.get('priceChangePercent', 0))
                abs_change = abs(price_change)
                
                if abs_change > 20:
                    score += 25
                    reasons.append(f"Move:{price_change:+.0f}%")
                elif abs_change > 15:
                    score += 22
                    reasons.append(f"Move:{price_change:+.0f}%")
                elif abs_change > 10:
                    score += 20
                    reasons.append(f"Move:{price_change:+.0f}%")
                elif abs_change > 7:
                    score += 18
                    reasons.append(f"Move:{price_change:+.0f}%")
                elif abs_change > 5:
                    score += 15
                    reasons.append(f"Move:{price_change:+.0f}%")
                elif abs_change > 3:
                    score += 12
                    reasons.append(f"Move:{price_change:+.0f}%")
                elif abs_change > 2:
                    score += 8
                    reasons.append(f"Move:{price_change:+.0f}%")
                elif abs_change > 1:
                    score += 5
                    reasons.append(f"Move:{price_change:+.0f}%")
            except (TypeError, ValueError):
                pass
            
            # 3. Volatility score (0-20 points)
            try:
                high = float(ticker.get('highPrice', 0))
                low = float(ticker.get('lowPrice', 0))
                current = float(ticker.get('lastPrice', 0))
                
                if high > 0 and low > 0 and current > 0:
                    daily_range = ((high - low) / current) * 100
                    
                    if daily_range > 15:
                        score += 20
                        reasons.append(f"Range:{daily_range:.0f}%")
                    elif daily_range > 10:
                        score += 18
                        reasons.append(f"Range:{daily_range:.0f}%")
                    elif daily_range > 8:
                        score += 16
                        reasons.append(f"Range:{daily_range:.0f}%")
                    elif daily_range > 6:
                        score += 14
                        reasons.append(f"Range:{daily_range:.0f}%")
                    elif daily_range > 4:
                        score += 12
                        reasons.append(f"Range:{daily_range:.0f}%")
                    elif daily_range > 3:
                        score += 8
                        reasons.append(f"Range:{daily_range:.1f}%")
                    elif daily_range > 2:
                        score += 5
                        reasons.append(f"Range:{daily_range:.1f}%")
            except (TypeError, ValueError, ZeroDivisionError):
                pass
            
            # 4. Trend strength score (0-15 points)
            try:
                df_1h = self.client.get_klines(symbol, '1h', 24)
                if df_1h is not None and len(df_1h) >= 20:
                    # Calculate EMAs
                    ema9 = float(df_1h['close'].iloc[-9:].mean())
                    ema21 = float(df_1h['close'].iloc[-21:].mean())
                    current_price = float(df_1h['close'].iloc[-1])
                    
                    # Trend alignment
                    if current_price > ema9 > ema21:
                        score += 15
                        reasons.append("Uptrend")
                    elif current_price < ema9 < ema21:
                        score += 15
                        reasons.append("Downtrend")
                    elif current_price > ema9:
                        score += 10
                        reasons.append("Weak up")
                    elif current_price < ema9:
                        score += 10
                        reasons.append("Weak down")
                    
                    # Volatility from klines
                    returns = df_1h['close'].pct_change().dropna()
                    if len(returns) > 0:
                        volatility = float(returns.std() * 100 * np.sqrt(24))
                        if 30 <= volatility <= 80:
                            score += 5
                            reasons.append("Good vol")
            except Exception:
                pass
            
            # 5. Momentum score (0-10 points)
            try:
                if abs_change > 3 and volume > 1_000_000:
                    score += 10
                    reasons.append("Momentum")
                elif abs_change > 2 and volume > 500_000:
                    score += 7
                    reasons.append("Good mom")
                elif abs_change > 1 and volume > 250_000:
                    score += 5
                    reasons.append("Light mom")
            except Exception:
                pass
            
            # Log detailed score for high scores
            if score > 50:
                logger.debug(f"{symbol}: Score {score:.1f} - {', '.join(reasons)}")
            
            return min(score, 100)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Error calculating score for {symbol}: {e}")
            return 0
    
    def get_top_symbols(self, symbols: List[str], limit: int = 10) -> List[str]:
        """Get top N symbols by opportunity score"""
        ranked = self.scan_all_symbols(symbols)
        return [s[0] for s in ranked[:limit]]
    
    def get_symbol_score(self, symbol: str) -> float:
        """Get cached score for a symbol"""
        if symbol in self.cache:
            score, timestamp = self.cache[symbol]
            if time.time() - timestamp < self.cache_timeout:
                return score
        return self._calculate_opportunity_score(symbol)


# ==============================================================================
# ADAPTIVE COOLDOWN
# ==============================================================================
class AdaptiveCooldown:
    """Adaptive cooldown manager to prevent signal spam"""
    
    def __init__(self):
        self.last_signals = defaultdict(list)
        self.base_cooldown = {
            SignalTier.TIER_1_ULTRA_SAFE: 15,
            SignalTier.TIER_2_BALANCED: 10,
            SignalTier.TIER_3_AGGRESSIVE: 5
        }
        self.max_history = 10
        
    def can_send_signal(self, symbol: str, tier: SignalTier, market_regime: Any = None) -> bool:
        """
        Check if signal can be sent based on cooldown
        
        Args:
            symbol: Trading symbol
            tier: Signal tier
            market_regime: Current market regime for adaptive cooldown
            
        Returns:
            True if signal can be sent, False otherwise
        """
        if symbol not in self.last_signals or not self.last_signals[symbol]:
            return True
        
        # Get base cooldown
        cooldown = self.base_cooldown.get(tier, 10)
        
        # Adjust for volatility
        if market_regime and hasattr(market_regime, 'volatility'):
            if market_regime.volatility == "HIGH":
                cooldown *= 1.5
            elif market_regime.volatility == "LOW":
                cooldown *= 0.7
        
        # Check last signal time
        last_time = self.last_signals[symbol][-1]
        time_diff = (datetime.now() - last_time).total_seconds() / 60
        
        return time_diff >= cooldown
    
    def record_signal(self, symbol: str, tier: SignalTier):
        """Record a signal for cooldown tracking"""
        self.last_signals[symbol].append(datetime.now())
        
        # Keep only recent history
        if len(self.last_signals[symbol]) > self.max_history:
            self.last_signals[symbol].pop(0)
    
    def get_remaining_cooldown(self, symbol: str, tier: SignalTier) -> float:
        """Get remaining cooldown time in minutes"""
        if symbol not in self.last_signals or not self.last_signals[symbol]:
            return 0
        
        cooldown = self.base_cooldown.get(tier, 10)
        last_time = self.last_signals[symbol][-1]
        elapsed = (datetime.now() - last_time).total_seconds() / 60
        
        return max(0, cooldown - elapsed)


# ==============================================================================
# BACKTEST ENGINE
# ==============================================================================
class BacktestEngine:
    """Backtest engine for strategy validation and performance testing"""
    
    def __init__(self, client: Any):
        self.client = client
        self.backtest_results: Dict[str, BacktestResult] = {}
        self.signals_history: List[Dict] = []
        self.cache = {}
        
    def backtest_symbol(self, symbol: str, days: int = 30) -> Optional[BacktestResult]:
        """
        Run backtest for a symbol
        
        Args:
            symbol: Trading symbol
            days: Number of days to backtest
            
        Returns:
            BacktestResult object or None if insufficient data
        """
        try:
            cache_key = f"{symbol}_{days}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Get historical data
            df = self.client.get_klines(symbol, '1h', limit=days*24)
            if df is None or len(df) < 100:
                return None
            
            total_signals = 0
            winning_trades = 0
            losing_trades = 0
            total_pnl = 0.0
            max_drawdown = 0.0
            pnl_history = []
            
            # Simple backtest strategy based on EMA cross
            for i in range(50, len(df)-24):
                # Calculate indicators
                ema9 = float(df['close'].iloc[i-9:i].mean())
                ema21 = float(df['close'].iloc[i-21:i].mean())
                
                # Future return (12 hours)
                future_return = (float(df['close'].iloc[i+12]) / float(df['close'].iloc[i]) - 1) * 100
                
                # Signal logic
                if ema9 > ema21:  # Bullish
                    total_signals += 1
                    if future_return > 0:
                        winning_trades += 1
                        total_pnl += future_return
                    else:
                        losing_trades += 1
                        total_pnl += future_return
                    pnl_history.append(total_pnl)
                    
                elif ema9 < ema21:  # Bearish
                    total_signals += 1
                    if future_return < 0:
                        winning_trades += 1
                        total_pnl += abs(future_return)
                    else:
                        losing_trades += 1
                        total_pnl -= future_return
                    pnl_history.append(total_pnl)
            
            if total_signals == 0:
                return None
            
            # Calculate metrics
            win_rate = (winning_trades / total_signals) * 100 if total_signals > 0 else 0
            avg_profit = total_pnl / winning_trades if winning_trades > 0 else 0
            avg_loss = abs(total_pnl) / losing_trades if losing_trades > 0 else 0
            profit_factor = (winning_trades * avg_profit) / (losing_trades * avg_loss + 1e-10)
            
            # Calculate max drawdown
            running_peak = 0
            for value in pnl_history:
                if value > running_peak:
                    running_peak = value
                drawdown = (running_peak - value) / (running_peak + 1e-10) * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            max_drawdown = min(max_drawdown, 100.0)
            
            # Calculate Sharpe ratio
            returns = np.diff(pnl_history) if len(pnl_history) > 1 else [0]
            sharpe_ratio = (np.mean(returns) / (np.std(returns) + 1e-10)) * np.sqrt(365)
            
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
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Backtest error for {symbol}: {e}")
            return None
    
    def get_backtest_result(self, symbol: str) -> Optional[BacktestResult]:
        """Get backtest result for a symbol (cached or fresh)"""
        if symbol in self.backtest_results:
            result = self.backtest_results[symbol]
            # Refresh if older than 1 day
            if result.last_updated and (datetime.now() - result.last_updated).days >= 1:
                return self.backtest_symbol(symbol)
            return result
        return self.backtest_symbol(symbol)


# ==============================================================================
# DOCUMENTATION GENERATOR
# ==============================================================================
class DocumentationGenerator:
    """Generate comprehensive documentation for the bot"""
    
    def __init__(self, config: HybridConfig):
        self.config = config
        self.lang = lang
        
    def generate_all_documentation(self) -> str:
        """Generate all documentation files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_dir = f"documentation_{timestamp}"
        
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)
        
        self._generate_technical_docs(doc_dir)
        self._generate_user_guide(doc_dir)
        self._generate_installation_guide(doc_dir)
        self._generate_api_reference(doc_dir)
        self._generate_version_history(doc_dir)
        self._generate_license_info(doc_dir)
        
        logger.info(f"✅ Documentation generated in {doc_dir}/")
        return doc_dir
    
    def _generate_technical_docs(self, doc_dir: str):
        """Generate technical documentation"""
        filename = f"{doc_dir}/technical_documentation.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# ULTIMATE HYBRID CRYPTO TRADING BOT - TECHNICAL DOCUMENTATION\n\n")
            f.write("## Version 12.0.1\n\n")
            f.write("## Architecture Overview\n\n")
            f.write("The bot uses a modular architecture with the following main components:\n\n")
            f.write("1. **Market Data Layer**: Fetches real-time data from Binance Futures\n")
            f.write("2. **Analysis Layer**: Technical indicators, order flow, smart money concepts\n")
            f.write("3. **Signal Generation**: Tiered signal generation (Ultra Safe, Balanced, Aggressive)\n")
            f.write("4. **Risk Management**: Position sizing, drawdown control, risk metrics\n")
            f.write("5. **Order Execution**: Advanced order types (OCO, Trailing Stop, Iceberg, TWAP)\n")
            f.write("6. **Portfolio Management**: Multi-symbol tracking, correlation analysis\n")
            f.write("7. **Performance Analytics**: Win rate, Sharpe ratio, drawdown analysis\n")
            f.write("8. **Security Layer**: API encryption, rate limiting\n\n")
            f.write("## Key Features\n\n")
            f.write("- Multi-timeframe analysis (3m to 1M)\n")
            f.write("- Tiered signal generation (Ultra Safe, Balanced, Aggressive)\n")
            f.write("- Advanced order types (OCO, Trailing Stop, Iceberg, TWAP)\n")
            f.write("- Real-time market scanning with opportunity scoring\n")
            f.write("- Telegram integration for instant alerts\n")
            f.write("- Backtesting engine for strategy validation\n")
            f.write("- Adaptive cooldown system to prevent spam\n")
            f.write("- Comprehensive risk management\n")
            f.write("- **Pro Trader Mode** with advanced candle patterns, order flow, smart money concepts\n")
    
    def _generate_user_guide(self, doc_dir: str):
        """Generate user guide"""
        filename = f"{doc_dir}/user_guide.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# ULTIMATE HYBRID CRYPTO TRADING BOT - USER GUIDE\n\n")
            f.write("## Version 12.0.1\n\n")
            f.write("## Getting Started\n\n")
            f.write("### 1. Installation\n")
            f.write("```bash\n")
            f.write("pip install requests pandas numpy scikit-learn joblib cryptography\n")
            f.write("```\n\n")
            f.write("### 2. Configuration\n")
            f.write("Edit `config.json` with your settings:\n\n")
            f.write("```json\n")
            f.write("{\n")
            f.write('  "telegram": {\n')
            f.write('    "bot_token": "YOUR_BOT_TOKEN",\n')
            f.write('    "chat_id": "YOUR_CHAT_ID",\n')
            f.write('    "min_confidence": 70.0,\n')
            f.write('    "min_accuracy": 75.0\n')
            f.write("  },\n")
            f.write('  "futures": {\n')
            f.write('    "api_key": "YOUR_API_KEY",\n')
            f.write('    "api_secret": "YOUR_API_SECRET",\n')
            f.write('    "use_testnet": true\n')
            f.write("  }\n")
            f.write("}\n")
            f.write("```\n\n")
            f.write("### 3. Running the Bot\n")
            f.write("```bash\n")
            f.write("python run_bot.py\n")
            f.write("```\n\n")
            f.write("### 4. Understanding Signals\n\n")
            f.write("The bot generates three tiers of signals:\n")
            f.write("- **Tier 1 (Ultra Safe)**: Highest confidence, strictest filters\n")
            f.write("- **Tier 2 (Balanced)**: Moderate confidence, balanced filters\n")
            f.write("- **Tier 3 (Aggressive)**: Lower confidence, more opportunities\n\n")
            f.write("### 5. Pro Trader Mode\n\n")
            f.write("Pro Trader Mode provides complete advanced analysis including:\n")
            f.write("- **Candle Patterns**: 25+ candle patterns (Doji, Hammer, Engulfing, etc.)\n")
            f.write("- **Support/Resistance**: Dynamic levels using 5 different methods\n")
            f.write("- **Market Profile**: Value area, POC, high/low volume nodes\n")
            f.write("- **Order Flow**: Bid-ask imbalance, cumulative delta, large trades\n")
            f.write("- **Smart Money Concepts**: Order blocks, FVGs, liquidity levels\n")
    
    def _generate_installation_guide(self, doc_dir: str):
        """Generate installation guide"""
        filename = f"{doc_dir}/installation_guide.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# INSTALLATION GUIDE\n\n")
            f.write("## System Requirements\n\n")
            f.write("- Python 3.8 or higher\n")
            f.write("- 4GB RAM minimum (8GB recommended)\n")
            f.write("- Internet connection\n")
            f.write("- Binance Futures account\n")
            f.write("- Telegram account (optional)\n\n")
            f.write("## Step-by-Step Installation\n\n")
            f.write("1. **Clone or download the bot files**\n")
            f.write("2. **Install Python dependencies**:\n")
            f.write("   ```bash\n")
            f.write("   pip install -r requirements.txt\n")
            f.write("   ```\n")
            f.write("3. **Configure API keys** in `config.json`\n")
            f.write("4. **Run the bot**:\n")
            f.write("   ```bash\n")
            f.write("   python run_bot.py\n")
            f.write("   ```\n")
    
    def _generate_api_reference(self, doc_dir: str):
        """Generate API reference"""
        filename = f"{doc_dir}/api_reference.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# API REFERENCE\n\n")
            f.write("## Core Classes\n\n")
            f.write("### `UltimateHybridBot`\n")
            f.write("Main bot class that orchestrates all components.\n\n")
            f.write("**Methods:**\n")
            f.write("- `__init__(telegram_config, futures_config)`: Initialize the bot\n")
            f.write("- `run_smart_scan(continuous, interval_seconds)`: Start scanning\n")
            f.write("- `run_pro_trader_scan(continuous, interval_seconds)`: Pro Trader Mode\n")
            f.write("- `update_performance_stats(signal)`: Update statistics\n")
            f.write("- `get_bot_win_rate()`: Get win rate statistics\n\n")
            f.write("### `EnhancedTieredSignalGenerator`\n")
            f.write("Generates trading signals with multiple confidence tiers and advanced analysis.\n\n")
            f.write("### `AdvancedRiskManager`\n")
            f.write("Manages risk, position sizing, and drawdown control.\n\n")
            f.write("### `MarketScanner`\n")
            f.write("Scans market and calculates opportunity scores.\n\n")
            f.write("### `UltimateDirectionAnalyzer`\n")
            f.write("Analyzes market direction using 6 factors.\n\n")
            f.write("### `AdvancedCandlePatternRecognizer`\n")
            f.write("Recognizes 25+ candle patterns across multiple timeframes.\n\n")
            f.write("### `CompleteOrderFlowAnalyzer`\n")
            f.write("Complete order flow analysis with delta, absorption, exhaustion detection.\n\n")
            f.write("### `CompleteSmartMoneyDetector`\n")
            f.write("Detects order blocks, fair value gaps, liquidity levels, and more.\n")
    
    def _generate_version_history(self, doc_dir: str):
        """Generate version history"""
        filename = f"{doc_dir}/version_history.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# VERSION HISTORY\n\n")
            f.write("## Version 12.0.1 (Current)\n\n")
            f.write("**Release Date:** March 2024\n\n")
            f.write("**New Features:**\n")
            f.write("- ✅ Complete market scanner with opportunity scoring (0-100)\n")
            f.write("- ✅ Ultimate direction analyzer with 6 components\n")
            f.write("- ✅ Adaptive cooldown system based on market volatility\n")
            f.write("- ✅ Enhanced backtest engine with performance metrics\n")
            f.write("- ✅ Pydroid/Termux optimization for mobile trading\n")
            f.write("- ✅ Multi-language support (English only)\n")
            f.write("- ✅ Comprehensive documentation generator\n")
            f.write("- ✅ Telegram integration with formatted messages\n")
            f.write("- ✅ **PRO TRADER MODE** with complete advanced analysis\n")
            f.write("   - 25+ candle patterns (Doji, Hammer, Engulfing, etc.)\n")
            f.write("   - Support/Resistance detection (5 methods)\n")
            f.write("   - Market Profile analysis (Value Area, POC)\n")
            f.write("   - Complete Order Flow analysis (delta, absorption, exhaustion)\n")
            f.write("   - Smart Money Concepts (order blocks, FVGs, liquidity levels)\n\n")
            f.write("**Bug Fixes:**\n")
            f.write("- Fixed type comparison errors in signal generation\n")
            f.write("- Fixed dataclass argument ordering\n")
            f.write("- Fixed import dependencies\n")
            f.write("- Improved error handling for API calls\n")
    
    def _generate_license_info(self, doc_dir: str):
        """Generate license information"""
        filename = f"{doc_dir}/license_info.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# LICENSE INFORMATION\n\n")
            f.write("## Commercial License\n\n")
            f.write("Copyright © 2024 Nhen Bol. All Rights Reserved.\n\n")
            f.write("This software is the proprietary and confidential information of Nhen Bol.\n")
            f.write("Unauthorized copying, distribution, or modification is strictly prohibited.\n\n")
            f.write("## Terms of Use\n\n")
            f.write("1. This software is for personal use only\n")
            f.write("2. Not for commercial distribution without permission\n")
            f.write("3. Use at your own risk - trading involves substantial risk\n")
            f.write("4. No warranty or liability for financial losses\n")


# ==============================================================================
# CONFIGURATION LOADER
# ==============================================================================
def load_hybrid_config():
    """Load configuration from file or create default"""
    config_file = "config.json"
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    else:
        # Create default config
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
                'enable_auto_trade': False,
                'max_position_size_usdt': 100.0,
                'default_leverage': 5,
                'language': 'en'
            },
            'futures': {
                'api_key': '',
                'api_secret': '',
                'use_testnet': True,
                'request_timeout': 30
            },
            'tp_config': {
                'scalping_tp1': 0.30,
                'scalping_tp2': 0.50,
                'scalping_tp3': 0.75,
                'intraday_tp1': 0.70,
                'intraday_tp2': 1.00,
                'intraday_tp3': 1.50,
                'swing_tp1': 1.50,
                'swing_tp2': 2.50,
                'swing_tp3': 3.50,
                'position_tp1': 2.00,
                'position_tp2': 3.50,
                'position_tp3': 5.00
            },
            'hybrid': {
                'enable_tier_1': True,
                'enable_tier_2': True,
                'enable_tier_3': True,
                'scan_top_symbols': 20,
                'tier_1_tech_threshold': 70,
                'tier_1_flow_threshold': 60,
                'tier_2_tech_threshold': 59,
                'tier_2_flow_threshold': 55,
                'tier_3_tech_threshold': 54,
                'tier_3_flow_threshold': 48,
                'atr_stop_loss_enabled': True,
                'atr_multiplier': 1.5,
                'volume_profile_entry_enabled': True,
                'liquidity_grab_enabled': True,
                'ema_200_trend_filter_enabled': True,
                'ai_confidence_model_enabled': False,
                'whale_detection_enabled': False,
                'keyzone_enabled': False,
                'pullback_enabled': False,
                'dome_detection_enabled': False,
                'language': 'en'
            },
            'scan': {
                'interval_seconds': 30,
                'continuous': True
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 Created default configuration file: {config_file}")
        print("⚠️  Please edit this file with your credentials")
        
        return default_config


# ==============================================================================
# SIMPLE TELEGRAM NOTIFIER
# ==============================================================================
class SimpleTelegramNotifier:
    """Simple Telegram notifier for sending messages and alerts"""
    
    def __init__(self, config: TelegramConfig, bot_config: Config):
        self.config = config
        self.bot_config = bot_config
        self.last_signal_time = {}
        self.sent_signals = []
        self.max_history = 100
        
        if hasattr(config, 'LANGUAGE'):
            lang.current_language = Language(config.LANGUAGE)
        
        if self.config.ENABLE_SUMMARY:
            self._start_summary_thread()
    
    def _start_summary_thread(self):
        """Start thread for hourly summaries"""
        def run_summary():
            while True:
                time.sleep(self.config.SUMMARY_INTERVAL_MINUTES * 60)
                self.send_hourly_summary()
        
        thread = threading.Thread(target=run_summary, daemon=True)
        thread.start()
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> Optional[int]:
        """Send message to Telegram"""
        if not self.config.BOT_TOKEN or not self.config.CHAT_ID:
            return None
        if self.config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
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
            else:
                logger.error(f"Telegram error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return None
    
    def get_alert_level(self, signal: EnhancedHighConfidenceSignal) -> AlertLevel:
        """Get alert level based on confidence and accuracy"""
        if signal.confidence >= self.config.EMERGENCY_THRESHOLD and signal.overall_accuracy_score >= 85:
            return AlertLevel.EMERGENCY
        elif signal.confidence >= self.config.HIGH_THRESHOLD and signal.overall_accuracy_score >= 75:
            return AlertLevel.HIGH
        elif signal.confidence >= self.config.MEDIUM_THRESHOLD:
            return AlertLevel.MEDIUM
        else:
            return AlertLevel.LOW
    
    def _format_price(self, price: float) -> str:
        """Format price based on value"""
        if price < 0.0001:
            return f"{price:.8f}"
        elif price < 0.01:
            return f"{price:.6f}"
        elif price < 1:
            return f"{price:.4f}"
        elif price < 100:
            return f"{price:.2f}"
        else:
            return f"{price:,.2f}"
    
    def _build_signal_message(self, signal: EnhancedHighConfidenceSignal) -> str:
        """Build formatted signal message for Telegram"""
        # Tier emojis and names
        tier_emojis = {
            SignalTier.TIER_1_ULTRA_SAFE: "🛡️",
            SignalTier.TIER_2_BALANCED: "⚖️",
            SignalTier.TIER_3_AGGRESSIVE: "⚡"
        }
        tier_names = {
            SignalTier.TIER_1_ULTRA_SAFE: "ULTRA SAFE",
            SignalTier.TIER_2_BALANCED: "BALANCED",
            SignalTier.TIER_3_AGGRESSIVE: "AGGRESSIVE"
        }
        
        emoji = tier_emojis.get(signal.tier, "🔵")
        tier_name = tier_names.get(signal.tier, "HYBRID")
        
        # Direction
        direction_emoji = "🟢" if signal.signal_type == "STRONG_BUY" else "🔴"
        direction_text = "LONG" if signal.signal_type == "STRONG_BUY" else "SHORT"
        
        # Build message
        lines = []
        lines.append(f"{emoji} <b>{tier_name} SIGNAL</b> {emoji}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"⏰ {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"💰 <b>{signal.symbol}</b> | {direction_emoji} {direction_text}")
        lines.append(f"🎯 Confidence: {signal.confidence:.1f}%")
        lines.append(f"📊 Accuracy: {signal.overall_accuracy_score:.1f}%")
        
        # Entry
        lines.append(f"\n📈 <b>Entry Price</b>")
        lines.append(f"├ ${self._format_price(signal.entry_price)}")
        lines.append(f"├ Bid: ${self._format_price(signal.best_bid)}")
        lines.append(f"├ Ask: ${self._format_price(signal.best_ask)}")
        lines.append(f"└ {signal.optimal_entry_timeframe}")
        
        # Stop Loss
        lines.append(f"\n🛑 <b>Stop Loss</b>")
        lines.append(f"├ ${self._format_price(signal.stop_loss)}")
        lines.append(f"└ {signal.stop_loss_percentage:.2f}%")
        
        # Take Profit
        lines.append(f"\n🎯 <b>Take Profit Levels</b>")
        lines.append(f"├ TP1: ${self._format_price(signal.take_profit_1)}")
        lines.append(f"├ TP2: ${self._format_price(signal.take_profit_2)}")
        lines.append(f"└ TP3: ${self._format_price(signal.take_profit_3)}")
        
        # Risk/Reward
        if signal.risk_reward:
            lines.append(f"\n📊 <b>Risk/Reward</b>")
            lines.append(f"├ 1:{signal.risk_reward.rr_ratio_1:.1f} (TP1)")
            lines.append(f"├ 1:{signal.risk_reward.rr_ratio_2:.1f} (TP2)")
            lines.append(f"└ Expected: {signal.risk_reward.expected_value:.2f}%")
        
        # Technical Summary
        lines.append(f"\n📊 <b>Technical Summary</b>")
        lines.append(f"├ RSI: {signal.rsi:.1f} ({signal.rsi_signal})")
        lines.append(f"├ MACD: {signal.macd_trend}")
        lines.append(f"├ EMA: {signal.ema_trend}")
        lines.append(f"├ Tech Score: {signal.tech_score:+.0f}")
        lines.append(f"└ Flow Score: {signal.flow_score:+.0f}")
        
        # Primary Reasons
        if signal.primary_reasons:
            lines.append(f"\n<b>⭐ Primary Reasons</b>")
            for i, reason in enumerate(signal.primary_reasons[:3], 1):
                lines.append(f"{i}. {reason}")
        
        # Footer
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"⚡ Risk Level: {signal.risk_level}")
        lines.append(f"⏱️ Cooldown: {signal.adaptive_cooldown_minutes} min")
        
        return "\n".join(lines)
    
    def send_enhanced_signal(self, signal: EnhancedHighConfidenceSignal) -> bool:
        """Send enhanced signal to Telegram"""
        # Check minimum requirements
        if signal.confidence < self.config.MIN_CONFIDENCE:
            return False
        
        if signal.overall_accuracy_score < self.config.MIN_ACCURACY_SCORE:
            return False
        
        # Check cooldown
        symbol = signal.symbol
        if symbol in self.last_signal_time:
            time_diff = (datetime.now() - self.last_signal_time[symbol]).total_seconds() / 60
            if time_diff < self.config.COOLDOWN_MINUTES:
                return False
        
        # Set alert level
        alert_level = self.get_alert_level(signal)
        signal.alert_level = alert_level
        
        # Send message
        message = self._build_signal_message(signal)
        message_id = self.send_message(message)
        
        if message_id:
            self.sent_signals.append(signal)
            self.last_signal_time[symbol] = datetime.now()
            
            # Keep history limited
            if len(self.sent_signals) > self.max_history:
                self.sent_signals = self.sent_signals[-self.max_history:]
            
            logger.info(f"✅ Telegram {alert_level.value} signal sent for {symbol}")
            return True
        
        return False
    
    def send_hourly_summary(self):
        """Send hourly summary of signals"""
        if not self.sent_signals:
            return
        
        # Get last hour signals
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_signals = [s for s in self.sent_signals if s.timestamp > one_hour_ago]
        
        if not recent_signals:
            return
        
        # Calculate statistics
        total = len(recent_signals)
        tier1 = sum(1 for s in recent_signals if s.tier == SignalTier.TIER_1_ULTRA_SAFE)
        tier2 = sum(1 for s in recent_signals if s.tier == SignalTier.TIER_2_BALANCED)
        tier3 = sum(1 for s in recent_signals if s.tier == SignalTier.TIER_3_AGGRESSIVE)
        buys = sum(1 for s in recent_signals if s.signal_type == "STRONG_BUY")
        sells = sum(1 for s in recent_signals if s.signal_type == "STRONG_SELL")
        
        avg_confidence = sum(s.confidence for s in recent_signals) / total
        avg_accuracy = sum(s.overall_accuracy_score for s in recent_signals) / total
        
        # Build summary
        summary = []
        summary.append("📊 <b>Hourly Summary</b>")
        summary.append("━━━━━━━━━━━━━━━━━━━━━━")
        summary.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        summary.append(f"📈 Total Signals: {total}")
        summary.append(f"\n<b>Tier Distribution:</b>")
        summary.append(f"├ 🛡️ Ultra Safe: {tier1}")
        summary.append(f"├ ⚖️ Balanced: {tier2}")
        summary.append(f"└ ⚡ Aggressive: {tier3}")
        summary.append(f"\n<b>Direction:</b>")
        summary.append(f"├ 🟢 Long: {buys}")
        summary.append(f"└ 🔴 Short: {sells}")
        summary.append(f"\n<b>Performance:</b>")
        summary.append(f"├ Avg Confidence: {avg_confidence:.1f}%")
        summary.append(f"└ Avg Accuracy: {avg_accuracy:.1f}%")
        
        # Top signals
        if recent_signals:
            summary.append(f"\n<b>Top Signals:</b>")
            top_signals = sorted(recent_signals, key=lambda x: x.confidence, reverse=True)[:3]
            for s in top_signals:
                direction = "🟢" if s.signal_type == "STRONG_BUY" else "🔴"
                summary.append(f"├ {s.symbol} {direction} ({s.confidence:.1f}%)")
        
        summary.append("━━━━━━━━━━━━━━━━━━━━━━")
        
        self.send_message("\n".join(summary))
    
    def send_startup_message(self, hybrid_config: HybridConfig):
        """Send startup message"""
        # Get enabled tiers
        tiers = []
        if hybrid_config.ENABLE_TIER_1:
            tiers.append("🛡️ Ultra Safe")
        if hybrid_config.ENABLE_TIER_2:
            tiers.append("⚖️ Balanced")
        if hybrid_config.ENABLE_TIER_3:
            tiers.append("⚡ Aggressive")
        
        auto_trade_status = "✅ Enabled" if self.config.ENABLE_AUTO_TRADE else "❌ Disabled"
        
        # Build message
        message = []
        message.append("🤖 <b>ULTIMATE HYBRID BOT V12.0.1</b>")
        message.append("━━━━━━━━━━━━━━━━━━━━━━")
        message.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        message.append(f"📊 Monitoring {len(self.bot_config.SYMBOLS)} symbols")
        message.append(f"🎯 Active Tiers: {', '.join(tiers)}")
        message.append(f"📈 Min Confidence: {self.config.MIN_CONFIDENCE}%")
        message.append(f"📊 Min Accuracy: {self.config.MIN_ACCURACY_SCORE}%")
        message.append(f"⏱️ Cooldown: {self.config.COOLDOWN_MINUTES} min")
        message.append(f"⚡ Auto Trade: {auto_trade_status}")
        message.append("━━━━━━━━━━━━━━━━━━━━━━")
        message.append("<i>Pydroid Optimized Edition ready...</i>")
        
        self.send_message("\n".join(message))


# ==============================================================================
# SIMPLE BINANCE CLIENT
# ==============================================================================
class BinanceFuturesClient:
    """Simple Binance Futures Client for API communication"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://fapi.binance.com"
        
        if hasattr(config, 'FUTURES_CONFIG') and config.FUTURES_CONFIG:
            if config.FUTURES_CONFIG.USE_TESTNET:
                self.base_url = config.FUTURES_CONFIG.TESTNET_URL
            else:
                self.base_url = config.FUTURES_CONFIG.BASE_URL
    
    def test_connection(self) -> bool:
        """Test connection to Binance Futures"""
        try:
            response = requests.get(f"{self.base_url}/fapi/v1/ping", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            response = requests.get(
                f"{self.base_url}/fapi/v1/ticker/price", 
                params={"symbol": symbol}, 
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
            return None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def get_ticker_24hr(self, symbol: str) -> Optional[Dict]:
        """Get 24hr ticker for symbol with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{self.base_url}/fapi/v1/ticker/24hr", 
                    params={"symbol": symbol}, 
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Error getting ticker for {symbol} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return None
        
        return None
    
    def get_klines(self, symbol: str, interval: str, limit: int) -> Optional[pd.DataFrame]:
        """Get klines/candlestick data with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{self.base_url}/fapi/v1/klines",
                    params={"symbol": symbol, "interval": interval, "limit": limit},
                    timeout=15  # Increased timeout for klines
                )
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                    ])
                    df['open'] = df['open'].astype(float)
                    df['high'] = df['high'].astype(float)
                    df['low'] = df['low'].astype(float)
                    df['close'] = df['close'].astype(float)
                    df['volume'] = df['volume'].astype(float)
                    return df
                else:
                    logger.warning(f"Error getting klines for {symbol}, attempt {attempt + 1}: {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout getting klines for {symbol}, attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error for {symbol}, attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Error getting klines for {symbol}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return None
        
        return None
    
    def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict]:
        """Get order book data"""
        try:
            response = requests.get(
                f"{self.base_url}/fapi/v1/depth",
                params={"symbol": symbol, "limit": limit},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting order book for {symbol}: {e}")
            return None
    
    def get_funding_rate(self, symbol: str) -> Optional[float]:
        """Get funding rate for symbol"""
        try:
            response = requests.get(
                f"{self.base_url}/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": 1},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return float(data[0]['fundingRate'])
            return 0.0
        except Exception as e:
            logger.error(f"Error getting funding rate for {symbol}: {e}")
            return 0.0
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> Optional[List]:
        """Get recent trades"""
        try:
            response = requests.get(
                f"{self.base_url}/fapi/v1/trades",
                params={"symbol": symbol, "limit": limit},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting recent trades for {symbol}: {e}")
            return []
    
    def get_depth_history(self) -> List:
        """Get depth history (placeholder)"""
        return []
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Optional[Dict]:
        """Make API request (placeholder for authenticated requests)"""
        logger.warning("_make_request not fully implemented - using placeholder")
        return None


class EnhancedBinanceFuturesClient(BinanceFuturesClient):
    """Enhanced Binance Futures Client with additional features"""
    
    def __init__(self, config):
        super().__init__(config)
        self.risk_manager = None
        self.portfolio_manager = None
        self.advanced_order_executor = None
        self.performance_analytics = None
        self.ml_models = None
        self.security_manager = None
    
    def test_connection(self) -> bool:
        """Test connection to Binance Futures"""
        return super().test_connection()
    
    def get_depth_history(self) -> List:
        """Get depth history (placeholder)"""
        return []
    
    def get_funding_rate(self, symbol: str) -> Optional[float]:
        """Get funding rate for symbol"""
        return super().get_funding_rate(symbol)
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> Optional[List]:
        """Get recent trades"""
        return super().get_recent_trades(symbol, limit)


# ==============================================================================
# ULTIMATE HYBRID BOT - MAIN CLASS
# ==============================================================================
class UltimateHybridBot:
    """Ultimate Hybrid Trading Bot Main Class"""
    
    def __init__(self, telegram_config: TelegramConfig, futures_config: BinanceFuturesConfig):
        # Initialize config
        self.config = Config()
        self.config.FUTURES_CONFIG = futures_config
        self.config.TELEGRAM_CONFIG = telegram_config
        self.config.HYBRID_CONFIG = HybridConfig()
        self.telegram_config = telegram_config
        
        # Initialize clients
        self.client = EnhancedBinanceFuturesClient(self.config)
        self.signal_generator = EnhancedTieredSignalGenerator(self.client, self.config)
        self.notifier = SimpleTelegramNotifier(telegram_config, self.config)
        self.backtest_engine = BacktestEngine(self.client)
        self.scanner = MarketScanner(self.client)
        self.cooldown = AdaptiveCooldown()
        self.ultimate_analyzer = UltimateDirectionAnalyzer(self.client)
        
        # Initialize advanced features
        self.signal_generator.initialize_advanced_features()
        self.signal_generator.ultimate_analyzer = self.ultimate_analyzer
        
        # Connect components
        self.client.risk_manager = self.signal_generator.risk_manager
        self.client.portfolio_manager = self.signal_generator.portfolio_manager
        self.client.advanced_order_executor = self.signal_generator.advanced_order_executor
        self.client.performance_analytics = self.signal_generator.performance_analytics
        self.client.ml_models = self.signal_generator.ml_models
        self.client.security_manager = self.signal_generator.security_manager
        
        # Runtime variables
        self.running = False
        self.signals_history = []
        self.enhanced_signals_history = []
        self.start_time = datetime.now()
        self.scan_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.trade_history = []
        self.signals_last_100 = deque(maxlen=100)
        
        # Statistics
        self.stats = {
            'total_scans': 0,
            'total_signals': 0,
            'tier1_signals': 0,
            'tier2_signals': 0,
            'tier3_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'avg_confidence': 0.0,
            'avg_accuracy': 0.0,
            'signals_by_symbol': defaultdict(int),
            'emergency_alerts': 0,
            'high_alerts': 0,
            'medium_alerts': 0
        }
        
        # Test connection
        if not self.client.test_connection():
            logger.error("Cannot connect to Binance Futures. Exiting.")
            sys.exit(1)
        
        # Display startup info
        hybrid_config = self.config.HYBRID_CONFIG
        logger.info("=" * 80)
        logger.info("ULTIMATE HYBRID FUTURES TRADING BOT V12.0.1")
        logger.info("PYDROID OPTIMIZED EDITION - ULTIMATE ACCURACY")
        logger.info("=" * 80)
        logger.info(f"Symbols: {len(self.config.SYMBOLS)}")
        logger.info(f"Tiers: Ultra Safe={hybrid_config.ENABLE_TIER_1}, Balanced={hybrid_config.ENABLE_TIER_2}, Aggressive={hybrid_config.ENABLE_TIER_3}")
        logger.info(f"Min Confidence: {self.telegram_config.MIN_CONFIDENCE}%")
        logger.info(f"Min Accuracy: {self.telegram_config.MIN_ACCURACY_SCORE}%")
        logger.info(f"Using: {'TESTNET' if futures_config.USE_TESTNET else 'REAL MARKET'}")
        logger.info(f"Language: English")
        logger.info("=" * 80)
        logger.info("✅ PRO TRADER MODE AVAILABLE - Select option 10 for complete analysis")
        logger.info("=" * 80)
    
    def update_performance_stats(self, signal: EnhancedHighConfidenceSignal):
        """Update performance statistics"""
        self.signals_last_100.append(signal)
        
        # Update tier counts
        if signal.tier == SignalTier.TIER_1_ULTRA_SAFE:
            self.stats['tier1_signals'] += 1
        elif signal.tier == SignalTier.TIER_2_BALANCED:
            self.stats['tier2_signals'] += 1
        elif signal.tier == SignalTier.TIER_3_AGGRESSIVE:
            self.stats['tier3_signals'] += 1
        
        # Update direction counts
        if signal.signal_type == "STRONG_BUY":
            self.stats['buy_signals'] += 1
        else:
            self.stats['sell_signals'] += 1
        
        # Update symbol counts
        self.stats['signals_by_symbol'][signal.symbol] += 1
        
        # Update alert levels
        if signal.alert_level == AlertLevel.EMERGENCY:
            self.stats['emergency_alerts'] += 1
        elif signal.alert_level == AlertLevel.HIGH:
            self.stats['high_alerts'] += 1
        elif signal.alert_level == AlertLevel.MEDIUM:
            self.stats['medium_alerts'] += 1
        
        # Update averages
        total_signals = len(self.signals_history) + 1
        self.stats['avg_confidence'] = (
            (self.stats['avg_confidence'] * (total_signals - 1) + signal.confidence) / total_signals
        )
        self.stats['avg_accuracy'] = (
            (self.stats['avg_accuracy'] * (total_signals - 1) + signal.overall_accuracy_score) / total_signals
        )
    
    def get_bot_win_rate(self) -> Tuple[float, int, float]:
        """Get bot win rate statistics"""
        if len(self.trade_history) > 0:
            total = len(self.trade_history)
            win_rate = (self.winning_trades / total) * 100 if total > 0 else 0
        else:
            win_rate = self.stats['avg_accuracy']
        
        last_100_signals = list(self.signals_last_100)
        signals_last_100_count = len(last_100_signals)
        win_rate_last_100 = (
            sum(s.overall_accuracy_score for s in last_100_signals) / signals_last_100_count 
            if signals_last_100_count > 0 else 0
        )
        
        return win_rate, signals_last_100_count, win_rate_last_100
    
    def run_smart_scan(self, continuous: bool = True, interval_seconds: int = 30):
        """Run smart scan to find trading opportunities (standard mode)"""
        self.running = True
        
        # Send startup message
        if (self.telegram_config.BOT_TOKEN and 
            self.telegram_config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE"):
            self.notifier.send_startup_message(self.config.HYBRID_CONFIG)
        
        try:
            while self.running:
                self.scan_count += 1
                self.stats['total_scans'] += 1
                
                logger.info(f"\n{'='*80}")
                logger.info(f"ULTIMATE SCAN V12.0.1 #{self.scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}")
                
                # Scan all symbols and get ranked list
                ranked_symbols = self.scanner.scan_all_symbols(self.config.SYMBOLS)
                
                # Get top symbols based on config
                top_symbols = [s[0] for s in ranked_symbols[:self.config.HYBRID_CONFIG.SCAN_TOP_SYMBOLS]]
                
                # Process top symbols for signals
                signals_found = []
                bot_win_rate, signals_last_100, win_rate_last_100 = self.get_bot_win_rate()
                
                if top_symbols:
                    logger.info(f"Processing top {len(top_symbols)} symbols...")
                    
                    with ThreadPoolExecutor(max_workers=3) as executor:
                        future_to_symbol = {
                            executor.submit(
                                self._process_symbol, symbol, bot_win_rate, 
                                signals_last_100, win_rate_last_100
                            ): symbol 
                            for symbol in top_symbols[:10]  # Process top 10 only
                        }
                        
                        for future in as_completed(future_to_symbol):
                            symbol = future_to_symbol[future]
                            try:
                                signal = future.result(timeout=30)
                                if signal:
                                    signals_found.append(signal)
                            except Exception as e:
                                logger.error(f"Error processing {symbol}: {e}")
                
                logger.info(f"\n✅ Found {len(signals_found)} ultimate signals")
                
                # Update stats
                self.stats['total_signals'] += len(signals_found)
                
                # Show summary
                if self.stats['total_signals'] > 0:
                    logger.info(f"📊 Total signals: {self.stats['total_signals']}")
                    logger.info(f"📊 Avg Confidence: {self.stats['avg_confidence']:.1f}%")
                    logger.info(f"📊 Avg Accuracy: {self.stats['avg_accuracy']:.1f}%")
                
                if not continuous:
                    break
                
                # Calculate next scan time
                next_scan = datetime.now() + timedelta(seconds=interval_seconds)
                logger.info(f"\n⏱️ Next scan at: {next_scan.strftime('%H:%M:%S')}")
                logger.info(f"💤 Waiting {interval_seconds} seconds...")
                
                # Wait with interrupt check
                for i in range(interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
                        
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
            if (self.telegram_config.BOT_TOKEN and 
                self.telegram_config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE"):
                self.notifier.send_message("🛑 Bot stopped successfully")
        except Exception as e:
            logger.error(f"Scan error: {e}")
        finally:
            self.running = False
            self._generate_final_report()
    
    def run_pro_trader_scan(self, continuous: bool = True, interval_seconds: int = 20):
        """Run pro trader scan with complete advanced analysis"""
        self.running = True
        
        logger.info("=" * 80)
        logger.info("🚀 PRO TRADER MODE ACTIVATED - COMPLETE ADVANCED ANALYSIS")
        logger.info("=" * 80)
        
        try:
            while self.running:
                self.scan_count += 1
                
                logger.info(f"\n{'='*80}")
                logger.info(f"PRO TRADER SCAN #{self.scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}")
                
                # Get top symbols
                ranked_symbols = self.scanner.scan_all_symbols(self.config.SYMBOLS)
                top_symbols = [s[0] for s in ranked_symbols[:100]]  # Focus on top 5 for pro analysis
                
                for symbol in top_symbols:
                    try:
                        logger.info(f"\n📊 Analyzing {symbol}...")
                        
                        # Get complete analysis
                        df_dict = {
                            '3m': self.client.get_klines(symbol, '3m', 100),
                            '5m': self.client.get_klines(symbol, '5m', 100),
                            '15m': self.client.get_klines(symbol, '15m', 100),
                            '30m': self.client.get_klines(symbol, '30m', 100),
                            '1h': self.client.get_klines(symbol, '1h', 200),
                            '4h': self.client.get_klines(symbol, '4h', 100),
                            '1d': self.client.get_klines(symbol, '1d', 50)
                        }
                        
                        analysis = self.signal_generator.get_complete_analysis(symbol, df_dict)
                        
                        # Display pro analysis
                        self._display_pro_analysis(symbol, analysis)
                        
                        # Generate signal
                        signal = self.signal_generator.generate_signal_with_advanced_features(symbol)
                        if signal:
                            self._display_ultimate_signal(signal)
                            
                            if self.telegram_config.BOT_TOKEN:
                                self.notifier.send_enhanced_signal(signal)
                        
                    except Exception as e:
                        logger.error(f"Error analyzing {symbol}: {e}")
                
                if not continuous:
                    break
                
                logger.info(f"\n⏱️ Next pro scan in {interval_seconds} seconds...")
                for i in range(interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("\n🛑 Pro Trader mode stopped")
        finally:
            self.running = False
    
    def _process_symbol(self, symbol: str, bot_win_rate: float, 
                        signals_last_100: int, win_rate_last_100: float) -> Optional[EnhancedHighConfidenceSignal]:
        """Process a single symbol for signals with type checking"""
        try:
            # Generate tiered signals
            tier_signals = self.signal_generator.generate_tiered_signals(symbol)
            
            for signal in tier_signals:
                # Check if signal is valid
                if signal is None:
                    continue
                    
                # Check cooldown
                if not hasattr(signal, 'tier') or not hasattr(signal, 'market_regime'):
                    continue
                    
                if self.cooldown.can_send_signal(symbol, signal.tier, signal.market_regime):
                    # Add bot stats with type checking
                    signal.bot_win_rate = float(bot_win_rate) if isinstance(bot_win_rate, (int, float)) else 0
                    signal.signals_last_100 = int(signals_last_100) if isinstance(signals_last_100, (int, float)) else 0
                    signal.win_rate_last_100 = float(win_rate_last_100) if isinstance(win_rate_last_100, (int, float)) else 0
                    
                    # Add to history
                    self.signals_history.append(signal)
                    self.enhanced_signals_history.append(signal)
                    
                    # Update stats
                    self.update_performance_stats(signal)
                    
                    # Record cooldown
                    self.cooldown.record_signal(symbol, signal.tier)
                    
                    # Display signal
                    self._display_ultimate_signal(signal)
                    
                    # Send Telegram alert
                    if (self.telegram_config.BOT_TOKEN and 
                        self.telegram_config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE"):
                        self.notifier.send_enhanced_signal(signal)
                    
                    return signal
            return None
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            return None
    
    def _display_pro_analysis(self, symbol: str, analysis: Dict):
        """Display pro trader analysis"""
        
        logger.info(f"\n{'─'*60}")
        logger.info(f"📊 PRO TRADER ANALYSIS - {symbol}")
        logger.info(f"{'─'*60}")
        
        # 1. Order Flow
        if analysis.get('order_flow'):
            of = analysis['order_flow']
            logger.info(f"\n📊 ORDER FLOW:")
            logger.info(f"  ├ Imbalance: {of.bid_ask_imbalance:+.1f}%")
            logger.info(f"  ├ Delta: {of.cumulative_delta:+,.0f} ({of.delta_trend})")
            logger.info(f"  ├ Aggressive: {'BUY' if of.aggressive_buying else 'SELL' if of.aggressive_selling else 'NONE'}")
            logger.info(f"  ├ Large Trades: {len(of.large_trades)}")
            logger.info(f"  └ Strength: {of.order_flow_strength:.1f}/100")
            
            if of.absorption_detected:
                logger.info(f"  ✅ Absorption detected")
            if of.exhaustion_detected:
                logger.info(f"  ⚠️ Exhaustion detected")
            if of.stop_hunting_detected:
                logger.info(f"  🎯 Stop hunting detected")
        
        # 2. Smart Money Concepts
        if analysis.get('smart_money'):
            sm = analysis['smart_money']
            logger.info(f"\n🧠 SMART MONEY:")
            logger.info(f"  ├ Order Blocks: {len(sm.order_blocks)}")
            logger.info(f"  ├ Fair Value Gaps: {len(sm.fair_value_gaps)}")
            logger.info(f"  ├ Liquidity Levels: {len(sm.liquidity_levels)}")
            logger.info(f"  ├ Breaker Blocks: {len(sm.breaker_blocks)}")
            logger.info(f"  └ Score: {sm.smart_money_score:.1f}/100")
        
        # 3. Candle Patterns
        if analysis.get('candle_patterns'):
            logger.info(f"\n🕯️ CANDLE PATTERNS:")
            pattern_count = 0
            for tf, patterns in analysis['candle_patterns'].items():
                if patterns and len(patterns) > 0:
                    top_pattern = patterns[0]['pattern']
                    logger.info(f"  ├ {tf}: {top_pattern.name} ({top_pattern.strength:.0f}%)")
                    pattern_count += 1
                    if pattern_count >= 3:
                        break
        
        # 4. Support/Resistance
        if analysis.get('nearest_support') and analysis['nearest_support']:
            logger.info(f"\n📈 SUPPORT/RESISTANCE:")
            for s in analysis['nearest_support'][:3]:
                logger.info(f"  ├ Support: {s.price:.4f} (strength: {s.strength:.0f}%)")
            for r in analysis['nearest_resistance'][:3]:
                logger.info(f"  ├ Resistance: {r.price:.4f} (strength: {r.strength:.0f}%)")
        
        # 5. Market Profile
        if analysis.get('market_profile'):
            mp = analysis['market_profile']
            logger.info(f"\n📊 MARKET PROFILE:")
            logger.info(f"  ├ POC: {mp.poc_price:.4f}")
            logger.info(f"  ├ Value Area: {mp.value_area_low:.4f} - {mp.value_area_high:.4f}")
            logger.info(f"  ├ Profile Type: {mp.profile_type}")
            logger.info(f"  └ High Volume Nodes: {len(mp.high_volume_nodes)}")
        
        # 6. Trading Opportunities
        if analysis.get('trading_opportunities'):
            opp = analysis['trading_opportunities']
            logger.info(f"\n🎯 TRADING OPPORTUNITIES:")
            for zone in opp.get('buy_zones', [])[:2]:
                logger.info(f"  ├ BUY: {zone['price']:.4f} - {zone['reason']}")
            for zone in opp.get('sell_zones', [])[:2]:
                logger.info(f"  ├ SELL: {zone['price']:.4f} - {zone['reason']}")
    
    def _display_ultimate_signal(self, signal: EnhancedHighConfidenceSignal):
        """Display ultimate signal in console"""
        # Tier emojis and names
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
        
        # Alert emojis
        alert_emojis = {
            AlertLevel.EMERGENCY: "🔴",
            AlertLevel.HIGH: "🟡",
            AlertLevel.MEDIUM: "🔵",
            AlertLevel.LOW: "⚪"
        }
        
        # Build display
        logger.info(f"\n{tier_emojis[signal.tier]} ULTIMATE SIGNAL V12.0.1 - {signal.symbol} ({tier_names[signal.tier]}) {alert_emojis.get(signal.alert_level, '')}")
        logger.info(f"Type: {signal.signal_type} | Confidence: {signal.confidence:.1f}%")
        logger.info(f"Accuracy: {signal.overall_accuracy_score:.1f}%")
        logger.info(f"Price: ${signal.current_price:,.4f}")
        logger.info(f"Entry: {signal.suggested_order_type.value if signal.suggested_order_type else 'N/A'} @ ${signal.entry_price:,.4f}")
        logger.info(f"Entry Logic: {signal.optimal_entry_timeframe}")
        logger.info(f"Stop Loss: ${signal.stop_loss:,.4f} ({signal.stop_loss_percentage:.2f}%)")
        logger.info(f"Take Profit 1: ${signal.take_profit_1:,.4f}")
        logger.info(f"Take Profit 2: ${signal.take_profit_2:,.4f}")
        logger.info(f"Take Profit 3: ${signal.take_profit_3:,.4f}")
        logger.info(f"Bid/Ask: ${signal.best_bid:,.4f} / ${signal.best_ask:,.4f}")
        
        if signal.multi_tf_regime and hasattr(signal.multi_tf_regime, 'overall_regime'):
            logger.info(f"Regime: {signal.multi_tf_regime.overall_regime} ({signal.multi_tf_regime.regime_alignment:.0f}% aligned)")
        
        if signal.risk_reward:
            logger.info(f"R:R: 1:{signal.risk_reward.rr_ratio_1:.1f}")
        
        logger.info(f"Tech Score: {signal.tech_score:+.0f} | Flow Score: {signal.flow_score:+.0f}")
        
        if signal.primary_reasons:
            logger.info(f"Reasons: {', '.join(signal.primary_reasons[:2])}")
        
        # Show advanced features if available
        if signal.order_flow and signal.order_flow.order_flow_strength > 70:
            logger.info(f"📊 Order Flow: {signal.order_flow.description}")
        if signal.smart_money_analysis and signal.smart_money_analysis.smart_money_score > 70:
            logger.info(f"🧠 Smart Money: {signal.smart_money_analysis.description}")
    
    def _generate_final_report(self):
        """Generate final performance report"""
        if not self.enhanced_signals_history:
            logger.info("\n📝 No ultimate signals generated")
            return
        
        runtime = datetime.now() - self.start_time
        hours = runtime.total_seconds() / 3600
        
        logger.info("\n" + "="*80)
        logger.info("ULTIMATE V12.0.1 FINAL REPORT")
        logger.info("="*80)
        logger.info(f"Runtime: {runtime}")
        logger.info(f"Total Scans: {self.stats['total_scans']}")
        logger.info(f"Total Signals: {self.stats['total_signals']}")
        
        if hours > 0:
            logger.info(f"Signals/hour: {self.stats['total_signals']/hours:.2f}")
        
        logger.info(f"Tier 1 (Ultra Safe): {self.stats['tier1_signals']}")
        logger.info(f"Tier 2 (Balanced): {self.stats['tier2_signals']}")
        logger.info(f"Tier 3 (Aggressive): {self.stats['tier3_signals']}")
        logger.info(f"Buy Signals: {self.stats['buy_signals']}")
        logger.info(f"Sell Signals: {self.stats['sell_signals']}")
        
        if self.stats['total_signals'] > 0:
            logger.info(f"Avg Confidence: {self.stats['avg_confidence']:.1f}%")
            logger.info(f"Avg Accuracy: {self.stats['avg_accuracy']:.1f}%")
        
        bot_win_rate, signals_last_100, win_rate_last_100 = self.get_bot_win_rate()
        logger.info(f"Bot Win Rate (est): {bot_win_rate:.1f}%")
        
        if signals_last_100 > 0:
            logger.info(f"Last 100 Win Rate: {win_rate_last_100:.1f}%")
        
        logger.info("\n📱 TELEGRAM STATS:")
        logger.info(f"  🔴 Emergency Alerts: {self.stats['emergency_alerts']}")
        logger.info(f"  🟡 High Alerts: {self.stats['high_alerts']}")
        logger.info(f"  🔵 Medium Alerts: {self.stats['medium_alerts']}")
        
        # Save report to file
        report_file = f"ultimate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ULTIMATE HYBRID FUTURES BOT V12.0.1 - FINAL REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Runtime: {runtime}\n")
            f.write(f"Total Scans: {self.stats['total_scans']}\n")
            f.write(f"Total Signals: {self.stats['total_signals']}\n")
            f.write(f"Tier 1: {self.stats['tier1_signals']}\n")
            f.write(f"Tier 2: {self.stats['tier2_signals']}\n")
            f.write(f"Tier 3: {self.stats['tier3_signals']}\n")
            f.write(f"Buy Signals: {self.stats['buy_signals']}\n")
            f.write(f"Sell Signals: {self.stats['sell_signals']}\n")
            f.write(f"Avg Confidence: {self.stats['avg_confidence']:.1f}%\n")
            f.write(f"Avg Accuracy: {self.stats['avg_accuracy']:.1f}%\n")
        
        logger.info(f"📄 Report saved to {report_file}")


# ==============================================================================
# MAIN FUNCTION
# ==============================================================================
def main():
    """Main entry point for the bot"""
    # Console setup for Windows
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
    
    # Display banner
    print("\n" + "="*80)
    print("ULTIMATE HYBRID FUTURES TRADING BOT V12.0.1")
    print("PYDROID OPTIMIZED EDITION - ULTIMATE ACCURACY")
    print("Developer: Nhen Bol")
    print("="*80 + "\n")
    
    # Language selection
    print("Select Language (English only):")
    print("1. English")
    lang_choice = input("\nEnter choice (1): ").strip() or "1"
    lang.current_language = Language.ENGLISH
    print(f"\n{lang.get_text('language')}: {lang.get_text('english')}")
    
    # Test internet connection
    if not test_internet_connection():
        print(f"\n❌ {lang.get_text('no_signal')}")
        input("Press Enter to exit...")
        return
    
    # Load configuration
    config_data = load_hybrid_config()
    
    # Create Telegram config
    telegram_config = TelegramConfig(
        BOT_TOKEN=config_data.get('telegram', {}).get('bot_token', ''),
        CHAT_ID=config_data.get('telegram', {}).get('chat_id', ''),
        MIN_CONFIDENCE=float(config_data.get('telegram', {}).get('min_confidence', 70.0)),
        MIN_ACCURACY_SCORE=float(config_data.get('telegram', {}).get('min_accuracy', 75.0)),
        COOLDOWN_MINUTES=int(config_data.get('telegram', {}).get('cooldown_minutes', 15)),
        EMERGENCY_THRESHOLD=float(config_data.get('telegram', {}).get('emergency_threshold', 90.0)),
        HIGH_THRESHOLD=float(config_data.get('telegram', {}).get('high_threshold', 80.0)),
        MEDIUM_THRESHOLD=float(config_data.get('telegram', {}).get('medium_threshold', 70.0)),
        ENABLE_SUMMARY=bool(config_data.get('telegram', {}).get('enable_summary', True)),
        SUMMARY_INTERVAL_MINUTES=int(config_data.get('telegram', {}).get('summary_interval_minutes', 60)),
        ENABLE_AUTO_TRADE=bool(config_data.get('telegram', {}).get('enable_auto_trade', False)),
        MAX_POSITION_SIZE_USDT=float(config_data.get('telegram', {}).get('max_position_size_usdt', 100.0)),
        DEFAULT_LEVERAGE=int(config_data.get('telegram', {}).get('default_leverage', 5)),
        LANGUAGE='en'
    )
    
    # Create Futures config
    futures_config = BinanceFuturesConfig(
        API_KEY=config_data.get('futures', {}).get('api_key', ''),
        API_SECRET=config_data.get('futures', {}).get('api_secret', ''),
        USE_TESTNET=bool(config_data.get('futures', {}).get('use_testnet', True)),
        REQUEST_TIMEOUT=int(config_data.get('futures', {}).get('request_timeout', 30))
    )
    
    # Get scan settings
    interval = config_data.get('scan', {}).get('interval_seconds', 30)
    continuous = config_data.get('scan', {}).get('continuous', True)
    
    # Check Telegram token
    if telegram_config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"\n⚠️ {lang.get_text('warning')}: Please configure Telegram bot in config.json")
        telegram_config.BOT_TOKEN = ""
    
    # Create TP config
    tp_data = config_data.get('tp_config', {})
    tp_config = TpConfig(
        scalping_tp1=tp_data.get('scalping_tp1', 0.30),
        scalping_tp2=tp_data.get('scalping_tp2', 0.50),
        scalping_tp3=tp_data.get('scalping_tp3', 0.75),
        intraday_tp1=tp_data.get('intraday_tp1', 0.70),
        intraday_tp2=tp_data.get('intraday_tp2', 1.00),
        intraday_tp3=tp_data.get('intraday_tp3', 1.50),
        swing_tp1=tp_data.get('swing_tp1', 1.50),
        swing_tp2=tp_data.get('swing_tp2', 2.50),
        swing_tp3=tp_data.get('swing_tp3', 3.50),
        position_tp1=tp_data.get('position_tp1', 2.00),
        position_tp2=tp_data.get('position_tp2', 3.50),
        position_tp3=tp_data.get('position_tp3', 5.00)
    )
    
    # Create Hybrid config
    hybrid_data = config_data.get('hybrid', {})
    hybrid_config = HybridConfig(
        ENABLE_TIER_1=hybrid_data.get('enable_tier_1', True),
        ENABLE_TIER_2=hybrid_data.get('enable_tier_2', True),
        ENABLE_TIER_3=hybrid_data.get('enable_tier_3', True),
        SCAN_TOP_SYMBOLS=hybrid_data.get('scan_top_symbols', 20),
        TIER_1_TECH_THRESHOLD=hybrid_data.get('tier_1_tech_threshold', 70),
        TIER_1_FLOW_THRESHOLD=hybrid_data.get('tier_1_flow_threshold', 60),
        TIER_2_TECH_THRESHOLD=hybrid_data.get('tier_2_tech_threshold', 59),
        TIER_2_FLOW_THRESHOLD=hybrid_data.get('tier_2_flow_threshold', 55),
        TIER_3_TECH_THRESHOLD=hybrid_data.get('tier_3_tech_threshold', 54),
        TIER_3_FLOW_THRESHOLD=hybrid_data.get('tier_3_flow_threshold', 48),
        ATR_STOP_LOSS_ENABLED=hybrid_data.get('atr_stop_loss_enabled', True),
        ATR_MULTIPLIER=hybrid_data.get('atr_multiplier', 1.5),
        VOLUME_PROFILE_ENTRY_ENABLED=hybrid_data.get('volume_profile_entry_enabled', True),
        LIQUIDITY_GRAB_ENABLED=hybrid_data.get('liquidity_grab_enabled', True),
        EMA_200_TREND_FILTER_ENABLED=hybrid_data.get('ema_200_trend_filter_enabled', True),
        AI_CONFIDENCE_MODEL_ENABLED=hybrid_data.get('ai_confidence_model_enabled', False),
        WHALE_DETECTION_ENABLED=hybrid_data.get('whale_detection_enabled', False),
        KEYZONE_ENABLED=hybrid_data.get('keyzone_enabled', False),
        PULLBACK_ENABLED=hybrid_data.get('pullback_enabled', False),
        DOME_DETECTION_ENABLED=hybrid_data.get('dome_detection_enabled', False),
        LANGUAGE='en',
        TP_CONFIG=tp_config
    )
    
    # Create main Config object
    config = Config()
    config.TELEGRAM_CONFIG = telegram_config
    config.FUTURES_CONFIG = futures_config
    config.HYBRID_CONFIG = hybrid_config
    
    # Test connection
    print(f"\n🔌 {lang.get_text('scanning')}...")
    test_client = BinanceFuturesClient(config)
    connected = False
    
    for attempt in range(3):
        try:
            if test_client.test_connection():
                connected = True
                break
        except:
            time.sleep(2)
    
    if connected:
        print(f"✅ {lang.get_text('success')}")
    else:
        print(f"⚠️ {lang.get_text('warning')}")
    
    # Initialize bot
    try:
        bot = UltimateHybridBot(telegram_config, futures_config)
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return
    
    # Send Telegram startup message
    if telegram_config.BOT_TOKEN and telegram_config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        print(f"\n📱 {lang.get_text('telegram_alert')}...")
        if bot.notifier.send_message(f"🤖 {lang.get_text('welcome')}"):
            print(f"✅ {lang.get_text('success')}")
        else:
            print(f"⚠️ {lang.get_text('warning')}")
    
    # Display menu
    print("\n" + "="*80)
    print(lang.get_text('scanning'))
    print("="*80)
    print("1. Single scan (run once)")
    print("2. Continuous (10 seconds)")
    print("3. Continuous (30 seconds)")
    print("4. Continuous (1 minute)")
    print("5. Continuous (5 minutes)")
    print("6. Continuous (15 minutes)")
    print(f"7. Use config setting ({interval} seconds)")
    print("8. Generate Documentation")
    print("9. Show Configuration")
    print("10. 🚀 PRO TRADER MODE (Complete Advanced Analysis)")
    print("0. Exit")
    
    # Handle user choice
    while True:
        choice = input(f"\n{lang.get_text('start')} (0-10): ").strip()
        
        if choice == '0':
            print(f"\n👋 {lang.get_text('goodbye')}")
            break
            
        elif choice == '1':
            print(f"\n🔍 {lang.get_text('scanning')}...")
            bot.run_smart_scan(continuous=False)
            
        elif choice == '2':
            print(f"\n🔍 {lang.get_text('scanning')} every 10 seconds...")
            print("Press Ctrl+C to stop")
            bot.run_smart_scan(continuous=True, interval_seconds=10)
            
        elif choice == '3':
            print(f"\n🔍 {lang.get_text('scanning')} every 30 seconds...")
            print("Press Ctrl+C to stop")
            bot.run_smart_scan(continuous=True, interval_seconds=30)
            
        elif choice == '4':
            print(f"\n🔍 {lang.get_text('scanning')} every 1 minute...")
            print("Press Ctrl+C to stop")
            bot.run_smart_scan(continuous=True, interval_seconds=60)
            
        elif choice == '5':
            print(f"\n🔍 {lang.get_text('scanning')} every 5 minutes...")
            print("Press Ctrl+C to stop")
            bot.run_smart_scan(continuous=True, interval_seconds=300)
            
        elif choice == '6':
            print(f"\n🔍 {lang.get_text('scanning')} every 15 minutes...")
            print("Press Ctrl+C to stop")
            bot.run_smart_scan(continuous=True, interval_seconds=900)
            
        elif choice == '7':
            interval = config_data.get('scan', {}).get('interval_seconds', 30)
            continuous = config_data.get('scan', {}).get('continuous', True)
            
            if interval < 60:
                time_display = f"{interval} {lang.get_text('seconds')}"
            else:
                minutes = interval // 60
                time_display = f"{minutes} {lang.get_text('minutes')}"
                
            print(f"\n🔍 {lang.get_text('scanning')} {time_display}...")
            print("Press Ctrl+C to stop")
            bot.run_smart_scan(continuous=continuous, interval_seconds=interval)
            
        elif choice == '8':
            print(f"\n📚 Generating documentation...")
            doc_gen = DocumentationGenerator(hybrid_config)
            doc_dir = doc_gen.generate_all_documentation()
            print(f"✅ Documentation generated in {doc_dir}/")
            
        elif choice == '9':
            print(f"\n⚙️ Current Configuration:")
            print(json.dumps(config_data, indent=2, ensure_ascii=False))
            
        elif choice == '10':
            pro_interval = 20  # Pro mode uses 60 seconds by default
            print(f"\n🚀 PRO TRADER MODE - Scanning every {pro_interval} seconds...")
            print("Press Ctrl+C to stop")
            bot.run_pro_trader_scan(continuous=True, interval_seconds=pro_interval)
            
        else:
            print(f"\n❌ {lang.get_text('error')} - Invalid choice")
    
    print(f"\n✅ {lang.get_text('completed')}")
    print(f"\n{lang.get_text('copyright')}")
    print(lang.get_text('powered_by'))


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n👋 Bot stopped by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
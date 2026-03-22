#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ADVANCED ANALYZERS FOR ULTIMATE HYBRID CRYPTO TRADING BOT
================================================================================
Developer: Nhen Bol
Version: 12.0.1
================================================================================
"""

from config_enums import *
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging
import time
from datetime import datetime

logger = logging.getLogger('ULTIMATE_V12')

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value) if value else default
        if callable(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            return int(float(value)) if value else default
        if callable(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default

# ==============================================================================
# ADVANCED CANDLE PATTERN RECOGNITION
# ==============================================================================

@dataclass
class CandlePattern:
    """Candle pattern data"""
    name: str
    type: str
    strength: float
    description: str
    confirmation_needed: bool = True
    reliability: float = 70.0


class AdvancedCandlePatternRecognizer:
    """Advanced candle pattern recognition for pro traders"""
    
    def __init__(self):
        self.patterns_detected = []
        
    def analyze_candle(self, candle: pd.Series, prev_candle: Optional[pd.Series] = None,
                       prev_2_candle: Optional[pd.Series] = None,
                       prev_3_candle: Optional[pd.Series] = None) -> List[CandlePattern]:
        """Analyze single candle for patterns"""
        patterns = []
        
        # Get candle properties with safe conversion
        try:
            open_price = safe_float(candle['open'])
            high = safe_float(candle['high'])
            low = safe_float(candle['low'])
            close = safe_float(candle['close'])
            volume = safe_float(candle['volume'])
        except Exception as e:
            logger.error(f"Error getting candle properties: {e}")
            return patterns
        
        body = abs(close - open_price)
        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low
        total_range = high - low
        
        if total_range == 0:
            return patterns
        
        body_percent = (body / total_range) * 100 if total_range > 0 else 0
        upper_wick_percent = (upper_wick / total_range) * 100 if total_range > 0 else 0
        lower_wick_percent = (lower_wick / total_range) * 100 if total_range > 0 else 0
        
        is_bullish = close > open_price
        is_bearish = close < open_price
        
        # ========== SINGLE CANDLE PATTERNS ==========
        
        # 1. Marubozu
        if upper_wick_percent < 5 and lower_wick_percent < 5 and body_percent > 90:
            if is_bullish:
                patterns.append(CandlePattern(
                    name="BULLISH MARUBOZU",
                    type="bullish",
                    strength=90,
                    description="Strong buying pressure",
                    reliability=85
                ))
            else:
                patterns.append(CandlePattern(
                    name="BEARISH MARUBOZU",
                    type="bearish",
                    strength=90,
                    description="Strong selling pressure",
                    reliability=85
                ))
        
        # 2. Doji
        elif body_percent < 10:
            if upper_wick_percent > 40 and lower_wick_percent < 10:
                patterns.append(CandlePattern(
                    name="DRAGONFLY DOJI",
                    type="reversal_bullish",
                    strength=75,
                    description="Long lower wick, bullish reversal",
                    reliability=70
                ))
            elif lower_wick_percent > 40 and upper_wick_percent < 10:
                patterns.append(CandlePattern(
                    name="GRAVESTONE DOJI",
                    type="reversal_bearish",
                    strength=75,
                    description="Long upper wick, bearish reversal",
                    reliability=70
                ))
            elif upper_wick_percent > 30 and lower_wick_percent > 30:
                patterns.append(CandlePattern(
                    name="LONG-LEGGED DOJI",
                    type="indecision",
                    strength=80,
                    description="High volatility, indecision",
                    reliability=75
                ))
            else:
                patterns.append(CandlePattern(
                    name="DOJI",
                    type="indecision",
                    strength=60,
                    description="Market indecision",
                    reliability=65
                ))
        
        # 3. Hammer / Hanging Man
        elif lower_wick_percent > 60 and body_percent < 30 and upper_wick_percent < 10:
            if is_bullish:
                patterns.append(CandlePattern(
                    name="HAMMER",
                    type="reversal_bullish",
                    strength=85,
                    description="Bullish reversal after downtrend",
                    reliability=80
                ))
            else:
                patterns.append(CandlePattern(
                    name="HANGING MAN",
                    type="reversal_bearish",
                    strength=85,
                    description="Bearish reversal after uptrend",
                    reliability=80
                ))
        
        # 4. Shooting Star / Inverted Hammer
        elif upper_wick_percent > 60 and body_percent < 30 and lower_wick_percent < 10:
            if is_bullish:
                patterns.append(CandlePattern(
                    name="INVERTED HAMMER",
                    type="reversal_bullish",
                    strength=80,
                    description="Potential bullish reversal",
                    reliability=75
                ))
            else:
                patterns.append(CandlePattern(
                    name="SHOOTING STAR",
                    type="reversal_bearish",
                    strength=85,
                    description="Bearish reversal after uptrend",
                    reliability=80
                ))
        
        # 5. Spinning Top
        elif 30 < body_percent < 50 and upper_wick_percent > 20 and lower_wick_percent > 20:
            patterns.append(CandlePattern(
                name="SPINNING TOP",
                type="indecision",
                strength=50,
                description="Market uncertainty",
                reliability=60
            ))
        
        # ========== TWO CANDLE PATTERNS ==========
        
        if prev_candle is not None:
            try:
                prev_open = safe_float(prev_candle['open'])
                prev_high = safe_float(prev_candle['high'])
                prev_low = safe_float(prev_candle['low'])
                prev_close = safe_float(prev_candle['close'])
                prev_body = abs(prev_close - prev_open)
                prev_is_bullish = prev_close > prev_open
                prev_is_bearish = prev_close < prev_open
                
                # 6. Engulfing Patterns
                if is_bullish and prev_is_bearish:
                    if close > prev_open and open < prev_close and body > prev_body * 1.2:
                        patterns.append(CandlePattern(
                            name="BULLISH ENGULFING",
                            type="reversal_bullish",
                            strength=90,
                            description="Strong bullish reversal",
                            reliability=85
                        ))
                
                elif is_bearish and prev_is_bullish:
                    if close < prev_open and open > prev_close and body > prev_body * 1.2:
                        patterns.append(CandlePattern(
                            name="BEARISH ENGULFING",
                            type="reversal_bearish",
                            strength=90,
                            description="Strong bearish reversal",
                            reliability=85
                        ))
                
                # 7. Harami Patterns
                if is_bullish and prev_is_bearish:
                    if open > prev_close and close < prev_open and body < prev_body * 0.6:
                        patterns.append(CandlePattern(
                            name="BULLISH HARAMI",
                            type="reversal_bullish",
                            strength=75,
                            description="Potential bullish reversal",
                            reliability=70
                        ))
                
                elif is_bearish and prev_is_bullish:
                    if open < prev_close and close > prev_open and body < prev_body * 0.6:
                        patterns.append(CandlePattern(
                            name="BEARISH HARAMI",
                            type="reversal_bearish",
                            strength=75,
                            description="Potential bearish reversal",
                            reliability=70
                        ))
                
                # 8. Piercing Line / Dark Cloud Cover
                if is_bullish and prev_is_bearish:
                    if open < prev_low and close > (prev_open + prev_close) / 2 and close < prev_open:
                        patterns.append(CandlePattern(
                            name="PIERCING LINE",
                            type="reversal_bullish",
                            strength=85,
                            description="Bullish reversal",
                            reliability=80
                        ))
                
                elif is_bearish and prev_is_bullish:
                    if open > prev_high and close < (prev_open + prev_close) / 2 and close > prev_close:
                        patterns.append(CandlePattern(
                            name="DARK CLOUD COVER",
                            type="reversal_bearish",
                            strength=85,
                            description="Bearish reversal",
                            reliability=80
                        ))
                
                # 9. Tweezer Tops / Bottoms
                if abs(high - prev_high) / prev_high < 0.001 if prev_high > 0 else False:
                    if is_bearish and prev_is_bullish:
                        patterns.append(CandlePattern(
                            name="TWEEZER TOP",
                            type="reversal_bearish",
                            strength=80,
                            description="Double top, strong resistance",
                            reliability=75
                        ))
                
                if abs(low - prev_low) / prev_low < 0.001 if prev_low > 0 else False:
                    if is_bullish and prev_is_bearish:
                        patterns.append(CandlePattern(
                            name="TWEEZER BOTTOM",
                            type="reversal_bullish",
                            strength=80,
                            description="Double bottom, strong support",
                            reliability=75
                        ))
                        
            except Exception as e:
                logger.error(f"Error in two candle patterns: {e}")
        
        # ========== THREE CANDLE PATTERNS ==========
        
        if prev_candle is not None and prev_2_candle is not None:
            try:
                prev_2_open = safe_float(prev_2_candle['open'])
                prev_2_close = safe_float(prev_2_candle['close'])
                
                # Morning Star / Evening Star
                if prev_2_close < prev_2_open and self._is_doji(prev_candle) and is_bullish:
                    patterns.append(CandlePattern(
                        name="MORNING STAR",
                        type="reversal_bullish",
                        strength=95,
                        description="Strong bullish reversal",
                        reliability=90
                    ))
                
                elif prev_2_close > prev_2_open and self._is_doji(prev_candle) and is_bearish:
                    patterns.append(CandlePattern(
                        name="EVENING STAR",
                        type="reversal_bearish",
                        strength=95,
                        description="Strong bearish reversal",
                        reliability=90
                    ))
            except Exception as e:
                logger.error(f"Error in three candle patterns: {e}")
        
        return patterns
    
    def _is_doji(self, candle: pd.Series) -> bool:
        """Check if candle is a doji"""
        try:
            body = abs(safe_float(candle['close']) - safe_float(candle['open']))
            total_range = safe_float(candle['high']) - safe_float(candle['low'])
            if total_range == 0:
                return False
            return (body / total_range) < 0.1
        except Exception:
            return False
    
    def analyze_multiple_timeframes(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict]]:
        """Analyze candle patterns across multiple timeframes"""
        results = {}
        
        for tf, df in dataframes.items():
            if df is None or len(df) < 5:
                continue
            
            tf_patterns = []
            
            for i in range(3, len(df)):
                try:
                    candle = df.iloc[i]
                    prev_candle = df.iloc[i-1] if i > 0 else None
                    prev_2_candle = df.iloc[i-2] if i > 1 else None
                    prev_3_candle = df.iloc[i-3] if i > 2 else None
                    
                    patterns = self.analyze_candle(candle, prev_candle, prev_2_candle, prev_3_candle)
                    
                    for pattern in patterns:
                        pattern_data = {
                            'pattern': pattern,
                            'timestamp': i,
                            'price': safe_float(candle['close'])
                        }
                        tf_patterns.append(pattern_data)
                except Exception as e:
                    logger.debug(f"Error analyzing candle at index {i} for {tf}: {e}")
                    continue
            
            results[tf] = tf_patterns
        
        return results


# ==============================================================================
# SUPPORT/RESISTANCE DETECTOR
# ==============================================================================

@dataclass
class SupportResistanceLevel:
    """Support/Resistance level data"""
    price: float
    type: str
    strength: float
    touches: int
    timeframe: str
    is_major: bool = False
    description: str = ""


class SupportResistanceDetector:
    """Advanced support and resistance detection"""
    
    def __init__(self):
        self.levels = []
        
    def detect_levels(self, df: pd.DataFrame, timeframe: str = '1h') -> List[SupportResistanceLevel]:
        """Detect support and resistance levels"""
        levels = []
        
        if df is None or len(df) < 50:
            return levels
        
        try:
            # Method 1: Swing Highs/Lows
            swing_levels = self._detect_swing_points(df)
            levels.extend(swing_levels)
            
            # Method 2: Volume Profile
            volume_levels = self._detect_volume_nodes(df)
            levels.extend(volume_levels)
            
            # Method 3: Fibonacci levels
            fib_levels = self._detect_fibonacci_levels(df)
            levels.extend(fib_levels)
            
            # Method 4: Moving averages
            ma_levels = self._detect_ma_levels(df)
            levels.extend(ma_levels)
            
            # Method 5: Pivot points
            pivot_levels = self._detect_pivot_points(df)
            levels.extend(pivot_levels)
            
            # Merge nearby levels
            levels = self._merge_levels(levels)
            
            # Mark major levels
            for level in levels:
                if level.strength > 70:
                    level.is_major = True
                    level.description = f"Major {level.type} level"
            
        except Exception as e:
            logger.error(f"Error detecting levels: {e}")
        
        self.levels = levels
        return levels
    
    def _detect_swing_points(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect swing highs and lows"""
        levels = []
        
        try:
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            
            # Find swing highs
            for i in range(2, len(high)-2):
                if (high[i] > high[i-1] and high[i] > high[i-2] and
                    high[i] > high[i+1] and high[i] > high[i+2]):
                    
                    touches = 0
                    for j in range(len(close)):
                        if abs(close[j] - high[i]) / high[i] < 0.01:
                            touches += 1
                    
                    strength = min(50 + touches * 5, 100)
                    
                    levels.append(SupportResistanceLevel(
                        price=float(high[i]),
                        type='resistance',
                        strength=strength,
                        touches=touches,
                        timeframe='all',
                        description=f"Swing high with {touches} touches"
                    ))
            
            # Find swing lows
            for i in range(2, len(low)-2):
                if (low[i] < low[i-1] and low[i] < low[i-2] and
                    low[i] < low[i+1] and low[i] < low[i+2]):
                    
                    touches = 0
                    for j in range(len(close)):
                        if abs(close[j] - low[i]) / low[i] < 0.01:
                            touches += 1
                    
                    strength = min(50 + touches * 5, 100)
                    
                    levels.append(SupportResistanceLevel(
                        price=float(low[i]),
                        type='support',
                        strength=strength,
                        touches=touches,
                        timeframe='all',
                        description=f"Swing low with {touches} touches"
                    ))
        except Exception as e:
            logger.error(f"Error detecting swing points: {e}")
        
        return levels
    
    def _detect_volume_nodes(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect high volume nodes"""
        levels = []
        
        if len(df) < 20:
            return levels
        
        try:
            price_min = float(df['low'].min())
            price_max = float(df['high'].max())
            price_range = price_max - price_min
            num_bins = 50
            bin_size = price_range / num_bins if num_bins > 0 else 0
            
            if bin_size == 0:
                return levels
            
            volume_by_price = defaultdict(float)
            
            for _, row in df.iterrows():
                row_low = float(row['low'])
                row_high = float(row['high'])
                row_volume = float(row['volume'])
                
                for i in range(num_bins):
                    bin_low = price_min + i * bin_size
                    bin_high = bin_low + bin_size
                    
                    if row_low <= bin_high and row_high >= bin_low:
                        overlap = min(row_high, bin_high) - max(row_low, bin_low)
                        if overlap > 0:
                            volume_by_price[(bin_low + bin_high)/2] += row_volume * (overlap / (row_high - row_low))
            
            if volume_by_price:
                volumes = list(volume_by_price.values())
                avg_volume = np.mean(volumes) if volumes else 0
                std_volume = np.std(volumes) if len(volumes) > 1 else avg_volume * 0.5
                
                for price, volume in volume_by_price.items():
                    if volume > avg_volume + 1.5 * std_volume:
                        recent_price = float(df['close'].iloc[-1])
                        
                        if recent_price > price:
                            level_type = 'support'
                            desc = "High volume support zone"
                        else:
                            level_type = 'resistance'
                            desc = "High volume resistance zone"
                        
                        strength = min(70 + (volume - avg_volume) / std_volume * 10, 100)
                        
                        levels.append(SupportResistanceLevel(
                            price=float(price),
                            type=level_type,
                            strength=strength,
                            touches=0,
                            timeframe='all',
                            description=desc
                        ))
        except Exception as e:
            logger.error(f"Error detecting volume nodes: {e}")
        
        return levels
    
    def _detect_fibonacci_levels(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect Fibonacci retracement levels"""
        levels = []
        
        if len(df) < 50:
            return levels
        
        try:
            high_idx = int(df['high'].argmax())
            low_idx = int(df['low'].argmin())
            
            fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
            fib_names = ['23.6%', '38.2%', '50%', '61.8%', '78.6%']
            
            if high_idx > low_idx:  # Downtrend
                swing_high = float(df['high'].iloc[high_idx])
                swing_low = float(df['low'].iloc[low_idx])
                
                for i, fib in enumerate(fib_levels):
                    price = swing_high - (swing_high - swing_low) * fib
                    level_type = 'resistance' if fib < 0.5 else 'support'
                    
                    levels.append(SupportResistanceLevel(
                        price=price,
                        type=level_type,
                        strength=70 + fib * 30,
                        touches=0,
                        timeframe='all',
                        description=f"Fibonacci {fib_names[i]} retracement"
                    ))
            else:  # Uptrend
                swing_low = float(df['low'].iloc[low_idx])
                swing_high = float(df['high'].iloc[high_idx])
                
                for i, fib in enumerate(fib_levels):
                    price = swing_low + (swing_high - swing_low) * fib
                    level_type = 'support' if fib < 0.5 else 'resistance'
                    
                    levels.append(SupportResistanceLevel(
                        price=price,
                        type=level_type,
                        strength=70 + fib * 30,
                        touches=0,
                        timeframe='all',
                        description=f"Fibonacci {fib_names[i]} retracement"
                    ))
        except Exception as e:
            logger.error(f"Error detecting fibonacci levels: {e}")
        
        return levels
    
    def _detect_ma_levels(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect moving average levels"""
        levels = []
        
        periods = [20, 50, 100, 200]
        
        try:
            for period in periods:
                if len(df) >= period:
                    ma = float(df['close'].rolling(window=period).mean().iloc[-1])
                    current_price = float(df['close'].iloc[-1])
                    
                    if current_price > ma:
                        level_type = 'support'
                        desc = f"{period} MA acting as support"
                    else:
                        level_type = 'resistance'
                        desc = f"{period} MA acting as resistance"
                    
                    strength = 60 + (period / 10)
                    
                    levels.append(SupportResistanceLevel(
                        price=ma,
                        type=level_type,
                        strength=strength,
                        touches=0,
                        timeframe='all',
                        description=desc
                    ))
        except Exception as e:
            logger.error(f"Error detecting MA levels: {e}")
        
        return levels
    
    def _detect_pivot_points(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect pivot points"""
        levels = []
        
        if len(df) < 20:
            return levels
        
        try:
            high = float(df['high'].iloc[-20:].max())
            low = float(df['low'].iloc[-20:].min())
            close = float(df['close'].iloc[-1])
            
            pivot = (high + low + close) / 3
            
            r1 = 2 * pivot - low
            r2 = pivot + (high - low)
            r3 = high + 2 * (pivot - low)
            s1 = 2 * pivot - high
            s2 = pivot - (high - low)
            s3 = low - 2 * (high - pivot)
            
            pivot_levels = [
                (pivot, 'pivot', 80, "Pivot Point"),
                (r1, 'resistance', 75, "Resistance 1"),
                (r2, 'resistance', 70, "Resistance 2"),
                (r3, 'resistance', 65, "Resistance 3"),
                (s1, 'support', 75, "Support 1"),
                (s2, 'support', 70, "Support 2"),
                (s3, 'support', 65, "Support 3")
            ]
            
            for price, level_type, strength, desc in pivot_levels:
                levels.append(SupportResistanceLevel(
                    price=price,
                    type=level_type,
                    strength=strength,
                    touches=0,
                    timeframe='daily',
                    description=desc
                ))
        except Exception as e:
            logger.error(f"Error detecting pivot points: {e}")
        
        return levels
    
    def _merge_levels(self, levels: List[SupportResistanceLevel], threshold: float = 0.01) -> List[SupportResistanceLevel]:
        """Merge nearby levels"""
        if not levels:
            return []
        
        # Sort by price
        levels.sort(key=lambda x: x.price)
        
        merged = []
        current_group = [levels[0]]
        
        for i in range(1, len(levels)):
            if abs(levels[i].price - current_group[-1].price) / current_group[-1].price < threshold:
                current_group.append(levels[i])
            else:
                # Merge current group
                if len(current_group) > 1:
                    avg_price = np.mean([l.price for l in current_group])
                    avg_strength = np.mean([l.strength for l in current_group])
                    total_touches = sum([l.touches for l in current_group])
                    
                    support_count = sum(1 for l in current_group if l.type == 'support')
                    resistance_count = sum(1 for l in current_group if l.type == 'resistance')
                    
                    level_type = 'support' if support_count > resistance_count else 'resistance'
                    
                    merged.append(SupportResistanceLevel(
                        price=avg_price,
                        type=level_type,
                        strength=min(avg_strength + 10, 100),
                        touches=total_touches,
                        timeframe='merged',
                        description=f"Merged level from {len(current_group)} touches"
                    ))
                else:
                    merged.append(current_group[0])
                
                current_group = [levels[i]]
        
        # Handle last group
        if current_group:
            if len(current_group) > 1:
                avg_price = np.mean([l.price for l in current_group])
                avg_strength = np.mean([l.strength for l in current_group])
                total_touches = sum([l.touches for l in current_group])
                
                support_count = sum(1 for l in current_group if l.type == 'support')
                resistance_count = sum(1 for l in current_group if l.type == 'resistance')
                
                level_type = 'support' if support_count > resistance_count else 'resistance'
                
                merged.append(SupportResistanceLevel(
                    price=avg_price,
                    type=level_type,
                    strength=min(avg_strength + 10, 100),
                    touches=total_touches,
                    timeframe='merged',
                    description=f"Merged level from {len(current_group)} touches"
                ))
            else:
                merged.append(current_group[0])
        
        return merged
    
    def get_nearest_levels(self, price: float, num_levels: int = 5) -> Tuple[List[SupportResistanceLevel], List[SupportResistanceLevel]]:
        """Get nearest support and resistance levels"""
        supports = [l for l in self.levels if l.type == 'support']
        resistances = [l for l in self.levels if l.type == 'resistance' or l.type == 'pivot']
        
        supports_below = [s for s in supports if s.price < price]
        resistances_above = [r for r in resistances if r.price > price]
        
        supports_below.sort(key=lambda x: price - x.price)
        resistances_above.sort(key=lambda x: x.price - price)
        
        return supports_below[:num_levels], resistances_above[:num_levels]


# ==============================================================================
# MARKET PROFILE ANALYZER
# ==============================================================================

@dataclass
class MarketProfile:
    """Market profile data"""
    value_area_high: float
    value_area_low: float
    poc_price: float
    high_volume_nodes: List[float]
    low_volume_nodes: List[float]
    volume_profile: Dict[float, float]
    tpo_count: int
    initial_balance_high: float
    initial_balance_low: float
    developing_range: Tuple[float, float]
    profile_type: str


class MarketProfileAnalyzer:
    """Complete market profile analyzer"""
    
    def __init__(self, num_bins: int = 24):
        self.num_bins = num_bins
        
    def analyze_profile(self, df: pd.DataFrame, period: str = 'day') -> Optional[MarketProfile]:
        """Analyze market profile"""
        
        if df is None or len(df) < 10:
            return None
        
        try:
            price_min = float(df['low'].min())
            price_max = float(df['high'].max())
            price_range = price_max - price_min
            
            if price_range == 0:
                return None
            
            bin_size = price_range / self.num_bins
            
            bins = {}
            tpo_count = {}
            
            for i in range(self.num_bins):
                low = price_min + i * bin_size
                high = low + bin_size
                bins[(low, high)] = 0.0
                tpo_count[(low, high)] = 0
            
            for _, row in df.iterrows():
                row_low = float(row['low'])
                row_high = float(row['high'])
                row_volume = float(row['volume'])
                
                for (low, high) in bins.keys():
                    if row_low <= high and row_high >= low:
                        overlap = min(row_high, high) - max(row_low, low)
                        if overlap > 0:
                            volume_contrib = row_volume * (overlap / (row_high - row_low))
                            bins[(low, high)] += volume_contrib
                            tpo_count[(low, high)] += 1
            
            if not bins:
                return None
            
            # Find Point of Control
            poc_bin = max(bins.items(), key=lambda x: x[1])
            poc_price = (poc_bin[0][0] + poc_bin[0][1]) / 2
            
            # Calculate value area
            total_volume = sum(bins.values())
            value_area_volume = 0
            sorted_bins = sorted(bins.items(), key=lambda x: x[1], reverse=True)
            value_area_bins = []
            
            for bin_range, volume in sorted_bins:
                value_area_volume += volume
                value_area_bins.append(bin_range)
                if value_area_volume >= total_volume * 0.7:
                    break
            
            if value_area_bins:
                value_area_low = min([b[0] for b in value_area_bins])
                value_area_high = max([b[1] for b in value_area_bins])
            else:
                value_area_low = poc_price * 0.98
                value_area_high = poc_price * 1.02
            
            # Find high/low volume nodes
            avg_volume_per_bin = total_volume / self.num_bins if self.num_bins > 0 else 0
            high_volume_nodes = []
            low_volume_nodes = []
            
            for bin_range, volume in bins.items():
                mid_price = (bin_range[0] + bin_range[1]) / 2
                if volume > avg_volume_per_bin * 1.5:
                    high_volume_nodes.append(mid_price)
                elif volume < avg_volume_per_bin * 0.5:
                    low_volume_nodes.append(mid_price)
            
            # Determine profile type
            if poc_price > value_area_high * 0.9:
                profile_type = 'p'
            elif poc_price < value_area_low * 1.1:
                profile_type = 'b'
            elif (value_area_high - poc_price) / (poc_price - value_area_low) > 1.5:
                profile_type = 'd'
            elif (poc_price - value_area_low) / (value_area_high - poc_price) > 1.5:
                profile_type = 'p'
            else:
                profile_type = 'normal'
            
            volume_profile = {}
            for bin_range, volume in bins.items():
                volume_profile[(bin_range[0] + bin_range[1]) / 2] = volume
            
            return MarketProfile(
                value_area_high=value_area_high,
                value_area_low=value_area_low,
                poc_price=poc_price,
                high_volume_nodes=high_volume_nodes,
                low_volume_nodes=low_volume_nodes,
                volume_profile=volume_profile,
                tpo_count=sum(tpo_count.values()),
                initial_balance_high=price_max,
                initial_balance_low=price_min,
                developing_range=(price_min, price_max),
                profile_type=profile_type
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market profile: {e}")
            return None
    
    def get_trading_opportunities(self, profile: MarketProfile, current_price: float) -> Dict[str, Any]:
        """Get trading opportunities"""
        opportunities = {
            'buy_zones': [],
            'sell_zones': [],
            'neutral_zones': [],
            'breakout_levels': []
        }
        
        if not profile:
            return opportunities
        
        try:
            # Discount zone
            if current_price < profile.value_area_low:
                opportunities['buy_zones'].append({
                    'price': profile.value_area_low,
                    'type': 'value_area_low',
                    'confidence': 80,
                    'reason': 'Price below value area - buying opportunity'
                })
            
            # Premium zone
            if current_price > profile.value_area_high:
                opportunities['sell_zones'].append({
                    'price': profile.value_area_high,
                    'type': 'value_area_high',
                    'confidence': 80,
                    'reason': 'Price above value area - selling opportunity'
                })
            
            # Point of Control
            if abs(current_price - profile.poc_price) / profile.poc_price < 0.01:
                opportunities['neutral_zones'].append({
                    'price': profile.poc_price,
                    'type': 'poc',
                    'confidence': 70,
                    'reason': 'At Point of Control - equilibrium'
                })
            
            # High volume nodes
            for node in profile.high_volume_nodes[:5]:
                if node < current_price:
                    opportunities['buy_zones'].append({
                        'price': node,
                        'type': 'high_volume_support',
                        'confidence': 75,
                        'reason': 'High volume node acting as support'
                    })
                elif node > current_price:
                    opportunities['sell_zones'].append({
                        'price': node,
                        'type': 'high_volume_resistance',
                        'confidence': 75,
                        'reason': 'High volume node acting as resistance'
                    })
            
            # Breakout levels
            opportunities['breakout_levels'] = [
                {'price': profile.value_area_high, 'type': 'value_area_high_breakout'},
                {'price': profile.value_area_low, 'type': 'value_area_low_breakout'}
            ]
            
        except Exception as e:
            logger.error(f"Error getting trading opportunities: {e}")
        
        return opportunities


# ==============================================================================
# ORDER FLOW ANALYZER
# ==============================================================================

@dataclass
class OrderFlowAnalysis:
    """Complete order flow analysis"""
    bid_ask_imbalance: float
    cumulative_delta: float
    delta_trend: str
    aggressive_buying: bool
    aggressive_selling: bool
    large_trades: List[Dict]
    absorption_detected: bool
    exhaustion_detected: bool
    stop_hunting_detected: bool
    iceberg_detected: bool
    spoofing_detected: bool
    order_flow_strength: float
    description: str


class CompleteOrderFlowAnalyzer:
    """Complete order flow analyzer"""
    
    def __init__(self, client):
        self.client = client
        from collections import deque
        self.delta_history = deque(maxlen=100)
        self.large_trade_threshold = 50000
        
    def analyze_order_flow(self, symbol: str, ob_data: Optional[Dict], trades: List[Dict]) -> OrderFlowAnalysis:
        """Complete order flow analysis"""
        
        try:
            imbalance = self._calculate_imbalance(ob_data)
            delta, delta_trend = self._calculate_delta(trades)
            aggressive_buying, aggressive_selling = self._detect_aggressive_trades(trades)
            large_trades = self._detect_large_trades(trades)
            absorption = self._detect_absorption(ob_data, trades)
            exhaustion = self._detect_exhaustion(trades, delta)
            stop_hunting = self._detect_stop_hunting(trades, ob_data)
            iceberg = self._detect_iceberg(ob_data)
            spoofing = self._detect_spoofing(ob_data)
            
            strength = self._calculate_flow_strength(
                imbalance, delta, aggressive_buying, aggressive_selling,
                large_trades, absorption, exhaustion
            )
            
            description = self._generate_description(
                imbalance, delta_trend, aggressive_buying, aggressive_selling,
                absorption, exhaustion, stop_hunting, iceberg, spoofing
            )
            
            return OrderFlowAnalysis(
                bid_ask_imbalance=imbalance,
                cumulative_delta=delta,
                delta_trend=delta_trend,
                aggressive_buying=aggressive_buying,
                aggressive_selling=aggressive_selling,
                large_trades=large_trades,
                absorption_detected=absorption,
                exhaustion_detected=exhaustion,
                stop_hunting_detected=stop_hunting,
                iceberg_detected=iceberg,
                spoofing_detected=spoofing,
                order_flow_strength=strength,
                description=description
            )
        except Exception as e:
            logger.error(f"Order flow analysis error: {e}")
            return OrderFlowAnalysis(
                bid_ask_imbalance=0, cumulative_delta=0, delta_trend="NEUTRAL",
                aggressive_buying=False, aggressive_selling=False, large_trades=[],
                absorption_detected=False, exhaustion_detected=False,
                stop_hunting_detected=False, iceberg_detected=False,
                spoofing_detected=False, order_flow_strength=50,
                description="Error analyzing order flow"
            )
    
    def _calculate_imbalance(self, ob_data: Optional[Dict]) -> float:
        """Calculate bid-ask imbalance"""
        if not ob_data or 'bids' not in ob_data or 'asks' not in ob_data:
            return 0.0
        
        try:
            bids = ob_data.get('bids', [])[:10]
            asks = ob_data.get('asks', [])[:10]
            
            bid_volume = 0.0
            for b in bids:
                try:
                    bid_volume += safe_float(b[1]) * safe_float(b[0])
                except Exception:
                    pass
            
            ask_volume = 0.0
            for a in asks:
                try:
                    ask_volume += safe_float(a[1]) * safe_float(a[0])
                except Exception:
                    pass
            
            total = bid_volume + ask_volume
            if total > 0:
                return ((bid_volume - ask_volume) / total) * 100
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating imbalance: {e}")
            return 0.0
    
    def _calculate_delta(self, trades: List[Dict]) -> Tuple[float, str]:
        """Calculate cumulative delta"""
        if not trades:
            return 0.0, "NEUTRAL"
        
        try:
            delta = 0.0
            for trade in trades:
                price = safe_float(trade.get('price', 0))
                qty = safe_float(trade.get('qty', 0))
                is_buyer_maker = trade.get('isBuyerMaker', False)
                
                if is_buyer_maker:
                    delta -= qty * price
                else:
                    delta += qty * price
            
            self.delta_history.append(delta)
            
            if len(self.delta_history) >= 10:
                recent = list(self.delta_history)[-10:]
                if all(d > 0 for d in recent[-3:]):
                    trend = "STRONG_BULLISH"
                elif all(d < 0 for d in recent[-3:]):
                    trend = "STRONG_BEARISH"
                elif sum(recent[-5:]) > 0:
                    trend = "BULLISH"
                elif sum(recent[-5:]) < 0:
                    trend = "BEARISH"
                else:
                    trend = "NEUTRAL"
            else:
                trend = "NEUTRAL"
            
            return delta, trend
        except Exception as e:
            logger.error(f"Error calculating delta: {e}")
            return 0.0, "NEUTRAL"
    
    def _detect_aggressive_trades(self, trades: List[Dict]) -> Tuple[bool, bool]:
        """Detect aggressive trades"""
        if not trades or len(trades) < 10:
            return False, False
        
        try:
            last_trades = trades[-10:]
            buys = 0
            sells = 0
            
            for trade in last_trades:
                is_buyer_maker = trade.get('isBuyerMaker', False)
                if not is_buyer_maker:
                    buys += 1
                else:
                    sells += 1
            
            return buys > 7, sells > 7
        except Exception:
            return False, False
    
    def _detect_large_trades(self, trades: List[Dict]) -> List[Dict]:
        """Detect large trades"""
        large_trades = []
        
        try:
            for trade in trades:
                price = safe_float(trade.get('price', 0))
                qty = safe_float(trade.get('qty', 0))
                value = price * qty
                
                if value >= self.large_trade_threshold:
                    large_trades.append({
                        'price': price,
                        'qty': qty,
                        'value': value,
                        'side': 'BUY' if not trade.get('isBuyerMaker', False) else 'SELL',
                        'time': trade.get('time', 0)
                    })
        except Exception as e:
            logger.error(f"Error detecting large trades: {e}")
        
        return large_trades
    
    def _detect_absorption(self, ob_data: Optional[Dict], trades: List[Dict]) -> bool:
        """Detect absorption"""
        if not ob_data or not trades:
            return False
        
        try:
            bids = ob_data.get('bids', [])
            asks = ob_data.get('asks', [])
            
            if len(bids) < 5 or len(asks) < 5:
                return False
            
            bid_wall_size = sum(safe_float(b[1]) for b in bids[:3]) * safe_float(bids[0][0])
            ask_wall_size = sum(safe_float(a[1]) for a in asks[:3]) * safe_float(asks[0][0])
            
            if bid_wall_size > ask_wall_size * 3 and len(trades) > 10:
                last_trades = trades[-10:]
                sell_count = sum(1 for t in last_trades if t.get('isBuyerMaker', False))
                if sell_count > 7:
                    return True
            
            if ask_wall_size > bid_wall_size * 3 and len(trades) > 10:
                last_trades = trades[-10:]
                buy_count = sum(1 for t in last_trades if not t.get('isBuyerMaker', False))
                if buy_count > 7:
                    return True
        except Exception:
            pass
        
        return False
    
    def _detect_exhaustion(self, trades: List[Dict], delta: float) -> bool:
        """Detect exhaustion"""
        if len(trades) < 20:
            return False
        
        try:
            recent_volume = sum(safe_float(t.get('qty', 0)) for t in trades[-10:])
            avg_volume = sum(safe_float(t.get('qty', 0)) for t in trades[-20:-10]) / 10 if len(trades) > 20 else recent_volume
            
            if avg_volume == 0:
                return False
            
            volume_ratio = recent_volume / avg_volume
            
            return volume_ratio < 0.5 and abs(delta) > 1000000
        except Exception:
            return False
    
    def _detect_stop_hunting(self, trades: List[Dict], ob_data: Optional[Dict]) -> bool:
        """Detect stop hunting"""
        if len(trades) < 10:
            return False
        
        try:
            prices = []
            for t in trades[-10:]:
                if 'price' in t:
                    prices.append(safe_float(t['price']))
            
            if len(prices) < 5:
                return False
            
            price_change = abs(prices[-1] - prices[0]) / prices[0] * 100
            volume = sum(safe_float(t.get('qty', 0)) for t in trades[-10:])
            
            return price_change > 1.0 and volume < 10000
        except Exception:
            return False
    
    def _detect_iceberg(self, ob_data: Optional[Dict]) -> bool:
        """Detect iceberg orders"""
        if not ob_data:
            return False
        
        try:
            bid_prices = [b[0] for b in ob_data.get('bids', [])]
            ask_prices = [a[0] for a in ob_data.get('asks', [])]
            
            if len(set(bid_prices)) < len(bid_prices) * 0.8:
                return True
            if len(set(ask_prices)) < len(ask_prices) * 0.8:
                return True
        except Exception:
            pass
        
        return False
    
    def _detect_spoofing(self, ob_data: Optional[Dict]) -> bool:
        """Detect spoofing"""
        if not ob_data:
            return False
        
        try:
            bids = ob_data.get('bids', [])
            asks = ob_data.get('asks', [])
            
            if len(bids) > 5:
                best_bid = safe_float(bids[0][0])
                
                for bid in bids[5:]:
                    bid_price = safe_float(bid[0])
                    bid_size = safe_float(bid[1])
                    if bid_price < best_bid * 0.99 and bid_size * bid_price > 1000000:
                        return True
            
            if len(asks) > 5:
                best_ask = safe_float(asks[0][0])
                
                for ask in asks[5:]:
                    ask_price = safe_float(ask[0])
                    ask_size = safe_float(ask[1])
                    if ask_price > best_ask * 1.01 and ask_size * ask_price > 1000000:
                        return True
        except Exception:
            pass
        
        return False
    
    def _calculate_flow_strength(self, imbalance: float, delta: float,
                                  aggressive_buying: bool, aggressive_selling: bool,
                                  large_trades: List, absorption: bool,
                                  exhaustion: bool) -> float:
        """Calculate flow strength"""
        strength = 50.0
        
        strength += min(abs(imbalance), 30)
        strength += min(abs(delta) / 1000000, 30)
        
        if aggressive_buying or aggressive_selling:
            strength += 10
        strength += len(large_trades) * 2
        
        if absorption:
            strength += 15
        if exhaustion:
            strength -= 10
        
        return max(0, min(100, strength))
    
    def _generate_description(self, imbalance: float, delta_trend: str,
                               aggressive_buying: bool, aggressive_selling: bool,
                               absorption: bool, exhaustion: bool,
                               stop_hunting: bool, iceberg: bool,
                               spoofing: bool) -> str:
        """Generate description"""
        parts = []
        
        if aggressive_buying:
            parts.append("🔥 Aggressive buying")
        if aggressive_selling:
            parts.append("🔥 Aggressive selling")
        
        if imbalance > 20:
            parts.append(f"📊 Strong buy imbalance ({imbalance:.1f}%)")
        elif imbalance < -20:
            parts.append(f"📊 Strong sell imbalance ({abs(imbalance):.1f}%)")
        
        if delta_trend != "NEUTRAL":
            parts.append(f"📈 Delta trend: {delta_trend}")
        
        if absorption:
            parts.append("🧽 Absorption detected")
        if exhaustion:
            parts.append("😮‍💨 Exhaustion detected")
        if stop_hunting:
            parts.append("🎯 Stop hunting")
        if iceberg:
            parts.append("🧊 Iceberg orders")
        if spoofing:
            parts.append("🎭 Spoofing detected")
        
        return " | ".join(parts) if parts else "Normal order flow"


# ==============================================================================
# SMART MONEY CONCEPTS DETECTOR
# ==============================================================================

@dataclass
class SmartMoneyAnalysis:
    """Complete smart money analysis"""
    order_blocks: List[Dict]
    fair_value_gaps: List[Dict]
    liquidity_levels: List[Dict]
    breaker_blocks: List[Dict]
    mitigation_blocks: List[Dict]
    institutional_divergence: Dict
    smart_money_score: float
    description: str


class CompleteSmartMoneyDetector:
    """Complete smart money concepts detector"""
    
    def __init__(self):
        self.swing_points = []
        
    def analyze(self, df: pd.DataFrame, ob_data: Optional[Dict]) -> SmartMoneyAnalysis:
        """Complete smart money analysis"""
        
        try:
            self._detect_swing_points(df)
            
            order_blocks = self._detect_order_blocks(df)
            fair_value_gaps = self._detect_fvg(df)
            liquidity_levels = self._detect_liquidity_levels(df, ob_data)
            breaker_blocks = self._detect_breaker_blocks(df)
            mitigation_blocks = self._detect_mitigation_blocks(df)
            divergence = self._detect_institutional_divergence(df)
            
            score = self._calculate_smart_money_score(
                order_blocks, fair_value_gaps, liquidity_levels,
                breaker_blocks, mitigation_blocks, divergence
            )
            
            description = self._generate_description(
                order_blocks, fair_value_gaps, liquidity_levels,
                breaker_blocks, mitigation_blocks, divergence
            )
            
            return SmartMoneyAnalysis(
                order_blocks=order_blocks,
                fair_value_gaps=fair_value_gaps,
                liquidity_levels=liquidity_levels,
                breaker_blocks=breaker_blocks,
                mitigation_blocks=mitigation_blocks,
                institutional_divergence=divergence,
                smart_money_score=score,
                description=description
            )
        except Exception as e:
            logger.error(f"Smart money analysis error: {e}")
            return SmartMoneyAnalysis(
                order_blocks=[], fair_value_gaps=[], liquidity_levels=[],
                breaker_blocks=[], mitigation_blocks=[],
                institutional_divergence={'detected': False},
                smart_money_score=0, description="Error analyzing smart money"
            )
    
    def _detect_swing_points(self, df: pd.DataFrame):
        """Detect swing points"""
        try:
            highs = df['high'].values
            lows = df['low'].values
            self.swing_points = []
            
            for i in range(2, len(highs)-2):
                if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
                    highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                    self.swing_points.append({
                        'type': 'high',
                        'price': float(highs[i]),
                        'index': i,
                        'strength': 70 + (i % 20)
                    })
                
                if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
                    lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                    self.swing_points.append({
                        'type': 'low',
                        'price': float(lows[i]),
                        'index': i,
                        'strength': 70 + (i % 20)
                    })
        except Exception as e:
            logger.error(f"Error detecting swing points: {e}")
    
    def _detect_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Detect order blocks"""
        order_blocks = []
        
        try:
            for i in range(2, len(df)-2):
                current = df.iloc[i]
                next_candle = df.iloc[i+1]
                next_2_candle = df.iloc[i+2]
                
                current_close = safe_float(current['close'])
                current_open = safe_float(current['open'])
                next_close = safe_float(next_candle['close'])
                next_open = safe_float(next_candle['open'])
                next_2_close = safe_float(next_2_candle['close'])
                next_2_open = safe_float(next_2_candle['open'])
                next_low = safe_float(next_candle['low'])
                current_low = safe_float(current['low'])
                next_high = safe_float(next_candle['high'])
                current_high = safe_float(current['high'])
                
                # Bullish order block
                if (current_close < current_open and
                    next_close > next_open and
                    next_2_close > next_2_open and
                    next_low < current_low):
                    order_blocks.append({
                        'type': 'bullish',
                        'price': current_low,
                        'high': current_high,
                        'low': current_low,
                        'strength': 80,
                        'description': 'Bullish order block'
                    })
                
                # Bearish order block
                if (current_close > current_open and
                    next_close < next_open and
                    next_2_close < next_2_open and
                    next_high > current_high):
                    order_blocks.append({
                        'type': 'bearish',
                        'price': current_high,
                        'high': current_high,
                        'low': current_low,
                        'strength': 80,
                        'description': 'Bearish order block'
                    })
        except Exception as e:
            logger.error(f"Error detecting order blocks: {e}")
        
        return order_blocks
    
    def _detect_fvg(self, df: pd.DataFrame) -> List[Dict]:
        """Detect Fair Value Gaps"""
        fvg_list = []
        
        try:
            for i in range(1, len(df)-1):
                prev = df.iloc[i-1]
                curr = df.iloc[i]
                
                prev_high = safe_float(prev['high'])
                prev_low = safe_float(prev['low'])
                curr_high = safe_float(curr['high'])
                curr_low = safe_float(curr['low'])
                
                # Bullish FVG
                if curr_low > prev_high:
                    fvg_list.append({
                        'type': 'bullish',
                        'top': curr_low,
                        'bottom': prev_high,
                        'filled': False,
                        'strength': 75,
                        'description': 'Bullish Fair Value Gap'
                    })
                
                # Bearish FVG
                if curr_high < prev_low:
                    fvg_list.append({
                        'type': 'bearish',
                        'top': prev_low,
                        'bottom': curr_high,
                        'filled': False,
                        'strength': 75,
                        'description': 'Bearish Fair Value Gap'
                    })
            
            # Check if gaps are filled
            if len(df) > 0:
                current_price = safe_float(df['close'].iloc[-1])
                for fvg in fvg_list:
                    if fvg['type'] == 'bullish':
                        if current_price <= fvg['bottom']:
                            fvg['filled'] = True
                    else:
                        if current_price >= fvg['top']:
                            fvg['filled'] = True
        except Exception as e:
            logger.error(f"Error detecting FVGs: {e}")
        
        return fvg_list
    
    def _detect_liquidity_levels(self, df: pd.DataFrame, ob_data: Optional[Dict]) -> List[Dict]:
        """Detect liquidity levels"""
        liquidity_levels = []
        
        try:
            if len(df) > 20:
                recent_high = float(df['high'].iloc[-20:].max())
                recent_low = float(df['low'].iloc[-20:].min())
                
                liquidity_levels.append({
                    'type': 'sell_liquidity',
                    'price': recent_high,
                    'description': 'Sell liquidity above recent high',
                    'strength': 70
                })
                
                liquidity_levels.append({
                    'type': 'buy_liquidity',
                    'price': recent_low,
                    'description': 'Buy liquidity below recent low',
                    'strength': 70
                })
        except Exception as e:
            logger.error(f"Error detecting liquidity levels: {e}")
        
        return liquidity_levels
    
    def _detect_breaker_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Detect breaker blocks"""
        breaker_blocks = []
        
        try:
            for i in range(2, len(df)-1):
                prev = df.iloc[i-1]
                curr = df.iloc[i]
                
                prev_low = safe_float(prev['low'])
                curr_low = safe_float(curr['low'])
                curr_close = safe_float(curr['close'])
                curr_open = safe_float(curr['open'])
                prev_high = safe_float(prev['high'])
                curr_high = safe_float(curr['high'])
                
                # Bullish breaker
                if (curr_low < prev_low and
                    curr_close > curr_open and
                    curr_close > prev_low):
                    breaker_blocks.append({
                        'type': 'bullish',
                        'price': curr_low,
                        'strength': 75,
                        'description': 'Bullish breaker - false breakdown'
                    })
                
                # Bearish breaker
                if (curr_high > prev_high and
                    curr_close < curr_open and
                    curr_close < prev_high):
                    breaker_blocks.append({
                        'type': 'bearish',
                        'price': curr_high,
                        'strength': 75,
                        'description': 'Bearish breaker - false breakout'
                    })
        except Exception as e:
            logger.error(f"Error detecting breaker blocks: {e}")
        
        return breaker_blocks
    
    def _detect_mitigation_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Detect mitigation blocks"""
        mitigation_blocks = []
        
        if len(df) < 20 or len(self.swing_points) < 10:
            return mitigation_blocks
        
        try:
            current_price = safe_float(df['close'].iloc[-1])
            
            for point in self.swing_points[-10:]:
                distance = abs(current_price - point['price']) / point['price'] * 100
                
                if distance < 1.0:
                    mitigation_blocks.append({
                        'type': 'mitigation',
                        'price': point['price'],
                        'original_type': point['type'],
                        'distance': distance,
                        'strength': 70 - distance * 10,
                        'description': f'Price mitigating {point["type"]}'
                    })
        except Exception as e:
            logger.error(f"Error detecting mitigation blocks: {e}")
        
        return mitigation_blocks
    
    def _detect_institutional_divergence(self, df: pd.DataFrame) -> Dict:
        """Detect institutional divergence"""
        if len(df) < 20:
            return {'detected': False, 'type': 'none', 'strength': 0}
        
        try:
            prices = [float(p) for p in df['close'].values[-20:]]
            volumes = [float(v) for v in df['volume'].values[-20:]]
            
            if not prices or not volumes:
                return {'detected': False, 'type': 'none', 'strength': 0}
            
            price_trend = 'up' if prices[-1] > prices[0] else 'down'
            volume_trend = 'up' if volumes[-1] > volumes[0] else 'down'
            
            if price_trend == 'up' and volume_trend == 'down':
                return {
                    'detected': True,
                    'type': 'hidden_bullish',
                    'strength': 80,
                    'description': 'Hidden bullish divergence'
                }
            
            if price_trend == 'down' and volume_trend == 'up':
                return {
                    'detected': True,
                    'type': 'hidden_bearish',
                    'strength': 80,
                    'description': 'Hidden bearish divergence'
                }
            
            if len(prices) >= 5:
                if prices[-1] < prices[-5] and volumes[-1] > volumes[-5]:
                    return {
                        'detected': True,
                        'type': 'regular_bullish',
                        'strength': 85,
                        'description': 'Regular bullish divergence'
                    }
                
                if prices[-1] > prices[-5] and volumes[-1] < volumes[-5]:
                    return {
                        'detected': True,
                        'type': 'regular_bearish',
                        'strength': 85,
                        'description': 'Regular bearish divergence'
                    }
        except Exception as e:
            logger.error(f"Error detecting institutional divergence: {e}")
        
        return {'detected': False, 'type': 'none', 'strength': 0}
    
    def _calculate_smart_money_score(self, order_blocks, fvg, liquidity,
                                      breaker, mitigation, divergence) -> float:
        """Calculate smart money score"""
        score = 50.0
        
        try:
            score += len(order_blocks) * 5
            unfilled_fvg = len([f for f in fvg if not f.get('filled', True)])
            score += unfilled_fvg * 3
            score += len(liquidity) * 2
            score += len(breaker) * 4
            score += len(mitigation) * 3
            
            if divergence.get('detected', False):
                score += divergence.get('strength', 0) * 0.5
        except Exception:
            pass
        
        return min(100, max(0, score))
    
    def _generate_description(self, order_blocks, fvg, liquidity,
                               breaker, mitigation, divergence) -> str:
        """Generate description"""
        parts = []
        
        if order_blocks:
            parts.append(f"📦 {len(order_blocks)} Order Blocks")
        if fvg:
            unfilled = len([f for f in fvg if not f.get('filled', True)])
            parts.append(f"🕳️ {unfilled} Unfilled FVGs")
        if liquidity:
            parts.append(f"💧 {len(liquidity)} Liquidity Levels")
        if breaker:
            parts.append(f"🔨 {len(breaker)} Breaker Blocks")
        if mitigation:
            parts.append(f"✅ {len(mitigation)} Mitigations")
        if divergence.get('detected', False):
            parts.append(f"📊 {divergence['type']} Divergence")
        
        return " | ".join(parts) if parts else "No smart money concepts detected"
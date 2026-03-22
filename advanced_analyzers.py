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
# ADVANCED CANDLE PATTERN RECOGNITION
# ==============================================================================

@dataclass
class CandlePattern:
    """Candle pattern data"""
    name: str
    type: str  # 'bullish', 'bearish', 'reversal_bullish', 'reversal_bearish', 'continuation'
    strength: float  # 0-100
    description: str
    confirmation_needed: bool = True
    reliability: float = 70.0  # 0-100


class AdvancedCandlePatternRecognizer:
    """Advanced candle pattern recognition for pro traders"""
    
    def __init__(self):
        self.patterns_detected = []
        
    def analyze_candle(self, candle: pd.Series, prev_candle: Optional[pd.Series] = None,
                       prev_2_candle: Optional[pd.Series] = None,
                       prev_3_candle: Optional[pd.Series] = None) -> List[CandlePattern]:
        """Analyze single candle for patterns"""
        patterns = []
        
        # Get candle properties
        open_price = candle['open']
        high = candle['high']
        low = candle['low']
        close = candle['close']
        volume = candle['volume']
        
        body = abs(close - open_price)
        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low
        total_range = high - low
        
        if total_range == 0:
            return patterns
        
        body_percent = (body / total_range) * 100
        upper_wick_percent = (upper_wick / total_range) * 100
        lower_wick_percent = (lower_wick / total_range) * 100
        
        is_bullish = close > open_price
        is_bearish = close < open_price
        
        # ========== SINGLE CANDLE PATTERNS ==========
        
        # 1. Marubozu (Full body, no wicks)
        if upper_wick_percent < 5 and lower_wick_percent < 5 and body_percent > 90:
            if is_bullish:
                patterns.append(CandlePattern(
                    name="BULLISH MARUBOZU",
                    type="bullish",
                    strength=90,
                    description="Strong buying pressure throughout the session",
                    reliability=85
                ))
            else:
                patterns.append(CandlePattern(
                    name="BEARISH MARUBOZU",
                    type="bearish",
                    strength=90,
                    description="Strong selling pressure throughout the session",
                    reliability=85
                ))
        
        # 2. Doji (Very small body)
        elif body_percent < 10:
            if upper_wick_percent > 40 and lower_wick_percent < 10:
                patterns.append(CandlePattern(
                    name="DRAGONFLY DOJI",
                    type="reversal_bullish",
                    strength=75,
                    description="Long lower wick, indicates potential bullish reversal",
                    reliability=70
                ))
            elif lower_wick_percent > 40 and upper_wick_percent < 10:
                patterns.append(CandlePattern(
                    name="GRAVESTONE DOJI",
                    type="reversal_bearish",
                    strength=75,
                    description="Long upper wick, indicates potential bearish reversal",
                    reliability=70
                ))
            elif upper_wick_percent > 30 and lower_wick_percent > 30:
                patterns.append(CandlePattern(
                    name="LONG-LEGGED DOJI",
                    type="indecision",
                    strength=80,
                    description="High volatility, market indecision",
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
        
        # 3. Hammer / Hanging Man (Small body, long lower wick)
        elif lower_wick_percent > 60 and body_percent < 30 and upper_wick_percent < 10:
            if is_bullish:
                patterns.append(CandlePattern(
                    name="HAMMER",
                    type="reversal_bullish",
                    strength=85,
                    description="Bullish reversal signal after downtrend",
                    reliability=80
                ))
            else:
                patterns.append(CandlePattern(
                    name="HANGING MAN",
                    type="reversal_bearish",
                    strength=85,
                    description="Bearish reversal signal after uptrend",
                    reliability=80
                ))
        
        # 4. Shooting Star / Inverted Hammer (Small body, long upper wick)
        elif upper_wick_percent > 60 and body_percent < 30 and lower_wick_percent < 10:
            if is_bullish:
                patterns.append(CandlePattern(
                    name="INVERTED HAMMER",
                    type="reversal_bullish",
                    strength=80,
                    description="Potential bullish reversal after downtrend",
                    reliability=75
                ))
            else:
                patterns.append(CandlePattern(
                    name="SHOOTING STAR",
                    type="reversal_bearish",
                    strength=85,
                    description="Bearish reversal signal after uptrend",
                    reliability=80
                ))
        
        # 5. Spinning Top (Small body, both wicks present)
        elif 30 < body_percent < 50 and upper_wick_percent > 20 and lower_wick_percent > 20:
            patterns.append(CandlePattern(
                name="SPINNING TOP",
                type="indecision",
                strength=50,
                description="Market uncertainty, potential reversal if extreme",
                reliability=60
            ))
        
        # ========== TWO CANDLE PATTERNS ==========
        
        if prev_candle is not None:
            prev_open = prev_candle['open']
            prev_high = prev_candle['high']
            prev_low = prev_candle['low']
            prev_close = prev_candle['close']
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
                        description="Strong bullish reversal, buyers overwhelmed sellers",
                        reliability=85
                    ))
            
            elif is_bearish and prev_is_bullish:
                if close < prev_open and open > prev_close and body > prev_body * 1.2:
                    patterns.append(CandlePattern(
                        name="BEARISH ENGULFING",
                        type="reversal_bearish",
                        strength=90,
                        description="Strong bearish reversal, sellers overwhelmed buyers",
                        reliability=85
                    ))
            
            # 7. Harami Patterns (Mother and child)
            if is_bullish and prev_is_bearish:
                if open > prev_close and close < prev_open and body < prev_body * 0.6:
                    patterns.append(CandlePattern(
                        name="BULLISH HARAMI",
                        type="reversal_bullish",
                        strength=75,
                        description="Potential bullish reversal, decreasing momentum",
                        reliability=70
                    ))
            
            elif is_bearish and prev_is_bullish:
                if open < prev_close and close > prev_open and body < prev_body * 0.6:
                    patterns.append(CandlePattern(
                        name="BEARISH HARAMI",
                        type="reversal_bearish",
                        strength=75,
                        description="Potential bearish reversal, decreasing momentum",
                        reliability=70
                    ))
            
            # 8. Piercing Line / Dark Cloud Cover
            if is_bullish and prev_is_bearish:
                if open < prev_low and close > (prev_open + prev_close) / 2 and close < prev_open:
                    patterns.append(CandlePattern(
                        name="PIERCING LINE",
                        type="reversal_bullish",
                        strength=85,
                        description="Bullish reversal, buyers pushed into previous body",
                        reliability=80
                    ))
            
            elif is_bearish and prev_is_bullish:
                if open > prev_high and close < (prev_open + prev_close) / 2 and close > prev_close:
                    patterns.append(CandlePattern(
                        name="DARK CLOUD COVER",
                        type="reversal_bearish",
                        strength=85,
                        description="Bearish reversal, sellers pushed into previous body",
                        reliability=80
                    ))
            
            # 9. Tweezer Tops / Bottoms
            if abs(high - prev_high) / prev_high < 0.001:  # Same high
                if is_bearish and prev_is_bullish:
                    patterns.append(CandlePattern(
                        name="TWEEZER TOP",
                        type="reversal_bearish",
                        strength=80,
                        description="Double top rejection, strong resistance",
                        reliability=75
                    ))
            
            if abs(low - prev_low) / prev_low < 0.001:  # Same low
                if is_bullish and prev_is_bearish:
                    patterns.append(CandlePattern(
                        name="TWEEZER BOTTOM",
                        type="reversal_bullish",
                        strength=80,
                        description="Double bottom rejection, strong support",
                        reliability=75
                    ))
        
        # ========== THREE CANDLE PATTERNS ==========
        
        if prev_candle is not None and prev_2_candle is not None:
            # 10. Morning Star / Evening Star
            if prev_2_candle is not None and prev_candle is not None:
                # Morning Star (Bullish reversal)
                if (prev_2_candle['close'] < prev_2_candle['open'] and  # Bearish
                    self._is_doji(prev_candle) and 
                    is_bullish and close > (prev_2_candle['open'] + prev_2_candle['close']) / 2):
                    patterns.append(CandlePattern(
                        name="MORNING STAR",
                        type="reversal_bullish",
                        strength=95,
                        description="Strong bullish reversal pattern",
                        reliability=90
                    ))
                
                # Evening Star (Bearish reversal)
                elif (prev_2_candle['close'] > prev_2_candle['open'] and  # Bullish
                      self._is_doji(prev_candle) and 
                      is_bearish and close < (prev_2_candle['open'] + prev_2_candle['close']) / 2):
                    patterns.append(CandlePattern(
                        name="EVENING STAR",
                        type="reversal_bearish",
                        strength=95,
                        description="Strong bearish reversal pattern",
                        reliability=90
                    ))
            
            # 11. Three White Soldiers / Three Black Crows
            if prev_2_candle is not None and prev_candle is not None:
                # Three White Soldiers
                if (is_bullish and prev_candle['close'] > prev_candle['open'] and 
                    prev_2_candle['close'] > prev_2_candle['open'] and
                    close > prev_candle['close'] and prev_candle['close'] > prev_2_candle['close'] and
                    open > prev_candle['open'] and prev_candle['open'] > prev_2_candle['open']):
                    patterns.append(CandlePattern(
                        name="THREE WHITE SOLDIERS",
                        type="continuation_bullish",
                        strength=90,
                        description="Strong uptrend continuation",
                        reliability=85
                    ))
                
                # Three Black Crows
                elif (is_bearish and prev_candle['close'] < prev_candle['open'] and 
                      prev_2_candle['close'] < prev_2_candle['open'] and
                      close < prev_candle['close'] and prev_candle['close'] < prev_2_candle['close'] and
                      open < prev_candle['open'] and prev_candle['open'] < prev_2_candle['open']):
                    patterns.append(CandlePattern(
                        name="THREE BLACK CROWS",
                        type="continuation_bearish",
                        strength=90,
                        description="Strong downtrend continuation",
                        reliability=85
                    ))
        
        # ========== FOUR+ CANDLE PATTERNS ==========
        
        if all([prev_candle is not None, prev_2_candle is not None, prev_3_candle is not None]):
            # 13. Bullish/Bearish Abandoned Baby
            if (prev_2_candle['high'] < prev_3_candle['low'] and  # Gap down
                self._is_doji(prev_candle) and 
                candle['low'] > prev_candle['high'] and  # Gap up
                is_bullish):
                patterns.append(CandlePattern(
                    name="BULLISH ABANDONED BABY",
                    type="reversal_bullish",
                    strength=95,
                    description="Major reversal pattern, island reversal",
                    reliability=90
                ))
            
            elif (prev_2_candle['low'] > prev_3_candle['high'] and  # Gap up
                  self._is_doji(prev_candle) and 
                  candle['high'] < prev_candle['low'] and  # Gap down
                  is_bearish):
                patterns.append(CandlePattern(
                    name="BEARISH ABANDONED BABY",
                    type="reversal_bearish",
                    strength=95,
                    description="Major reversal pattern, island reversal",
                    reliability=90
                ))
        
        return patterns
    
    def _is_doji(self, candle: pd.Series) -> bool:
        """Check if candle is a doji"""
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        if total_range == 0:
            return False
        return (body / total_range) < 0.1
    
    def analyze_multiple_timeframes(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict]]:
        """Analyze candle patterns across multiple timeframes"""
        results = {}
        
        for tf, df in dataframes.items():
            if df is None or len(df) < 5:
                continue
            
            tf_patterns = []
            
            for i in range(3, len(df)):
                candle = df.iloc[i]
                prev_candle = df.iloc[i-1] if i > 0 else None
                prev_2_candle = df.iloc[i-2] if i > 1 else None
                prev_3_candle = df.iloc[i-3] if i > 2 else None
                
                patterns = self.analyze_candle(candle, prev_candle, prev_2_candle, prev_3_candle)
                
                for pattern in patterns:
                    pattern_data = {
                        'pattern': pattern,
                        'timestamp': i,
                        'price': candle['close']
                    }
                    tf_patterns.append(pattern_data)
            
            results[tf] = tf_patterns
        
        return results


# ==============================================================================
# SUPPORT/RESISTANCE DETECTOR
# ==============================================================================

@dataclass
class SupportResistanceLevel:
    """Support/Resistance level data"""
    price: float
    type: str  # 'support', 'resistance'
    strength: float  # 0-100
    touches: int
    timeframe: str
    is_major: bool = False
    description: str = ""


class SupportResistanceDetector:
    """Advanced support and resistance detection"""
    
    def __init__(self):
        self.levels = []
        
    def detect_levels(self, df: pd.DataFrame, timeframe: str = '1h') -> List[SupportResistanceLevel]:
        """Detect support and resistance levels using multiple methods"""
        levels = []
        
        if df is None or len(df) < 50:
            return levels
        
        # Method 1: Swing Highs/Lows
        swing_levels = self._detect_swing_points(df)
        levels.extend(swing_levels)
        
        # Method 2: Volume Profile (High volume nodes)
        volume_levels = self._detect_volume_nodes(df)
        levels.extend(volume_levels)
        
        # Method 3: Fibonacci Retracement levels
        fib_levels = self._detect_fibonacci_levels(df)
        levels.extend(fib_levels)
        
        # Method 4: Moving Averages (dynamic levels)
        ma_levels = self._detect_ma_levels(df)
        levels.extend(ma_levels)
        
        # Method 5: Pivot Points
        pivot_levels = self._detect_pivot_points(df)
        levels.extend(pivot_levels)
        
        # Merge nearby levels and calculate strength
        levels = self._merge_levels(levels)
        
        # Mark major levels (strength > 70)
        for level in levels:
            if level.strength > 70:
                level.is_major = True
                level.description = f"Major {level.type} level"
        
        self.levels = levels
        return levels
    
    def _detect_swing_points(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect swing highs and lows"""
        levels = []
        
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        # Find swing highs (local maxima)
        for i in range(2, len(high)-2):
            if (high[i] > high[i-1] and high[i] > high[i-2] and
                high[i] > high[i+1] and high[i] > high[i+2]):
                
                # Count how many times price touched this level
                touches = 0
                for j in range(len(close)):
                    if abs(close[j] - high[i]) / high[i] < 0.01:
                        touches += 1
                
                strength = min(50 + touches * 5, 100)
                
                levels.append(SupportResistanceLevel(
                    price=high[i],
                    type='resistance',
                    strength=strength,
                    touches=touches,
                    timeframe='all',
                    description=f"Swing high with {touches} touches"
                ))
        
        # Find swing lows (local minima)
        for i in range(2, len(low)-2):
            if (low[i] < low[i-1] and low[i] < low[i-2] and
                low[i] < low[i+1] and low[i] < low[i+2]):
                
                touches = 0
                for j in range(len(close)):
                    if abs(close[j] - low[i]) / low[i] < 0.01:
                        touches += 1
                
                strength = min(50 + touches * 5, 100)
                
                levels.append(SupportResistanceLevel(
                    price=low[i],
                    type='support',
                    strength=strength,
                    touches=touches,
                    timeframe='all',
                    description=f"Swing low with {touches} touches"
                ))
        
        return levels
    
    def _detect_volume_nodes(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect high volume nodes"""
        levels = []
        
        if len(df) < 20:
            return levels
        
        # Create price bins
        price_min = df['low'].min()
        price_max = df['high'].max()
        price_range = price_max - price_min
        num_bins = 50
        bin_size = price_range / num_bins
        
        volume_by_price = defaultdict(float)
        
        for _, row in df.iterrows():
            for i in range(num_bins):
                bin_low = price_min + i * bin_size
                bin_high = bin_low + bin_size
                
                if (row['low'] <= bin_high and row['high'] >= bin_low):
                    # Candle overlaps with this bin
                    overlap = min(row['high'], bin_high) - max(row['low'], bin_low)
                    if overlap > 0:
                        volume_by_price[(bin_low + bin_high)/2] += row['volume'] * (overlap / (row['high'] - row['low']))
        
        # Find high volume nodes
        if volume_by_price:
            avg_volume = np.mean(list(volume_by_price.values()))
            std_volume = np.std(list(volume_by_price.values())) if len(volume_by_price) > 1 else avg_volume * 0.5
            
            for price, volume in volume_by_price.items():
                if volume > avg_volume + 1.5 * std_volume:  # High volume node
                    # Determine if support or resistance based on price action
                    recent_price = df['close'].iloc[-1]
                    
                    if recent_price > price:
                        level_type = 'support'
                        desc = "High volume support zone"
                    else:
                        level_type = 'resistance'
                        desc = "High volume resistance zone"
                    
                    strength = min(70 + (volume - avg_volume) / std_volume * 10, 100)
                    
                    levels.append(SupportResistanceLevel(
                        price=price,
                        type=level_type,
                        strength=strength,
                        touches=0,
                        timeframe='all',
                        description=desc
                    ))
        
        return levels
    
    def _detect_fibonacci_levels(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect Fibonacci retracement levels from recent swing"""
        levels = []
        
        if len(df) < 50:
            return levels
        
        # Find recent significant swing
        high_idx = df['high'].argmax()
        low_idx = df['low'].argmin()
        
        if high_idx > low_idx:  # Downtrend
            swing_high = df['high'].iloc[high_idx]
            swing_low = df['low'].iloc[low_idx]
            fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
            fib_names = ['23.6%', '38.2%', '50%', '61.8%', '78.6%']
            
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
            swing_low = df['low'].iloc[low_idx]
            swing_high = df['high'].iloc[high_idx]
            fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
            fib_names = ['23.6%', '38.2%', '50%', '61.8%', '78.6%']
            
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
        
        return levels
    
    def _detect_ma_levels(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect moving average levels (dynamic support/resistance)"""
        levels = []
        
        periods = [20, 50, 100, 200]
        
        for period in periods:
            if len(df) >= period:
                ma = df['close'].rolling(window=period).mean().iloc[-1]
                
                # Determine if MA acts as support or resistance
                current_price = df['close'].iloc[-1]
                
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
        
        return levels
    
    def _detect_pivot_points(self, df: pd.DataFrame) -> List[SupportResistanceLevel]:
        """Detect pivot points"""
        levels = []
        
        if len(df) < 20:
            return levels
        
        high = df['high'].iloc[-20:].max()
        low = df['low'].iloc[-20:].min()
        close = df['close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        
        # Standard pivot levels
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
                    
                    # Determine predominant type
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
        supports = [l for l in self.levels if l.type == 'support' or l.type.startswith('s')]
        resistances = [l for l in self.levels if l.type == 'resistance' or l.type.startswith('r') or l.type == 'pivot']
        
        # Filter to only those below (support) and above (resistance) current price
        supports_below = [s for s in supports if s.price < price]
        resistances_above = [r for r in resistances if r.price > price]
        
        # Sort by distance to current price
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
    poc_price: float  # Point of Control
    high_volume_nodes: List[float]
    low_volume_nodes: List[float]
    volume_profile: Dict[float, float]
    tpo_count: int
    initial_balance_high: float
    initial_balance_low: float
    developing_range: Tuple[float, float]
    profile_type: str  # 'normal', 'b', 'p', 'd' etc.


class MarketProfileAnalyzer:
    """Complete market profile analyzer for pro traders"""
    
    def __init__(self, num_bins: int = 24):
        self.num_bins = num_bins
        
    def analyze_profile(self, df: pd.DataFrame, period: str = 'day') -> Optional[MarketProfile]:
        """Analyze market profile from price/volume data"""
        
        if df is None or len(df) < 10:
            return None
        
        # Create price bins
        price_min = df['low'].min()
        price_max = df['high'].max()
        price_range = price_max - price_min
        bin_size = price_range / self.num_bins
        
        bins = {}
        tpo_count = {}
        
        # Initialize bins
        for i in range(self.num_bins):
            low = price_min + i * bin_size
            high = low + bin_size
            bins[(low, high)] = 0.0
            tpo_count[(low, high)] = 0
        
        # Accumulate volume and TPO
        for _, row in df.iterrows():
            for (low, high) in bins.keys():
                if row['low'] <= high and row['high'] >= low:
                    # Volume contribution based on overlap
                    overlap = min(row['high'], high) - max(row['low'], low)
                    if overlap > 0:
                        volume_contrib = row['volume'] * (overlap / (row['high'] - row['low']))
                        bins[(low, high)] += volume_contrib
                        tpo_count[(low, high)] += 1
        
        # Find Point of Control (highest volume bin)
        if not bins:
            return None
            
        poc_bin = max(bins.items(), key=lambda x: x[1])
        poc_price = (poc_bin[0][0] + poc_bin[0][1]) / 2
        
        # Calculate value area (70% of volume)
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
        
        # Calculate initial balance (first hour)
        if len(df) >= 2:
            first_candle = df.iloc[0]
            initial_balance_high = first_candle['high']
            initial_balance_low = first_candle['low']
        else:
            initial_balance_high = price_max
            initial_balance_low = price_min
        
        # Determine developing range
        developing_range = (price_min, price_max)
        
        # Determine profile type
        profile_type = self._determine_profile_type(bins, poc_price, value_area_low, value_area_high)
        
        # Create volume profile dict
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
            initial_balance_high=initial_balance_high,
            initial_balance_low=initial_balance_low,
            developing_range=developing_range,
            profile_type=profile_type
        )
    
    def _determine_profile_type(self, bins: Dict, poc: float, va_low: float, va_high: float) -> str:
        """Determine market profile type"""
        
        # Check if POC is near high (P profile)
        if poc > va_high * 0.9:
            return 'p'  # P-shape (buying tail)
        
        # Check if POC is near low (b profile)
        elif poc < va_low * 1.1:
            return 'b'  # b-shape (selling tail)
        
        # Check if profile is balanced
        elif (va_high - poc) / (poc - va_low) > 1.5:
            return 'd'  # d-shape (developed upside)
        
        elif (poc - va_low) / (va_high - poc) > 1.5:
            return 'p'  # p-shape (developed downside)
        
        else:
            return 'normal'  # Normal distribution
    
    def get_trading_opportunities(self, profile: MarketProfile, current_price: float) -> Dict[str, Any]:
        """Get trading opportunities based on market profile"""
        
        opportunities = {
            'buy_zones': [],
            'sell_zones': [],
            'neutral_zones': [],
            'breakout_levels': []
        }
        
        if not profile:
            return opportunities
        
        # Discount zone (below value area)
        if current_price < profile.value_area_low:
            opportunities['buy_zones'].append({
                'price': profile.value_area_low,
                'type': 'value_area_low',
                'confidence': 80,
                'reason': 'Price below value area - potential buying opportunity'
            })
        
        # Premium zone (above value area)
        if current_price > profile.value_area_high:
            opportunities['sell_zones'].append({
                'price': profile.value_area_high,
                'type': 'value_area_high',
                'confidence': 80,
                'reason': 'Price above value area - potential selling opportunity'
            })
        
        # Point of Control
        if abs(current_price - profile.poc_price) / profile.poc_price < 0.01:
            opportunities['neutral_zones'].append({
                'price': profile.poc_price,
                'type': 'poc',
                'confidence': 70,
                'reason': 'At Point of Control - equilibrium'
            })
        
        # High volume nodes (support/resistance)
        for node in profile.high_volume_nodes:
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
    """Complete order flow analyzer for pro traders"""
    
    def __init__(self, client):
        self.client = client
        from collections import deque
        self.delta_history = deque(maxlen=100)
        self.large_trade_threshold = 50000  # $50k
        
    def analyze_order_flow(self, symbol: str, ob_data: Optional[Dict], trades: List[Dict]) -> OrderFlowAnalysis:
        """Complete order flow analysis"""
        
        # 1. Bid-Ask Imbalance
        imbalance = self._calculate_imbalance(ob_data)
        
        # 2. Cumulative Delta
        delta, delta_trend = self._calculate_delta(trades)
        
        # 3. Aggressive Buying/Selling
        aggressive_buying, aggressive_selling = self._detect_aggressive_trades(trades)
        
        # 4. Large Trades Detection
        large_trades = self._detect_large_trades(trades)
        
        # 5. Absorption Detection
        absorption = self._detect_absorption(ob_data, trades)
        
        # 6. Exhaustion Detection
        exhaustion = self._detect_exhaustion(trades, delta)
        
        # 7. Stop Hunting Detection
        stop_hunting = self._detect_stop_hunting(trades, ob_data)
        
        # 8. Iceberg Detection
        iceberg = self._detect_iceberg(ob_data)
        
        # 9. Spoofing Detection
        spoofing = self._detect_spoofing(ob_data)
        
        # Calculate overall order flow strength
        strength = self._calculate_flow_strength(
            imbalance, delta, aggressive_buying, aggressive_selling,
            large_trades, absorption, exhaustion
        )
        
        # Generate description
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
    
    def _calculate_imbalance(self, ob_data: Optional[Dict]) -> float:
        """Calculate bid-ask imbalance"""
        if not ob_data or 'bids' not in ob_data or 'asks' not in ob_data:
            return 0.0
        
        bids = ob_data.get('bids', [])[:10]
        asks = ob_data.get('asks', [])[:10]
        
        bid_volume = 0.0
        for b in bids:
            try:
                bid_volume += float(b[1]) * float(b[0])
            except:
                pass
        
        ask_volume = 0.0
        for a in asks:
            try:
                ask_volume += float(a[1]) * float(a[0])
            except:
                pass
        
        total = bid_volume + ask_volume
        if total > 0:
            return ((bid_volume - ask_volume) / total) * 100
        return 0.0
    
    def _calculate_delta(self, trades: List[Dict]) -> Tuple[float, str]:
        """Calculate cumulative delta and trend"""
        if not trades:
            return 0.0, "NEUTRAL"
        
        delta = 0.0
        for trade in trades:
            try:
                price = float(trade['price'])
                qty = float(trade['qty'])
                is_buyer_maker = trade.get('isBuyerMaker', False)
                
                if is_buyer_maker:
                    delta -= qty * price  # Seller initiated
                else:
                    delta += qty * price  # Buyer initiated
            except:
                pass
        
        # Store in history for trend analysis
        self.delta_history.append(delta)
        
        # Determine trend
        if len(self.delta_history) >= 10:
            recent_deltas = list(self.delta_history)[-10:]
            if all(d > 0 for d in recent_deltas[-3:]):
                trend = "STRONG_BULLISH"
            elif all(d < 0 for d in recent_deltas[-3:]):
                trend = "STRONG_BEARISH"
            elif sum(recent_deltas[-5:]) > 0:
                trend = "BULLISH"
            elif sum(recent_deltas[-5:]) < 0:
                trend = "BEARISH"
            else:
                trend = "NEUTRAL"
        else:
            trend = "NEUTRAL"
        
        return delta, trend
    
    def _detect_aggressive_trades(self, trades: List[Dict]) -> Tuple[bool, bool]:
        """Detect aggressive buying/selling"""
        if not trades or len(trades) < 10:
            return False, False
        
        aggressive_buying = False
        aggressive_selling = False
        
        # Check last 10 trades
        last_trades = trades[-10:]
        buys = 0
        sells = 0
        
        for trade in last_trades:
            try:
                is_buyer_maker = trade.get('isBuyerMaker', False)
                if not is_buyer_maker:
                    buys += 1
                else:
                    sells += 1
            except:
                pass
        
        if buys > 7:  # 70%+ aggressive buying
            aggressive_buying = True
        if sells > 7:  # 70%+ aggressive selling
            aggressive_selling = True
        
        return aggressive_buying, aggressive_selling
    
    def _detect_large_trades(self, trades: List[Dict]) -> List[Dict]:
        """Detect large trades"""
        large_trades = []
        
        for trade in trades:
            try:
                price = float(trade['price'])
                qty = float(trade['qty'])
                value = price * qty
                
                if value >= self.large_trade_threshold:
                    large_trades.append({
                        'price': price,
                        'qty': qty,
                        'value': value,
                        'side': 'BUY' if not trade.get('isBuyerMaker', False) else 'SELL',
                        'time': trade.get('time', 0)
                    })
            except:
                pass
        
        return large_trades
    
    def _detect_absorption(self, ob_data: Optional[Dict], trades: List[Dict]) -> bool:
        """Detect absorption (large bids/asks being eaten)"""
        if not ob_data or 'bids' not in ob_data or 'asks' not in ob_data:
            return False
        
        bids = ob_data.get('bids', [])
        asks = ob_data.get('asks', [])
        
        if len(bids) < 5 or len(asks) < 5:
            return False
        
        # Check for large bid wall
        try:
            bid_wall_size = sum(float(b[1]) for b in bids[:3]) * float(bids[0][0])
            ask_wall_size = sum(float(a[1]) for a in asks[:3]) * float(asks[0][0])
            
            # If one side is much larger but price isn't moving
            if bid_wall_size > ask_wall_size * 3 and len(trades) > 10:
                # Check if trades are eating into the bid wall
                last_trades = trades[-10:]
                sell_count = sum(1 for t in last_trades if t.get('isBuyerMaker', False))
                if sell_count > 7:  # Heavy selling into bid wall
                    return True
            
            if ask_wall_size > bid_wall_size * 3 and len(trades) > 10:
                last_trades = trades[-10:]
                buy_count = sum(1 for t in last_trades if not t.get('isBuyerMaker', False))
                if buy_count > 7:  # Heavy buying into ask wall
                    return True
        except:
            pass
        
        return False
    
    def _detect_exhaustion(self, trades: List[Dict], delta: float) -> bool:
        """Detect exhaustion (decreasing volume with price extension)"""
        if len(trades) < 20:
            return False
        
        # Compare recent volume to average
        recent_volume = sum(float(t.get('qty', 0)) for t in trades[-10:])
        avg_volume = sum(float(t.get('qty', 0)) for t in trades[-20:-10]) / 10 if len(trades) > 20 else recent_volume
        
        if avg_volume == 0:
            return False
        
        volume_ratio = recent_volume / avg_volume
        
        # Exhaustion when volume decreases but delta is large
        if volume_ratio < 0.5 and abs(delta) > 1000000:
            return True
        
        return False
    
    def _detect_stop_hunting(self, trades: List[Dict], ob_data: Optional[Dict]) -> bool:
        """Detect stop hunting (price spikes with low volume)"""
        if len(trades) < 10:
            return False
        
        # Check for rapid price movement with low volume
        prices = []
        for t in trades[-10:]:
            try:
                if 'price' in t:
                    prices.append(float(t['price']))
            except:
                pass
        
        if len(prices) < 5:
            return False
        
        price_change = abs(prices[-1] - prices[0]) / prices[0] * 100
        volume = sum(float(t.get('qty', 0)) for t in trades[-10:])
        
        if price_change > 1.0 and volume < 10000:  # 1% move with low volume
            return True
        
        return False
    
    def _detect_iceberg(self, ob_data: Optional[Dict]) -> bool:
        """Detect iceberg orders (replenishing orders)"""
        if not ob_data or 'bids' not in ob_data or 'asks' not in ob_data:
            return False
        
        # Check for same price level appearing multiple times
        bid_prices = [b[0] for b in ob_data.get('bids', [])]
        ask_prices = [a[0] for a in ob_data.get('asks', [])]
        
        # Look for duplicate prices (iceberg replenishment)
        if len(set(bid_prices)) < len(bid_prices) * 0.8:
            return True
        if len(set(ask_prices)) < len(ask_prices) * 0.8:
            return True
        
        return False
    
    def _detect_spoofing(self, ob_data: Optional[Dict]) -> bool:
        """Detect spoofing (large orders that disappear)"""
        if not ob_data or 'bids' not in ob_data or 'asks' not in ob_data:
            return False
        
        try:
            best_bid = float(ob_data['bids'][0][0]) if ob_data['bids'] else 0
            best_ask = float(ob_data['asks'][0][0]) if ob_data['asks'] else 0
            
            # Check for large orders at distant prices
            for bid in ob_data['bids'][5:]:  # Look beyond top 5
                bid_price = float(bid[0])
                bid_size = float(bid[1])
                if bid_price < best_bid * 0.99 and bid_size * bid_price > 1000000:
                    return True
            
            for ask in ob_data['asks'][5:]:
                ask_price = float(ask[0])
                ask_size = float(ask[1])
                if ask_price > best_ask * 1.01 and ask_size * ask_price > 1000000:
                    return True
        except:
            pass
        
        return False
    
    def _calculate_flow_strength(self, imbalance: float, delta: float,
                                  aggressive_buying: bool, aggressive_selling: bool,
                                  large_trades: List, absorption: bool,
                                  exhaustion: bool) -> float:
        """Calculate overall order flow strength (0-100)"""
        strength = 50.0  # Baseline
        
        # Imbalance contribution
        strength += abs(imbalance) * 0.5
        
        # Delta contribution
        delta_norm = min(abs(delta) / 1000000, 30)  # Cap at 30
        strength += delta_norm
        
        # Aggressive trading
        if aggressive_buying or aggressive_selling:
            strength += 10
        
        # Large trades
        strength += len(large_trades) * 2
        
        # Absorption/Exhaustion
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
        """Generate human-readable description"""
        parts = []
        
        if aggressive_buying:
            parts.append("🔥 Aggressive buying detected")
        if aggressive_selling:
            parts.append("🔥 Aggressive selling detected")
        
        if imbalance > 20:
            parts.append(f"📊 Strong buy imbalance ({imbalance:.1f}%)")
        elif imbalance < -20:
            parts.append(f"📊 Strong sell imbalance ({abs(imbalance):.1f}%)")
        
        if delta_trend != "NEUTRAL":
            parts.append(f"📈 Delta trend: {delta_trend}")
        
        if absorption:
            parts.append("🧽 Absorption detected - large orders being eaten")
        if exhaustion:
            parts.append("😮‍💨 Exhaustion detected - volume decreasing")
        if stop_hunting:
            parts.append("🎯 Stop hunting detected")
        if iceberg:
            parts.append("🧊 Iceberg orders detected")
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
    """Complete smart money concepts detector for pro traders"""
    
    def __init__(self):
        self.swing_points = []
        
    def analyze(self, df: pd.DataFrame, ob_data: Optional[Dict]) -> SmartMoneyAnalysis:
        """Complete smart money analysis"""
        
        # Detect swing points first
        self._detect_swing_points(df)
        
        # 1. Order Blocks
        order_blocks = self._detect_order_blocks(df)
        
        # 2. Fair Value Gaps
        fair_value_gaps = self._detect_fvg(df)
        
        # 3. Liquidity Levels
        liquidity_levels = self._detect_liquidity_levels(df, ob_data)
        
        # 4. Breaker Blocks
        breaker_blocks = self._detect_breaker_blocks(df)
        
        # 5. Mitigation Blocks
        mitigation_blocks = self._detect_mitigation_blocks(df)
        
        # 6. Institutional Divergence
        divergence = self._detect_institutional_divergence(df)
        
        # Calculate smart money score
        score = self._calculate_smart_money_score(
            order_blocks, fair_value_gaps, liquidity_levels,
            breaker_blocks, mitigation_blocks, divergence
        )
        
        # Generate description
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
    
    def _detect_swing_points(self, df: pd.DataFrame):
        """Detect swing highs and lows"""
        highs = df['high'].values
        lows = df['low'].values
        
        for i in range(2, len(highs)-2):
            # Swing high
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                self.swing_points.append({
                    'type': 'high',
                    'price': highs[i],
                    'index': i,
                    'strength': 70 + (i % 20)  # Simple strength calculation
                })
            
            # Swing low
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                self.swing_points.append({
                    'type': 'low',
                    'price': lows[i],
                    'index': i,
                    'strength': 70 + (i % 20)
                })
    
    def _detect_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Detect order blocks (last candle before strong move)"""
        order_blocks = []
        
        for i in range(2, len(df)-2):
            current = df.iloc[i]
            next_candle = df.iloc[i+1]
            next_2_candle = df.iloc[i+2]
            
            # Bullish order block
            if (current['close'] < current['open'] and  # Bearish candle
                next_candle['close'] > next_candle['open'] and  # Bullish candle
                next_2_candle['close'] > next_2_candle['open'] and  # Another bullish
                next_candle['low'] < current['low']):  # Broke below
                
                order_blocks.append({
                    'type': 'bullish',
                    'price': current['low'],
                    'high': current['high'],
                    'low': current['low'],
                    'time': i,
                    'strength': 80,
                    'description': 'Bullish order block - last sell before rally'
                })
            
            # Bearish order block
            if (current['close'] > current['open'] and  # Bullish candle
                next_candle['close'] < next_candle['open'] and  # Bearish candle
                next_2_candle['close'] < next_2_candle['open'] and  # Another bearish
                next_candle['high'] > current['high']):  # Broke above
                
                order_blocks.append({
                    'type': 'bearish',
                    'price': current['high'],
                    'high': current['high'],
                    'low': current['low'],
                    'time': i,
                    'strength': 80,
                    'description': 'Bearish order block - last buy before sell-off'
                })
        
        return order_blocks
    
    def _detect_fvg(self, df: pd.DataFrame) -> List[Dict]:
        """Detect Fair Value Gaps (imbalances)"""
        fvg_list = []
        
        for i in range(1, len(df)-1):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            next_candle = df.iloc[i+1]
            
            # Bullish FVG
            if curr['low'] > prev['high']:  # Gap up
                fvg_list.append({
                    'type': 'bullish',
                    'top': curr['low'],
                    'bottom': prev['high'],
                    'time': i,
                    'filled': False,
                    'strength': 75,
                    'description': 'Bullish Fair Value Gap'
                })
            
            # Bearish FVG
            if curr['high'] < prev['low']:  # Gap down
                fvg_list.append({
                    'type': 'bearish',
                    'top': prev['low'],
                    'bottom': curr['high'],
                    'time': i,
                    'filled': False,
                    'strength': 75,
                    'description': 'Bearish Fair Value Gap'
                })
        
        # Check if gaps are filled
        if len(df) > 0:
            current_price = df['close'].iloc[-1]
            for fvg in fvg_list:
                if fvg['type'] == 'bullish':
                    if current_price <= fvg['bottom']:
                        fvg['filled'] = True
                else:
                    if current_price >= fvg['top']:
                        fvg['filled'] = True
        
        return fvg_list
    
    def _detect_liquidity_levels(self, df: pd.DataFrame, ob_data: Optional[Dict]) -> List[Dict]:
        """Detect liquidity levels (above highs/below lows)"""
        liquidity_levels = []
        
        if len(df) > 20:
            # Recent highs/lows as liquidity
            recent_high = df['high'].iloc[-20:].max()
            recent_low = df['low'].iloc[-20:].min()
            
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
        
        # Order book liquidity
        if ob_data and 'bids' in ob_data and 'asks' in ob_data:
            try:
                # Large bid clusters
                bid_prices = [float(b[0]) for b in ob_data['bids'][:10]]
                bid_sizes = [float(b[1]) for b in ob_data['bids'][:10]]
                
                for i, (price, size) in enumerate(zip(bid_prices, bid_sizes)):
                    if size * price > 500000:  # Large bid
                        liquidity_levels.append({
                            'type': 'bid_liquidity',
                            'price': price,
                            'size': size,
                            'description': f'Large bid liquidity at {price}',
                            'strength': 65 + i
                        })
                
                # Large ask clusters
                ask_prices = [float(a[0]) for a in ob_data['asks'][:10]]
                ask_sizes = [float(a[1]) for a in ob_data['asks'][:10]]
                
                for i, (price, size) in enumerate(zip(ask_prices, ask_sizes)):
                    if size * price > 500000:  # Large ask
                        liquidity_levels.append({
                            'type': 'ask_liquidity',
                            'price': price,
                            'size': size,
                            'description': f'Large ask liquidity at {price}',
                            'strength': 65 + i
                        })
            except:
                pass
        
        return liquidity_levels
    
    def _detect_breaker_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Detect breaker blocks (failed breaks)"""
        breaker_blocks = []
        
        for i in range(2, len(df)-1):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            # Bullish breaker (broke below then reversed)
            if (curr['low'] < prev['low'] and  # Broke below previous low
                curr['close'] > curr['open'] and  # Closed bullish
                curr['close'] > prev['low']):  # Closed above breakdown
                
                breaker_blocks.append({
                    'type': 'bullish',
                    'price': curr['low'],
                    'high': curr['high'],
                    'low': curr['low'],
                    'time': i,
                    'strength': 75,
                    'description': 'Bullish breaker - false breakdown'
                })
            
            # Bearish breaker (broke above then reversed)
            if (curr['high'] > prev['high'] and  # Broke above previous high
                curr['close'] < curr['open'] and  # Closed bearish
                curr['close'] < prev['high']):  # Closed below breakout
                
                breaker_blocks.append({
                    'type': 'bearish',
                    'price': curr['high'],
                    'high': curr['high'],
                    'low': curr['low'],
                    'time': i,
                    'strength': 75,
                    'description': 'Bearish breaker - false breakout'
                })
        
        return breaker_blocks
    
    def _detect_mitigation_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Detect mitigation blocks (price returning to previous levels)"""
        mitigation_blocks = []
        
        if len(df) < 20 or len(self.swing_points) < 10:
            return mitigation_blocks
        
        current_price = df['close'].iloc[-1]
        
        # Check if price is returning to previous swing points
        for point in self.swing_points[-10:]:  # Last 10 swing points
            distance = abs(current_price - point['price']) / point['price'] * 100
            
            if distance < 1.0:  # Within 1%
                mitigation_blocks.append({
                    'type': 'mitigation',
                    'price': point['price'],
                    'original_type': point['type'],
                    'distance': distance,
                    'strength': 70 - distance * 10,
                    'description': f'Price mitigating {point["type"]} at {point["price"]:.4f}'
                })
        
        return mitigation_blocks
    
    def _detect_institutional_divergence(self, df: pd.DataFrame) -> Dict:
        """Detect institutional divergence (price vs volume)"""
        if len(df) < 20:
            return {'detected': False, 'type': 'none', 'strength': 0}
        
        # Compare price action with volume
        prices = df['close'].values[-20:]
        volumes = df['volume'].values[-20:]
        
        price_trend = 'up' if prices[-1] > prices[0] else 'down'
        volume_trend = 'up' if volumes[-1] > volumes[0] else 'down'
        
        # Hidden bullish divergence (price making higher lows, volume making lower lows)
        if price_trend == 'up' and volume_trend == 'down':
            return {
                'detected': True,
                'type': 'hidden_bullish',
                'strength': 80,
                'description': 'Hidden bullish divergence - price up on decreasing volume'
            }
        
        # Hidden bearish divergence (price making lower highs, volume making higher highs)
        if price_trend == 'down' and volume_trend == 'up':
            return {
                'detected': True,
                'type': 'hidden_bearish',
                'strength': 80,
                'description': 'Hidden bearish divergence - price down on increasing volume'
            }
        
        # Regular divergence checks
        if len(prices) >= 5:
            # Bullish divergence (lower low in price, higher low in volume)
            if prices[-1] < prices[-5] and volumes[-1] > volumes[-5]:
                return {
                    'detected': True,
                    'type': 'regular_bullish',
                    'strength': 85,
                    'description': 'Regular bullish divergence - lower price, higher volume'
                }
            
            # Bearish divergence (higher high in price, lower high in volume)
            if prices[-1] > prices[-5] and volumes[-1] < volumes[-5]:
                return {
                    'detected': True,
                    'type': 'regular_bearish',
                    'strength': 85,
                    'description': 'Regular bearish divergence - higher price, lower volume'
                }
        
        return {'detected': False, 'type': 'none', 'strength': 0}
    
    def _calculate_smart_money_score(self, order_blocks, fvg, liquidity,
                                      breaker, mitigation, divergence) -> float:
        """Calculate overall smart money score"""
        score = 50.0  # Baseline
        
        score += len(order_blocks) * 5
        unfilled_fvg = len([f for f in fvg if not f.get('filled', True)])
        score += unfilled_fvg * 3
        score += len(liquidity) * 2
        score += len(breaker) * 4
        score += len(mitigation) * 3
        
        if divergence.get('detected', False):
            score += divergence.get('strength', 0) * 0.5
        
        return min(100, score)
    
    def _generate_description(self, order_blocks, fvg, liquidity,
                               breaker, mitigation, divergence) -> str:
        """Generate human-readable description"""
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ULTIMATE HYBRID CRYPTO TRADING BOT - MAIN BOT PART 2
Order Type Analyzer, Entry Optimizer, Tier Generators, and Advanced Data Classes
================================================================================
Developer: Nhen Bol
Version: 12.0.1
================================================================================
"""

from config_enums import *
from security_ml_risk import *
from advanced_orders_portfolio import *
from bot_main_part1 import *
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
import time
import threading
import logging

logger = logging.getLogger('ULTIMATE_V12')

# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class EnhancedTechnicalAnalysis:
    """Enhanced technical analysis data"""
    rsi: float
    rsi_signal: str
    macd_trend: str
    ema_trend: str
    bb_position: str
    adx: float
    adx_trend: str
    volume_surge: bool
    volume_ratio: float
    obv_trend: str
    stoch_signal: str
    vwap_position: str
    mfi_signal: str


@dataclass
class OrderBookAnalysis:
    """Order book analysis data"""
    best_bid: float
    best_ask: float
    spread: float
    spread_percentage: float
    imbalance: float
    bid_ask_ratio: float
    buy_pressure: float
    sell_pressure: float
    top_bids: List
    top_asks: List
    support_levels: List[float]
    resistance_levels: List[float]


@dataclass
class MarketTradeAnalysis:
    """Market trade analysis data"""
    aggressive_buying: bool
    aggressive_selling: bool
    large_trades_buy: int
    large_trades_sell: int


@dataclass
class CumulativeFlow:
    """Cumulative flow data"""
    delta_15min: float
    trend_strength: str


@dataclass
class RiskRewardAnalysis:
    """Risk reward analysis data"""
    risk_percentage: float = 0.0
    reward_1_percentage: float = 0.0
    reward_2_percentage: float = 0.0
    reward_3_percentage: float = 0.0
    rr_ratio_1: float = 0.0
    rr_ratio_2: float = 0.0
    rr_ratio_3: float = 0.0
    expected_value: float = 0.0
    scalping_target_1: float = 0.0
    scalping_target_2: float = 0.0
    intraday_target_1: float = 0.0
    intraday_target_2: float = 0.0
    swing_target_1: float = 0.0
    swing_target_2: float = 0.0
    position_target_1: float = 0.0
    position_target_2: float = 0.0


@dataclass
class ConfirmationSignals:
    """Confirmation signals data"""
    bullish_timeframes: int = 0
    bearish_timeframes: int = 0
    total_timeframes: int = 0
    volume_confirmation: bool = False
    volume_ratio: float = 1.0
    obv_confirmation: str = "NEUTRAL"
    divergence_confirmation: str = "NEUTRAL"
    pattern_confirmation: str = "NEUTRAL"
    confirmation_score: float = 0.0


@dataclass
class MarketContext:
    """Market context data"""
    btc_price: float = 0.0
    btc_change_24h: float = 0.0
    eth_price: float = 0.0
    eth_change_24h: float = 0.0
    total_market_cap: float = 0.0
    market_cap_change_24h: float = 0.0
    btc_dominance: float = 50.0
    dominance_change: float = 0.0
    fear_greed_index: float = 50.0
    fear_greed_text: str = "NEUTRAL"


@dataclass
class BacktestResult:
    """Backtest result data"""
    symbol: str = ""
    total_signals: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    last_updated: Optional[datetime] = None


@dataclass
class SmartMoneyDisplay:
    """Smart money display data"""
    primary_concept: Any = None
    secondary_concepts: List[Any] = field(default_factory=list)
    concept_details: Dict[str, Any] = field(default_factory=dict)
    smart_money_score: float = 0.0
    concept_description: str = ""


@dataclass
class WhaleActivity:
    """Whale activity data"""
    whale_buy_detected: bool = False
    whale_sell_detected: bool = False
    whale_cancel_detected: bool = False
    whale_confidence: float = 0.0
    whale_sentiment: str = "NEUTRAL"
    whale_description: str = ""
    
    def analyze(self, trades=None, order_book=None, depth_history=None, 
                min_order_value=50000, cancel_window=60):
        """Analyze whale activity"""
        return self


@dataclass
class KeyZone:
    """Key zone data - Support and Resistance zones with strength analysis"""
    zone_type: str  # 'SUPPORT' or 'RESISTANCE'
    zone_low: float
    zone_high: float
    zone_strength: float  # 0-100
    is_pullback: bool = False
    pullback_percent: Optional[float] = None
    pullback_price: Optional[float] = None
    dome_detected: bool = False
    dome_formation: Optional[str] = None  # 'TOP' or 'BOTTOM'
    dome_height: Optional[float] = None
    touches: int = 0
    volume_at_zone: float = 0.0
    last_touch_time: Optional[datetime] = None
    is_major: bool = False


class KeyZoneDetector:
    """Advanced Key Zone Detector with Support/Resistance, Pullback, and Dome Pattern Detection"""
    
    def __init__(self, config):
        self.config = config
        self.swing_points = []
        self.zones = []
        self.levels = []
        
        # Configuration parameters
        self.swing_lookback = getattr(config, 'KEYZONE_LOOKBACK_BARS', 50)
        self.min_touches = getattr(config, 'KEYZONE_MIN_TOUCHES', 3)
        self.pullback_percent = getattr(config, 'KEYZONE_PULLBACK_PERCENT', 0.5)
        self.merge_threshold = 0.02  # 2% merge threshold
        
    def detect_zones(self, df: pd.DataFrame, current_price: float) -> List[KeyZone]:
        """Detect all key zones (support and resistance)"""
        zones = []
        
        if df is None or len(df) < 20:
            return zones
        
        # Method 1: Detect from swing highs and lows
        swing_zones = self._detect_swing_zones(df)
        zones.extend(swing_zones)
        
        # Method 2: Detect from volume profile
        volume_zones = self._detect_volume_zones(df)
        zones.extend(volume_zones)
        
        # Method 3: Detect from moving averages
        ma_zones = self._detect_ma_zones(df, current_price)
        zones.extend(ma_zones)
        
        # Method 4: Detect from fibonacci levels
        fib_zones = self._detect_fibonacci_zones(df)
        zones.extend(fib_zones)
        
        # Method 5: Detect from order book (if available)
        # This will be called separately with order book data
        
        # Merge nearby zones
        zones = self._merge_zones(zones)
        
        # Calculate strength for each zone
        for zone in zones:
            zone.zone_strength = self._calculate_zone_strength(df, zone)
            zone.touches = self._count_zone_touches(df, zone)
            
            # Check for pullback
            self._check_pullback(zone, df, current_price)
            
            # Check for dome pattern
            self._check_dome_pattern(zone, df)
            
            # Mark major zones
            if zone.zone_strength > 70 or zone.touches >= 5:
                zone.is_major = True
        
        # Sort by strength
        zones.sort(key=lambda x: x.zone_strength, reverse=True)
        
        self.zones = zones
        return zones
    
    def _detect_swing_zones(self, df: pd.DataFrame) -> List[KeyZone]:
        """Detect zones from swing highs and lows"""
        zones = []
        
        highs = df['high'].values
        lows = df['low'].values
        close = df['close'].values
        
        # Detect swing highs (local maxima)
        for i in range(2, len(highs)-2):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                
                # Count touches at this level
                touches = 0
                for j in range(len(close)):
                    if abs(close[j] - highs[i]) / highs[i] < 0.01:
                        touches += 1
                
                # Calculate volume at this zone
                zone_volume = 0
                for j in range(len(df)):
                    if abs(df['high'].iloc[j] - highs[i]) / highs[i] < 0.01:
                        zone_volume += df['volume'].iloc[j]
                
                zones.append(KeyZone(
                    zone_type='RESISTANCE',
                    zone_low=highs[i] * 0.995,
                    zone_high=highs[i] * 1.005,
                    zone_strength=min(50 + touches * 5, 100),
                    touches=touches,
                    volume_at_zone=zone_volume,
                    last_touch_time=self._get_last_touch_time(df, highs[i], 'high')
                ))
            
            # Detect swing lows (local minima)
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                
                touches = 0
                for j in range(len(close)):
                    if abs(close[j] - lows[i]) / lows[i] < 0.01:
                        touches += 1
                
                zone_volume = 0
                for j in range(len(df)):
                    if abs(df['low'].iloc[j] - lows[i]) / lows[i] < 0.01:
                        zone_volume += df['volume'].iloc[j]
                
                zones.append(KeyZone(
                    zone_type='SUPPORT',
                    zone_low=lows[i] * 0.995,
                    zone_high=lows[i] * 1.005,
                    zone_strength=min(50 + touches * 5, 100),
                    touches=touches,
                    volume_at_zone=zone_volume,
                    last_touch_time=self._get_last_touch_time(df, lows[i], 'low')
                ))
        
        return zones
    
    def _detect_volume_zones(self, df: pd.DataFrame) -> List[KeyZone]:
        """Detect zones from volume profile"""
        zones = []
        
        if len(df) < 50:
            return zones
        
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
                
                if row['low'] <= bin_high and row['high'] >= bin_low:
                    overlap = min(row['high'], bin_high) - max(row['low'], bin_low)
                    if overlap > 0:
                        volume_by_price[(bin_low + bin_high)/2] += row['volume'] * (overlap / (row['high'] - row['low']))
        
        # Find high volume nodes
        if volume_by_price:
            avg_volume = np.mean(list(volume_by_price.values()))
            std_volume = np.std(list(volume_by_price.values())) if len(volume_by_price) > 1 else avg_volume * 0.5
            
            for price, volume in volume_by_price.items():
                if volume > avg_volume + 1.5 * std_volume:
                    current_price = df['close'].iloc[-1]
                    
                    if current_price > price:
                        zone_type = 'SUPPORT'
                    else:
                        zone_type = 'RESISTANCE'
                    
                    zones.append(KeyZone(
                        zone_type=zone_type,
                        zone_low=price * 0.99,
                        zone_high=price * 1.01,
                        zone_strength=min(70 + (volume - avg_volume) / std_volume * 10, 100),
                        volume_at_zone=volume
                    ))
        
        return zones
    
    def _detect_ma_zones(self, df: pd.DataFrame, current_price: float) -> List[KeyZone]:
        """Detect zones from moving averages"""
        zones = []
        
        periods = [20, 50, 100, 200]
        
        for period in periods:
            if len(df) >= period:
                ma = df['close'].rolling(window=period).mean().iloc[-1]
                
                # Determine if MA acts as support or resistance
                if current_price > ma:
                    zone_type = 'SUPPORT'
                else:
                    zone_type = 'RESISTANCE'
                
                zones.append(KeyZone(
                    zone_type=zone_type,
                    zone_low=ma * 0.995,
                    zone_high=ma * 1.005,
                    zone_strength=60 + (period / 20),
                    touches=0
                ))
        
        return zones
    
    def _detect_fibonacci_zones(self, df: pd.DataFrame) -> List[KeyZone]:
        """Detect zones from Fibonacci retracement levels"""
        zones = []
        
        if len(df) < 50:
            return zones
        
        # Find recent significant swing
        high_idx = df['high'].argmax()
        low_idx = df['low'].argmin()
        
        fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        fib_names = ['23.6%', '38.2%', '50%', '61.8%', '78.6%']
        
        if high_idx > low_idx:  # Downtrend
            swing_high = df['high'].iloc[high_idx]
            swing_low = df['low'].iloc[low_idx]
            
            for i, fib in enumerate(fib_levels):
                price = swing_high - (swing_high - swing_low) * fib
                zone_type = 'RESISTANCE' if fib < 0.5 else 'SUPPORT'
                
                zones.append(KeyZone(
                    zone_type=zone_type,
                    zone_low=price * 0.995,
                    zone_high=price * 1.005,
                    zone_strength=70 + fib * 30,
                    touches=0,
                    is_major=fib == 0.618
                ))
        else:  # Uptrend
            swing_low = df['low'].iloc[low_idx]
            swing_high = df['high'].iloc[high_idx]
            
            for i, fib in enumerate(fib_levels):
                price = swing_low + (swing_high - swing_low) * fib
                zone_type = 'SUPPORT' if fib < 0.5 else 'RESISTANCE'
                
                zones.append(KeyZone(
                    zone_type=zone_type,
                    zone_low=price * 0.995,
                    zone_high=price * 1.005,
                    zone_strength=70 + fib * 30,
                    touches=0,
                    is_major=fib == 0.618
                ))
        
        return zones
    
    def _merge_zones(self, zones: List[KeyZone], threshold: float = 0.02) -> List[KeyZone]:
        """Merge nearby zones to avoid duplicates"""
        if not zones:
            return []
        
        # Sort by price
        zones.sort(key=lambda x: x.zone_low)
        
        merged = []
        current_group = [zones[0]]
        
        for i in range(1, len(zones)):
            if abs(zones[i].zone_low - current_group[-1].zone_low) / current_group[-1].zone_low < threshold:
                current_group.append(zones[i])
            else:
                # Merge current group
                if len(current_group) > 1:
                    avg_low = np.mean([z.zone_low for z in current_group])
                    avg_high = np.mean([z.zone_high for z in current_group])
                    avg_strength = np.mean([z.zone_strength for z in current_group])
                    total_touches = sum([z.touches for z in current_group])
                    total_volume = sum([z.volume_at_zone for z in current_group])
                    
                    # Determine predominant type
                    support_count = sum(1 for z in current_group if z.zone_type == 'SUPPORT')
                    resistance_count = sum(1 for z in current_group if z.zone_type == 'RESISTANCE')
                    
                    zone_type = 'SUPPORT' if support_count > resistance_count else 'RESISTANCE'
                    
                    merged.append(KeyZone(
                        zone_type=zone_type,
                        zone_low=avg_low,
                        zone_high=avg_high,
                        zone_strength=min(avg_strength + 10, 100),
                        touches=total_touches,
                        volume_at_zone=total_volume,
                        is_major=any(z.is_major for z in current_group)
                    ))
                else:
                    merged.append(current_group[0])
                
                current_group = [zones[i]]
        
        # Handle last group
        if current_group:
            if len(current_group) > 1:
                avg_low = np.mean([z.zone_low for z in current_group])
                avg_high = np.mean([z.zone_high for z in current_group])
                avg_strength = np.mean([z.zone_strength for z in current_group])
                total_touches = sum([z.touches for z in current_group])
                total_volume = sum([z.volume_at_zone for z in current_group])
                
                support_count = sum(1 for z in current_group if z.zone_type == 'SUPPORT')
                resistance_count = sum(1 for z in current_group if z.zone_type == 'RESISTANCE')
                
                zone_type = 'SUPPORT' if support_count > resistance_count else 'RESISTANCE'
                
                merged.append(KeyZone(
                    zone_type=zone_type,
                    zone_low=avg_low,
                    zone_high=avg_high,
                    zone_strength=min(avg_strength + 10, 100),
                    touches=total_touches,
                    volume_at_zone=total_volume,
                    is_major=any(z.is_major for z in current_group)
                ))
            else:
                merged.append(current_group[0])
        
        return merged
    
    def _calculate_zone_strength(self, df: pd.DataFrame, zone: KeyZone) -> float:
        """Calculate zone strength based on multiple factors"""
        strength = 50.0
        
        # Factor 1: Number of touches
        strength += min(zone.touches * 5, 25)
        
        # Factor 2: Volume at zone
        avg_volume = df['volume'].mean()
        if avg_volume > 0:
            volume_ratio = zone.volume_at_zone / avg_volume
            strength += min(volume_ratio * 10, 20)
        
        # Factor 3: Time since last touch (recent = stronger)
        if zone.last_touch_time:
            days_since = (datetime.now() - zone.last_touch_time).days
            time_factor = max(0, 20 - days_since)
            strength += time_factor
        
        # Factor 4: Zone width (tighter = stronger)
        width = (zone.zone_high - zone.zone_low) / zone.zone_low * 100
        if width < 0.5:
            strength += 15
        elif width < 1.0:
            strength += 10
        elif width < 2.0:
            strength += 5
        
        # Factor 5: Multiple timeframes confluence
        # This would require multi-timeframe data
        
        return min(100, max(0, strength))
    
    def _count_zone_touches(self, df: pd.DataFrame, zone: KeyZone) -> int:
        """Count how many times price touched the zone"""
        touches = 0
        
        for _, row in df.iterrows():
            if zone.zone_type == 'SUPPORT':
                if row['low'] <= zone.zone_high and row['low'] >= zone.zone_low:
                    touches += 1
                elif abs(row['close'] - zone.zone_low) / zone.zone_low < 0.01:
                    touches += 1
            else:  # RESISTANCE
                if row['high'] >= zone.zone_low and row['high'] <= zone.zone_high:
                    touches += 1
                elif abs(row['close'] - zone.zone_high) / zone.zone_high < 0.01:
                    touches += 1
        
        return touches
    
    def _get_last_touch_time(self, df: pd.DataFrame, price: float, side: str) -> Optional[datetime]:
        """Get timestamp of last touch at price level"""
        for i in range(len(df)-1, -1, -1):
            row = df.iloc[i]
            if side == 'high':
                if abs(row['high'] - price) / price < 0.01:
                    return row.name if isinstance(row.name, datetime) else None
            else:
                if abs(row['low'] - price) / price < 0.01:
                    return row.name if isinstance(row.name, datetime) else None
        return None
    
    def _check_pullback(self, zone: KeyZone, df: pd.DataFrame, current_price: float):
        """Check if price is pulling back to zone"""
        if zone.zone_type == 'SUPPORT':
            # Price above support and pulling back
            if current_price > zone.zone_high and current_price < zone.zone_high * 1.05:
                retrace = (current_price - zone.zone_high) / (zone.zone_high - zone.zone_low) * 100
                if retrace <= 61.8:  # Fibonacci retracement limit
                    zone.is_pullback = True
                    zone.pullback_percent = retrace
                    zone.pullback_price = zone.zone_high
        else:  # RESISTANCE
            # Price below resistance and pulling back
            if current_price < zone.zone_low and current_price > zone.zone_low * 0.95:
                retrace = (zone.zone_low - current_price) / (zone.zone_high - zone.zone_low) * 100
                if retrace <= 61.8:
                    zone.is_pullback = True
                    zone.pullback_percent = retrace
                    zone.pullback_price = zone.zone_low
    
    def _check_dome_pattern(self, zone: KeyZone, df: pd.DataFrame):
        """Check for dome pattern (rounding top/bottom)"""
        if len(df) < 20:
            return
        
        recent_prices = df['close'].iloc[-20:].values
        
        # Check for rounding top (dome)
        if self._is_rounding_top(recent_prices):
            zone.dome_detected = True
            zone.dome_formation = 'TOP'
            zone.dome_height = self._calculate_dome_height(recent_prices)
        
        # Check for rounding bottom (inverse dome)
        elif self._is_rounding_bottom(recent_prices):
            zone.dome_detected = True
            zone.dome_formation = 'BOTTOM'
            zone.dome_height = self._calculate_dome_height(recent_prices)
    
    def _is_rounding_top(self, prices: np.ndarray) -> bool:
        """Check if prices form a rounding top pattern"""
        if len(prices) < 10:
            return False
        
        first_half = prices[:len(prices)//2]
        second_half = prices[len(prices)//2:]
        
        first_slope = (first_half[-1] - first_half[0]) / len(first_half)
        second_slope = (second_half[-1] - second_half[0]) / len(second_half)
        
        # Dome pattern: first half rising, second half falling
        return first_slope > 0 and second_slope < 0 and abs(first_slope + second_slope) < 0.1
    
    def _is_rounding_bottom(self, prices: np.ndarray) -> bool:
        """Check if prices form a rounding bottom pattern"""
        if len(prices) < 10:
            return False
        
        first_half = prices[:len(prices)//2]
        second_half = prices[len(prices)//2:]
        
        first_slope = (first_half[-1] - first_half[0]) / len(first_half)
        second_slope = (second_half[-1] - second_half[0]) / len(second_half)
        
        # Inverse dome pattern: first half falling, second half rising
        return first_slope < 0 and second_slope > 0 and abs(first_slope + second_slope) < 0.1
    
    def _calculate_dome_height(self, prices: np.ndarray) -> float:
        """Calculate dome height percentage"""
        low = min(prices)
        high = max(prices)
        return ((high - low) / low) * 100
    
    def get_best_entry_zone(self, direction: str, current_price: float) -> Optional[KeyZone]:
        """Get best entry zone for given direction"""
        if not self.zones:
            return None
        
        if direction == "BUY":
            # Find support zones below current price
            supports = [z for z in self.zones if z.zone_type == 'SUPPORT' and z.zone_high < current_price]
            if not supports:
                return None
            # Return the closest support with highest strength
            return max(supports, key=lambda z: z.zone_strength / (current_price - z.zone_high + 0.001))
        else:
            # Find resistance zones above current price
            resistances = [z for z in self.zones if z.zone_type == 'RESISTANCE' and z.zone_low > current_price]
            if not resistances:
                return None
            # Return the closest resistance with highest strength
            return max(resistances, key=lambda z: z.zone_strength / (z.zone_low - current_price + 0.001))
    
    def get_nearest_zones(self, current_price: float, num_zones: int = 3) -> Tuple[List[KeyZone], List[KeyZone]]:
        """Get nearest support and resistance zones"""
        supports = [z for z in self.zones if z.zone_type == 'SUPPORT' and z.zone_high < current_price]
        resistances = [z for z in self.zones if z.zone_type == 'RESISTANCE' and z.zone_low > current_price]
        
        # Sort by distance
        supports.sort(key=lambda x: current_price - x.zone_high)
        resistances.sort(key=lambda x: x.zone_low - current_price)
        
        return supports[:num_zones], resistances[:num_zones]
    
    def get_strongest_zones(self, num_zones: int = 5) -> List[KeyZone]:
        """Get strongest zones overall"""
        return sorted(self.zones, key=lambda x: x.zone_strength, reverse=True)[:num_zones]


class TPSLManager:
    """Take profit and stop loss manager with multiple levels"""
    
    def __init__(self, config):
        self.config = config
    
    def calculate_levels(self, entry_price: float, stop_loss: float, direction: str, 
                         style=None, atr: float = 0) -> Dict[str, float]:
        """Calculate take profit levels with style-based multipliers"""
        risk = abs(entry_price - stop_loss)
        
        # Get multipliers from TP config
        if style:
            style_name = style.value if hasattr(style, 'value') else str(style)
            tp_config = self.config.TP_CONFIG if hasattr(self.config, 'TP_CONFIG') else None
            
            if tp_config:
                tp1_mult, tp2_mult, tp3_mult = tp_config.get_multipliers(style_name)
            else:
                tp1_mult, tp2_mult, tp3_mult = 1.5, 2.5, 4.0
        else:
            tp1_mult, tp2_mult, tp3_mult = 1.5, 2.5, 4.0
        
        if direction == "BUY":
            tp1 = entry_price + risk * tp1_mult
            tp2 = entry_price + risk * tp2_mult
            tp3 = entry_price + risk * tp3_mult
        else:
            tp1 = entry_price - risk * tp1_mult
            tp2 = entry_price - risk * tp2_mult
            tp3 = entry_price - risk * tp3_mult
        
        return {'tp1': tp1, 'tp2': tp2, 'tp3': tp3}


# ==============================================================================
# ORDER TYPE ANALYZER
# ==============================================================================
class OrderTypeAnalyzer:
    """Analyze and recommend order types based on market conditions"""
    
    def __init__(self):
        self.volume_spike_threshold = 1.5
        self.volatility_threshold = 2.0
        
    def analyze_order_type(self, signal: Any, ob_analysis: Any, current_price: float,
                          bid_ask_spread: float, volume_24h: float,
                          avg_volume_24h: float) -> Tuple[OrderType, OrderRecommendation, str]:
        """Analyze and recommend order type"""
        reasons = []
        order_type = None
        recommendation = None
        
        # Calculate metrics with type checking
        try:
            spread_percent = (bid_ask_spread / current_price) * 100 if current_price > 0 else 0
        except (TypeError, ZeroDivisionError):
            spread_percent = 0.1
        
        try:
            volume_ratio = volume_24h / avg_volume_24h if avg_volume_24h > 0 else 1.0
        except (TypeError, ZeroDivisionError):
            volume_ratio = 1.0
        
        volatility = self._calculate_volatility(signal)
        
        # Get imbalance with type checking
        imbalance = 0.0
        if ob_analysis and hasattr(ob_analysis, 'imbalance'):
            try:
                imbalance = float(ob_analysis.imbalance)
            except (TypeError, ValueError):
                imbalance = 0.0
        
        # Get position size with type checking
        position_size = 1.0
        if hasattr(signal, 'optimal_position_size'):
            try:
                position_size = float(signal.optimal_position_size)
            except (TypeError, ValueError):
                position_size = 1.0
        
        # Get signal type with type checking
        signal_type = ""
        if hasattr(signal, 'signal_type'):
            signal_type = signal.signal_type
        
        # Get primary style with type checking
        primary_style = None
        if hasattr(signal, 'primary_style'):
            primary_style = signal.primary_style
        
        # Get confidence with type checking
        confidence = 0
        if hasattr(signal, 'confidence'):
            try:
                confidence = float(signal.confidence)
            except (TypeError, ValueError):
                confidence = 0
        
        # Large position size - use Iceberg
        if volume_24h > 10_000_000 or position_size > 1.5:
            order_type = OrderType.ICEBERG
            recommendation = OrderRecommendation.ICEBERG_RECOMMENDED
            reasons.append("Large position size - Use Iceberg orders to hide size")
        
        # High volatility - use TWAP
        elif volatility > self.volatility_threshold * 1.5:
            order_type = OrderType.TWAP
            recommendation = OrderRecommendation.TWAP_RECOMMENDED
            reasons.append(f"High volatility ({volatility:.1f}%) - Use TWAP to reduce slippage")
        
        # Strong imbalance - use Market
        elif (abs(imbalance) > 30 and spread_percent < 0.02 and volume_ratio > 1.3 and 
              confidence > 85):
            
            if signal_type == "STRONG_BUY":
                order_type = OrderType.MARKET_BUY
                recommendation = OrderRecommendation.AGGRESSIVE_MARKET
                reasons.append(f"Strong buying pressure (imbalance: {imbalance:.1f}%)")
            else:
                order_type = OrderType.MARKET_SELL
                recommendation = OrderRecommendation.AGGRESSIVE_MARKET
                reasons.append(f"Strong selling pressure (imbalance: {imbalance:.1f}%)")
        
        # Scalping opportunity
        elif (primary_style == SignalStyle.SCALPING and
              abs(imbalance) > 20 and spread_percent < 0.03):
            
            if signal_type == "STRONG_BUY":
                order_type = OrderType.MARKET_BUY
                recommendation = OrderRecommendation.SCALPER_MARKET
                reasons.append("Scalping opportunity with strong order flow")
            else:
                order_type = OrderType.MARKET_SELL
                recommendation = OrderRecommendation.SCALPER_MARKET
                reasons.append("Scalping opportunity with strong order flow")
        
        # Buy signal but no extreme pressure - use Limit
        elif (signal_type == "STRONG_BUY" and 
              imbalance < 10 and volume_ratio < 1.2):
            order_type = OrderType.LIMIT_BUY
            recommendation = OrderRecommendation.LIMIT_BUY_DIP
            reasons.append("Wait for dip - Buying pressure not extreme")
        
        # Sell signal but no extreme pressure - use Limit
        elif (signal_type == "STRONG_SELL" and 
              imbalance > -10 and volume_ratio < 1.2):
            order_type = OrderType.LIMIT_SELL
            recommendation = OrderRecommendation.LIMIT_SELL_RALLY
            reasons.append("Wait for rally - Selling pressure not extreme")
        
        # Long-term position - use Limit
        elif (primary_style in [SignalStyle.POSITION, SignalStyle.SWING]):
            
            if signal_type == "STRONG_BUY":
                order_type = OrderType.LIMIT_BUY
                recommendation = OrderRecommendation.POSITION_LIMIT
                reasons.append("Long-term position - Use limit orders for better entry")
            else:
                order_type = OrderType.LIMIT_SELL
                recommendation = OrderRecommendation.POSITION_LIMIT
                reasons.append("Long-term position - Use limit orders for better entry")
        
        # Default - wait for confirmation
        else:
            if signal_type == "STRONG_BUY":
                order_type = OrderType.LIMIT_BUY
                recommendation = OrderRecommendation.WAIT_CONFIRMATION
                reasons.append("Wait for confirmation - Market conditions not ideal for immediate entry")
            else:
                order_type = OrderType.LIMIT_SELL
                recommendation = OrderRecommendation.WAIT_CONFIRMATION
                reasons.append("Wait for confirmation - Market conditions not ideal for immediate entry")
        
        reasons.append(f"Bid-Ask spread: {spread_percent:.3f}%")
        
        if volume_ratio > 1.5:
            reasons.append(f"Volume spike: {volume_ratio:.1f}x average")
        
        return order_type, recommendation, " | ".join(reasons)
    
    def _calculate_volatility(self, signal: Any) -> float:
        """Calculate volatility from signal"""
        try:
            if hasattr(signal, 'expected_move') and signal.expected_move:
                return float(signal.expected_move)
            
            if (hasattr(signal, 'atr_value') and signal.atr_value and 
                hasattr(signal, 'current_price') and signal.current_price):
                return (float(signal.atr_value) / float(signal.current_price)) * 100
            
            return 2.0
        except (TypeError, ValueError, ZeroDivisionError):
            return 2.0


# ==============================================================================
# ENHANCED ENTRY OPTIMIZER
# ==============================================================================
class EnhancedEntryOptimizer:
    """Optimize entry prices based on market conditions"""
    
    def __init__(self, client: Any, config: HybridConfig):
        self.client = client
        self.config = config
        self.volume_profile = VolumeProfileEntry()
    
    def get_style_entries(self, symbol: str, direction: str, current_price: float, 
                          df_1h: Optional[pd.DataFrame] = None, 
                          style: str = "INTRADAY") -> Dict[str, Any]:
        """Get entry prices for different trading styles"""
        try:
            # Get order book data
            ob_data = None
            if hasattr(self.client, 'get_order_book'):
                ob_data = self.client.get_order_book(symbol, self.config.ENTRY_ORDER_BOOK_DEPTH)
            
            # Calculate volume profile entry
            vp_entry = None
            if df_1h is not None and len(df_1h) >= 20:
                vp_entry = self.volume_profile.calculate_entry(df_1h, direction, current_price, style)
            
            entries = {}
            
            if direction == "BUY":
                entries = self._get_buy_entries(current_price, vp_entry, ob_data)
            else:
                entries = self._get_sell_entries(current_price, vp_entry, ob_data)
            
            # Ensure we have basic fields
            if 'best_bid' not in entries:
                entries['best_bid'] = current_price * 0.999
            if 'best_ask' not in entries:
                entries['best_ask'] = current_price * 1.001
            if 'mid' not in entries:
                entries['mid'] = current_price
            
            # Calculate imbalance and spread
            entries['imbalance'] = self._calculate_imbalance(ob_data)
            
            try:
                entries['spread_percent'] = ((entries['best_ask'] - entries['best_bid']) / 
                                             entries['best_bid']) * 100
            except (TypeError, ZeroDivisionError):
                entries['spread_percent'] = 0.2
            
            return entries
            
        except Exception as e:
            logger.error(f"Entry optimization error for {symbol}: {e}")
            return self._get_fallback_entries(current_price, direction)
    
    def _get_buy_entries(self, current_price: float, vp_entry: Optional[Dict], 
                         ob_data: Optional[Dict]) -> Dict[str, Any]:
        """Get buy entries"""
        entries = {}
        
        if vp_entry and vp_entry.get('entry_confidence', 0) >= 60:
            poc = vp_entry.get('poc_price', current_price)
            va_low = vp_entry.get('value_area_low', current_price * 0.98)
            va_high = vp_entry.get('value_area_high', current_price * 1.02)
            
            entries['scalping'] = {
                'price': max(current_price, current_price * 0.998),
                'range_low': current_price * 0.997,
                'range_high': current_price * 1.001,
                'logic': f"Scalping: {vp_entry.get('entry_logic', 'Volume Profile')}"
            }
            
            entries['intraday'] = {
                'price': va_low if va_low < current_price else current_price * 0.995,
                'range_low': min(va_low, current_price * 0.99),
                'range_high': current_price,
                'logic': f"Intraday: {vp_entry.get('entry_logic', 'Volume Profile')}"
            }
            
            entries['swing'] = {
                'price': min(va_low, current_price * 0.99),
                'range_low': min(va_low, current_price * 0.985),
                'range_high': current_price * 0.995,
                'logic': f"Swing: {vp_entry.get('entry_logic', 'Volume Profile')}"
            }
            
            entries['position'] = {
                'price': min(va_low, current_price * 0.98),
                'range_low': min(va_low, current_price * 0.975),
                'range_high': current_price * 0.99,
                'logic': f"Position: {vp_entry.get('entry_logic', 'Volume Profile')}"
            }
            
            entries['poc_price'] = poc
            entries['value_area_low'] = va_low
            entries['value_area_high'] = va_high
            
        elif ob_data and 'bids' in ob_data and 'asks' in ob_data:
            entries = self._get_order_book_entries(ob_data, current_price, "BUY")
            
        else:
            entries['scalping'] = {
                'price': current_price * 1.001,
                'range_low': current_price,
                'range_high': current_price * 1.002,
                'logic': 'Scalping: Market'
            }
            entries['intraday'] = {
                'price': current_price,
                'range_low': current_price * 0.998,
                'range_high': current_price * 1.002,
                'logic': 'Intraday: Current'
            }
            entries['swing'] = {
                'price': current_price * 0.995,
                'range_low': current_price * 0.99,
                'range_high': current_price,
                'logic': 'Swing: Discount'
            }
            entries['position'] = {
                'price': current_price * 0.99,
                'range_low': current_price * 0.985,
                'range_high': current_price * 0.995,
                'logic': 'Position: Deep Discount'
            }
        
        return entries
    
    def _get_sell_entries(self, current_price: float, vp_entry: Optional[Dict], 
                          ob_data: Optional[Dict]) -> Dict[str, Any]:
        """Get sell entries"""
        entries = {}
        
        if vp_entry and vp_entry.get('entry_confidence', 0) >= 60:
            poc = vp_entry.get('poc_price', current_price)
            va_low = vp_entry.get('value_area_low', current_price * 0.98)
            va_high = vp_entry.get('value_area_high', current_price * 1.02)
            
            entries['scalping'] = {
                'price': min(current_price, current_price * 1.002),
                'range_low': current_price * 0.999,
                'range_high': current_price * 1.003,
                'logic': f"Scalping: {vp_entry.get('entry_logic', 'Volume Profile')}"
            }
            
            entries['intraday'] = {
                'price': va_high if va_high > current_price else current_price * 1.005,
                'range_low': current_price,
                'range_high': max(va_high, current_price * 1.01),
                'logic': f"Intraday: {vp_entry.get('entry_logic', 'Volume Profile')}"
            }
            
            entries['swing'] = {
                'price': max(va_high, current_price * 1.01),
                'range_low': current_price * 1.005,
                'range_high': max(va_high, current_price * 1.015),
                'logic': f"Swing: {vp_entry.get('entry_logic', 'Volume Profile')}"
            }
            
            entries['position'] = {
                'price': max(va_high, current_price * 1.02),
                'range_low': current_price * 1.01,
                'range_high': max(va_high, current_price * 1.025),
                'logic': f"Position: {vp_entry.get('entry_logic', 'Volume Profile')}"
            }
            
            entries['poc_price'] = poc
            entries['value_area_low'] = va_low
            entries['value_area_high'] = va_high
            
        elif ob_data and 'bids' in ob_data and 'asks' in ob_data:
            entries = self._get_order_book_entries(ob_data, current_price, "SELL")
            
        else:
            entries['scalping'] = {
                'price': current_price * 0.999,
                'range_low': current_price * 0.998,
                'range_high': current_price,
                'logic': 'Scalping: Market'
            }
            entries['intraday'] = {
                'price': current_price,
                'range_low': current_price * 0.998,
                'range_high': current_price * 1.002,
                'logic': 'Intraday: Current'
            }
            entries['swing'] = {
                'price': current_price * 1.005,
                'range_low': current_price,
                'range_high': current_price * 1.01,
                'logic': 'Swing: Premium'
            }
            entries['position'] = {
                'price': current_price * 1.01,
                'range_low': current_price * 1.005,
                'range_high': current_price * 1.015,
                'logic': 'Position: Deep Premium'
            }
        
        return entries
    
    def _get_order_book_entries(self, ob_data: Dict, current_price: float, 
                                 direction: str) -> Dict[str, Any]:
        """Get entries from order book data"""
        entries = {}
        
        try:
            bids = ob_data.get('bids', [])
            asks = ob_data.get('asks', [])
            
            if len(bids) > 0 and len(asks) > 0:
                best_bid = float(bids[0][0])
                best_ask = float(asks[0][0])
                mid_price = (best_bid + best_ask) / 2
                
                if direction == "BUY":
                    entries['scalping'] = {
                        'price': best_ask,
                        'range_low': best_ask,
                        'range_high': best_ask,
                        'logic': 'Scalping: Market Ask'
                    }
                    entries['intraday'] = {
                        'price': mid_price,
                        'range_low': best_bid,
                        'range_high': best_ask,
                        'logic': 'Intraday: Mid Price'
                    }
                    entries['swing'] = {
                        'price': best_bid,
                        'range_low': best_bid * 0.998,
                        'range_high': best_bid,
                        'logic': 'Swing: Bid Level'
                    }
                    entries['position'] = {
                        'price': best_bid * 0.995,
                        'range_low': best_bid * 0.99,
                        'range_high': best_bid * 0.998,
                        'logic': 'Position: Deep Bid'
                    }
                else:  # SELL
                    entries['scalping'] = {
                        'price': best_bid,
                        'range_low': best_bid,
                        'range_high': best_bid,
                        'logic': 'Scalping: Market Bid'
                    }
                    entries['intraday'] = {
                        'price': mid_price,
                        'range_low': best_bid,
                        'range_high': best_ask,
                        'logic': 'Intraday: Mid Price'
                    }
                    entries['swing'] = {
                        'price': best_ask,
                        'range_low': best_ask,
                        'range_high': best_ask * 1.002,
                        'logic': 'Swing: Ask Level'
                    }
                    entries['position'] = {
                        'price': best_ask * 1.005,
                        'range_low': best_ask * 1.002,
                        'range_high': best_ask * 1.01,
                        'logic': 'Position: Deep Ask'
                    }
                
                entries['best_bid'] = best_bid
                entries['best_ask'] = best_ask
                entries['mid'] = mid_price
                
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"Error parsing order book: {e}")
            entries['best_bid'] = current_price * 0.999
            entries['best_ask'] = current_price * 1.001
            entries['mid'] = current_price
        
        return entries
    
    def _get_fallback_entries(self, current_price: float, direction: str) -> Dict[str, Any]:
        """Get fallback entries when everything fails"""
        if direction == "BUY":
            return {
                'scalping': {
                    'price': current_price,
                    'range_low': current_price * 0.999,
                    'range_high': current_price * 1.001,
                    'logic': 'Fallback'
                },
                'intraday': {
                    'price': current_price,
                    'range_low': current_price * 0.998,
                    'range_high': current_price * 1.002,
                    'logic': 'Fallback'
                },
                'swing': {
                    'price': current_price * 0.995,
                    'range_low': current_price * 0.99,
                    'range_high': current_price,
                    'logic': 'Fallback'
                },
                'position': {
                    'price': current_price * 0.99,
                    'range_low': current_price * 0.985,
                    'range_high': current_price * 0.995,
                    'logic': 'Fallback'
                },
                'best_bid': current_price * 0.999,
                'best_ask': current_price * 1.001,
                'mid': current_price,
                'imbalance': 0,
                'spread_percent': 0.2
            }
        else:
            return {
                'scalping': {
                    'price': current_price,
                    'range_low': current_price * 0.999,
                    'range_high': current_price * 1.001,
                    'logic': 'Fallback'
                },
                'intraday': {
                    'price': current_price,
                    'range_low': current_price * 0.998,
                    'range_high': current_price * 1.002,
                    'logic': 'Fallback'
                },
                'swing': {
                    'price': current_price * 1.005,
                    'range_low': current_price,
                    'range_high': current_price * 1.01,
                    'logic': 'Fallback'
                },
                'position': {
                    'price': current_price * 1.01,
                    'range_low': current_price * 1.005,
                    'range_high': current_price * 1.015,
                    'logic': 'Fallback'
                },
                'best_bid': current_price * 0.999,
                'best_ask': current_price * 1.001,
                'mid': current_price,
                'imbalance': 0,
                'spread_percent': 0.2
            }
    
    def _calculate_imbalance(self, ob_data: Optional[Dict]) -> float:
        """Calculate order book imbalance"""
        try:
            if not ob_data or 'bids' not in ob_data or 'asks' not in ob_data:
                return 0.0
            
            bids = ob_data.get('bids', [])[:5]
            asks = ob_data.get('asks', [])[:5]
            
            bid_volume = 0.0
            for b in bids:
                try:
                    bid_volume += float(b[1]) * float(b[0])
                except (TypeError, ValueError, IndexError):
                    pass
            
            ask_volume = 0.0
            for a in asks:
                try:
                    ask_volume += float(a[1]) * float(a[0])
                except (TypeError, ValueError, IndexError):
                    pass
            
            total = bid_volume + ask_volume
            if total > 0:
                return ((bid_volume - ask_volume) / total) * 100
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating imbalance: {e}")
            return 0.0


# ==============================================================================
# TIER 1 GENERATOR (ULTRA SAFE)
# ==============================================================================
class Tier1Generator:
    """Tier 1 Ultra Safe signal generator"""
    
    def __init__(self, parent: 'TieredSignalGenerator'):
        self.parent = parent
        self.config = parent.hybrid_config
        self.order_type_analyzer = OrderTypeAnalyzer()
        self.keyzone_detector = KeyZoneDetector(self.config)
        self.tpsl_manager = TPSLManager(self.config)
        
        if hasattr(self.config, 'LANGUAGE'):
            lang.current_language = Language(self.config.LANGUAGE)
    
    def generate(self, symbol: str, base_analysis: Tuple, 
                 multi_tf_regime: 'MultiTimeframeRegime') -> Optional['EnhancedHighConfidenceSignal']:
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
                key_zones, active_key_zone, key_zone_entry, key_zone_confidence,
                False, None, None, False, None, None
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
        
        # Simple direction analysis based on EMAs
        if hasattr(tech, 'ema_trend'):
            if tech.ema_trend == "BULLISH":
                direction = "BUY"
                direction_confidence = 65
            elif tech.ema_trend == "BEARISH":
                direction = "SELL"
                direction_confidence = 65
        
        # Override with multi-timeframe regime
        if hasattr(multi_tf_regime, 'overall_regime'):
            if "BULL" in multi_tf_regime.overall_regime:
                direction = "BUY"
                direction_confidence = 70
            elif "BEAR" in multi_tf_regime.overall_regime:
                direction = "SELL"
                direction_confidence = 70
        
        # Consider order book
        if ob and hasattr(ob, 'imbalance'):
            try:
                imbalance = float(ob.imbalance)
                if imbalance > 20:
                    direction = "BUY"
                    direction_confidence = 75
                elif imbalance < -20:
                    direction = "SELL"
                    direction_confidence = 75
            except (TypeError, ValueError):
                pass
        
        return direction, direction_confidence, ultimate_result
    
    def _has_strong_confirmations(self, tech: Any, ob: Any, multi_tf: MultiTimeframeRegime,
                                   direction_confidence: float, whale_signal: bool = False,
                                   key_zone_entry: bool = False) -> bool:
        """Check if there are strong confirmations"""
        confirmations = 0
        
        # Technical confirmations
        if hasattr(tech, 'ema_trend') and tech.ema_trend in ["BULLISH", "BEARISH"]:
            confirmations += 1
        
        if hasattr(tech, 'macd_trend') and tech.macd_trend in ["BULLISH", "BEARISH"]:
            confirmations += 1
        
        if hasattr(tech, 'rsi_signal') and tech.rsi_signal in ["OVERSOLD", "OVERBOUGHT"]:
            confirmations += 1.5
        
        if hasattr(tech, 'adx') and isinstance(tech.adx, (int, float)) and tech.adx > 35:
            confirmations += 1
        
        # Order book confirmations
        if ob and hasattr(ob, 'imbalance'):
            try:
                imbalance = float(ob.imbalance)
                if abs(imbalance) > 20:
                    confirmations += 1.5
                elif abs(imbalance) > 10:
                    confirmations += 1
            except (TypeError, ValueError):
                pass
        
        if ob and hasattr(ob, 'bid_ask_ratio'):
            try:
                ratio = float(ob.bid_ask_ratio)
                if ratio > 1.3 or ratio < 0.7:
                    confirmations += 1
            except (TypeError, ValueError):
                pass
        
        # Multi-timeframe confirmations
        if hasattr(multi_tf, 'regime_alignment'):
            try:
                alignment = float(multi_tf.regime_alignment)
                if alignment > 70:
                    confirmations += 1.5
            except (TypeError, ValueError):
                pass
        
        if hasattr(multi_tf, 'overall_regime'):
            if multi_tf.overall_regime in ["BULL", "BEAR"]:
                confirmations += 1
        
        # Special signals
        if whale_signal:
            confirmations += 2
        if key_zone_entry:
            confirmations += 2
        
        # Confidence-based
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
                      dome_height: Optional[float] = None) -> 'EnhancedHighConfidenceSignal':
        """Build enhanced signal"""
        from datetime import datetime
        
        current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
        
        # Get volume
        volume_24h = 0
        if ticker and isinstance(ticker, dict):
            try:
                volume_24h = float(ticker.get('quoteVolume', 0))
            except (TypeError, ValueError):
                volume_24h = 0
        
        # Calculate stop loss
        stop_loss, stop_percentage, atr_value = self.parent.calculate_atr_stop_loss(
            current_price, direction, df_1h
        )
        
        # Get entry data
        entry_data = self.parent.get_style_entries(symbol, direction, current_price, df_1h, "INTRADAY")
        
        # Select entry price with key zone consideration
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
        
        # Recalculate stop loss at entry price
        stop_loss, stop_percentage, atr_value = self.parent.calculate_atr_stop_loss(
            entry_price, direction, df_1h
        )
        
        # Calculate TP levels
        if direction == "BUY":
            tp1 = entry_price + (entry_price - stop_loss) * 1.5
            tp2 = entry_price + (entry_price - stop_loss) * 2.5
            tp3 = entry_price + (entry_price - stop_loss) * 4.0
        else:
            tp1 = entry_price - (stop_loss - entry_price) * 1.5
            tp2 = entry_price - (stop_loss - entry_price) * 2.5
            tp3 = entry_price - (stop_loss - entry_price) * 4.0
        
        # Calculate leverage with key zone boost
        leverage = self._calculate_leverage(multi_tf_regime, key_zone_entry)
        
        # Create risk reward analysis
        risk_reward = RiskRewardAnalysis(
            risk_percentage=stop_percentage,
            reward_1_percentage=abs(tp1 - entry_price) / entry_price * 100,
            reward_2_percentage=abs(tp2 - entry_price) / entry_price * 100,
            reward_3_percentage=abs(tp3 - entry_price) / entry_price * 100,
            rr_ratio_1=abs(tp1 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            rr_ratio_2=abs(tp2 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            rr_ratio_3=abs(tp3 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            expected_value=(abs(tp1 - entry_price) * 0.5 - abs(stop_loss - entry_price) * 0.5) / entry_price * 100,
            scalping_target_1=1.0,
            scalping_target_2=1.5,
            intraday_target_1=abs(tp1 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            intraday_target_2=abs(tp2 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            swing_target_1=abs(tp2 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            swing_target_2=abs(tp3 - entry_price) / abs(stop_loss - entry_price) if abs(stop_loss - entry_price) > 0 else 0,
            position_target_1=abs(tp2 - entry_price) / abs(stop_loss - entry_price) * 1.5 if abs(stop_loss - entry_price) > 0 else 0,
            position_target_2=abs(tp3 - entry_price) / abs(stop_loss - entry_price) * 1.5 if abs(stop_loss - entry_price) > 0 else 0
        )
        
        # Primary reasons with key zone info
        primary_reasons = [
            f"Direction: {direction} with {direction_confidence:.1f}% confidence",
            f"Tech score: {tech_score:+.0f}, Flow score: {flow_score:+.0f}",
            f"Regime: {multi_tf_regime.overall_regime} ({multi_tf_regime.regime_alignment:.0f}% aligned)"
        ]
        
        if key_zone_entry and active_key_zone:
            primary_reasons.insert(0, f"🎯 Key zone: {active_key_zone.zone_type} at {active_key_zone.zone_low:.4f}-{active_key_zone.zone_high:.4f} (strength: {active_key_zone.zone_strength:.0f}%)")
        
        if whale_signal and whale_description:
            primary_reasons.insert(0, f"🐋 {whale_description}")
        
        if pullback_detected:
            primary_reasons.insert(0, f"🔄 Pullback detected: {pullback_percent:.1f}%")
        
        if dome_detected:
            primary_reasons.insert(0, f"🏛️ Dome pattern: {dome_type} (height: {dome_height:.1f}%)")
        
        # Determine signal type
        signal_type = "STRONG_BUY" if direction == "BUY" else "STRONG_SELL"
        
        # Get risk level
        risk_level = self._get_risk_level(multi_tf_regime, stop_percentage)
        
        # Get primary style
        primary_style = SignalStyle.INTRADAY
        
        # Create signal
        from bot_main_part3 import EnhancedHighConfidenceSignal
        
        signal = EnhancedHighConfidenceSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal_type,
            confidence=85.0,
            current_price=current_price,
            best_bid=entry_data.get('best_bid', current_price * 0.999),
            best_ask=entry_data.get('best_ask', current_price * 1.001),
            spread=entry_data.get('best_ask', current_price * 1.001) - entry_data.get('best_bid', current_price * 0.999),
            spread_percentage=entry_data.get('spread_percent', 0.2),
            suggested_order_type=OrderType.LIMIT_BUY if direction == "BUY" else OrderType.LIMIT_SELL,
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
            funding_rate=0.0,
            funding_sentiment="NEUTRAL",
            open_interest=None,
            oi_change_1h=None,
            support_levels=ob.support_levels if hasattr(ob, 'support_levels') else [],
            resistance_levels=ob.resistance_levels if hasattr(ob, 'resistance_levels') else [],
            nearest_support=ob.support_levels[0] if ob.support_levels else current_price * 0.98,
            nearest_resistance=ob.resistance_levels[0] if ob.resistance_levels else current_price * 1.02,
            primary_reasons=primary_reasons,
            secondary_reasons=[],
            aligned_styles=[],
            style_scores={},
            recommendation="",
            risk_level=risk_level,
            time_horizon="INTRADAY",
            market_regime=None,
            multi_tf_regime=multi_tf_regime,
            smart_money=None,
            market_profile=None,
            intermarket=None,
            onchain=None,
            sentiment=None,
            divergence=None,
            patterns=None,
            liquidity=None,
            timeframe_confluence=None,
            enhanced_tech=tech,
            overall_accuracy_score=85.0,
            risk_adjusted_confidence=85.0,
            expected_move=abs(tp1 - entry_price) / entry_price * 100,
            optimal_position_size=1.0,
            tech_score=tech_score,
            flow_score=flow_score,
            backtest_result=None,
            market_context=None,
            risk_reward=risk_reward,
            confirmations=None,
            bot_win_rate=0.0,
            signals_last_100=0,
            win_rate_last_100=0.0,
            entry_timeframe_3m_signal=None,
            entry_timeframe_5m_signal=None,
            tier=tier,
            tier_confidence=direction_confidence,
            smart_scan_score=0.0,
            adaptive_cooldown_minutes=15,
            entry_bid_level=entry_data.get('best_bid'),
            entry_ask_level=entry_data.get('best_ask'),
            entry_mid_price=entry_data.get('mid'),
            order_book_imbalance=entry_data.get('imbalance', 0.0),
            ultra_short_regime_aligned="BULL" in multi_tf_regime.ultra_short_regime if direction == "BUY" else "BEAR" in multi_tf_regime.ultra_short_regime,
            short_regime_aligned="BULL" in multi_tf_regime.short_regime if direction == "BUY" else "BEAR" in multi_tf_regime.short_regime,
            medium_regime_aligned="BULL" in multi_tf_regime.medium_regime if direction == "BUY" else "BEAR" in multi_tf_regime.medium_regime,
            long_regime_aligned="BULL" in multi_tf_regime.long_regime if direction == "BUY" else "BEAR" in multi_tf_regime.long_regime,
            scalping_entry=entry_data.get('scalping', {}).get('price') if entry_data else None,
            intraday_entry=entry_data.get('intraday', {}).get('price') if entry_data else None,
            swing_entry=entry_data.get('swing', {}).get('price') if entry_data else None,
            position_entry=entry_data.get('position', {}).get('price') if entry_data else None,
            scalping_tp1=None,
            scalping_tp2=None,
            scalping_tp3=None,
            intraday_tp1=None,
            intraday_tp2=None,
            intraday_tp3=None,
            swing_tp1=None,
            swing_tp2=None,
            swing_tp3=None,
            position_tp1=None,
            position_tp2=None,
            position_tp3=None,
            primary_style=primary_style,
            secondary_styles=[],
            style_confidence={},
            smart_money_display=None,
            atr_stop_loss=None,
            atr_value=atr_value,
            atr_multiplier=self.config.ATR_MULTIPLIER,
            volume_profile_entry=None,
            volume_poc_price=entry_data.get('poc_price', current_price) if entry_data else current_price,
            volume_value_area_low=entry_data.get('value_area_low', current_price * 0.98) if entry_data else current_price * 0.98,
            volume_value_area_high=entry_data.get('value_area_high', current_price * 1.02) if entry_data else current_price * 1.02,
            liquidity_grab=None,
            liquidity_grab_detected=False,
            liquidity_grab_type="NONE",
            liquidity_grab_strength=0.0,
            trend_filter_200ema=None,
            ema_200=0.0,
            price_vs_ema_200="UNKNOWN",
            ema_200_trend="UNKNOWN",
            trend_filter_passed=True,
            ai_confidence=85.0,
            ai_confidence_prediction=0.0,
            ai_confidence_in_prediction=0.0,
            ai_model_used=False,
            alert_level=None,
            is_confirmed=True,
            calculated_imbalance=entry_data.get('imbalance', 0.0),
            volume_ratio_24h=1.0,
            avg_volume_24h=volume_24h,
            ultimate_direction_confidence=direction_confidence,
            ultimate_analysis=ultimate_result,
            whale_activity=whale_activity,
            whale_signal=whale_signal,
            whale_confidence=whale_confidence,
            whale_description=whale_description,
            key_zones=key_zones or [],
            active_key_zone=active_key_zone,
            key_zone_entry=key_zone_entry,
            key_zone_confidence=key_zone_confidence,
            pullback_detected=pullback_detected,
            pullback_percent=pullback_percent,
            pullback_entry_price=pullback_entry_price,
            dome_detected=dome_detected,
            dome_type=dome_type,
            dome_height=dome_height,
            tp_levels={'tp1': tp1, 'tp2': tp2, 'tp3': tp3},
            tp_description=f"TP1: {abs(tp1-entry_price)/entry_price*100:.1f}%, TP2: {abs(tp2-entry_price)/entry_price*100:.1f}%, TP3: {abs(tp3-entry_price)/entry_price*100:.1f}%",
            ml_predictions=None
        )
        
        return self._validate_signal(signal, direction, current_price)
    
    def _calculate_leverage(self, multi_tf: MultiTimeframeRegime, key_zone_entry: bool = False, **kwargs) -> int:
        """Calculate recommended leverage with key zone boost"""
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
        
        # Key zone boost
        if key_zone_entry:
            leverage = int(leverage * 1.15)
        
        return max(2, min(25, leverage))
    
    def _check_regime_alignment(self, direction: str, multi_tf: MultiTimeframeRegime) -> bool:
        """Check if regimes are aligned with direction"""
        if direction == "BUY":
            bullish_count = 0
            if "BULL" in multi_tf.ultra_short_regime:
                bullish_count += 1
            if "BULL" in multi_tf.short_regime:
                bullish_count += 2
            if "BULL" in multi_tf.medium_regime:
                bullish_count += 2
            if "BULL" in multi_tf.long_regime:
                bullish_count += 1
            return bullish_count >= 3
        else:
            bearish_count = 0
            if "BEAR" in multi_tf.ultra_short_regime:
                bearish_count += 1
            if "BEAR" in multi_tf.short_regime:
                bearish_count += 2
            if "BEAR" in multi_tf.medium_regime:
                bearish_count += 2
            if "BEAR" in multi_tf.long_regime:
                bearish_count += 1
            return bearish_count >= 3
    
    def _check_order_book_entry(self, ob: Any, direction: str) -> bool:
        """Check if order book conditions are good for entry"""
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
                
        except (TypeError, ValueError):
            return True
    
    def _get_risk_level(self, multi_tf: MultiTimeframeRegime, stop_percentage: float) -> str:
        """Get risk level based on volatility and stop loss"""
        if stop_percentage < 1.0:
            risk_level = "LOW"
        elif stop_percentage < 2.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        if hasattr(multi_tf, 'ultra_short_volatility'):
            if multi_tf.ultra_short_volatility == "HIGH":
                if risk_level == "LOW":
                    risk_level = "MEDIUM"
                elif risk_level == "MEDIUM":
                    risk_level = "HIGH"
        
        return risk_level
    
    def _validate_signal(self, signal: 'EnhancedHighConfidenceSignal', 
                         direction: str, current_price: float) -> 'EnhancedHighConfidenceSignal':
        """Validate and adjust signal values"""
        try:
            # Check entry price
            if abs(signal.entry_price - current_price) / current_price > 0.05:
                logger.warning(f"Entry price {signal.entry_price:.2f} too far from current {current_price:.2f}")
                signal.entry_price = current_price
                signal.entry_range_low = current_price * 0.998
                signal.entry_range_high = current_price * 1.002
                signal.optimal_entry_timeframe = "Corrected: Using current price"
            
            # Check stop loss
            if abs(signal.stop_loss - signal.entry_price) < 1e-8:
                logger.error(f"Stop loss equals entry price for {signal.symbol}")
                if direction == "BUY":
                    signal.stop_loss = signal.entry_price * 0.99
                    signal.stop_loss_percentage = 1.0
                else:
                    signal.stop_loss = signal.entry_price * 1.01
                    signal.stop_loss_percentage = 1.0
            
            # Check TP levels
            if direction == "BUY" and signal.take_profit_1 <= signal.entry_price:
                risk = abs(signal.entry_price - signal.stop_loss)
                signal.take_profit_1 = signal.entry_price + (risk * 1.5)
                signal.take_profit_2 = signal.entry_price + (risk * 2.5)
                signal.take_profit_3 = signal.entry_price + (risk * 4.0)
            
            if direction == "SELL" and signal.take_profit_1 >= signal.entry_price:
                risk = abs(signal.entry_price - signal.stop_loss)
                signal.take_profit_1 = signal.entry_price - (risk * 1.5)
                signal.take_profit_2 = signal.entry_price - (risk * 2.5)
                signal.take_profit_3 = signal.entry_price - (risk * 4.0)
            
        except Exception as e:
            logger.error(f"Signal validation error: {e}")
        
        return signal


# ==============================================================================
# TIER 2 GENERATOR (BALANCED)
# ==============================================================================
class Tier2Generator(Tier1Generator):
    """Tier 2 Balanced signal generator"""
    
    def __init__(self, parent: 'TieredSignalGenerator'):
        super().__init__(parent)
        self.recent_signals = deque(maxlen=50)
        self.config = parent.hybrid_config
    
    def generate(self, symbol: str, base_analysis: Tuple, 
                 multi_tf_regime: 'MultiTimeframeRegime') -> Optional['EnhancedHighConfidenceSignal']:
        """Generate Tier 2 signal"""
        try:
            # Check recent signals
            if self._has_recent_signal(symbol, 30):
                logger.debug(f"Tier2 {symbol}: Recent signal within 30 minutes")
                return None
            
            current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
            
            # Calculate scores
            tech_score = self.parent.calculate_technical_score(tech)
            flow_score = self.parent.calculate_order_flow_score(ob, mt, cf)
            
            # Get thresholds
            tech_threshold, flow_threshold = self._get_dynamic_thresholds(multi_tf_regime)
            
            if abs(tech_score) < tech_threshold or abs(flow_score) < flow_threshold:
                logger.debug(f"Tier2 {symbol}: Tech score {tech_score} < {tech_threshold} or Flow score {flow_score} < {flow_threshold}")
                return None
            
            # Determine direction
            combined_score = tech_score * 0.45 + flow_score * 0.55
            
            if combined_score > 15:
                direction = "BUY"
            elif combined_score < -15:
                direction = "SELL"
            else:
                logger.debug(f"Tier2 {symbol}: Combined score {combined_score} not strong enough")
                return None
            
            # Check basic alignment
            if not self._check_basic_regime_alignment(direction, multi_tf_regime):
                logger.debug(f"Tier2 {symbol}: Basic regime alignment failed")
                return None
            
            # Check safety
            if not self._safety_checks(tech, ob, multi_tf_regime):
                logger.debug(f"Tier2 {symbol}: Safety checks failed")
                return None
            
            # Get key zones
            key_zones = self.keyzone_detector.detect_zones(df_1h, current_price)
            active_key_zone = self.keyzone_detector.get_best_entry_zone(direction, current_price)
            key_zone_entry = active_key_zone is not None
            key_zone_confidence = active_key_zone.zone_strength if active_key_zone else 0
            
            # Build signal
            signal = self._build_signal(
                symbol, base_analysis, tech_score, flow_score, direction,
                SignalTier.TIER_2_BALANCED, multi_tf_regime, None, 70,
                None, False, 0, None, key_zones, active_key_zone, 
                key_zone_entry, key_zone_confidence
            )
            
            signal.adaptive_cooldown_minutes = 10
            self.recent_signals.append((symbol, time.time()))
            
            return signal
            
        except Exception as e:
            logger.error(f"Tier2 generation error for {symbol}: {e}")
            return None
    
    def _has_recent_signal(self, symbol: str, minutes: int) -> bool:
        """Check if there's a recent signal for this symbol"""
        current_time = time.time()
        for sym, ts in self.recent_signals:
            if sym == symbol and (current_time - ts) < minutes * 60:
                return True
        return False
    
    def _get_dynamic_thresholds(self, multi_tf: MultiTimeframeRegime) -> Tuple[float, float]:
        """Get dynamic thresholds based on volatility"""
        base_tech = self.config.TIER_2_TECH_THRESHOLD
        base_flow = self.config.TIER_2_FLOW_THRESHOLD
        
        if hasattr(multi_tf, 'ultra_short_volatility'):
            if multi_tf.ultra_short_volatility == "HIGH":
                return base_tech * 1.2, base_flow * 1.2
            elif multi_tf.ultra_short_volatility == "LOW":
                return base_tech * 0.8, base_flow * 0.8
        
        return base_tech, base_flow
    
    def _check_basic_regime_alignment(self, direction: str, multi_tf: MultiTimeframeRegime) -> bool:
        """Check basic regime alignment"""
        if direction == "BUY":
            return "BULL" in multi_tf.ultra_short_regime or "BULL" in multi_tf.short_regime
        else:
            return "BEAR" in multi_tf.ultra_short_regime or "BEAR" in multi_tf.short_regime
    
    def _safety_checks(self, tech: Any, ob: Any, multi_tf: MultiTimeframeRegime) -> bool:
        """Perform safety checks"""
        # Check RSI
        if hasattr(tech, 'rsi'):
            try:
                rsi = float(tech.rsi)
                if rsi > 85 or rsi < 15:
                    return False
            except (TypeError, ValueError):
                pass
        
        # Check spread
        if ob and hasattr(ob, 'spread_percentage'):
            try:
                spread = float(ob.spread_percentage)
                if spread > 0.1:
                    return False
            except (TypeError, ValueError):
                pass
        
        # Check volatility
        if hasattr(multi_tf, 'ultra_short_volatility'):
            if multi_tf.ultra_short_volatility == "HIGH":
                if hasattr(multi_tf, 'ultra_short_strength'):
                    try:
                        strength = float(multi_tf.ultra_short_strength)
                        if strength > 80:
                            return False
                    except (TypeError, ValueError):
                        pass
        
        return True


# ==============================================================================
# TIER 3 GENERATOR (AGGRESSIVE)
# ==============================================================================
class Tier3Generator(Tier2Generator):
    """Tier 3 Aggressive signal generator"""
    
    def __init__(self, parent: 'TieredSignalGenerator'):
        super().__init__(parent)
        self.signal_count = defaultdict(int)
        self.config = parent.hybrid_config
    
    def generate(self, symbol: str, base_analysis: Tuple, 
                 multi_tf_regime: 'MultiTimeframeRegime') -> Optional['EnhancedHighConfidenceSignal']:
        """Generate Tier 3 signal"""
        try:
            # Check signal count
            if self.signal_count[symbol] >= 4:
                logger.debug(f"Tier3 {symbol}: Already generated 4 signals")
                return None
            
            current_price, tech, ob, mt, cf, ticker, df_1h = base_analysis
            
            # Calculate scores
            tech_score = self.parent.calculate_technical_score(tech)
            flow_score = self.parent.calculate_order_flow_score(ob, mt, cf)
            
            if abs(tech_score) < self.config.TIER_3_TECH_THRESHOLD:
                logger.debug(f"Tier3 {symbol}: Tech score {tech_score} too low")
                return None
            
            if abs(flow_score) < self.config.TIER_3_FLOW_THRESHOLD:
                logger.debug(f"Tier3 {symbol}: Flow score {flow_score} too low")
                return None
            
            # Determine direction
            combined_score = tech_score * 0.5 + flow_score * 0.5
            
            if combined_score > 10:
                direction = "BUY"
            elif combined_score < -10:
                direction = "SELL"
            else:
                logger.debug(f"Tier3 {symbol}: Combined score {combined_score} not strong enough")
                return None
            
            # Basic safety check
            if not self._basic_safety_check(tech, ob):
                logger.debug(f"Tier3 {symbol}: Basic safety check failed")
                return None
            
            # Increment signal count
            self.signal_count[symbol] += 1
            
            # Build signal
            signal = self._build_signal(
                symbol, base_analysis, tech_score, flow_score, direction,
                SignalTier.TIER_3_AGGRESSIVE, multi_tf_regime, None, 60
            )
            
            signal.adaptive_cooldown_minutes = 5
            
            return signal
            
        except Exception as e:
            logger.error(f"Tier3 generation error for {symbol}: {e}")
            return None
    
    def _basic_safety_check(self, tech: Any, ob: Any) -> bool:
        """Perform basic safety checks"""
        # Check RSI
        if hasattr(tech, 'rsi'):
            try:
                rsi = float(tech.rsi)
                if rsi > 90 or rsi < 10:
                    return False
            except (TypeError, ValueError):
                pass
        
        # Check spread
        if ob and hasattr(ob, 'spread_percentage'):
            try:
                spread = float(ob.spread_percentage)
                if spread > 0.2:
                    return False
            except (TypeError, ValueError):
                pass
        
        return True
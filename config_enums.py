#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ULTIMATE HYBRID CRYPTO TRADING BOT - ENTERPRISE EDITION V1.0.0
================================================================================
Developer: Nhen Bol
Version: 1.0.0
================================================================================
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
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import copy
import pickle
import csv

# Cryptography imports
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ cryptography not installed, using fallback encryption")

warnings.filterwarnings('ignore')

# ==============================================================================
# FIX UNICODE ENCODING FOR ANDROID/PYDROID
# ==============================================================================
if sys.platform == 'win32' or 'android' in sys.platform or 'linux' in sys.platform:
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# ==============================================================================
# IMPORTS WITH FALLBACK
# ==============================================================================
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
    
    XGBOOST_AVAILABLE = False
    print("ℹ️ Running in Pydroid-compatible mode (XGBoost disabled)")
    
except ImportError as e:
    print(f"⚠️ Please install required modules: {e}")
    print("Run: pip install requests pandas numpy urllib3 scikit-learn joblib cryptography")
    sys.exit(1)

# ==============================================================================
# CONNECTION TEST
# ==============================================================================
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

# ==============================================================================
# LOGGING SETUP
# ==============================================================================
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
logger = logging.getLogger('ULTIMATE_V12')

# ==============================================================================
# ENUMS - ទាំងអស់ពេញលេញ
# ==============================================================================

class Language(Enum):
    """ភាសាដែលគាំទ្រ"""
    ENGLISH = "en"
    # អាចបន្ថែមភាសាផ្សេងទៀតនៅពេលក្រោយ
    # KHMER = "km"
    # CHINESE = "zh"
    # VIETNAMESE = "vi"
    # THAI = "th"


class TradingStyle(Enum):
    """រចនាប័ទ្មការជួញដូរ"""
    SCALPING = "SCALPING"      # រយៈពេលខ្លីបំផុត (នាទី)
    INTRADAY = "INTRADAY"      # រយៈពេលខ្លី (ម៉ោង)
    SWING = "SWING"            # រយៈពេលមធ្យម (ថ្ងៃ)
    POSITION = "POSITION"      # រយៈពេលវែង (សប្តាហ៍-ខែ)


class SignalStyle(Enum):
    """រចនាប័ទ្មសញ្ញា"""
    SCALPING = "SCALPING"
    INTRADAY = "INTRADAY"
    SWING = "SWING"
    POSITION = "POSITION"
    HYBRID = "HYBRID"          # លាយឡំគ្នា


class OrderType(Enum):
    """ប្រភេទនៃការបញ្ជាទិញ"""
    # Limit Orders
    LIMIT_BUY = "LIMIT BUY"
    LIMIT_SELL = "LIMIT SELL"
    
    # Market Orders
    MARKET_BUY = "MARKET BUY"
    MARKET_SELL = "MARKET SELL"
    
    # Advanced Orders
    OCO = "OCO"                          # One-Cancels-Other
    TRAILING_STOP = "TRAILING STOP"      # Trailing Stop Loss
    ICEBERG = "ICEBERG"                   # Iceberg Order
    TWAP = "TWAP"                         # Time-Weighted Average Price
    VWAP = "VWAP"                         # Volume-Weighted Average Price
    
    # Stop Orders
    STOP_LOSS = "STOP LOSS"
    TAKE_PROFIT = "TAKE PROFIT"
    STOP_LOSS_LIMIT = "STOP LOSS LIMIT"
    TAKE_PROFIT_LIMIT = "TAKE PROFIT LIMIT"


class AlertLevel(Enum):
    """កម្រិតនៃការជូនដំណឹង"""
    EMERGENCY = "🔴 EMERGENCY"     # បន្ទាន់បំផុត (90-100%)
    HIGH = "🟡 HIGH"               # ខ្ពស់ (80-89%)
    MEDIUM = "🔵 MEDIUM"           # មធ្យម (70-79%)
    LOW = "⚪ LOW"                  # ទាប (ក្រោម 70%)


class SignalTier(Enum):
    """កម្រិតនៃសញ្ញា"""
    TIER_1_ULTRA_SAFE = "ULTRA_SAFE"      # កម្រិតទី១ - សុវត្ថិភាពខ្ពស់បំផុត
    TIER_2_BALANCED = "BALANCED"           # កម្រិតទី២ - លំនឹង
    TIER_3_AGGRESSIVE = "AGGRESSIVE"       # កម្រិតទី៣ - ប្រថុយប្រថាន


class TimeframeType(Enum):
    """ប្រភេទនៃពេលវេលា"""
    ULTRA_SHORT = "ULTRA_SHORT"    # 3m, 5m, 15m
    SHORT = "SHORT"                 # 30m, 1h, 2h
    MEDIUM = "MEDIUM"               # 4h, 6h, 8h, 12h
    LONG = "LONG"                    # 1d, 3d, 1w, 1M


class SmartMoneyConcept(Enum):
    """គោលគំនិត Smart Money"""
    ORDER_BLOCK = "📦 Order Block"                    # ប្លុកបញ្ជាទិញ
    LIQUIDITY_SWEEP = "🌊 Liquidity Sweep"            # ការបោសសំអាតសាច់ប្រាក់
    FVG = "🕳️ Fair Value Gap"                         # គម្លាតតម្លៃសមរម្យ
    BREAKER = "🔨 Breaker Block"                      # ប្លុកបំបែក
    MITIGATION = "✅ Mitigation"                       # ការកាត់បន្ថយ
    INSTITUTIONAL_DIVERGENCE = "📉 Institutional Divergence"  # ភាពខុសគ្នារបស់ស្ថាប័ន
    LIQUIDITY_GRAB = "🎣 Liquidity Grab"               # ការចាប់យកសាច់ប្រាក់
    NONE = "❌ None"                                    # គ្មាន


class MLModelType(Enum):
    """ប្រភេទម៉ូដែល Machine Learning"""
    RANDOM_FOREST = "🌲 Random Forest"                 # Random Forest
    GRADIENT_BOOSTING = "📈 Gradient Boosting"         # Gradient Boosting
    LSTM = "🧠 LSTM"                                    # Long Short-Term Memory
    ENSEMBLE = "🤝 Ensemble"                            # Ensemble Model
    XGBOOST = "⚡ XGBoost"                               # XGBoost (ប្រសិនបើមាន)
    NEURAL_NETWORK = "🧬 Neural Network"                # Neural Network


class MarketRegimeType(Enum):
    """ប្រភេទនៃរបបទីផ្សារ"""
    # Bull Market
    STRONG_BULL = "🐂 STRONG BULL"        # កើនខ្លាំង
    TRENDING_BULL = "📈 TRENDING BULL"    # កើនតាមនិន្នាការ
    WEAK_BULL = "📊 WEAK BULL"            # កើនខ្សោយ
    
    # Bear Market
    STRONG_BEAR = "🐻 STRONG BEAR"        # ធ្លាក់ខ្លាំង
    TRENDING_BEAR = "📉 TRENDING BEAR"    # ធ្លាក់តាមនិន្នាការ
    WEAK_BEAR = "📊 WEAK BEAR"            # ធ្លាក់ខ្សោយ
    
    # Sideways
    RANGING = "📊 RANGING"                 # ចំហៀង
    VOLATILE = "🌪️ VOLATILE"               # ប្រែប្រួលខ្ពស់
    CHOPPY = "🔪 CHOPPY"                    # កាត់ផ្តាច់


class OrderRecommendation(Enum):
    """អនុសាសន៍សម្រាប់ការបញ្ជាទិញ"""
    # Market Orders
    AGGRESSIVE_MARKET = "🔥 AGGRESSIVE MARKET"        # ប្រើទីផ្សារភ្លាមៗ
    SCALPER_MARKET = "⚡ SCALPER MARKET"               # សម្រាប់ scalping
    
    # Limit Orders
    LIMIT_BUY_DIP = "📉 LIMIT BUY DIP"                 # រង់ចាំទិញពេលធ្លាក់
    LIMIT_SELL_RALLY = "📈 LIMIT SELL RALLY"           # រង់ចាំលក់ពេលឡើង
    POSITION_LIMIT = "🎯 POSITION LIMIT"               # សម្រាប់ position trading
    
    # Advanced Orders
    ICEBERG_RECOMMENDED = "🧊 ICEBERG RECOMMENDED"     # ប្រើ Iceberg Order
    TWAP_RECOMMENDED = "⏱️ TWAP RECOMMENDED"           # ប្រើ TWAP Order
    OCO_RECOMMENDED = "🔄 OCO RECOMMENDED"             # ប្រើ OCO Order
    TRAILING_STOP_RECOMMENDED = "🎯 TRAILING STOP RECOMMENDED"  # ប្រើ Trailing Stop
    
    # Wait
    WAIT_CONFIRMATION = "⏳ WAIT CONFIRMATION"         # រង់ចាំការបញ្ជាក់


class IndicatorSignal(Enum):
    """សញ្ញាពីសូចនាករបច្ចេកទេស"""
    # RSI Signals
    RSI_OVERSOLD = "RSI OVERSOLD"          # លក់ហួស (ក្រោម 30)
    RSI_OVERBOUGHT = "RSI OVERBOUGHT"      # ទិញហួស (លើស 70)
    RSI_NEUTRAL = "RSI NEUTRAL"            # អព្យាក្រឹត (30-70)
    
    # MACD Signals
    MACD_BULLISH_CROSS = "MACD BULLISH CROSS"      # កាត់ឡើង
    MACD_BEARISH_CROSS = "MACD BEARISH CROSS"      # កាត់ចុះ
    MACD_BULLISH_DIVERGENCE = "MACD BULLISH DIVERGENCE"  # ភាពខុសគ្នាឡើង
    MACD_BEARISH_DIVERGENCE = "MACD BEARISH DIVERGENCE"   # ភាពខុសគ្នាចុះ
    
    # EMA Signals
    EMA_GOLDEN_CROSS = "EMA GOLDEN CROSS"        # កាត់មាស (50 កាត់ 200)
    EMA_DEATH_CROSS = "EMA DEATH CROSS"          # កាត់មរណៈ (50 កាត់ 200)
    EMA_BULLISH_ALIGNMENT = "EMA BULLISH ALIGNMENT"    # តម្រឹមឡើង
    EMA_BEARISH_ALIGNMENT = "EMA BEARISH ALIGNMENT"    # តម្រឹមចុះ
    
    # Bollinger Bands
    BB_SQUEEZE = "BB SQUEEZE"                    # បង្រួម
    BB_EXPANSION = "BB EXPANSION"                 # ពង្រីក
    BB_BOUNCE_LOWER = "BB BOUNCE LOWER"           # លោតពីក្រោម
    BB_BOUNCE_UPPER = "BB BOUNCE UPPER"           # លោតពីលើ


class RiskLevel(Enum):
    """កម្រិតហានិភ័យ"""
    VERY_LOW = "🟢 VERY LOW"        # ទាបខ្លាំង (ក្រោម 0.5%)
    LOW = "🟢 LOW"                  # ទាប (0.5-1%)
    MEDIUM = "🟡 MEDIUM"            # មធ្យម (1-2%)
    HIGH = "🟠 HIGH"                # ខ្ពស់ (2-3%)
    VERY_HIGH = "🔴 VERY HIGH"      # ខ្ពស់ខ្លាំង (លើស 3%)


class TrendDirection(Enum):
    """ទិសដៅនិន្នាការ"""
    STRONG_UPTREND = "🚀 STRONG UPTREND"        # ឡើងខ្លាំង
    UPTREND = "📈 UPTREND"                       # ឡើង
    WEAK_UPTREND = "↗️ WEAK UPTREND"             # ឡើងខ្សោយ
    SIDEWAYS = "⬅️➡️ SIDEWAYS"                    # ចំហៀង
    WEAK_DOWNTREND = "↘️ WEAK DOWNTREND"         # ចុះខ្សោយ
    DOWNTREND = "📉 DOWNTREND"                    # ចុះ
    STRONG_DOWNTREND = "🔻 STRONG DOWNTREND"     # ចុះខ្លាំង


class VolatilityLevel(Enum):
    """កម្រិតនៃការប្រែប្រួល"""
    VERY_LOW = "😴 VERY LOW"        # ទាបខ្លាំង
    LOW = "😌 LOW"                  # ទាប
    MEDIUM = "😐 MEDIUM"            # មធ្យម
    HIGH = "😰 HIGH"                # ខ្ពស់
    VERY_HIGH = "😱 VERY HIGH"      # ខ្ពស់ខ្លាំង
    EXTREME = "🤯 EXTREME"          # ខ្លាំងក្លា


class PositionSide(Enum):
    """ផ្នែកនៃមុខងារ"""
    LONG = "LONG"           # ទិញ (ឡើង)
    SHORT = "SHORT"         # លក់ (ចុះ)
    BOTH = "BOTH"           # ទាំងពីរ
    NEUTRAL = "NEUTRAL"     # អព្យាក្រឹត


class OrderStatus(Enum):
    """ស្ថានភាពនៃការបញ្ជាទិញ"""
    NEW = "NEW"                     # ថ្មី
    PARTIALLY_FILLED = "PARTIALLY FILLED"  # បំពេញខ្លះ
    FILLED = "FILLED"               # បំពេញទាំងស្រុង
    CANCELED = "CANCELED"           # បោះបង់
    PENDING_CANCEL = "PENDING CANCEL"  # កំពុងបោះបង់
    REJECTED = "REJECTED"           # បដិសេធ
    EXPIRED = "EXPIRED"             # ផុតកំណត់


class TimeInForce(Enum):
    """រយៈពេលនៃការបញ្ជាទិញ"""
    GTC = "GTC"      # Good Till Cancel (ល្អរហូតដល់បោះបង់)
    IOC = "IOC"      # Immediate or Cancel (ភ្លាមៗ ឬបោះបង់)
    FOK = "FOK"      # Fill or Kill (បំពេញ ឬបោះបង់)
    GTX = "GTX"      # Good Till Crossing (ល្អរហូតដល់ឆ្លងកាត់)


class LogLevel(Enum):
    """កម្រិតកំណត់ហេតុ"""
    DEBUG = "DEBUG"          # បំបាត់កំហុស
    INFO = "INFO"            # ព័ត៌មាន
    WARNING = "WARNING"      # ការព្រមាន
    ERROR = "ERROR"          # កំហុស
    CRITICAL = "CRITICAL"    # ធ្ងន់ធ្ងរ


class ConnectionStatus(Enum):
    """ស្ថានភាពការតភ្ជាប់"""
    CONNECTED = "✅ CONNECTED"          # ភ្ជាប់រួច
    DISCONNECTED = "❌ DISCONNECTED"    # ផ្តាច់
    CONNECTING = "⏳ CONNECTING"        # កំពុងភ្ជាប់
    RECONNECTING = "🔄 RECONNECTING"    # កំពុងភ្ជាប់ឡើងវិញ
    ERROR = "⚠️ ERROR"                   # កំហុស


class WebSocketEvent(Enum):
    """ព្រឹត្តិការណ៍ WebSocket"""
    OPEN = "OPEN"                # បើក
    MESSAGE = "MESSAGE"          # សារ
    ERROR = "ERROR"              # កំហុស
    CLOSE = "CLOSE"              # បិទ
    PING = "PING"                # Ping
    PONG = "PONG"                # Pong


class DatabaseOperation(Enum):
    """ប្រតិបត្តិការមូលដ្ឋានទិន្នន័យ"""
    INSERT = "INSERT"        # បញ្ចូល
    UPDATE = "UPDATE"        # ធ្វើបច្ចុប្បន្នភាព
    DELETE = "DELETE"        # លុប
    SELECT = "SELECT"        # ជ្រើសរើស
    UPSERT = "UPSERT"        # បញ្ចូល ឬធ្វើបច្ចុប្បន្នភាព


class BacktestPeriod(Enum):
    """រយៈពេល Backtest"""
    DAY_1 = "1d"              # ១ ថ្ងៃ
    WEEK_1 = "1w"             # ១ សប្តាហ៍
    MONTH_1 = "1M"            # ១ ខែ
    MONTH_3 = "3M"            # ៣ ខែ
    MONTH_6 = "6M"            # ៦ ខែ
    YEAR_1 = "1Y"             # ១ ឆ្នាំ
    YEAR_2 = "2Y"             # ២ ឆ្នាំ
    YEAR_5 = "5Y"             # ៥ ឆ្នាំ


class ChartPattern(Enum):
    """លំនាំតារាង"""
    # Reversal Patterns
    HEAD_AND_SHOULDERS = "👤 HEAD AND SHOULDERS"        # ក្បាលនិងស្មា
    INVERSE_HEAD_AND_SHOULDERS = "🔄 INVERSE HEAD AND SHOULDERS"
    DOUBLE_TOP = "🔝 DOUBLE TOP"                         # កំពូលទ្វេ
    DOUBLE_BOTTOM = "🔻 DOUBLE BOTTOM"                   # បាតទ្វេ
    TRIPLE_TOP = "🔝🔝 TRIPLE TOP"                        # កំពូលបី
    TRIPLE_BOTTOM = "🔻🔻 TRIPLE BOTTOM"                  # បាតបី
    ROUNDING_TOP = "🌊 ROUNDING TOP"                     # កំពូលមូល
    ROUNDING_BOTTOM = "🌊 ROUNDING BOTTOM"               # បាតមូល
    V_TOP = "V🔝 V TOP"                                   # កំពូលរាងV
    V_BOTTOM = "V🔻 V BOTTOM"                             # បាតរាងV
    
    # Continuation Patterns
    FLAG = "🚩 FLAG"                                      # ទង់
    PENNANT = "⛳ PENNANT"                                 # ទង់ត្រីកោណ
    WEDGE = "📐 WEDGE"                                    # ក្រូចឆ្មារ
    SYMMETRICAL_TRIANGLE = "🔺 SYMMETRICAL TRIANGLE"     # ត្រីកោណស៊ីមេទ្រី
    ASCENDING_TRIANGLE = "⬆️ ASCENDING TRIANGLE"         # ត្រីកោណឡើង
    DESCENDING_TRIANGLE = "⬇️ DESCENDING TRIANGLE"       # ត្រីកោណចុះ
    RECTANGLE = "📏 RECTANGLE"                             # ចតុកោណ
    CUP_AND_HANDLE = "☕ CUP AND HANDLE"                   # ពែងនិងដៃ


class CandlestickPattern(Enum):
    """លំនាំទៀន"""
    # Bullish Patterns
    HAMMER = "🔨 HAMMER"                                   # ញញួរ
    INVERTED_HAMMER = "🔨 INVERTED HAMMER"                 # ញញួរដាក់បញ្ច្រាស
    BULLISH_ENGULFING = "🟢 BULLISH ENGULFING"             # ព័ទ្ធជុំឡើង
    PIERCING_LINE = "📌 PIERCING LINE"                     # បន្ទាត់ទម្លុះ
    MORNING_STAR = "⭐ MORNING STAR"                       # ផ្កាយព្រឹក
    THREE_WHITE_SOLDIERS = "⚪⚪⚪ THREE WHITE SOLDIERS"    # ទាហានសបី
    BULLISH_HARAMI = "🟢 BULLISH HARAMI"                   # ហារ៉ាមីឡើង
    
    # Bearish Patterns
    SHOOTING_STAR = "🌠 SHOOTING STAR"                     # ផ្កាយបាញ់
    HANGING_MAN = "💀 HANGING MAN"                          # មនុស្សព្យួរ
    BEARISH_ENGULFING = "🔴 BEARISH ENGULFING"             # ព័ទ្ធជុំចុះ
    EVENING_STAR = "🌆 EVENING STAR"                       # ផ្កាយល្ងាច
    THREE_BLACK_CROWS = "⚫⚫⚫ THREE BLACK CROWS"          # ក្អែកខ្មៅបី
    DARK_CLOUD_COVER = "☁️ DARK CLOUD COVER"               # ពពកខ្មៅគ្របដណ្តប់
    BEARISH_HARAMI = "🔴 BEARISH HARAMI"                   # ហារ៉ាមីចុះ
    
    # Indecision Patterns
    DOJI = "➕ DOJI"                                         # ដូជី
    SPINNING_TOP = "🎯 SPINNING TOP"                        # កំពូលវិល
    MARUBOZU = "⬛ MARUBOZU"                                # ម៉ារូបូហ្ស៊ូ


class FibonacciLevel(Enum):
    """កម្រិត Fibonacci"""
    LEVEL_0 = "0%"
    LEVEL_236 = "23.6%"
    LEVEL_382 = "38.2%"
    LEVEL_5 = "50%"
    LEVEL_618 = "61.8%"
    LEVEL_786 = "78.6%"
    LEVEL_1 = "100%"
    LEVEL_1272 = "127.2%"
    LEVEL_1618 = "161.8%"
    LEVEL_2618 = "261.8%"
    LEVEL_4236 = "423.6%"


class MarketSession(Enum):
    """វគ្គទីផ្សារ"""
    ASIAN = "🇯🇵 ASIAN"           # វគ្គអាស៊ី
    LONDON = "🇬🇧 LONDON"         # វគ្គឡុងដ៍
    NEW_YORK = "🇺🇸 NEW YORK"     # វគ្គញូវយ៉ក
    SYDNEY = "🇦🇺 SYDNEY"         # វគ្គស៊ីដនី
    FRANKFURT = "🇩🇪 FRANKFURT"   # វគ្គហ្វ្រែងហ្វួត


class DayOfWeek(Enum):
    """ថ្ងៃនៃសប្តាហ៍"""
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class MonthOfYear(Enum):
    """ខែនៃឆ្នាំ"""
    JANUARY = "JANUARY"
    FEBRUARY = "FEBRUARY"
    MARCH = "MARCH"
    APRIL = "APRIL"
    MAY = "MAY"
    JUNE = "JUNE"
    JULY = "JULY"
    AUGUST = "AUGUST"
    SEPTEMBER = "SEPTEMBER"
    OCTOBER = "OCTOBER"
    NOVEMBER = "NOVEMBER"
    DECEMBER = "DECEMBER"


class QuarterOfYear(Enum):
    """ត្រីមាសនៃឆ្នាំ"""
    Q1 = "Q1"  # មករា-មីនា
    Q2 = "Q2"  # មេសា-មិថុនា
    Q3 = "Q3"  # កក្កដា-កញ្ញា
    Q4 = "Q4"  # តុលា-ធ្នូ


class TrendStrength(Enum):
    """កម្លាំងនិន្នាការ"""
    VERY_WEAK = "😴 VERY WEAK"        # ខ្សោយខ្លាំង
    WEAK = "😌 WEAK"                  # ខ្សោយ
    MODERATE = "😐 MODERATE"          # មធ្យម
    STRONG = "💪 STRONG"              # ខ្លាំង
    VERY_STRONG = "🔥 VERY STRONG"    # ខ្លាំងខ្លាំង
    EXTREME = "⚡ EXTREME"             # ខ្លាំងក្លា


class Momentum(Enum):
    """សន្ទុះ"""
    VERY_BEARISH = "🔻 VERY BEARISH"      # ធ្លាក់ខ្លាំង
    BEARISH = "📉 BEARISH"                 # ធ្លាក់
    SLIGHTLY_BEARISH = "↘️ SLIGHTLY BEARISH"  # ធ្លាក់បន្តិច
    NEUTRAL = "⚪ NEUTRAL"                 # អព្យាក្រឹត
    SLIGHTLY_BULLISH = "↗️ SLIGHTLY BULLISH"  # ឡើងបន្តិច
    BULLISH = "📈 BULLISH"                 # ឡើង
    VERY_BULLISH = "🚀 VERY BULLISH"       # ឡើងខ្លាំង


class VolumeTrend(Enum):
    """និន្នាការបរិមាណ"""
    DECREASING = "📉 DECREASING"      # ថយចុះ
    STABLE = "📊 STABLE"              # លំនឹង
    INCREASING = "📈 INCREASING"      # កើនឡើង
    SPIKING = "⚡ SPIKING"             # កើនឡើងខ្លាំង


class OrderFlowImbalance(Enum):
    """អតុល្យភាពលំហូរបញ្ជាទិញ"""
    EXTREME_BUYING = "🟢 EXTREME BUYING"      # ទិញខ្លាំង
    STRONG_BUYING = "🟢 STRONG BUYING"        # ទិញខ្លាំង
    MODERATE_BUYING = "🟢 MODERATE BUYING"    # ទិញមធ្យម
    SLIGHT_BUYING = "🟢 SLIGHT BUYING"        # ទិញបន្តិច
    NEUTRAL = "⚪ NEUTRAL"                    # អព្យាក្រឹត
    SLIGHT_SELLING = "🔴 SLIGHT SELLING"      # លក់បន្តិច
    MODERATE_SELLING = "🔴 MODERATE SELLING"  # លក់មធ្យម
    STRONG_SELLING = "🔴 STRONG SELLING"      # លក់ខ្លាំង
    EXTREME_SELLING = "🔴 EXTREME SELLING"    # លក់ខ្លាំង


class SupportResistanceType(Enum):
    """ប្រភេទនៃកម្រិតគាំទ្រ និងធន់"""
    MAJOR_SUPPORT = "🛡️ MAJOR SUPPORT"        # គាំទ្រសំខាន់
    MINOR_SUPPORT = "🛡️ MINOR SUPPORT"        # គាំទ្របន្ទាប់បន្សំ
    MAJOR_RESISTANCE = "🔴 MAJOR RESISTANCE"  # ធន់សំខាន់
    MINOR_RESISTANCE = "🔴 MINOR RESISTANCE"  # ធន់បន្ទាប់បន្សំ
    PSYCHOLOGICAL = "🧠 PSYCHOLOGICAL"        # កម្រិតផ្លូវចិត្ត
    ALL_TIME_HIGH = "🏆 ALL TIME HIGH"        # កំពូលគ្រប់ពេល
    ALL_TIME_LOW = "📉 ALL TIME LOW"          # បាតគ្រប់ពេល


class BreakoutType(Enum):
    """ប្រភេទនៃការបំបែក"""
    FALSE_BREAKOUT = "🎭 FALSE BREAKOUT"          # បំបែកក្លែងក្លាយ
    MINOR_BREAKOUT = "🔓 MINOR BREAKOUT"          # បំបែកបន្តិច
    MAJOR_BREAKOUT = "🔓🔓 MAJOR BREAKOUT"        # បំបែកសំខាន់
    DECISIVE_BREAKOUT = "⚡ DECISIVE BREAKOUT"    # បំបែកច្បាស់លាស់
    RETEST = "🔄 RETEST"                          # សាកល្បងឡើងវិញ


class PullbackType(Enum):
    """ប្រភេទនៃការថយក្រោយ"""
    SHALLOW = "📉 SHALLOW"          # រាក់ (ក្រោម 38.2%)
    MEDIUM = "📊 MEDIUM"            # មធ្យម (38.2-61.8%)
    DEEP = "📈 DEEP"                # ជ្រៅ (លើស 61.8%)
    FULL = "🔄 FULL"                # ពេញ (100%)


class DivergenceType(Enum):
    """ប្រភេទនៃភាពខុសគ្នា"""
    REGULAR_BULLISH = "🟢 REGULAR BULLISH"      # ភាពខុសគ្នាធម្មតាឡើង
    REGULAR_BEARISH = "🔴 REGULAR BEARISH"      # ភាពខុសគ្នាធម្មតាចុះ
    HIDDEN_BULLISH = "🟢 HIDDEN BULLISH"        # ភាពខុសគ្នាលាក់កំបាំងឡើង
    HIDDEN_BEARISH = "🔴 HIDDEN BEARISH"        # ភាពខុសគ្នាលាក់កំបាំងចុះ
    CLASSIC_BULLISH = "🟢 CLASSIC BULLISH"      # ភាពខុសគ្នាបុរាណឡើង
    CLASSIC_BEARISH = "🔴 CLASSIC BEARISH"      # ភាពខុសគ្នាបុរាណចុះ


class WhaleActivityType(Enum):
    """ប្រភេទនៃសកម្មភាពត្រីបាឡែន"""
    ACCUMULATION = "🐋 ACCUMULATION"        # ប្រមូលទិញ
    DISTRIBUTION = "🐋 DISTRIBUTION"        # ចែកចាយលក់
    DUMP = "🐋 DUMP"                        # បោះចោល
    PUMP = "🐋 PUMP"                         # បូមឡើង
    SPOOFING = "🎭 SPOOFING"                 # បញ្ឆោត
    WASH_TRADING = "🧼 WASH TRADING"         # លាងសម្អាតការជួញដូរ


class KeyZoneType(Enum):
    """ប្រភេទនៃតំបន់សំខាន់"""
    SUPPORT = "🛡️ SUPPORT"                  # តំបន់គាំទ្រ
    RESISTANCE = "🔴 RESISTANCE"            # តំបន់ធន់
    ORDER_BLOCK = "📦 ORDER BLOCK"           # ប្លុកបញ្ជាទិញ
    FAIR_VALUE_GAP = "🕳️ FAIR VALUE GAP"    # គម្លាតតម្លៃសមរម្យ
    IMBALANCE = "⚖️ IMBALANCE"               # អតុល្យភាព
    LIQUIDITY = "💧 LIQUIDITY"               # តំបន់សាច់ប្រាក់
    BREAKER = "🔨 BREAKER"                   # ប្លុកបំបែក
    MITIGATION = "✅ MITIGATION"              # ការកាត់បន្ថយ


class DomeFormation(Enum):
    """ប្រភេទនៃការបង្កើតដំបូល"""
    TOP = "🏛️ TOP"           # កំពូលដំបូល
    BOTTOM = "🏛️ BOTTOM"     # បាតដំបូល
    LEFT = "🏛️ LEFT"         # ឆ្វេង
    RIGHT = "🏛️ RIGHT"       # ស្តាំ
    COMPLETE = "🏛️ COMPLETE" # ពេញលេញ


class MarketPhase(Enum):
    """ដំណាក់កាលទីផ្សារ"""
    ACCUMULATION = "📦 ACCUMULATION"        # ប្រមូលទិញ
    MARKUP = "📈 MARKUP"                    # ឡើងថ្លៃ
    DISTRIBUTION = "📤 DISTRIBUTION"        # ចែកចាយ
    MARKDOWN = "📉 MARKDOWN"                # ចុះថ្លៃ
    RE_ACCUMULATION = "📦 RE-ACCUMULATION"  # ប្រមូលទិញម្តងទៀត
    RE_DISTRIBUTION = "📤 RE-DISTRIBUTION"  # ចែកចាយម្តងទៀត


class WyckoffPhase(Enum):
    """ដំណាក់កាល Wyckoff"""
    PHASE_A = "A - Accumulation"        # ដំណាក់កាល A - ប្រមូលទិញ
    PHASE_B = "B - Markup"              # ដំណាក់កាល B - ឡើងថ្លៃ
    PHASE_C = "C - Distribution"        # ដំណាក់កាល C - ចែកចាយ
    PHASE_D = "D - Markdown"            # ដំណាក់កាល D - ចុះថ្លៃ
    PHASE_E = "E - Re-accumulation"     # ដំណាក់កាល E - ប្រមូលទិញម្តងទៀត


class ElliottWave(Enum):
    """រលក Elliott"""
    WAVE_1 = "1️⃣ Wave 1"      # រលកទី១
    WAVE_2 = "2️⃣ Wave 2"      # រលកទី២
    WAVE_3 = "3️⃣ Wave 3"      # រលកទី៣
    WAVE_4 = "4️⃣ Wave 4"      # រលកទី៤
    WAVE_5 = "5️⃣ Wave 5"      # រលកទី៥
    WAVE_A = "🅰️ Wave A"       # រលក A
    WAVE_B = "🅱️ Wave B"       # រលក B
    WAVE_C = "🅲️ Wave C"       # រលក C
    WAVE_X = "❌ Wave X"        # រលក X


class GannAngle(Enum):
    """មុំ Gann"""
    ANGLE_1x1 = "1x1 (45°)"     # មុំ ៤៥ ដឺក្រេ
    ANGLE_1x2 = "1x2 (26.25°)"  # មុំ ២៦.២៥ ដឺក្រេ
    ANGLE_2x1 = "2x1 (63.75°)"  # មុំ ៦៣.៧៥ ដឺក្រេ
    ANGLE_1x4 = "1x4 (15°)"     # មុំ ១៥ ដឺក្រេ
    ANGLE_4x1 = "4x1 (75°)"     # មុំ ៧៥ ដឺក្រេ
    ANGLE_1x8 = "1x8 (7.5°)"    # មុំ ៧.៥ ដឺក្រេ
    ANGLE_8x1 = "8x1 (82.5°)"   # មុំ ៨២.៥ ដឺក្រេ


class HarmonicPattern(Enum):
    """លំនាំ Harmonic"""
    GARTLEY = "📐 GARTLEY"              # ហ្គាតលី
    BUTTERFLY = "🦋 BUTTERFLY"          # មេអំបៅ
    BAT = "🦇 BAT"                      # ប្រចៀវ
    CRAB = "🦀 CRAB"                    # ក្តាម
    DEEP_CRAB = "🦀 DEEP CRAB"          # ក្តាមជ្រៅ
    SHARK = "🦈 SHARK"                  # ត្រីឆ្លាម
    CYPRIAN = "🐟 CYPRIAN"              # ស៊ីព្រីន
    ABCD = "📏 ABCD"                     # អេប៊ីស៊ីឌី
    THREE_DRIVES = "🚗🚗🚗 THREE DRIVES"  # បីដ្រាយ


class TimePriceHarmonic(Enum):
    """អាម៉ូនិកពេលវេលា-តម្លៃ"""
    GOLDEN_RATIO = "✨ GOLDEN RATIO"          # សមាមាត្រមាស (1.618)
    GOLDEN_RATIO_INVERSE = "✨ GOLDEN RATIO INVERSE"  # សមាមាត្រមាសច្រាស (0.618)
    SILVER_RATIO = "🥈 SILVER RATIO"          # សមាមាត្រប្រាក់ (2.618)
    BRONZE_RATIO = "🥉 BRONZE RATIO"          # សមាមាត្រសំរិទ្ធ (3.618)
    SQUARE_ROOT_2 = "√2"                      # ឫសការ៉េនៃ២ (1.414)
    SQUARE_ROOT_3 = "√3"                      # ឫសការ៉េនៃ៣ (1.732)
    SQUARE_ROOT_5 = "√5"                      # ឫសការ៉េនៃ៥ (2.236)


class OrderBookPressure(Enum):
    """សម្ពាធសៀវភៅបញ្ជាទិញ"""
    EXTREME_BUY = "🟢 EXTREME BUY"          # ទិញខ្លាំង
    STRONG_BUY = "🟢 STRONG BUY"            # ទិញខ្លាំង
    MODERATE_BUY = "🟢 MODERATE BUY"        # ទិញមធ្យម
    SLIGHT_BUY = "🟢 SLIGHT BUY"            # ទិញបន្តិច
    NEUTRAL = "⚪ NEUTRAL"                  # អព្យាក្រឹត
    SLIGHT_SELL = "🔴 SLIGHT SELL"          # លក់បន្តិច
    MODERATE_SELL = "🔴 MODERATE SELL"      # លក់មធ្យម
    STRONG_SELL = "🔴 STRONG SELL"          # លក់ខ្លាំង
    EXTREME_SELL = "🔴 EXTREME SELL"        # លក់ខ្លាំង


class FundingRateSentiment(Enum):
    """មនោសញ្ចេតនាអត្រាមូលនិធិ"""
    EXTREME_POSITIVE = "🟢 EXTREME POSITIVE"    # វិជ្ជមានខ្លាំង
    POSITIVE = "🟢 POSITIVE"                    # វិជ្ជមាន
    SLIGHTLY_POSITIVE = "🟢 SLIGHTLY POSITIVE"  # វិជ្ជមានបន្តិច
    NEUTRAL = "⚪ NEUTRAL"                      # អព្យាក្រឹត
    SLIGHTLY_NEGATIVE = "🔴 SLIGHTLY NEGATIVE"  # អវិជ្ជមានបន្តិច
    NEGATIVE = "🔴 NEGATIVE"                    # អវិជ្ជមាន
    EXTREME_NEGATIVE = "🔴 EXTREME NEGATIVE"    # អវិជ្ជមានខ្លាំង


class OpenInterestTrend(Enum):
    """និន្នាការការប្រាក់បើកចំហ"""
    RISING = "📈 RISING"          # កើនឡើង
    FALLING = "📉 FALLING"        # ថយចុះ
    FLAT = "📊 FLAT"              # រាបស្មើ
    SPIKING_UP = "⚡ SPIKING UP"   # កើនឡើងខ្លាំង
    SPIKING_DOWN = "⚡ SPIKING DOWN"  # ថយចុះខ្លាំង


class LiquidityLevel(Enum):
    """កម្រិតសាច់ប្រាក់"""
    VERY_HIGH = "💧 VERY HIGH"      # ខ្ពស់ខ្លាំង
    HIGH = "💧 HIGH"                # ខ្ពស់
    MEDIUM = "💧 MEDIUM"            # មធ្យម
    LOW = "💧 LOW"                  # ទាប
    VERY_LOW = "💧 VERY LOW"        # ទាបខ្លាំង


class CorrelationStrength(Enum):
    """កម្លាំងទំនាក់ទំនង"""
    VERY_STRONG = "🔗 VERY STRONG"      # ខ្លាំងខ្លាំង (0.8-1.0)
    STRONG = "🔗 STRONG"                # ខ្លាំង (0.6-0.8)
    MODERATE = "🔗 MODERATE"            # មធ្យម (0.4-0.6)
    WEAK = "🔗 WEAK"                    # ខ្សោយ (0.2-0.4)
    VERY_WEAK = "🔗 VERY WEAK"          # ខ្សោយខ្លាំង (0.0-0.2)
    NEGATIVE_STRONG = "🔗 NEGATIVE STRONG"  # អវិជ្ជមានខ្លាំង (-0.8 ដល់ -1.0)
    NEGATIVE_MODERATE = "🔗 NEGATIVE MODERATE"  # អវិជ្ជមានមធ្យម (-0.4 ដល់ -0.6)


class BetaCategory(Enum):
    """ប្រភេទ Beta"""
    HIGH_BETA = "⚡ HIGH BETA"          # បេតាខ្ពស់ (>1.5)
    MEDIUM_BETA = "📊 MEDIUM BETA"      # បេតាមធ្យម (0.8-1.5)
    LOW_BETA = "🐢 LOW BETA"            # បេតាទាប (0.3-0.8)
    VERY_LOW_BETA = "🐌 VERY LOW BETA"  # បេតាទាបខ្លាំង (<0.3)
    NEGATIVE_BETA = "🔄 NEGATIVE BETA"  # បេតាអវិជ្ជមាន (<0)


class VolatilityRegime(Enum):
    """របបភាពប្រែប្រួល"""
    EXPANDING = "🌋 EXPANDING"      # ពង្រីក
    CONTRACTING = "🌀 CONTRACTING"  # ចុះកិច្ចសន្យា
    BREAKOUT = "💥 BREAKOUT"        # បំបែក
    BREAKDOWN = "💥 BREAKDOWN"      # បំបែកចុះ
    CHOPPY = "🔪 CHOPPY"            # កាត់ផ្តាច់
    TRENDING = "📈 TRENDING"        # និន្នាការ


class ATRState(Enum):
    """ស្ថានភាព ATR"""
    EXPANDING = "🌋 EXPANDING"      # ពង្រីក
    CONTRACTING = "🌀 CONTRACTING"  # ចុះកិច្ចសន្យា
    STABLE = "📊 STABLE"            # លំនឹង
    SPIKING = "⚡ SPIKING"           # កើនឡើងខ្លាំង


class RSIState(Enum):
    """ស្ថានភាព RSI"""
    OVERBOUGHT = "🟢 OVERBOUGHT"        # ទិញហួស (>70)
    BULLISH = "🟢 BULLISH"              # កើន (50-70)
    NEUTRAL = "⚪ NEUTRAL"              # អព្យាក្រឹត (40-60)
    BEARISH = "🔴 BEARISH"              # ចុះ (30-50)
    OVERSOLD = "🔴 OVERSOLD"            # លក់ហួស (<30)


class MACDState(Enum):
    """ស្ថានភាព MACD"""
    BULLISH_CROSS = "🟢 BULLISH CROSS"          # កាត់ឡើង
    BULLISH_DIVERGENCE = "🟢 BULLISH DIVERGENCE"  # ភាពខុសគ្នាឡើង
    BULLISH_MOMENTUM = "🟢 BULLISH MOMENTUM"    # សន្ទុះឡើង
    NEUTRAL = "⚪ NEUTRAL"                      # អព្យាក្រឹត
    BEARISH_MOMENTUM = "🔴 BEARISH MOMENTUM"    # សន្ទុះចុះ
    BEARISH_DIVERGENCE = "🔴 BEARISH DIVERGENCE"  # ភាពខុសគ្នាចុះ
    BEARISH_CROSS = "🔴 BEARISH CROSS"          # កាត់ចុះ


class BBState(Enum):
    """ស្ថានភាព Bollinger Bands"""
    ABOVE_UPPER = "🔝 ABOVE UPPER"      # លើសក្រុមតន្រ្តីខាងលើ
    TOUCHING_UPPER = "👆 TOUCHING UPPER"  # ប៉ះក្រុមតន្រ្តីខាងលើ
    INSIDE_UPPER = "📈 INSIDE UPPER"    # ខាងក្នុងផ្នែកខាងលើ
    MIDDLE = "⚪ MIDDLE"                # កណ្តាល
    INSIDE_LOWER = "📉 INSIDE LOWER"    # ខាងក្នុងផ្នែកខាងក្រោម
    TOUCHING_LOWER = "👇 TOUCHING LOWER"  # ប៉ះក្រុមតន្រ្តីខាងក្រោម
    BELOW_LOWER = "🔻 BELOW LOWER"      # ក្រោមក្រុមតន្រ្តីខាងក្រោម
    SQUEEZE = "🔒 SQUEEZE"              # បង្រួម
    EXPANSION = "🔓 EXPANSION"          # ពង្រីក


class VWAPState(Enum):
    """ស្ថានភាព VWAP"""
    ABOVE_VWAP = "🟢 ABOVE VWAP"    # លើស VWAP
    AT_VWAP = "⚪ AT VWAP"          # ស្មើ VWAP
    BELOW_VWAP = "🔴 BELOW VWAP"    # ក្រោម VWAP


class OBVState(Enum):
    """ស្ថានភាព OBV"""
    RISING = "📈 RISING"          # កើនឡើង
    FALLING = "📉 FALLING"        # ថយចុះ
    FLAT = "📊 FLAT"              # រាបស្មើ
    DIVERGENCE_BULLISH = "🟢 DIVERGENCE BULLISH"  # ភាពខុសគ្នាឡើង
    DIVERGENCE_BEARISH = "🔴 DIVERGENCE BEARISH"  # ភាពខុសគ្នាចុះ


class MoneyFlowState(Enum):
    """ស្ថានភាពលំហូរប្រាក់"""
    POSITIVE = "🟢 POSITIVE"      # វិជ្ជមាន (MFI>50)
    NEGATIVE = "🔴 NEGATIVE"      # អវិជ្ជមាន (MFI<50)
    OVERBOUGHT = "🟢 OVERBOUGHT"  # ទិញហួស (MFI>80)
    OVERSOLD = "🔴 OVERSOLD"      # លក់ហួស (MFI<20)


class StochasticState(Enum):
    """ស្ថានភាព Stochastic"""
    OVERBOUGHT = "🟢 OVERBOUGHT"      # ទិញហួស (>80)
    BULLISH = "🟢 BULLISH"            # កើន (50-80)
    NEUTRAL = "⚪ NEUTRAL"            # អព្យាក្រឹត (20-80)
    BEARISH = "🔴 BEARISH"            # ចុះ (20-50)
    OVERSOLD = "🔴 OVERSOLD"          # លក់ហួស (<20)
    BULLISH_CROSS = "🟢 BULLISH CROSS"  # កាត់ឡើង
    BEARISH_CROSS = "🔴 BEARISH CROSS"  # កាត់ចុះ


class ADXState(Enum):
    """ស្ថានភាព ADX"""
    VERY_STRONG_TREND = "⚡ VERY STRONG TREND"      # និន្នាការខ្លាំងខ្លាំង (>50)
    STRONG_TREND = "💪 STRONG TREND"                # និន្នាការខ្លាំង (35-50)
    WEAK_TREND = "😐 WEAK TREND"                    # និន្នាការខ្សោយ (25-35)
    NO_TREND = "😴 NO TREND"                        # គ្មាននិន្នាការ (<25)
    TRENDING_UP = "📈 TRENDING UP"                  # និន្នាការឡើង
    TRENDING_DOWN = "📉 TRENDING DOWN"              # និន្នាការចុះ


class ParabolicSARState(Enum):
    """ស្ថានភាព Parabolic SAR"""
    ABOVE_PRICE = "🔴 ABOVE PRICE"  # លើសតម្លៃ (សញ្ញាចុះ)
    BELOW_PRICE = "🟢 BELOW PRICE"  # ក្រោមតម្លៃ (សញ្ញាឡើង)
    REVERSAL = "🔄 REVERSAL"        # បញ្ច្រាស


class IchimokuState(Enum):
    """ស្ថានភាព Ichimoku"""
    BULLISH = "🟢 BULLISH"                      # កើន
    BEARISH = "🔴 BEARISH"                      # ចុះ
    NEUTRAL = "⚪ NEUTRAL"                      # អព្យាក្រឹត
    CLOUD_ABOVE = "☁️ CLOUD ABOVE"              # ពពកពីលើ
    CLOUD_BELOW = "☁️ CLOUD BELOW"              # ពពកពីក្រោម
    TK_CROSS_BULLISH = "🟢 TK CROSS BULLISH"    # កាត់ TK ឡើង
    TK_CROSS_BEARISH = "🔴 TK CROSS BEARISH"    # កាត់ TK ចុះ
    SENKOU_BULLISH = "🟢 SENKOU BULLISH"        # សេនកូវស្ពាន់ឡើង
    SENKOU_BEARISH = "🔴 SENKOU BEARISH"        # សេនកូវស្ពាន់ចុះ
    CHIKOU_BULLISH = "🟢 CHIKOU BULLISH"        # ឈីកូវស្ពាន់ឡើង
    CHIKOU_BEARISH = "🔴 CHIKOU BEARISH"        # ឈីកូវស្ពាន់ចុះ


class FibonacciState(Enum):
    """ស្ថានភាព Fibonacci"""
    RETRACEMENT_236 = "📊 23.6% RETRACEMENT"    # ថយក្រោយ 23.6%
    RETRACEMENT_382 = "📊 38.2% RETRACEMENT"    # ថយក្រោយ 38.2%
    RETRACEMENT_5 = "📊 50% RETRACEMENT"        # ថយក្រោយ 50%
    RETRACEMENT_618 = "📊 61.8% RETRACEMENT"    # ថយក្រោយ 61.8%
    RETRACEMENT_786 = "📊 78.6% RETRACEMENT"    # ថយក្រោយ 78.6%
    EXTENSION_1272 = "🚀 127.2% EXTENSION"      # ពង្រីក 127.2%
    EXTENSION_1618 = "🚀 161.8% EXTENSION"      # ពង្រីក 161.8%
    EXTENSION_2618 = "🚀 261.8% EXTENSION"      # ពង្រីក 261.8%
    EXTENSION_4236 = "🚀 423.6% EXTENSION"      # ពង្រីក 423.6%


class PivotPointType(Enum):
    """ប្រភេទចំណុច Pivot"""
    CLASSIC = "📐 CLASSIC"          # បុរាណ
    FIBONACCI = "🌀 FIBONACCI"      # ហ្វីបូណាឈី
    WOODIE = "🪵 WOODIE"            # វូឌី
    CAMARILLA = "🏠 CAMARILLA"      # កាម៉ារីឡា
    DEMARK = "📝 DEMARK"            # ឌីម៉ាក


class PivotLevel(Enum):
    """កម្រិត Pivot"""
    R3 = "🔴 R3"    # Resistance 3
    R2 = "🔴 R2"    # Resistance 2
    R1 = "🔴 R1"    # Resistance 1
    PP = "⚪ PP"    # Pivot Point
    S1 = "🟢 S1"    # Support 1
    S2 = "🟢 S2"    # Support 2
    S3 = "🟢 S3"    # Support 3


class MarketStructure(Enum):
    """រចនាសម្ព័ន្ធទីផ្សារ"""
    HIGHER_HIGH = "📈 HIGHER HIGH"          # ខ្ពស់ខ្ពស់ជាង
    LOWER_HIGH = "📉 LOWER HIGH"            # ខ្ពស់ទាបជាង
    HIGHER_LOW = "📈 HIGHER LOW"            # ទាបខ្ពស់ជាង
    LOWER_LOW = "📉 LOWER LOW"              # ទាបទាបជាង
    BREAK_OF_STRUCTURE = "💥 BREAK OF STRUCTURE"  # បំបែករចនាសម្ព័ន្ធ
    CHANGE_OF_CHARACTER = "🔄 CHANGE OF CHARACTER"  # ផ្លាស់ប្តូរលក្ខណៈ
    INDUCEMENT = "🎣 INDUCEMENT"            # ការទាក់ទាញ


class OrderFlowType(Enum):
    """ប្រភេទលំហូរបញ្ជាទិញ"""
    AGGRESSIVE_BUYING = "🔥 AGGRESSIVE BUYING"      # ទិញឈ្លានពាន
    AGGRESSIVE_SELLING = "🔥 AGGRESSIVE SELLING"    # លក់ឈ្លានពាន
    PASSIVE_BUYING = "😐 PASSIVE BUYING"            # ទិញអកម្ម
    PASSIVE_SELLING = "😐 PASSIVE SELLING"          # លក់អកម្ម
    ABSORPTION = "🧽 ABSORPTION"                    # ស្រូបយក
    EXHAUSTION = "😮‍💨 EXHAUSTION"                   # អស់កម្លាំង


class TapeReadingSignal(Enum):
    """សញ្ញាអានតេប"""
    BUYING_CLIMAX = "🔝 BUYING CLIMAX"        # កំពូលទិញ
    SELLING_CLIMAX = "🔻 SELLING CLIMAX"      # កំពូលលក់
    STOP_HUNTING = "🎯 STOP HUNTING"           # ប្រមាញ់ឈប់
    ICEBERG_DETECTED = "🧊 ICEBERG DETECTED"  # រកឃើញ Iceberg
    SPOOFING_DETECTED = "🎭 SPOOFING DETECTED"  # រកឃើញ Spoofing
    WASH_TRADE_DETECTED = "🧼 WASH TRADE DETECTED"  # រកឃើញ Wash Trade


class MarketMakerAction(Enum):
    """សកម្មភាពអ្នកបង្កើតទីផ្សារ"""
    ACCUMULATING = "📦 ACCUMULATING"      # កំពុងប្រមូល
    DISTRIBUTING = "📤 DISTRIBUTING"      # កំពុងចែកចាយ
    MARKING_UP = "📈 MARKING UP"          # កំពុងឡើងថ្លៃ
    MARKING_DOWN = "📉 MARKING DOWN"      # កំពុងចុះថ្លៃ
    STOP_RUN = "🏃 STOP RUN"               # រត់ឈប់
    LIQUIDITY_SWEEP = "🌊 LIQUIDITY SWEEP"  # បោសសំអាតសាច់ប្រាក់
    ENGINEERING = "🔧 ENGINEERING"         # វិស្វកម្ម


class TimeframeAlignment(Enum):
    """ការតម្រឹមពេលវេលា"""
    ALL_ALIGNED = "✅ ALL ALIGNED"              # ទាំងអស់តម្រឹម
    MAJORITY_ALIGNED = "🟢 MAJORITY ALIGNED"    # ភាគច្រើនតម្រឹម
    MIXED = "🟡 MIXED"                          # លាយឡំ
    MAJORITY_CONFLICT = "🟠 MAJORITY CONFLICT"  # ភាគច្រើនប៉ះទង្គិច
    ALL_CONFLICT = "🔴 ALL CONFLICT"            # ទាំងអស់ប៉ះទង្គិច


class TradeOutcome(Enum):
    """លទ្ធផលការជួញដូរ"""
    WIN = "✅ WIN"          # ឈ្នះ
    LOSS = "❌ LOSS"        # ចាញ់
    BREAK_EVEN = "⚪ BREAK EVEN"  # ស្មើ
    PARTIAL = "🟡 PARTIAL"  # មួយផ្នែក
    PENDING = "⏳ PENDING"  # កំពុងរង់ចាំ


class RiskRewardRatio(Enum):
    """សមាមាត្រហានិភ័យ-រង្វាន់"""
    VERY_POOR = "😱 VERY POOR"          # អាក្រក់ខ្លាំង (<1:0.5)
    POOR = "😟 POOR"                    # អាក្រក់ (1:0.5-1:1)
    ACCEPTABLE = "😐 ACCEPTABLE"        # អាចទទួលយកបាន (1:1-1:1.5)
    GOOD = "😊 GOOD"                    # ល្អ (1:1.5-1:2)
    VERY_GOOD = "😃 VERY GOOD"          # ល្អខ្លាំង (1:2-1:3)
    EXCELLENT = "🤩 EXCELLENT"          # ល្អឥតខ្ចោះ (>1:3)


class TradeManagement(Enum):
    """ការគ្រប់គ្រងការជួញដូរ"""
    SCALING_OUT = "📤 SCALING OUT"          # ចេញបន្តិចម្តងៗ
    SCALING_IN = "📥 SCALING IN"            # ចូលបន្តិចម្តងៗ
    TRAILING_STOP = "🎯 TRAILING STOP"      # ឈប់តាម
    BREAK_EVEN_STOP = "⚪ BREAK EVEN STOP"  # ឈប់ចំណេញស្មើ
    PARTIAL_TAKE_PROFIT = "💰 PARTIAL TAKE PROFIT"  # យកចំណេញខ្លះ
    FULL_TAKE_PROFIT = "💰💰 FULL TAKE PROFIT"      # យកចំណេញទាំងអស់
    HOLDING = "💎 HOLDING"                  # កាន់


class SessionQuality(Enum):
    """គុណភាពវគ្គ"""
    EXCELLENT = "🌟 EXCELLENT"      # ល្អឥតខ្ចោះ
    GOOD = "⭐ GOOD"                # ល្អ
    AVERAGE = "⚪ AVERAGE"          # មធ្យម
    POOR = "🌑 POOR"                # អន់
    VERY_POOR = "🌚 VERY POOR"      # អន់ខ្លាំង


class BotMode(Enum):
    """របៀប Bot"""
    LIVE = "🔴 LIVE"              # ផ្សាយផ្ទាល់
    PAPER = "📝 PAPER"            # ក្រដាស
    BACKTEST = "📊 BACKTEST"      # សាកល្បងក្រោយ
    OPTIMIZATION = "⚙️ OPTIMIZATION"  # បង្កើនប្រសិទ្ធភាព
    ANALYSIS = "🔬 ANALYSIS"      # វិភាគ
    MONITORING = "👀 MONITORING"  # ត្រួតពិនិត្យ


class LogCategory(Enum):
    """ប្រភេទកំណត់ហេតុ"""
    SYSTEM = "⚙️ SYSTEM"              # ប្រព័ន្ធ
    TRADE = "💰 TRADE"                # ការជួញដូរ
    SIGNAL = "📶 SIGNAL"              # សញ្ញា
    ERROR = "❌ ERROR"                # កំហុស
    WARNING = "⚠️ WARNING"            # ព្រមាន
    INFO = "ℹ️ INFO"                  # ព័ត៌មាន
    DEBUG = "🐛 DEBUG"                # បំបាត់កំហុស
    PERFORMANCE = "📊 PERFORMANCE"    # ដំណើរការ
    SECURITY = "🔒 SECURITY"          # សុវត្ថិភាព


class NotificationPriority(Enum):
    """អាទិភាពការជូនដំណឹង"""
    LOW = "⚪ LOW"              # ទាប
    MEDIUM = "🟡 MEDIUM"        # មធ្យម
    HIGH = "🟠 HIGH"            # ខ្ពស់
    URGENT = "🔴 URGENT"        # បន្ទាន់
    CRITICAL = "💥 CRITICAL"    # ធ្ងន់ធ្ងរ


class ChartTimeframe(Enum):
    """ពេលវេលាតារាង"""
    M1 = "1m"      # 1 នាទី
    M3 = "3m"      # 3 នាទី
    M5 = "5m"      # 5 នាទី
    M15 = "15m"    # 15 នាទី
    M30 = "30m"    # 30 នាទី
    H1 = "1h"      # 1 ម៉ោង
    H2 = "2h"      # 2 ម៉ោង
    H4 = "4h"      # 4 ម៉ោង
    H6 = "6h"      # 6 ម៉ោង
    H8 = "8h"      # 8 ម៉ោង
    H12 = "12h"    # 12 ម៉ោង
    D1 = "1d"      # 1 ថ្ងៃ
    D3 = "3d"      # 3 ថ្ងៃ
    W1 = "1w"      # 1 សប្តាហ៍
    MN1 = "1M"     # 1 ខែ


# ==============================================================================
# LANGUAGE CONFIG
# ==============================================================================
@dataclass
class LanguageConfig:
    """English only language configuration"""
    current_language: Language = Language.ENGLISH
    
    translations = {
        'en': {
            'app_name': "ULTIMATE HYBRID TRADING BOT V1.0.0",
            'welcome': "🤖 ULTIMATE HYBRID BOT V1.0.0 STARTED",
            'scanning': "🔍 Scanning for opportunities...",
            'signal_found': "✅ Signal found",
            'no_signal': "❌ No signal",
            'error': "⚠️ Error",
            'warning': "⚠️ Warning",
            'success': "✅ Success",
            'info': "ℹ️ Info",
            'loading': "⏳ Loading...",
            'please_wait': "⏳ Please wait...",
            'completed': "✅ Completed",
            'failed': "❌ Failed",
            'cancelled': "⏹️ Cancelled",
            'initializing': "🔧 Initializing...",
            'testing': "🧪 Testing...",
            'seconds': "seconds",
            'minutes': "minutes",
            'goodbye': "👋 Goodbye!",
            'monitoring': "📊 Monitoring",
            'symbols': "symbols",
            'tiers': "🎯 Tiers",
            'min_confidence': "📊 Min Confidence",
            'min_accuracy': "📊 Min Accuracy",
            'cooldown': "⏱️ Cooldown",
            'auto_trade': "⚡ Auto Trade",
            'language': "🌐 Language",
            'core_features': "🔧 Core Features",
            'advanced_features': "🔬 Advanced Features",
            'ultimate_analysis': "📊 Ultimate Analysis",
            'order_recommendations': "📊 Order Recommendations",
            'tp_multipliers': "⚙️ TP Multipliers",
            'copyright': "© 2026 Nhen Bol. All rights reserved.",
            'powered_by': "⚡Developer By: Nhen Bol",
            'disclaimer': "⚠️ សូមធ្វើការចូលដោយទំនួសខុសត្រូវខ្លួនឯង - Trading involves substantial risk. Use at your own risk. Do your owner research",
            
            'tier_1': "🛡️ ULTRA SAFE",
            'tier_2': "⚖️ BALANCED",
            'tier_3': "⚡ AGGRESSIVE",
            'buy_signal': "🟢 LONG SIGNAL",
            'sell_signal': "🔴 SHORT SIGNAL",
            'confidence': "🎯 Confidence",
            'accuracy': "📊 Accuracy",
            
            'entry_price': "📈 Entry Price",
            'stop_loss': "🛑 Stop Loss",
            'take_profit_1': "🎯 TP1",
            'take_profit_2': "🎯 TP2",
            'take_profit_3': "🎯 TP3",
            'risk_reward': "📊 Risk/Reward",
            
            'order_type': "📊 Order Type",
            'market_buy': "🔥 MARKET BUY",
            'market_sell': "🔥 MARKET SELL",
            'limit_buy': "📉 LIMIT BUY",
            'limit_sell': "📈 LIMIT SELL",
            'iceberg': "🧊 ICEBERG",
            'twap': "⏱️ TWAP",
            'oco': "🔄 OCO",
            'trailing_stop': "🎯 TRAILING STOP",
            
            'aggressive_market': "🔥 AGGRESSIVE MARKET",
            'limit_buy_dip': "📉 LIMIT BUY DIP",
            'limit_sell_rally': "📈 LIMIT SELL RALLY",
            'scalper_market': "⚡ SCALPER MARKET",
            'position_limit': "🎯 POSITION LIMIT",
            'iceberg_recommended': "🧊 ICEBERG RECOMMENDED",
            'twap_recommended': "⏱️ TWAP RECOMMENDED",
            'wait_confirmation': "⏳ WAIT CONFIRMATION",
            
            'whale_alert': "🐋 WHALE ALERT",
            'whale_buy': "🐋 Whale Buying Detected",
            'whale_sell': "🐋 Whale Selling Detected",
            'whale_cancel': "🔄 Whale Cancel Order Detected",
            'whale_accumulation': "📊 Whale Accumulation",
            'whale_distribution': "📊 Whale Distribution",
            'no_whale_activity': "No whale activity",
            
            'key_zone': "🎯 Key Zone",
            'support_zone': "🛡️ Support Zone",
            'resistance_zone': "🔴 Resistance Zone",
            'pullback': "🔄 Pullback",
            'pullback_buy': "📉 Pullback Buy Opportunity",
            'pullback_sell': "📈 Pullback Sell Opportunity",
            'dome': "🏛️ Dome Formation",
            'dome_top': "🏛️ Dome Top",
            'dome_bottom': "🏛️ Dome Bottom",
            
            'bull_market': "🐂 BULL MARKET",
            'bear_market': "🐻 BEAR MARKET",
            'ranging': "📊 RANGING",
            'volatile': "🌪️ VOLATILE",
            'trending_bull': "🐂 TRENDING BULL",
            'trending_bear': "🐻 TRENDING BEAR",
            'strong_bull': "🐂 STRONG BULL",
            'strong_bear': "🐻 STRONG BEAR",
            'weak_bull': "📈 WEAK BULL",
            'weak_bear': "📉 WEAK BEAR",
            'short_term': "Short Term",
            'medium_term': "Medium Term",
            'long_term': "Long Term",
            'alignment_score': "Alignment Score",
            
            'smart_money': "🧠 Smart Money",
            'order_block': "📦 Order Block",
            'liquidity_grab': "🎣 Liquidity Grab",
            'fvg': "🕳️ Fair Value Gap",
            'breaker': "🔨 Breaker Block",
            'mitigation': "✅ Mitigation",
            'institutional_divergence': "📉 Institutional Divergence",
            
            'risk_level': "⚠️ Risk Level",
            'position_size': "📊 Position Size",
            'drawdown': "📉 Drawdown",
            'kelly_fraction': "📊 Kelly Fraction",
            'var_95': "📊 VaR 95%",
            'var_99': "📊 VaR 99%",
            'expected_move': "📊 Expected Move",
            
            'scalping': "⚡ Scalping",
            'intraday': "📊 Intraday",
            'swing': "🔄 Swing",
            'position': "🎯 Position",
            
            'ml_ensemble': "🧠 ML Ensemble",
            'ai_confidence': "🤖 AI Confidence",
            'random_forest': "🌲 Random Forest",
            'gradient_boosting': "📈 Gradient Boosting",
            'lstm': "🧠 LSTM",
            
            'telegram_alert': "📱 Telegram Alert",
            'alert_level': "🔔 Alert Level",
            'emergency': "🔴 EMERGENCY",
            'high': "🟡 HIGH",
            'medium': "🔵 MEDIUM",
            'low': "⚪ LOW",
            
            'win_rate': "📈 Win Rate",
            'profit_factor': "💰 Profit Factor",
            'sharpe_ratio': "📊 Sharpe Ratio",
            'sortino_ratio': "📊 Sortino Ratio",
            'calmar_ratio': "📊 Calmar Ratio",
            'max_drawdown': "📉 Max Drawdown",
            'total_signals': "📊 Total Signals",
            'avg_confidence': "📊 Avg Confidence",
            'avg_accuracy': "📊 Avg Accuracy",
            
            'english': "🇬🇧 English",
            
            'start': "▶️ Start",
            'stop': "⏹️ Stop",
            'pause': "⏸️ Pause",
            'resume': "▶️ Resume",
            'settings': "⚙️ Settings",
            'status': "📊 Status",
            'backtest': "📈 Backtest",
            'report': "📄 Report",
            
            'config_loaded': "✅ Configuration loaded",
            'config_saved': "✅ Configuration saved",
            'config_error': "❌ Configuration error",
            'feature_enabled': "✅ Feature enabled",
            'feature_disabled': "❌ Feature disabled",
            
            'technical_summary': "📊 Technical Summary",
            'market_context': "🌍 Market Context",
            'backtest_result': "📈 Backtest Result",
            'primary_reasons': "⭐ Primary Reasons",
            'tier_distribution': "📊 Tier Distribution",
            'direction_distribution': "📊 Direction Distribution",
            'hourly_summary': "📊 Hourly Summary",
            'top_signals': "🏆 Top Signals",
            
            'technical_documentation': "📚 TECHNICAL DOCUMENTATION",
            'user_guide': "📖 USER GUIDE",
            'installation_guide': "🔧 INSTALLATION GUIDE",
            'api_reference': "🔌 API REFERENCE",
            'version_history': "📋 VERSION HISTORY",
            'license_info': "⚖️ LICENSE INFORMATION",
            
            'tp_table': "📊 TAKE PROFIT TABLE",
            'tp1_allocation': "TP1 Allocation",
            'tp2_allocation': "TP2 Allocation",
            'tp3_allocation': "TP3 Allocation",
            'rr_ratio': "R:R Ratio",
            'target_percent': "Target %"
        }
    }
    
    def get_text(self, key: str) -> str:
        """Get translated text based on current language"""
        try:
            return self.translations[self.current_language.value].get(key, 
                   self.translations['en'].get(key, key))
        except:
            return key

# Global language instance
lang = LanguageConfig()

# ==============================================================================
# CONFIGURATION CLASSES
# ==============================================================================
@dataclass
class FeatureFlags:
    TIER_1_ENABLED: bool = True
    TIER_2_ENABLED: bool = True
    TIER_3_ENABLED: bool = True
    ATR_STOP_LOSS_ENABLED: bool = True
    VOLUME_PROFILE_ENABLED: bool = True
    LIQUIDITY_GRAB_ENABLED: bool = True
    EMA_200_FILTER_ENABLED: bool = True
    AI_CONFIDENCE_ENABLED: bool = True
    WHALE_DETECTION_ENABLED: bool = True
    KEY_ZONE_ENABLED: bool = True
    PULLBACK_DETECTION_ENABLED: bool = True
    DOME_DETECTION_ENABLED: bool = True
    ORDER_RECOMMENDATION_ENABLED: bool = True
    ULTIMATE_DIRECTION_ENABLED: bool = True
    SMART_MONEY_ENABLED: bool = True
    SENTIMENT_ANALYSIS_ENABLED: bool = True
    DIVERGENCE_DETECTION_ENABLED: bool = True
    ML_ENSEMBLE_ENABLED: bool = True
    RISK_MANAGEMENT_ENABLED: bool = True
    PORTFOLIO_TRACKING_ENABLED: bool = True
    PERFORMANCE_ANALYTICS_ENABLED: bool = True
    BACKTESTING_ENABLED: bool = True
    ADVANCED_ORDERS_ENABLED: bool = True
    SECURITY_FEATURES_ENABLED: bool = True
    LANGUAGE: str = "en"

@dataclass
class ThresholdConfig:
    MIN_CONFIDENCE: float = 70.0
    MIN_ACCURACY: float = 75.0
    MIN_VOLUME_24H: float = 500000.0
    MAX_SPREAD_PERCENT: float = 0.1
    TIER_1_TECH_THRESHOLD: float = 70.0
    TIER_1_FLOW_THRESHOLD: float = 60.0
    TIER_2_TECH_THRESHOLD: float = 59.0
    TIER_2_FLOW_THRESHOLD: float = 55.0
    TIER_3_TECH_THRESHOLD: float = 54.0
    TIER_3_FLOW_THRESHOLD: float = 48.0
    MIN_REGIME_ALIGNMENT: float = 60.0
    MIN_STYLE_CONFIDENCE: float = 70.0
    SECONDARY_STYLE_THRESHOLD: float = 70.0
    WHALE_MIN_ORDER_VALUE: float = 50000.0
    WHALE_CANCEL_WINDOW: int = 60
    KEYZONE_MIN_TOUCHES: int = 3
    KEYZONE_PULLBACK_PERCENT: float = 0.5
    PULLBACK_MIN_RETRACE: float = 0.382
    PULLBACK_MAX_RETRACE: float = 0.618
    DOME_MIN_HEIGHT_PERCENT: float = 2.0
    MAX_DRAWDOWN_PERCENT: float = 20.0
    MAX_POSITION_SIZE_USDT: float = 100.0
    DEFAULT_LEVERAGE: int = 5
    RISK_PER_TRADE: float = 0.01

@dataclass
class WeightConfig:
    ULTRA_SHORT_WEIGHT: float = 0.30
    SHORT_WEIGHT: float = 0.25
    MEDIUM_WEIGHT: float = 0.25
    LONG_WEIGHT: float = 0.20
    REGIME_WEIGHT: float = 0.20
    CORRELATION_WEIGHT: float = 0.15
    VOLUME_PROFILE_WEIGHT: float = 0.20
    SENTIMENT_WEIGHT: float = 0.15
    DIVERGENCE_WEIGHT: float = 0.15
    SMART_MONEY_WEIGHT: float = 0.15

@dataclass
class TPConfig:
    SCALPING_TP1: float = 0.30
    SCALPING_TP2: float = 0.50
    SCALPING_TP3: float = 0.75
    INTRADAY_TP1: float = 0.70
    INTRADAY_TP2: float = 1.00
    INTRADAY_TP3: float = 1.50
    SWING_TP1: float = 1.50
    SWING_TP2: float = 2.50
    SWING_TP3: float = 3.50
    POSITION_TP1: float = 2.00
    POSITION_TP2: float = 3.50
    POSITION_TP3: float = 5.00
    
    def get_multipliers(self, style: str) -> Tuple[float, float, float]:
        style = style.upper()
        if style == "SCALPING":
            return self.SCALPING_TP1, self.SCALPING_TP2, self.SCALPING_TP3
        elif style == "INTRADAY":
            return self.INTRADAY_TP1, self.INTRADAY_TP2, self.INTRADAY_TP3
        elif style == "SWING":
            return self.SWING_TP1, self.SWING_TP2, self.SWING_TP3
        elif style == "POSITION":
            return self.POSITION_TP1, self.POSITION_TP2, self.POSITION_TP3
        else:
            return self.INTRADAY_TP1, self.INTRADAY_TP2, self.INTRADAY_TP3
    
    def get_allocations(self, style: str) -> Tuple[float, float, float]:
        style = style.upper()
        if style == "SCALPING":
            return 0.50, 0.30, 0.20
        elif style == "INTRADAY":
            return 0.40, 0.35, 0.25
        elif style == "SWING":
            return 0.30, 0.30, 0.40
        elif style == "POSITION":
            return 0.20, 0.30, 0.50
        else:
            return 0.40, 0.35, 0.25

@dataclass
class ATRConfig:
    ENABLED: bool = True
    PERIOD: int = 14
    MULTIPLIER: float = 1.5
    DYNAMIC_MULTIPLIER: bool = True

@dataclass
class VolumeProfileConfig:
    ENABLED: bool = True
    BINS: int = 24
    VALUE_AREA_PERCENT: float = 70.0
    MIN_BARS: int = 20

@dataclass
class LiquidityGrabConfig:
    ENABLED: bool = True
    LOOKBACK: int = 10
    MIN_WICK_PERCENT: float = 0.5
    VOLUME_CONFIRMATION: bool = True

@dataclass
class EMA200Config:
    ENABLED: bool = True
    REQUIRED_FOR_TIER1: bool = True
    REQUIRED_FOR_TIER2: bool = True
    REQUIRED_FOR_TIER3: bool = True

@dataclass
class AIConfig:
    ENABLED: bool = True
    MIN_SIGNALS_FOR_TRAINING: int = 20
    OVERRIDE_CONFIDENCE: bool = True
    MAX_HISTORY: int = 100

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
    LANGUAGE: str = "en"

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
    scalping_tp1: float = 0.30
    scalping_tp2: float = 0.50
    scalping_tp3: float = 0.75
    intraday_tp1: float = 0.70
    intraday_tp2: float = 1.00
    intraday_tp3: float = 1.50
    swing_tp1: float = 1.50
    swing_tp2: float = 2.50
    swing_tp3: float = 3.50
    position_tp1: float = 2.00
    position_tp2: float = 3.50
    position_tp3: float = 5.00
    
    def get_multipliers(self, style: str) -> Tuple[float, float, float]:
        style = style.upper()
        if style == "SCALPING":
            return self.scalping_tp1, self.scalping_tp2, self.scalping_tp3
        elif style == "INTRADAY":
            return self.intraday_tp1, self.intraday_tp2, self.intraday_tp3
        elif style == "SWING":
            return self.swing_tp1, self.swing_tp2, self.swing_tp3
        elif style == "POSITION":
            return self.position_tp1, self.position_tp2, self.position_tp3
        else:
            return self.intraday_tp1, self.intraday_tp2, self.intraday_tp3
    
    def get_allocations(self, style: str) -> Tuple[float, float, float]:
        style = style.upper()
        if style == "SCALPING":
            return 0.50, 0.30, 0.20
        elif style == "INTRADAY":
            return 0.40, 0.35, 0.25
        elif style == "SWING":
            return 0.30, 0.30, 0.40
        elif style == "POSITION":
            return 0.20, 0.30, 0.50
        else:
            return 0.40, 0.35, 0.25

@dataclass
class SecurityConfig:
    ENCRYPTION_ENABLED: bool = True
    IP_WHITELIST_ENABLED: bool = False
    ALLOWED_IPS: List[str] = field(default_factory=list)
    TWO_FA_ENABLED: bool = False
    RATE_LIMIT_ENABLED: bool = True
    MAX_REQUESTS_PER_MINUTE: int = 60
    FAILED_ATTEMPT_LIMIT: int = 5

@dataclass
class MLConfig:
    RANDOM_FOREST_ENABLED: bool = True
    GRADIENT_BOOSTING_ENABLED: bool = True
    LSTM_ENABLED: bool = True
    ENSEMBLE_ENABLED: bool = True
    AUTO_RETRAIN: bool = True
    RETRAIN_INTERVAL_HOURS: int = 24
    MODEL_DIR: str = "ml_models"

@dataclass
class RiskConfig:
    KELLY_CRITERION_ENABLED: bool = True
    VAR_CALCULATION_ENABLED: bool = True
    MONTE_CARLO_ENABLED: bool = True
    DRAWDOWN_PROTECTION_ENABLED: bool = True
    MAX_DRAWDOWN_PERCENT: float = 20.0
    POSITION_SIZING_METHOD: str = "kelly"
    CORRELATION_CHECK_ENABLED: bool = True
    MAX_CORRELATION: float = 0.7

@dataclass
class OrderConfig:
    OCO_ENABLED: bool = True
    TRAILING_STOP_ENABLED: bool = True
    ICEBERG_ENABLED: bool = True
    TWAP_ENABLED: bool = True
    VWAP_ENABLED: bool = True
    DEFAULT_TRAILING_CALLBACK: float = 1.0
    DEFAULT_ICEBERG_SIZE: float = 0.1
    DEFAULT_TWAP_SLICES: int = 10

@dataclass
class BacktestConfig:
    WALK_FORWARD_ENABLED: bool = True
    MONTE_CARLO_ENABLED: bool = True
    OPTIMIZATION_ENABLED: bool = True
    MULTI_TIMEFRAME_ENABLED: bool = True
    TRAIN_WINDOW_DAYS: int = 30
    TEST_WINDOW_DAYS: int = 7
    NUM_SIMULATIONS: int = 1000

@dataclass
class PortfolioConfig:
    TRACK_POSITIONS: bool = True
    GENERATE_HEATMAP: bool = True
    CALCULATE_CORRELATION: bool = True
    SECTOR_ALLOCATION: bool = True
    REBALANCE_THRESHOLD: float = 10.0

@dataclass
class PerformanceConfig:
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
    
    # Weights
    ULTRA_SHORT_WEIGHT: float = 0.30
    SHORT_WEIGHT: float = 0.25
    MEDIUM_WEIGHT: float = 0.25
    LONG_WEIGHT: float = 0.20
    
    ENTRY_ORDER_BOOK_DEPTH: int = 10
    ENTRY_MAX_SPREAD_PERCENT: float = 0.05
    ENTRY_USE_MID_PRICE: bool = True
    ENTRY_BUY_BID_LEVEL: int = 1
    ENTRY_SELL_ASK_LEVEL: int = 1
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
    WHALE_DETECTION_ENABLED: bool = True
    WHALE_MIN_ORDER_VALUE: float = 50000.0
    WHALE_CANCEL_DETECTION_ENABLED: bool = True
    WHALE_CANCEL_WINDOW_SECONDS: int = 60
    KEYZONE_ENABLED: bool = True
    KEYZONE_LOOKBACK_BARS: int = 50
    KEYZONE_MIN_TOUCHES: int = 3
    KEYZONE_PULLBACK_PERCENT: float = 0.5
    PULLBACK_ENABLED: bool = True
    PULLBACK_MIN_RETRACE: float = 0.382
    PULLBACK_MAX_RETRACE: float = 0.618
    PULLBACK_CONFIRMATION_CANDLES: int = 2
    DOME_DETECTION_ENABLED: bool = True
    DOME_MIN_POINTS: int = 5
    DOME_MIN_HEIGHT_PERCENT: float = 2.0
    LANGUAGE: str = "en"
    SECURITY_CONFIG: SecurityConfig = field(default_factory=SecurityConfig)
    ML_CONFIG: MLConfig = field(default_factory=MLConfig)
    RISK_CONFIG: RiskConfig = field(default_factory=RiskConfig)
    ORDER_CONFIG: OrderConfig = field(default_factory=OrderConfig)
    BACKTEST_CONFIG: BacktestConfig = field(default_factory=BacktestConfig)
    PORTFOLIO_CONFIG: PortfolioConfig = field(default_factory=PortfolioConfig)
    PERFORMANCE_CONFIG: PerformanceConfig = field(default_factory=PerformanceConfig)
    TP_CONFIG: TpConfig = field(default_factory=TpConfig)

# ==============================================================================
# BINANCE FUTURES CLIENT
# ==============================================================================
class BinanceFuturesClient:
    """Binance Futures Client for API communication"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://fapi.binance.com"
        if hasattr(config, 'FUTURES_CONFIG') and config.FUTURES_CONFIG:
            self.base_url = config.FUTURES_CONFIG.BASE_URL
    
    def test_connection(self) -> bool:
        """Test connection to Binance Futures"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/fapi/v1/ping", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            import requests
            response = requests.get(
                f"{self.base_url}/fapi/v1/ticker/price", 
                params={"symbol": symbol}, 
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
            return None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def get_ticker_24hr(self, symbol: str) -> Optional[Dict]:
        """Get 24hr ticker for symbol"""
        try:
            import requests
            response = requests.get(
                f"{self.base_url}/fapi/v1/ticker/24hr", 
                params={"symbol": symbol}, 
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting ticker for {symbol}: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str, limit: int) -> Optional[pd.DataFrame]:
        """Get klines/candlestick data"""
        try:
            import requests
            import pandas as pd
            response = requests.get(
                f"{self.base_url}/fapi/v1/klines",
                params={"symbol": symbol, "interval": interval, "limit": limit},
                timeout=5
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
            return None
        except Exception as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            return None
    
    def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict]:
        """Get order book data"""
        try:
            import requests
            response = requests.get(
                f"{self.base_url}/fapi/v1/depth",
                params={"symbol": symbol, "limit": limit},
                timeout=5
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
            import requests
            response = requests.get(
                f"{self.base_url}/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": 1},
                timeout=5
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
            import requests
            response = requests.get(
                f"{self.base_url}/fapi/v1/trades",
                params={"symbol": symbol, "limit": limit},
                timeout=5
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

@dataclass
class Config:
    SYMBOLS: List[str] = field(default_factory=lambda: [
        "1INCHUSDT", "AAVEUSDT", "ACHUSDT", "ADAUSDT", "ALGOUSDT", 
        "ALICEUSDT", "API3USDT", "APTUSDT", 
        "ATOMUSDT", "AVAXUSDT", "AXSUSDT", "BANDUSDT", "BATUSDT", "BCHUSDT",
        "BICOUSDT", "BNBUSDT", "BNTUSDT", "BTCUSDT", "C98USDT", "CELOUSDT", 
        "CELRUSDT", "CHRUSDT", "CHZUSDT", "COMPUSDT", "COTIUSDT",
        "CTSIUSDT", "DASHUSDT", "DENTUSDT", "DOTUSDT",
        "DYDXUSDT", "ENSUSDT", "ETCUSDT", "ETHUSDT",
        "FETUSDT", "FILUSDT", "FLOWUSDT", "FLUXUSDT", "GALAUSDT", "GRTUSDT",
        "HBARUSDT", "HOTUSDT", "ICPUSDT", "ICXUSDT", "ILVUSDT", "IMXUSDT",
        "IOSTUSDT", "IOTAUSDT", "IOTXUSDT", "LINKUSDT", "LITUSDT", "LTCUSDT",
        "NEARUSDT", "OPUSDT", "SOLUSDT", "UNIUSDT", "XRPUSDT"
    ])
    
    TIMEFRAMES: Dict[str, str] = field(default_factory=lambda: {
        "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h",
        "2h": "2h", "4h": "4h", "6h": "6h", "8h": "8h", "12h": "12h",
        "1d": "1d", "3d": "3d", "1w": "1w", "1M": "1M"
    })
    
    DEFAULT_TIMEFRAMES: Dict[str, str] = field(default_factory=lambda: {
        "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h",
        "2h": "2h", "4h": "4h", "1d": "1d"
    })
    
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
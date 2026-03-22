#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ULTIMATE HYBRID CRYPTO TRADING BOT - RUN FILE
================================================================================
This file imports all modules and starts the bot.
Just run this single file to start the entire bot.
================================================================================
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from collections import defaultdict, deque

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all required modules
from config_enums import *
from security_ml_risk import *
from advanced_orders_portfolio import *
from bot_main_part1 import *
from bot_main_part2 import *
from bot_main_part3 import *
from bot_main_part4 import *

# ==============================================================================
# ប្រកាស BinanceFuturesClient នៅទីនេះ ក្នុងករណីដែលវាមិនទាន់មានក្នុង config_enums.py
# ==============================================================================
if 'BinanceFuturesClient' not in globals():
    class BinanceFuturesClient:
        """Binance Futures Client for API communication"""
        
        def __init__(self, config):
            self.config = config
            self.base_url = "https://fapi.binance.com"
            if hasattr(config, 'FUTURES_CONFIG') and config.FUTURES_CONFIG:
                self.base_url = config.FUTURES_CONFIG.BASE_URL
        
        def test_connection(self) -> bool:
            try:
                import requests
                response = requests.get(f"{self.base_url}/fapi/v1/ping", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        def get_current_price(self, symbol: str):
            try:
                import requests
                response = requests.get(f"{self.base_url}/fapi/v1/ticker/price", 
                                       params={"symbol": symbol}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return float(data['price'])
                return None
            except:
                return None
        
        def get_ticker_24hr(self, symbol: str):
            try:
                import requests
                response = requests.get(f"{self.base_url}/fapi/v1/ticker/24hr", 
                                       params={"symbol": symbol}, timeout=5)
                if response.status_code == 200:
                    return response.json()
                return {}
            except:
                return {}
        
        def get_klines(self, symbol: str, interval: str, limit: int):
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
            except:
                return None
        
        def get_order_book(self, symbol: str, limit: int = 10):
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
            except:
                return None
        
        def get_funding_rate(self, symbol: str) -> Optional[float]:
            return 0.0
        
        def get_recent_trades(self, symbol: str, limit: int = 100) -> Optional[List]:
            return []
        
        def get_depth_history(self) -> List:
            return []

# ==============================================================================
# ប្រកាស EnhancedBinanceFuturesClient
# ==============================================================================
if 'EnhancedBinanceFuturesClient' not in globals():
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
            return super().test_connection()
        
        def get_depth_history(self) -> List:
            return []
        
        def get_funding_rate(self, symbol: str) -> Optional[float]:
            return super().get_funding_rate(symbol)
        
        def get_recent_trades(self, symbol: str, limit: int = 100) -> Optional[List]:
            return super().get_recent_trades(symbol, limit)

# ==============================================================================
# MAIN FUNCTION (from bot_main_part4)
# ==============================================================================
def main():
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
    
    print("\n" + "="*80)
    print("ULTIMATE HYBRID FUTURES TRADING BOT V12.0.1")
    print("PYDROID OPTIMIZED EDITION - ULTIMATE ACCURACY")
    print("Developer: Nhen Bol")
    print("="*80 + "\n")
    
    print("Select Language (English only):")
    print("1. English")
    lang_choice = input("\nEnter choice (1): ").strip() or "1"
    lang.current_language = Language.ENGLISH
    print(f"\n{lang.get_text('language')}: {lang.get_text('english')}")
    
    if not test_internet_connection():
        print(f"\n❌ {lang.get_text('no_signal')}")
        input("Press Enter to exit...")
        return
    
    config_data = load_hybrid_config()
    
    telegram_config = TelegramConfig(
        BOT_TOKEN=config_data.get('telegram', {}).get('bot_token', ''),
        CHAT_ID=config_data.get('telegram', {}).get('chat_id', ''),
        MIN_CONFIDENCE=float(config_data.get('telegram', {}).get('min_confidence', 70.0)),
        MIN_ACCURACY_SCORE=float(config_data.get('telegram', {}).get('min_accuracy', 75.0)),
        COOLDOWN_MINUTES=int(config_data.get('telegram', {}).get('cooldown_minutes', 30)),
        EMERGENCY_THRESHOLD=float(config_data.get('telegram', {}).get('emergency_threshold', 90.0)),
        HIGH_THRESHOLD=float(config_data.get('telegram', {}).get('high_threshold', 80.0)),
        MEDIUM_THRESHOLD=float(config_data.get('telegram', {}).get('medium_threshold', 70.0)),
        ENABLE_VOICE_ALERTS=bool(config_data.get('telegram', {}).get('enable_voice_alerts', False)),
        ENABLE_BUTTONS=False,
        ENABLE_SUMMARY=bool(config_data.get('telegram', {}).get('enable_summary', True)),
        SUMMARY_INTERVAL_MINUTES=int(config_data.get('telegram', {}).get('summary_interval_minutes', 60)),
        ENABLE_AUTO_TRADE=bool(config_data.get('telegram', {}).get('enable_auto_trade', True)),
        MAX_POSITION_SIZE_USDT=float(config_data.get('telegram', {}).get('max_position_size_usdt', 100.0)),
        DEFAULT_LEVERAGE=int(config_data.get('telegram', {}).get('default_leverage', 5)),
        LANGUAGE='en'
    )
    
    futures_config = BinanceFuturesConfig(
        API_KEY=config_data.get('futures', {}).get('api_key', ''),
        API_SECRET=config_data.get('futures', {}).get('api_secret', ''),
        USE_TESTNET=bool(config_data.get('futures', {}).get('use_testnet', False)),
        REQUEST_TIMEOUT=int(config_data.get('futures', {}).get('request_timeout', 30))
    )
    
    interval = config_data.get('scan', {}).get('interval_seconds', 30)
    continuous = config_data.get('scan', {}).get('continuous', True)
    
    if telegram_config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"\n⚠️ {lang.get_text('warning')}: Please configure Telegram bot in ultimate_v12.0.1_config.json")
        telegram_config.BOT_TOKEN = ""
    
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
    
    hybrid_data = config_data.get('hybrid', {})
    hybrid_config = HybridConfig(
        ENABLE_TIER_1=hybrid_data.get('enable_tier_1', True),
        ENABLE_TIER_2=hybrid_data.get('enable_tier_2', True),
        ENABLE_TIER_3=hybrid_data.get('enable_tier_3', True),
        SCAN_TOP_SYMBOLS=hybrid_data.get('scan_top_symbols', 100),
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
        AI_CONFIDENCE_MODEL_ENABLED=hybrid_data.get('ai_confidence_model_enabled', True),
        WHALE_DETECTION_ENABLED=hybrid_data.get('whale_detection_enabled', True),
        KEYZONE_ENABLED=hybrid_data.get('keyzone_enabled', True),
        PULLBACK_ENABLED=hybrid_data.get('pullback_enabled', True),
        DOME_DETECTION_ENABLED=hybrid_data.get('dome_detection_enabled', True),
        LANGUAGE='en',
        TP_CONFIG=tp_config
    )
    
    # Create Config object
    config = Config()
    config.TELEGRAM_CONFIG = telegram_config
    config.FUTURES_CONFIG = futures_config
    config.HYBRID_CONFIG = hybrid_config
    
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
    
    try:
        # Import UltimateHybridBot from bot_main_part4
        from bot_main_part4 import UltimateHybridBot
        bot = UltimateHybridBot(telegram_config, futures_config)
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return
    
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
    
    while True:
        choice = input(f"\n{lang.get_text('start')} (0-9): ").strip()
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
        print("\n" + "="*80)
        print("🚀 ULTIMATE HYBRID TRADING BOT V1.0.0 - STARTING...")
        print("="*80 + "\n")
        
        # Run the main function
        main()
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Bot stopped by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
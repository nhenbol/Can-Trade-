#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
BINANCE FUTURES CLIENT FOR ULTIMATE HYBRID TRADING BOT
================================================================================
"""

from config_enums import *

class BinanceFuturesClient:
    """Binance Futures Client for API communication"""
    
    def __init__(self, config: 'Config'):
        self.config = config
        self.base_url = "https://fapi.binance.com"
        if config.FUTURES_CONFIG:
            self.base_url = config.FUTURES_CONFIG.BASE_URL
    
    def test_connection(self) -> bool:
        """Test connection to Binance Futures"""
        try:
            response = requests.get(f"{self.base_url}/fapi/v1/ping", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
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
        # This is a placeholder - in production, you would implement proper authentication
        logger.warning("_make_request not fully implemented - using placeholder")
        return None


class EnhancedBinanceFuturesClient(BinanceFuturesClient):
    """Enhanced Binance Futures Client with additional features"""
    
    def __init__(self, config: Config):
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
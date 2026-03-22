#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
ULTIMATE HYBRID CRYPTO TRADING BOT - ADVANCED ORDERS, PORTFOLIO, PERFORMANCE
================================================================================
"""

from config_enums import *
from security_ml_risk import *

# ==============================================================================
# ADVANCED ORDER EXECUTOR
# ==============================================================================
class AdvancedOrderExecutor:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.active_orders = {}
        self.trailing_stops = {}
        self.twap_schedules = {}
        self.iceberg_orders = {}
        self.order_history = []
        self.monitoring_thread = None
        self._start_monitoring()
    
    def _start_monitoring(self):
        def monitor():
            while True:
                try:
                    self.monitor_trailing_stops()
                    self.monitor_twap_schedules()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
        self.monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self.monitoring_thread.start()
    
    def place_oco_order(self, symbol: str, side: str, quantity: float, price: float,
                        stop_price: float, limit_price: float) -> Optional[Dict]:
        try:
            params = {
                'symbol': symbol, 'side': side.upper(), 'quantity': quantity, 'price': price,
                'stopPrice': stop_price, 'stopLimitPrice': limit_price, 'stopLimitTimeInForce': 'GTC'
            }
            result = self.client._make_request("POST", "/fapi/v1/order/oco", params, signed=True)
            if result:
                order_id = result.get('orderId', 'Unknown')
                self.active_orders[order_id] = {
                    'type': 'OCO', 'symbol': symbol, 'side': side, 'quantity': quantity,
                    'price': price, 'stop_price': stop_price, 'limit_price': limit_price,
                    'time': time.time(), 'status': 'ACTIVE'
                }
                self.order_history.append({
                    'order_id': order_id, 'type': 'OCO', 'symbol': symbol, 'side': side,
                    'quantity': quantity, 'price': price, 'time': datetime.now().isoformat()
                })
                logger.info(f"✅ OCO order placed: {symbol} {side} {quantity}")
            return result
        except Exception as e:
            logger.error(f"OCO order error: {e}")
            return None
    
    def place_trailing_stop(self, symbol: str, side: str, quantity: float, 
                           activation_price: float, callback_rate: float) -> Optional[Dict]:
        try:
            params = {
                'symbol': symbol, 'side': side.upper(), 'type': 'TRAILING_STOP_MARKET',
                'quantity': quantity, 'callbackRate': callback_rate, 'activationPrice': activation_price
            }
            result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
            if result:
                order_id = result.get('orderId', 'Unknown')
                current_price = self.client.get_current_price(symbol)
                self.trailing_stops[order_id] = {
                    'symbol': symbol, 'side': side, 'quantity': quantity,
                    'activation_price': activation_price, 'callback_rate': callback_rate,
                    'initial_price': current_price,
                    'highest_price': current_price if side == 'SELL' else 0,
                    'lowest_price': current_price if side == 'BUY' else float('inf'),
                    'time': time.time(), 'status': 'ACTIVE'
                }
                self.order_history.append({
                    'order_id': order_id, 'type': 'TRAILING_STOP', 'symbol': symbol,
                    'side': side, 'quantity': quantity, 'activation_price': activation_price,
                    'time': datetime.now().isoformat()
                })
                logger.info(f"✅ Trailing stop placed: {symbol} {side} {quantity}")
            return result
        except Exception as e:
            logger.error(f"Trailing stop error: {e}")
            return None
    
    def monitor_trailing_stops(self):
        try:
            for order_id, data in list(self.trailing_stops.items()):
                if data.get('status') != 'ACTIVE':
                    continue
                current_price = self.client.get_current_price(data['symbol'])
                if not current_price:
                    continue
                
                if data['side'] == 'SELL':
                    if current_price > data['highest_price']:
                        data['highest_price'] = current_price
                        stop_distance = data['highest_price'] * (data['callback_rate'] / 100)
                        new_stop = data['highest_price'] - stop_distance
                        logger.debug(f"Trailing stop updated for {data['symbol']}: {new_stop:.4f}")
                else:
                    if current_price < data['lowest_price']:
                        data['lowest_price'] = current_price
                        stop_distance = data['lowest_price'] * (data['callback_rate'] / 100)
                        new_stop = data['lowest_price'] + stop_distance
                        logger.debug(f"Trailing stop updated for {data['symbol']}: {new_stop:.4f}")
        except Exception as e:
            logger.error(f"Trailing stop monitoring error: {e}")
    
    def monitor_twap_schedules(self):
        try:
            current_time = time.time()
            for schedule_id, schedule in list(self.twap_schedules.items()):
                if schedule.get('completed', False):
                    continue
                if current_time >= schedule.get('next_execution', float('inf')):
                    self._execute_twap_slice(schedule_id, schedule)
        except Exception as e:
            logger.error(f"TWAP monitoring error: {e}")
    
    def _execute_twap_slice(self, schedule_id: str, schedule: Dict):
        try:
            if schedule['remaining'] <= 0:
                schedule['completed'] = True
                return
            
            current_price = self.client.get_current_price(schedule['symbol'])
            if not current_price:
                return
            
            slice_qty = min(schedule['slice_qty'], schedule['remaining'])
            params = {
                'symbol': schedule['symbol'], 'side': schedule['side'].upper(), 'type': 'LIMIT',
                'timeInForce': 'GTC', 'quantity': slice_qty, 'price': current_price
            }
            result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
            
            if result:
                order_id = result.get('orderId', 'Unknown')
                schedule['orders'].append(order_id)
                schedule['remaining'] -= slice_qty
                schedule['slices_executed'] = schedule.get('slices_executed', 0) + 1
                logger.info(f"TWAP slice executed for {schedule['symbol']}: {slice_qty} @ {current_price}")
            
            schedule['next_execution'] = time.time() + schedule['interval']
        except Exception as e:
            logger.error(f"TWAP slice execution error: {e}")
    
    def place_iceberg_order(self, symbol: str, side: str, total_quantity: float,
                           price: float, iceberg_qty: float) -> List[Dict]:
        try:
            orders = []
            remaining = total_quantity
            
            while remaining > 0:
                qty = min(iceberg_qty, remaining)
                params = {
                    'symbol': symbol, 'side': side.upper(), 'type': 'LIMIT',
                    'timeInForce': 'GTC', 'quantity': qty, 'price': price
                }
                result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
                
                if result:
                    order_id = result.get('orderId', 'Unknown')
                    orders.append(result)
                    
                    if order_id not in self.iceberg_orders:
                        self.iceberg_orders[order_id] = {
                            'symbol': symbol, 'side': side,
                            'total_quantity': total_quantity, 'filled_quantity': 0,
                            'remaining': remaining - qty, 'iceberg_qty': iceberg_qty,
                            'price': price, 'child_orders': []
                        }
                    
                    self.iceberg_orders[order_id]['child_orders'].append(order_id)
                    remaining -= qty
                    time.sleep(0.5)
                else:
                    break
            
            self.order_history.append({
                'type': 'ICEBERG', 'symbol': symbol, 'side': side,
                'total_quantity': total_quantity, 'iceberg_qty': iceberg_qty,
                'price': price, 'orders_count': len(orders),
                'time': datetime.now().isoformat()
            })
            logger.info(f"✅ Iceberg order placed: {symbol} {side} total={total_quantity} in {len(orders)} pieces")
            return orders
        except Exception as e:
            logger.error(f"Iceberg order error: {e}")
            return []
    
    def execute_twap(self, symbol: str, side: str, total_quantity: float,
                    duration_minutes: int, num_slices: int = 10) -> List[Dict]:
        try:
            orders = []
            slice_qty = total_quantity / num_slices
            interval_seconds = (duration_minutes * 60) / num_slices
            schedule_id = f"twap_{symbol}_{int(time.time())}"
            
            self.twap_schedules[schedule_id] = {
                'symbol': symbol, 'side': side, 'total_quantity': total_quantity,
                'remaining': total_quantity, 'slice_qty': slice_qty,
                'num_slices': num_slices, 'interval': interval_seconds,
                'start_time': time.time(), 'next_execution': time.time(),
                'orders': [], 'slices_executed': 0, 'completed': False
            }
            
            current_price = self.client.get_current_price(symbol)
            if current_price:
                params = {
                    'symbol': symbol, 'side': side.upper(), 'type': 'LIMIT',
                    'timeInForce': 'GTC', 'quantity': slice_qty, 'price': current_price
                }
                result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
                
                if result:
                    order_id = result.get('orderId', 'Unknown')
                    orders.append(result)
                    self.twap_schedules[schedule_id]['orders'].append(order_id)
                    self.twap_schedules[schedule_id]['remaining'] -= slice_qty
                    self.twap_schedules[schedule_id]['slices_executed'] = 1
                    self.twap_schedules[schedule_id]['next_execution'] = time.time() + interval_seconds
            
            self.order_history.append({
                'type': 'TWAP', 'schedule_id': schedule_id, 'symbol': symbol, 'side': side,
                'total_quantity': total_quantity, 'num_slices': num_slices,
                'duration_minutes': duration_minutes, 'time': datetime.now().isoformat()
            })
            logger.info(f"✅ TWAP schedule created: {symbol} {side} over {duration_minutes}min")
            return orders
        except Exception as e:
            logger.error(f"TWAP execution error: {e}")
            return []
    
    def execute_vwap(self, symbol: str, side: str, total_quantity: float,
                    volume_profile: Dict[str, float]) -> List[Dict]:
        try:
            orders = []
            total_volume = sum(volume_profile.values())
            
            if total_volume == 0:
                return self.execute_twap(symbol, side, total_quantity, 30)
            
            for period, volume_ratio in volume_profile.items():
                period_qty = total_quantity * (volume_ratio / total_volume)
                if period_qty < 0.001:
                    continue
                
                current_price = self.client.get_current_price(symbol)
                if current_price:
                    params = {
                        'symbol': symbol, 'side': side.upper(), 'type': 'LIMIT',
                        'timeInForce': 'GTC', 'quantity': period_qty, 'price': current_price
                    }
                    result = self.client._make_request("POST", "/fapi/v1/order", params, signed=True)
                    if result:
                        orders.append(result)
                    
                    delay_seconds = max(1, int(60 * (1 - volume_ratio / total_volume)))
                    time.sleep(delay_seconds)
            
            self.order_history.append({
                'type': 'VWAP', 'symbol': symbol, 'side': side,
                'total_quantity': total_quantity, 'orders_count': len(orders),
                'time': datetime.now().isoformat()
            })
            logger.info(f"✅ VWAP execution completed: {symbol} {side}")
            return orders
        except Exception as e:
            logger.error(f"VWAP execution error: {e}")
            return []
    
    def cancel_oco_order(self, symbol: str, order_id: str) -> bool:
        try:
            params = {'symbol': symbol, 'orderId': order_id}
            result = self.client._make_request("DELETE", "/fapi/v1/order", params, signed=True)
            if result and order_id in self.active_orders:
                self.active_orders[order_id]['status'] = 'CANCELLED'
                del self.active_orders[order_id]
                logger.info(f"✅ OCO order cancelled: {order_id}")
            return result is not None
        except Exception as e:
            logger.error(f"Cancel OCO error: {e}")
            return False
    
    def cancel_trailing_stop(self, order_id: str) -> bool:
        try:
            if order_id in self.trailing_stops:
                data = self.trailing_stops[order_id]
                params = {'symbol': data['symbol'], 'orderId': order_id}
                result = self.client._make_request("DELETE", "/fapi/v1/order", params, signed=True)
                if result:
                    self.trailing_stops[order_id]['status'] = 'CANCELLED'
                    del self.trailing_stops[order_id]
                    logger.info(f"✅ Trailing stop cancelled: {order_id}")
                return result is not None
            return False
        except Exception as e:
            logger.error(f"Cancel trailing stop error: {e}")
            return False
    
    def cancel_all_orders(self, symbol: str) -> bool:
        try:
            params = {'symbol': symbol}
            result = self.client._make_request("DELETE", "/fapi/v1/allOpenOrders", params, signed=True)
            
            for order_id in list(self.active_orders.keys()):
                if self.active_orders[order_id]['symbol'] == symbol:
                    del self.active_orders[order_id]
            
            for order_id in list(self.trailing_stops.keys()):
                if self.trailing_stops[order_id]['symbol'] == symbol:
                    del self.trailing_stops[order_id]
            
            logger.info(f"✅ All orders cancelled for {symbol}")
            return result is not None
        except Exception as e:
            logger.error(f"Cancel all orders error: {e}")
            return False
    
    def get_order_status(self, symbol: str, order_id: str) -> Optional[Dict]:
        try:
            params = {'symbol': symbol, 'orderId': order_id}
            return self.client._make_request("GET", "/fapi/v1/order", params, signed=True)
        except Exception as e:
            logger.error(f"Order status error: {e}")
            return None
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            return self.client._make_request("GET", "/fapi/v1/openOrders", params, signed=True) or []
        except Exception as e:
            logger.error(f"Get open orders error: {e}")
            return []
    
    def get_order_history(self, limit: int = 100) -> List[Dict]:
        return self.order_history[-limit:]

# ==============================================================================
# PORTFOLIO MANAGEMENT
# ==============================================================================
@dataclass
class PortfolioPosition:
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    allocation: float
    beta: float
    correlation: float
    sector: str
    style: str
    tier: str
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    leverage: int = 1

class PortfolioManager:
    def __init__(self, initial_capital: float = 10000.0):
        self.positions: Dict[str, PortfolioPosition] = {}
        self.position_history: List[Dict] = []
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.sector_allocation = defaultdict(float)
        self.style_allocation = defaultdict(float)
        self.tier_allocation = defaultdict(float)
        self.correlation_matrix = {}
        self.heatmap_data = {}
        self.returns_data: Dict[str, List[float]] = defaultdict(list)
        self.rebalance_threshold = 10.0
        
    def update_position(self, symbol: str, quantity: float, entry_price: float,
                        sector: str = "Unknown", style: str = "Unknown", 
                        tier: str = "Unknown", stop_loss: Optional[float] = None,
                        take_profit: Optional[float] = None, leverage: int = 1):
        current_price = entry_price
        position = PortfolioPosition(
            symbol=symbol, quantity=quantity, entry_price=entry_price,
            current_price=current_price, pnl=0, pnl_percentage=0,
            allocation=quantity * entry_price, beta=1.0, correlation=0.5,
            sector=sector, style=style, tier=tier, entry_time=datetime.now(),
            stop_loss=stop_loss, take_profit=take_profit, leverage=leverage
        )
        self.positions[symbol] = position
        self._update_allocations()
        logger.info(f"✅ Position added: {symbol} {quantity} @ {entry_price}")
    
    def close_position(self, symbol: str, exit_price: float, reason: str = "MANUAL"):
        if symbol in self.positions:
            pos = self.positions[symbol]
            pnl = (exit_price - pos.entry_price) * pos.quantity
            pnl_percentage = (exit_price / pos.entry_price - 1) * 100
            
            trade_record = {
                'symbol': symbol, 'entry_price': pos.entry_price, 'exit_price': exit_price,
                'quantity': pos.quantity, 'pnl': pnl, 'pnl_percentage': pnl_percentage,
                'sector': pos.sector, 'style': pos.style, 'tier': pos.tier, 'leverage': pos.leverage,
                'entry_time': pos.entry_time, 'exit_time': datetime.now(),
                'duration': (datetime.now() - pos.entry_time).total_seconds() / 3600, 'reason': reason
            }
            
            self.position_history.append(trade_record)
            self.current_capital += pnl
            
            if pnl_percentage != 0:
                self.returns_data[symbol].append(pnl_percentage)
            
            del self.positions[symbol]
            self._update_allocations()
            logger.info(f"✅ Position closed: {symbol} @ {exit_price} (P&L: {pnl:.2f}, {pnl_percentage:.2f}%)")
    
    def update_prices(self, price_data: Dict[str, float]):
        total_value = 0
        for symbol, price in price_data.items():
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.current_price = price
                pos.pnl = (price - pos.entry_price) * pos.quantity
                pos.pnl_percentage = (price / pos.entry_price - 1) * 100
                pos.allocation = price * pos.quantity
                total_value += pos.allocation
                
                if pos.pnl_percentage != 0:
                    self.returns_data[symbol].append(pos.pnl_percentage)
        
        self.current_capital = total_value + (self.initial_capital - sum(p.entry_price * p.quantity for p in self.positions.values()))
    
    def _update_allocations(self):
        self.sector_allocation.clear()
        self.style_allocation.clear()
        self.tier_allocation.clear()
        
        total_value = sum(p.allocation for p in self.positions.values())
        if total_value == 0:
            return
        
        for pos in self.positions.values():
            weight = pos.allocation / total_value * 100
            self.sector_allocation[pos.sector] += weight
            self.style_allocation[pos.style] += weight
            self.tier_allocation[pos.tier] += weight
    
    def calculate_correlation_matrix(self, min_periods: int = 20) -> pd.DataFrame:
        symbols = list(self.positions.keys())
        if len(symbols) < 2:
            return pd.DataFrame()
        
        returns_matrix = []
        valid_symbols = []
        
        for symbol in symbols:
            if symbol in self.returns_data and len(self.returns_data[symbol]) >= min_periods:
                returns_matrix.append(self.returns_data[symbol][-100:])
                valid_symbols.append(symbol)
        
        if len(valid_symbols) < 2:
            return pd.DataFrame()
        
        min_len = min(len(r) for r in returns_matrix)
        returns_matrix = [r[:min_len] for r in returns_matrix]
        corr_matrix = np.corrcoef(returns_matrix)
        df = pd.DataFrame(corr_matrix, index=valid_symbols, columns=valid_symbols)
        self.correlation_matrix = df.to_dict()
        return df
    
    def calculate_beta(self, symbol: str, market_returns: List[float]) -> float:
        if symbol not in self.returns_data or len(self.returns_data[symbol]) < 20:
            return 1.0
        
        asset_returns = self.returns_data[symbol][-len(market_returns):]
        if len(asset_returns) != len(market_returns) or len(asset_returns) < 20:
            return 1.0
        
        covariance = np.cov(asset_returns, market_returns)[0][1]
        variance = np.var(market_returns)
        return covariance / variance if variance > 0 else 1.0
    
    def generate_heatmap(self) -> Dict:
        heatmap = {
            'sectors': {}, 'styles': {}, 'tiers': {}, 'pnl_by_symbol': {},
            'allocation_by_symbol': {}, 'risk_by_symbol': {}
        }
        
        for symbol, pos in self.positions.items():
            heatmap['pnl_by_symbol'][symbol] = pos.pnl_percentage
            heatmap['allocation_by_symbol'][symbol] = pos.allocation
            risk = abs(pos.stop_loss - pos.entry_price) / pos.entry_price * 100 if pos.stop_loss else 2.0
            heatmap['risk_by_symbol'][symbol] = risk
        
        heatmap['sectors'] = dict(self.sector_allocation)
        heatmap['styles'] = dict(self.style_allocation)
        heatmap['tiers'] = dict(self.tier_allocation)
        self.heatmap_data = heatmap
        return heatmap
    
    def get_portfolio_summary(self) -> Dict:
        total_value = sum(p.allocation for p in self.positions.values())
        total_pnl = sum(p.pnl for p in self.positions.values())
        total_pnl_pct = (total_pnl / self.initial_capital * 100) if self.initial_capital > 0 else 0
        
        avg_beta = np.mean([p.beta for p in self.positions.values()]) if self.positions else 1.0
        num_sectors = len(self.sector_allocation)
        num_positions = len(self.positions)
        
        if num_positions == 0:
            diversification = 0
        elif num_positions == 1:
            diversification = 20
        else:
            weights = [p.allocation / total_value for p in self.positions.values()] if total_value > 0 else []
            hhi = sum(w ** 2 for w in weights) * 100
            diversification = 100 - min(hhi, 100)
        
        best_performer = None
        worst_performer = None
        
        if self.positions:
            best_performer = max(self.positions.values(), key=lambda p: p.pnl_percentage)
            worst_performer = min(self.positions.values(), key=lambda p: p.pnl_percentage)
        
        total_exposure = sum(p.allocation * p.leverage for p in self.positions.values())
        
        return {
            'total_value': total_value, 'total_pnl': total_pnl, 'total_pnl_percentage': total_pnl_pct,
            'num_positions': num_positions, 'num_sectors': num_sectors, 'avg_beta': avg_beta,
            'diversification_score': diversification, 'total_exposure': total_exposure,
            'sector_allocation': dict(self.sector_allocation), 'style_allocation': dict(self.style_allocation),
            'tier_allocation': dict(self.tier_allocation),
            'largest_position': max(self.positions.values(), key=lambda p: p.allocation).symbol if self.positions else None,
            'best_performer': best_performer.symbol if best_performer else None,
            'best_performer_pnl': best_performer.pnl_percentage if best_performer else 0,
            'worst_performer': worst_performer.symbol if worst_performer else None,
            'worst_performer_pnl': worst_performer.pnl_percentage if worst_performer else 0,
            'heatmap': self.generate_heatmap(),
            'needs_rebalancing': self._check_rebalancing_needed()
        }
    
    def _check_rebalancing_needed(self) -> bool:
        if not self.positions:
            return False
        
        target_allocation = 100.0 / len(self.positions)
        for pos in self.positions.values():
            current_allocation = (pos.allocation / sum(p.allocation for p in self.positions.values())) * 100
            if abs(current_allocation - target_allocation) > self.rebalance_threshold:
                return True
        return False
    
    def get_position_history(self, days: int = 30) -> List[Dict]:
        cutoff = datetime.now() - timedelta(days=days)
        return [h for h in self.position_history if h['exit_time'] > cutoff]
    
    def get_monthly_performance(self) -> Dict[str, float]:
        monthly_pnl = defaultdict(float)
        for trade in self.position_history:
            month_key = trade['exit_time'].strftime('%Y-%m')
            monthly_pnl[month_key] += trade['pnl']
        return dict(monthly_pnl)
    
    def get_open_positions(self) -> List[Dict]:
        positions = []
        for symbol, pos in self.positions.items():
            positions.append({
                'symbol': symbol, 'quantity': pos.quantity, 'entry_price': pos.entry_price,
                'current_price': pos.current_price, 'pnl': pos.pnl, 'pnl_percentage': pos.pnl_percentage,
                'allocation': pos.allocation, 'sector': pos.sector, 'style': pos.style, 'tier': pos.tier,
                'entry_time': pos.entry_time.isoformat(), 'stop_loss': pos.stop_loss,
                'take_profit': pos.take_profit, 'leverage': pos.leverage
            })
        return positions

# ==============================================================================
# PERFORMANCE ANALYTICS
# ==============================================================================
class PerformanceAnalytics:
    def __init__(self):
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        self.monthly_returns = []
        self.yearly_returns = []
        self.metrics = {}
        
    def add_trade(self, trade_data: Dict):
        self.trades.append(trade_data)
        
        if self.equity_curve:
            last_equity = self.equity_curve[-1]['equity']
            new_equity = last_equity + trade_data.get('pnl', 0)
        else:
            new_equity = trade_data.get('initial_capital', 10000) + trade_data.get('pnl', 0)
        
        self.equity_curve.append({
            'timestamp': trade_data.get('exit_time', datetime.now()),
            'equity': new_equity, 'trade_id': trade_data.get('trade_id', len(self.trades))
        })
        
        trade_date = trade_data.get('exit_time', datetime.now()).date()
        daily_entry = next((item for item in self.daily_returns if item['date'] == trade_date), None)
        
        if daily_entry:
            daily_entry['return'] += trade_data.get('pnl', 0)
            daily_entry['trades'] += 1
        else:
            self.daily_returns.append({'date': trade_date, 'return': trade_data.get('pnl', 0), 'trades': 1})
    
    def calculate_equity_curve(self) -> pd.DataFrame:
        if not self.equity_curve:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.equity_curve)
        df.set_index('timestamp', inplace=True)
        df['peak'] = df['equity'].cummax()
        df['drawdown'] = (df['peak'] - df['equity']) / df['peak'] * 100
        df['drawdown'] = df['drawdown'].clip(lower=0)
        df['returns'] = df['equity'].pct_change()
        return df
    
    def generate_monthly_report(self, year: int = None, month: int = None) -> Dict:
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        month_trades = []
        for trade in self.trades:
            exit_time = trade.get('exit_time')
            if exit_time and exit_time.year == year and exit_time.month == month:
                month_trades.append(trade)
        
        if not month_trades:
            return {'error': 'No trades for this month'}
        
        total_trades = len(month_trades)
        winning_trades = [t for t in month_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in month_trades if t.get('pnl', 0) < 0]
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        total_pnl = sum(t.get('pnl', 0) for t in month_trades)
        avg_win = np.mean([t.get('pnl', 0) for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.get('pnl', 0) for t in losing_trades])) if losing_trades else 0
        profit_factor = (len(winning_trades) * avg_win) / (len(losing_trades) * avg_loss + 1e-10)
        
        # Symbol performance
        symbol_performance = defaultdict(lambda: {'trades': 0, 'pnl': 0, 'win_rate': 0})
        for trade in month_trades:
            symbol = trade.get('symbol', 'Unknown')
            symbol_performance[symbol]['trades'] += 1
            symbol_performance[symbol]['pnl'] += trade.get('pnl', 0)
        
        for symbol in symbol_performance:
            symbol_trades = [t for t in month_trades if t.get('symbol') == symbol]
            symbol_wins = [t for t in symbol_trades if t.get('pnl', 0) > 0]
            symbol_performance[symbol]['win_rate'] = len(symbol_wins) / len(symbol_trades) * 100 if symbol_trades else 0
        
        # Consecutive wins/losses
        consecutive_wins = 0
        max_consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_losses = 0
        
        for trade in month_trades:
            if trade.get('pnl', 0) > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        returns = [t.get('return_pct', 0) for t in month_trades if 'return_pct' in t]
        sharpe = np.mean(returns) / (np.std(returns) + 0.001) * np.sqrt(252) if returns else 0
        
        return {
            'year': year, 'month': month, 'month_name': datetime(year, month, 1).strftime('%B'),
            'total_trades': total_trades, 'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades), 'win_rate': win_rate, 'total_pnl': total_pnl,
            'avg_win': avg_win, 'avg_loss': avg_loss, 'profit_factor': profit_factor,
            'sharpe_ratio': sharpe, 'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'symbol_performance': dict(symbol_performance)
        }
    
    def generate_yearly_report(self, year: int = None) -> Dict:
        if year is None:
            year = datetime.now().year
        
        year_trades = [t for t in self.trades if t.get('exit_time', datetime.now()).year == year]
        if not year_trades:
            return {'error': 'No trades for this year'}
        
        total_trades = len(year_trades)
        winning_trades = [t for t in year_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in year_trades if t.get('pnl', 0) < 0]
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        total_pnl = sum(t.get('pnl', 0) for t in year_trades)
        returns = [t.get('return_pct', 0) for t in year_trades if 'return_pct' in t]
        sharpe = np.mean(returns) / (np.std(returns) + 0.001) * np.sqrt(252) if returns else 0
        
        return {
            'year': year, 'total_trades': total_trades, 'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades), 'win_rate': win_rate, 'total_pnl': total_pnl,
            'sharpe_ratio': sharpe
        }
    
    def win_rate_by_symbol(self, min_trades: int = 5) -> Dict:
        symbol_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        for trade in self.trades:
            symbol = trade.get('symbol', 'Unknown')
            symbol_stats[symbol]['trades'] += 1
            symbol_stats[symbol]['pnl'] += trade.get('pnl', 0)
            if trade.get('pnl', 0) > 0:
                symbol_stats[symbol]['wins'] += 1
        
        result = {}
        for symbol, stats in symbol_stats.items():
            if stats['trades'] >= min_trades:
                result[symbol] = {
                    'trades': stats['trades'], 'win_rate': stats['wins'] / stats['trades'] * 100,
                    'total_pnl': stats['pnl'], 'avg_pnl': stats['pnl'] / stats['trades']
                }
        
        return dict(sorted(result.items(), key=lambda x: x[1]['win_rate'], reverse=True))
    
    def win_rate_by_style(self, min_trades: int = 3) -> Dict:
        style_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        for trade in self.trades:
            style = trade.get('style', 'Unknown')
            style_stats[style]['trades'] += 1
            style_stats[style]['pnl'] += trade.get('pnl', 0)
            if trade.get('pnl', 0) > 0:
                style_stats[style]['wins'] += 1
        
        result = {}
        for style, stats in style_stats.items():
            if stats['trades'] >= min_trades:
                result[style] = {
                    'trades': stats['trades'], 'win_rate': stats['wins'] / stats['trades'] * 100,
                    'total_pnl': stats['pnl'], 'avg_pnl': stats['pnl'] / stats['trades']
                }
        return result
    
    def win_rate_by_tier(self, min_trades: int = 3) -> Dict:
        tier_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        for trade in self.trades:
            tier = trade.get('tier', 'Unknown')
            tier_stats[tier]['trades'] += 1
            tier_stats[tier]['pnl'] += trade.get('pnl', 0)
            if trade.get('pnl', 0) > 0:
                tier_stats[tier]['wins'] += 1
        
        result = {}
        for tier, stats in tier_stats.items():
            if stats['trades'] >= min_trades:
                result[tier] = {
                    'trades': stats['trades'], 'win_rate': stats['wins'] / stats['trades'] * 100,
                    'total_pnl': stats['pnl'], 'avg_pnl': stats['pnl'] / stats['trades']
                }
        return result
    
    def calculate_max_drawdown(self) -> float:
        if not self.equity_curve:
            return 0.0
        df = self.calculate_equity_curve()
        return df['drawdown'].max() if not df.empty else 0.0
    
    def calculate_sortino_ratio(self) -> float:
        if len(self.trades) < 10:
            return 0.0
        returns = [t.get('return_pct', 0) for t in self.trades if 'return_pct' in t]
        mean_return = np.mean(returns)
        downside_returns = [r for r in returns if r < 0]
        downside_std = np.std(downside_returns) if downside_returns else 0.001
        return mean_return / downside_std * np.sqrt(252) if downside_std > 0 else 0.0
    
    def calculate_calmar_ratio(self) -> float:
        if len(self.trades) < 5:
            return 0.0
        total_return = (self.equity_curve[-1]['equity'] - self.equity_curve[0]['equity']) / self.equity_curve[0]['equity'] * 100
        max_dd = self.calculate_max_drawdown()
        return total_return / max_dd if max_dd > 0 else 0.0
    
    def get_comprehensive_stats(self) -> Dict:
        if not self.trades:
            return {'error': 'No trades'}
        
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('pnl', 0) < 0]
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        total_pnl = sum(t.get('pnl', 0) for t in self.trades)
        avg_win = np.mean([t.get('pnl', 0) for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.get('pnl', 0) for t in losing_trades])) if losing_trades else 0
        profit_factor = (len(winning_trades) * avg_win) / (len(losing_trades) * avg_loss + 1e-10)
        
        # Consecutive wins/losses
        consecutive_wins = 0
        max_consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_losses = 0
        
        for trade in self.trades:
            if trade.get('pnl', 0) > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        returns = [t.get('return_pct', 0) for t in self.trades if 'return_pct' in t]
        sharpe = np.mean(returns) / (np.std(returns) + 0.001) * np.sqrt(252) if returns else 0
        sortino = self.calculate_sortino_ratio()
        max_dd = self.calculate_max_drawdown()
        calmar = self.calculate_calmar_ratio()
        
        durations = [t.get('duration', 0) for t in self.trades if 'duration' in t]
        avg_duration = np.mean(durations) if durations else 0
        
        return {
            'total_trades': total_trades, 'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades), 'win_rate': win_rate, 'total_pnl': total_pnl,
            'avg_win': avg_win, 'avg_loss': avg_loss, 'profit_factor': profit_factor,
            'sharpe_ratio': sharpe, 'sortino_ratio': sortino, 'calmar_ratio': calmar,
            'max_drawdown': max_dd, 'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses, 'avg_duration_hours': avg_duration,
            'by_symbol': self.win_rate_by_symbol(), 'by_style': self.win_rate_by_style(),
            'by_tier': self.win_rate_by_tier()
        }
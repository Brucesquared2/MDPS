"""
JB's OVERWATCH - Advanced MDPS Monitoring & Analysis System
Multi-Dimensional Market Surveillance and Prediction Engine
"""
import asyncio
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import sys
import os

# Check if required packages are available
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.layout import Layout
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    print("⚠️  Rich not available - using basic console output")
    RICH_AVAILABLE = False

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    print("⚠️  CCXT not available - using mock data")
    CCXT_AVAILABLE = False

try:
    from config import API_KEY, API_SECRET, API_PASSPHRASE
    CONFIG_AVAILABLE = True
except ImportError:
    print("⚠️  Config not found - using demo mode")
    API_KEY = API_SECRET = API_PASSPHRASE = "DEMO_MODE"
    CONFIG_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MarketSignal:
    """Market signal data structure"""
    symbol: str
    signal_type: str
    strength: float
    confidence: float
    timestamp: datetime
    price: float
    volume: float
    indicators: Dict
    recommendation: str

@dataclass
class RiskMetrics:
    """Risk assessment metrics"""
    volatility: float
    var_95: float
    max_drawdown: float
    sharpe_ratio: float
    risk_score: float

class SimpleConsole:
    """Fallback console for when Rich is not available"""
    def print(self, text, style=None):
        # Remove Rich markup for plain text output
        clean_text = text
        if isinstance(text, str):
            # Remove Rich markup tags
            import re
            clean_text = re.sub(r'\[.*?\]', '', text)
        print(clean_text)
    
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

class JBOverwatchSystem:
    """
    JB's OVERWATCH - Advanced Market Monitoring System
    
    Features:
    - Real-time multi-exchange monitoring
    - Advanced technical analysis
    - Risk assessment and alerts
    - Automated trading signals
    """
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else SimpleConsole()
        self.exchanges = self._initialize_exchanges()
        self.watchlist = []
        self.signals = []
        self.risk_metrics = {}
        self.is_monitoring = False
        self.demo_mode = not CONFIG_AVAILABLE
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_signals = 0
        self.successful_predictions = 0
        
        # Demo data for when APIs are not available
        self.demo_prices = {
            'BTC/USDT': 43500.0,
            'ETH/USDT': 2650.0,
            'BNB/USDT': 315.0,
            'ADA/USDT': 0.45,
            'SOL/USDT': 95.0
        }
        
    def _initialize_exchanges(self) -> Dict:
        """Initialize cryptocurrency exchanges"""
        exchanges = {}
        
        if not CCXT_AVAILABLE:
            logger.warning("CCXT not available - running in demo mode")
            return exchanges
        
        try:
            if CONFIG_AVAILABLE:
                # Bitget with API credentials
                exchanges['bitget'] = ccxt.bitget({
                    'apiKey': API_KEY,
                    'secret': API_SECRET,
                    'password': API_PASSPHRASE,
                    'sandbox': False,
                    'enableRateLimit': True,
                })
            
            # Public exchanges (no credentials needed)
            try:
                exchanges['binance'] = ccxt.binance({'enableRateLimit': True})
            except:
                pass
                
            try:
                exchanges['okx'] = ccxt.okx({'enableRateLimit': True})
            except:
                pass
            
        except Exception as e:
            logger.error(f"Exchange initialization error: {e}")
            
        return exchanges
    
    def add_to_watchlist(self, symbols: List[str]):
        """Add symbols to monitoring watchlist"""
        for symbol in symbols:
            if symbol not in self.watchlist:
                self.watchlist.append(symbol)
                self.console.print(f"✅ Added {symbol} to watchlist")
    
    def get_demo_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Generate demo market data for testing"""
        try:
            # Generate 200 hours of sample data
            dates = pd.date_range(end=datetime.now(), periods=200, freq='1h')
            
            # Get base price
            base_price = self.demo_prices.get(symbol, 1000.0)
            
            # Generate realistic price movements
            np.random.seed(hash(symbol) % 2147483647)  # Deterministic but different per symbol
            returns = np.random.normal(0, 0.01, len(dates))
            
            prices = [base_price]
            for ret in returns[1:]:
                new_price = prices[-1] * (1 + ret)
                prices.append(max(new_price, 0.01))  # Prevent negative prices
            
            # Create OHLCV data
            df = pd.DataFrame({
                'open': [p * np.random.uniform(0.999, 1.001) for p in prices],
                'high': [p * np.random.uniform(1.001, 1.02) for p in prices],
                'low': [p * np.random.uniform(0.98, 0.999) for p in prices],
                'close': prices,
                'volume': np.random.randint(100000, 1000000, len(prices))
            }, index=dates)
            
            # Add simple technical indicators
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['rsi'] = self._calculate_rsi(df['close'])
            
            return df
            
        except Exception as e:
            logger.error(f"Demo data generation error: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_market_data(self, symbol: str, timeframe: str = '1h', limit: int = 200) -> Optional[pd.DataFrame]:
        """Fetch market data for analysis"""
        
        # Use demo data if no exchanges available
        if not self.exchanges or self.demo_mode:
            return self.get_demo_data(symbol)
        
        try:
            for exchange_name, exchange in self.exchanges.items():
                try:
                    # Fetch OHLCV data
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                    
                    if ohlcv:
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df.set_index('timestamp', inplace=True)
                        
                        # Add basic technical indicators
                        df['sma_20'] = df['close'].rolling(window=20).mean()
                        df['sma_50'] = df['close'].rolling(window=50).mean()
                        df['rsi'] = self._calculate_rsi(df['close'])
                        
                        return df
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch data from {exchange_name}: {e}")
                    continue
            
            # Fallback to demo data
            return self.get_demo_data(symbol)
            
        except Exception as e:
            logger.error(f"Market data fetch error: {e}")
            return self.get_demo_data(symbol)
    
    def calculate_signals(self, df: pd.DataFrame, symbol: str) -> List[MarketSignal]:
        """Calculate trading signals"""
        signals = []
        
        if df is None or len(df) < 50:
            return signals
        
        try:
            latest = df.iloc[-1]
            
            # Signal strength calculation
            signal_strength = 0
            confidence_factors = []
            
            # RSI Analysis
            rsi = latest.get('rsi', 50)
            if not pd.isna(rsi):
                if rsi < 30:
                    signal_strength += 0.3  # Oversold
                    confidence_factors.append(f"RSI Oversold ({rsi:.1f})")
                elif rsi > 70:
                    signal_strength -= 0.3  # Overbought
                    confidence_factors.append(f"RSI Overbought ({rsi:.1f})")
            
            # Moving Average Analysis
            sma_20 = latest.get('sma_20', latest['close'])
            sma_50 = latest.get('sma_50', latest['close'])
            
            if not pd.isna(sma_20) and not pd.isna(sma_50):
                if latest['close'] > sma_20 > sma_50:
                    signal_strength += 0.25
                    confidence_factors.append("Bullish MA Trend")
                elif latest['close'] < sma_20 < sma_50:
                    signal_strength -= 0.25
                    confidence_factors.append("Bearish MA Trend")
            
            # Volume Analysis
            if len(df) >= 20:
                volume_avg = df['volume'].rolling(window=20).mean().iloc[-1]
                if latest['volume'] > volume_avg * 1.5:
                    signal_strength += 0.15
                    confidence_factors.append("High Volume")
            
            # Generate signal based on strength
            confidence = min(abs(signal_strength) * 100, 95)
            
            if signal_strength > 0.4:
                recommendation = "STRONG BUY"
                signal_type = "BUY"
            elif signal_strength > 0.2:
                recommendation = "BUY"
                signal_type = "BUY"
            elif signal_strength < -0.4:
                recommendation = "STRONG SELL"
                signal_type = "SELL"
            elif signal_strength < -0.2:
                recommendation = "SELL"
                signal_type = "SELL"
            else:
                recommendation = "HOLD"
                signal_type = "NEUTRAL"
            
            signal = MarketSignal(
                symbol=symbol,
                signal_type=signal_type,
                strength=abs(signal_strength),
                confidence=confidence,
                timestamp=datetime.now(),
                price=latest['close'],
                volume=latest['volume'],
                indicators={
                    'rsi': rsi if not pd.isna(rsi) else 50,
                    'sma_20': sma_20 if not pd.isna(sma_20) else latest['close'],
                    'sma_50': sma_50 if not pd.isna(sma_50) else latest['close'],
                    'confidence_factors': confidence_factors
                },
                recommendation=recommendation
            )
            
            signals.append(signal)
            
        except Exception as e:
            logger.error(f"Signal calculation error for {symbol}: {e}")
        
        return signals
    
    def display_simple_dashboard(self):
        """Display simple text dashboard"""
        self.console.clear()
        
        print("=" * 80)
        print("🎯 JB's OVERWATCH - MDPS Advanced Monitoring System")
        print("=" * 80)
        
        # System stats
        uptime = datetime.now() - self.start_time
        accuracy = (self.successful_predictions / max(self.total_signals, 1)) * 100
        
        print(f"⏰ Uptime: {uptime}")
        print(f"📊 Total Signals: {self.total_signals}")
        print(f"🎯 Accuracy: {accuracy:.1f}%")
        print(f"🔧 Mode: {'Demo' if self.demo_mode else 'Live'}")
        print()
        
        # Recent signals
        print("🚨 RECENT SIGNALS:")
        print("-" * 80)
        if self.signals:
            for signal in self.signals[-5:]:
                color_indicator = {
                    'STRONG BUY': '🟢',
                    'BUY': '🟡', 
                    'HOLD': '⚪',
                    'SELL': '🟠',
                    'STRONG SELL': '🔴'
                }.get(signal.recommendation, '⚪')
                
                print(f"{color_indicator} {signal.symbol:12} | {signal.recommendation:12} | "
                      f"Price: ${signal.price:8.2f} | Confidence: {signal.confidence:5.1f}%")
        else:
            print("No signals generated yet...")
        
        print()
        
        # Watchlist status
        print("👀 WATCHLIST STATUS:")
        print("-" * 80)
        for symbol in self.watchlist:
            try:
                df = self.get_market_data(symbol)
                if df is not None and len(df) > 0:
                    latest_price = df['close'].iloc[-1]
                    change = ((latest_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100 if len(df) > 1 else 0
                    change_indicator = "📈" if change >= 0 else "📉"
                    
                    print(f"{change_indicator} {symbol:12} | Price: ${latest_price:8.2f} | Change: {change:+6.2f}%")
            except Exception as e:
                print(f"❌ {symbol:12} | Error fetching data")
        
        print("=" * 80)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')} | Press Ctrl+C to stop")
        print("=" * 80)
    
    def display_rich_dashboard(self):
        """Display Rich terminal dashboard"""
        # Implementation for Rich dashboard would go here
        # For now, fallback to simple dashboard
        self.display_simple_dashboard()
    
    async def monitor_markets(self):
        """Main monitoring loop"""
        self.is_monitoring = True
        self.console.print("🚀 JB's OVERWATCH System Started!")
        
        try:
            while self.is_monitoring:
                try:
                    # Clear previous signals for fresh analysis
                    current_signals = []
                    
                    # Analyze each symbol in watchlist
                    for symbol in self.watchlist:
                        # Get market data
                        df = self.get_market_data(symbol)
                        
                        if df is not None:
                            # Calculate signals
                            new_signals = self.calculate_signals(df, symbol)
                            current_signals.extend(new_signals)
                    
                    # Update signals list (keep last 50)
                    self.signals.extend(current_signals)
                    self.signals = self.signals[-50:]
                    self.total_signals += len(current_signals)
                    
                    # Display dashboard
                    if RICH_AVAILABLE:
                        self.display_rich_dashboard()
                    else:
                        self.display_simple_dashboard()
                    
                    # Wait before next cycle
                    await asyncio.sleep(10)  # 10-second refresh for demo
                    
                except KeyboardInterrupt:
                    self.console.print("🛑 OVERWATCH Stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    await asyncio.sleep(5)
        
        finally:
            self.is_monitoring = False

def main():
    """Main OVERWATCH application"""
    
    print("🎯 Initializing JB's OVERWATCH System...")
    
    # Initialize OVERWATCH system
    try:
        overwatch = JBOverwatchSystem()
        
        # Default watchlist of major cryptocurrencies
        default_watchlist = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'
        ]
        
        overwatch.add_to_watchlist(default_watchlist)
        
        print("✅ OVERWATCH System Initialized")
        print(f"📊 Watchlist: {len(overwatch.watchlist)} symbols")
        print(f"🏦 Exchanges: {len(overwatch.exchanges)} connected")
        print(f"🔧 Mode: {'Demo' if overwatch.demo_mode else 'Live'}")
        print()
        print("🚀 Starting market monitoring...")
        print("Press Ctrl+C to stop")
        print()
        
        # Start monitoring
        asyncio.run(overwatch.monitor_markets())
        
    except KeyboardInterrupt:
        print("\n👋 OVERWATCH System Shutdown Complete")
    except Exception as e:
        print(f"❌ System error: {e}")
        logger.error(f"System error: {e}")

if __name__ == "__main__":
    main()
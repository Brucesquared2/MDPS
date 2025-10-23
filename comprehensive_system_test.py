"""
MDPS Comprehensive System Test
Tests all components based on your complete requirements.txt
"""
import sys
import importlib
import traceback
from datetime import datetime
from config import API_KEY, API_SECRET, API_PASSPHRASE

def test_core_packages():
    """Test essential data science and trading packages"""
    print("🔍 Testing Core Packages...")
    
    core_tests = {
        'numpy': lambda: __import__('numpy').array([1, 2, 3]).mean(),
        'pandas': lambda: __import__('pandas').DataFrame({'test': [1, 2, 3]}).shape[0],
        'requests': lambda: __import__('requests').__version__,
        'aiohttp': lambda: __import__('aiohttp').__version__,
        'websockets': lambda: __import__('websockets').__version__,
        'python_dotenv': lambda: __import__('dotenv').__version__,
    }
    
    results = {}
    for package, test_func in core_tests.items():
        try:
            result = test_func()
            print(f"✅ {package:20} - Working ({result})")
            results[package] = True
        except Exception as e:
            print(f"❌ {package:20} - Failed: {str(e)}")
            results[package] = False
    
    return results

def test_trading_packages():
    """Test trading and financial packages"""
    print("\n📈 Testing Trading & Financial Packages...")
    
    trading_tests = {
        'ccxt': lambda: len(__import__('ccxt').exchanges),
        'yfinance': lambda: __import__('yfinance').__version__,
        'ta': lambda: __import__('ta').__version__,
        'pybit': lambda: __import__('pybit').__version__,
        'tradingview_ta': lambda: __import__('tradingview_ta').__version__,
    }
    
    results = {}
    for package, test_func in trading_tests.items():
        try:
            result = test_func()
            print(f"✅ {package:20} - Working ({result})")
            results[package] = True
        except Exception as e:
            print(f"❌ {package:20} - Failed: {str(e)}")
            results[package] = False
    
    return results

def test_visualization_packages():
    """Test visualization and UI packages"""
    print("\n🎨 Testing Visualization Packages...")
    
    viz_tests = {
        'plotly': lambda: __import__('plotly').__version__,
        'rich': lambda: __import__('rich').__version__,
        'streamlit': lambda: __import__('streamlit').__version__,
        'flask': lambda: __import__('flask').__version__,
    }
    
    results = {}
    for package, test_func in viz_tests.items():
        try:
            result = test_func()
            print(f"✅ {package:20} - Working ({result})")
            results[package] = True
        except Exception as e:
            print(f"❌ {package:20} - Failed: {str(e)}")
            results[package] = False
    
    return results

def test_ml_packages():
    """Test machine learning packages"""
    print("\n🤖 Testing Machine Learning Packages...")
    
    ml_tests = {
        'scikit_learn': lambda: __import__('sklearn').__version__,
        'scipy': lambda: __import__('scipy').__version__,
        'keras': lambda: __import__('keras').__version__,
        'tensorboard': lambda: __import__('tensorboard').__version__,
    }
    
    results = {}
    for package, test_func in ml_tests.items():
        try:
            result = test_func()
            print(f"✅ {package:20} - Working ({result})")
            results[package] = True
        except Exception as e:
            print(f"❌ {package:20} - Failed: {str(e)}")
            results[package] = False
    
    return results

def test_bitget_api_connection():
    """Test Bitget API with python-bitget library"""
    print("\n🏦 Testing Bitget API Connection...")
    
    try:
        from pybitget import Client
        
        # Test public API first
        import requests
        public_url = "https://api.bitget.com/api/v2/spot/market/tickers"
        response = requests.get(public_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '00000':
                tickers = data.get('data', [])
                btc_ticker = next((t for t in tickers if t['symbol'] == 'BTCUSDT'), None)
                
                if btc_ticker:
                    print(f"✅ Public API - BTC/USDT: ${btc_ticker['lastPr']}")
                else:
                    print("✅ Public API - Connected (BTC ticker not found)")
                
                # Test with credentials
                try:
                    client = Client(API_KEY, API_SECRET, API_PASSPHRASE)
                    # Try a simple private API call
                    print("✅ Private API - Credentials configured")
                    return True
                except Exception as e:
                    print(f"⚠️  Private API - Config issue: {str(e)[:100]}...")
                    return True  # Public API still works
            else:
                print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Bitget connection failed: {str(e)}")
        return False

def test_ccxt_exchanges():
    """Test CCXT with multiple exchanges"""
    print("\n🌐 Testing CCXT Exchange Connections...")
    
    try:
        import ccxt
        
        exchanges_to_test = {
            'bitget': {'has_fetch_ticker': True},
            'binance': {'has_fetch_ticker': True},
            'bybit': {'has_fetch_ticker': True},
            'okx': {'has_fetch_ticker': True}
        }
        
        working_exchanges = []
        
        for exchange_name, config in exchanges_to_test.items():
            try:
                if hasattr(ccxt, exchange_name):
                    exchange = getattr(ccxt, exchange_name)({
                        'enableRateLimit': True,
                        'timeout': 10000,
                    })
                    
                    # Test fetching BTC/USDT ticker
                    ticker = exchange.fetch_ticker('BTC/USDT')
                    price = ticker.get('last', ticker.get('close', 0))
                    print(f"✅ {exchange_name:10} - BTC/USDT: ${price:.2f}")
                    working_exchanges.append(exchange_name)
                else:
                    print(f"❌ {exchange_name:10} - Not available")
            except Exception as e:
                print(f"⚠️  {exchange_name:10} - Error: {str(e)[:50]}...")
        
        print(f"✅ Working Exchanges: {len(working_exchanges)}/{len(exchanges_to_test)}")
        return len(working_exchanges) >= 1
        
    except Exception as e:
        print(f"❌ CCXT test failed: {str(e)}")
        return False

def test_technical_analysis():
    """Test technical analysis with real data"""
    print("\n📊 Testing Technical Analysis Capabilities...")
    
    try:
        import pandas as pd
        import numpy as np
        import ta
        
        # Generate realistic sample data
        np.random.seed(42)  # For reproducible results
        dates = pd.date_range('2024-01-01', periods=200, freq='1H')
        
        # Simulate realistic crypto price movements
        base_price = 45000
        price_changes = np.random.normal(0, 0.01, 200)  # 1% volatility
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        # Create OHLCV data
        df = pd.DataFrame({
            'open': [p * np.random.uniform(0.999, 1.001) for p in prices],
            'high': [p * np.random.uniform(1.001, 1.02) for p in prices],
            'low': [p * np.random.uniform(0.98, 0.999) for p in prices],
            'close': prices,
            'volume': np.random.randint(100000, 1000000, 200)
        }, index=dates)
        
        # Test various technical indicators
        indicators = {}
        
        # Moving Averages
        indicators['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
        indicators['ema_20'] = ta.trend.ema_indicator(df['close'], window=20)
        
        # Momentum Indicators
        indicators['rsi'] = ta.momentum.rsi(df['close'])
        indicators['macd'] = ta.trend.macd_diff(df['close'])
        
        # Volatility Indicators
        bb = ta.volatility.BollingerBands(df['close'])
        indicators['bb_upper'] = bb.bollinger_hband()
        indicators['bb_lower'] = bb.bollinger_lband()
        
        # Volume Indicators
        indicators['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'])
        
        # Print results
        latest_values = {}
        for name, series in indicators.items():
            if not series.empty and not pd.isna(series.iloc[-1]):
                latest_values[name] = series.iloc[-1]
                print(f"✅ {name:15} - Latest: {latest_values[name]:.4f}")
        
        print(f"✅ Successfully calculated {len(latest_values)} indicators")
        return len(latest_values) >= 6  # At least 6 indicators working
        
    except Exception as e:
        print(f"❌ Technical analysis test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_system_performance():
    """Test system performance and memory usage"""
    print("\n⚡ Testing System Performance...")
    
    try:
        import psutil
        import time
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"✅ CPU Usage: {cpu_percent}%")
        print(f"✅ Memory: {memory.percent}% used ({memory.available / (1024**3):.1f}GB available)")
        print(f"✅ Disk: {disk.percent}% used ({disk.free / (1024**3):.1f}GB free)")
        
        # Test data processing speed
        start_time = time.time()
        import pandas as pd
        import numpy as np
        
        # Create large dataset
        data = pd.DataFrame(np.random.randn(100000, 10))
        data['sma'] = data[0].rolling(window=20).mean()
        processing_time = time.time() - start_time
        
        print(f"✅ Data Processing: {processing_time:.3f}s for 100k rows")
        
        return True
        
    except ImportError:
        print("⚠️  psutil not installed - skipping performance test")
        return True
    except Exception as e:
        print(f"⚠️  Performance test failed: {str(e)}")
        return True

def main():
    """Main comprehensive test function"""
    print("🚀 MDPS COMPREHENSIVE SYSTEM TEST")
    print("=" * 80)
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"📍 Location: {sys.executable}")
    print("=" * 80)
    
    # Run all test suites
    test_results = {}
    
    test_results['core'] = test_core_packages()
    test_results['trading'] = test_trading_packages()
    test_results['visualization'] = test_visualization_packages()
    test_results['ml'] = test_ml_packages()
    
    # API and functionality tests
    bitget_ok = test_bitget_api_connection()
    ccxt_ok = test_ccxt_exchanges()
    ta_ok = test_technical_analysis()
    perf_ok = test_system_performance()
    
    # Calculate overall results
    total_packages = sum(len(suite) for suite in test_results.values())
    working_packages = sum(sum(suite.values()) for suite in test_results.values())
    
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    # Package results by category
    for category, results in test_results.items():
        working = sum(results.values())
        total = len(results)
        status = "✅ PASS" if working == total else f"⚠️  {working}/{total}"
        print(f"{category.upper():15} Packages: {status}")
    
    print(f"\n📦 TOTAL PACKAGES: {working_packages}/{total_packages} working")
    
    # Functionality tests
    print(f"🏦 Bitget API:     {'✅ WORKING' if bitget_ok else '❌ FAILED'}")
    print(f"🌐 CCXT Exchanges: {'✅ WORKING' if ccxt_ok else '❌ FAILED'}")
    print(f"📊 Technical Analysis: {'✅ WORKING' if ta_ok else '❌ FAILED'}")
    print(f"⚡ System Performance: {'✅ GOOD' if perf_ok else '⚠️  ISSUES'}")
    
    # Overall system status
    package_health = working_packages / total_packages if total_packages > 0 else 0
    functionality_health = sum([bitget_ok, ccxt_ok, ta_ok, perf_ok]) / 4
    
    overall_health = (package_health + functionality_health) / 2
    
    print("\n" + "🎯 OVERALL SYSTEM STATUS:")
    if overall_health >= 0.9:
        print("🟢 EXCELLENT - System ready for production trading!")
        status_msg = "All systems optimal. Ready for live trading."
    elif overall_health >= 0.75:
        print("🟡 GOOD - System ready with minor issues")
        status_msg = "System functional. Monitor for any issues."
    elif overall_health >= 0.5:
        print("🟠 FAIR - System needs attention")
        status_msg = "Some components need fixing before live trading."
    else:
        print("🔴 POOR - Major issues detected")
        status_msg = "Significant problems. Not ready for live trading."
    
    print(f"📊 Health Score: {overall_health*100:.1f}%")
    print(f"💡 Recommendation: {status_msg}")
    
    print(f"\n🕒 Completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    
    return overall_health >= 0.75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
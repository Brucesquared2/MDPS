"""
MetaTrader5 Connection and Data Feed Management
"""
# Safe import guard for MetaTrader5 (optional dependency)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None

from PyQt5.QtCore import QObject, pyqtSignal
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime
import os
import winreg


def mt5_initialize(**kwargs):
    """
    Safe wrapper for mt5.initialize() that checks if MT5 is available.
    
    Args:
        **kwargs: Arguments to pass to mt5.initialize()
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    if not MT5_AVAILABLE:
        return False
    return mt5.initialize(**kwargs)


def mt5_shutdown():
    """
    Safe wrapper for mt5.shutdown() that checks if MT5 is available.
    """
    if MT5_AVAILABLE and mt5 is not None:
        mt5.shutdown()

class MT5ConnectionManager(QObject):
    # Define signals for connection status updates
    connection_success = pyqtSignal(str)  # Emits terminal info on success
    connection_error = pyqtSignal(str)    # Emits error message on failure
    connection_status = pyqtSignal(bool)  # Emits True/False for connected status
    data_received = pyqtSignal(object)    # Emits received market data
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config
        self.is_connected = False
        self.default_mt5_path = r"C:\Program Files\FxPro - MetaTrader 5"
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for MT5 connection"""
        self.logger = logging.getLogger('MT5Connection')
        self.logger.setLevel(logging.INFO)
        
    def find_mt5_terminals(self):
        """
        Find all installed MT5 terminals on the system
        Returns:
            list: List of tuples containing (terminal_name, path)
        """
        terminals = []
        try:
            # Check common installation paths
            common_paths = [
                os.path.expandvars(r"%PROGRAMFILES%\FxPro - MetaTrader 5"),
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\MetaTrader 5"),
                os.path.expandvars(r"%PROGRAMFILES%\MetaTrader 5"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%\MetaTrader 5"),
            ]
            
            # Check registry for installed terminals
            registry_paths = [
                r"SOFTWARE\MetaQuotes\Terminal\\",
                r"SOFTWARE\WOW6432Node\MetaQuotes\Terminal\\"
            ]
            
            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    path = winreg.QueryValueEx(subkey, "Path")[0]
                                    if os.path.exists(path):
                                        name = f"MT5 Terminal {i+1}"
                                        terminals.append((name, path))
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    continue
                    
            # Check common paths
            for path in common_paths:
                if os.path.exists(path):
                    terminals.append((f"MT5 at {path}", path))
                    
        except Exception as e:
            self.logger.error(f"Error finding MT5 terminals: {str(e)}")
            
        return terminals
        
    def connect(self, path=None, login=None, password=None, server=None):
        """
        Connect to MT5 terminal
        Args:
            path: Optional MT5 terminal path
            login: Optional MT5 account login
            password: Optional MT5 account password
            server: Optional MT5 server name
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Check if MT5 is available
            if not MT5_AVAILABLE:
                error = "MetaTrader5 module is not available. Please install it with: pip install MetaTrader5"
                self.logger.error(error)
                self.connection_error.emit(error)
                self.connection_status.emit(False)
                return False

            # Shutdown existing connection if any
            if self.is_connected:
                mt5_shutdown()
                self.is_connected = False

            # Use specified path or default path
            if not path:
                path = self.default_mt5_path
                self.logger.info(f"Using default MT5 terminal at: {path}")
                    
            # Initialize MT5 connection with provided credentials
            init_params = {}
            if path:
                init_params['path'] = str(Path(path) / "terminal64.exe")
            if login:
                init_params['login'] = int(login)  # Ensure login is integer
            if password:
                init_params['password'] = password
            if server:
                init_params['server'] = server
            
            self.logger.info(f"Connecting to MT5... Server: {server}")
            
            if not mt5_initialize(**init_params):
                error = f"MT5 Initialize failed. Error: {mt5.last_error() if mt5 else 'MT5 not available'}"
                self.logger.error(error)
                self.connection_error.emit(error)
                self.connection_status.emit(False)
                return False
            
            # Enable RPC protocol for symbols and market data if credentials provided
            if login and password and server:
                mt5.login(login=int(login), password=password, server=server)
            
            # Get terminal info
            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                error = "Failed to get terminal info"
                self.logger.error(error)
                self.connection_error.emit(error)
                self.connection_status.emit(False)
                mt5_shutdown()
                return False
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                error = "Failed to get account info"
                self.logger.error(error)
                self.connection_error.emit(error)
                self.connection_status.emit(False)
                mt5_shutdown()
                return False
                
            # Successfully connected
            self.is_connected = True
            
            # Build success message with available information
            success_parts = ["Connected to MT5"]
            
            # Add terminal info if available
            if terminal_info:
                if hasattr(terminal_info, 'name'):
                    success_parts.append(f"Terminal: {terminal_info.name}")
                if hasattr(terminal_info, 'path'):
                    success_parts.append(f"Path: {terminal_info.path}")
            
            # Add account info if available
            if account_info:
                if hasattr(account_info, 'login'):
                    success_parts.append(f"Account: {account_info.login}")
                if hasattr(account_info, 'server'):
                    success_parts.append(f"Server: {account_info.server}")
                if hasattr(account_info, 'balance') and hasattr(account_info, 'currency'):
                    success_parts.append(f"Balance: {account_info.balance} {account_info.currency}")
            
            success_msg = "\n".join(success_parts)
            self.logger.info("Successfully connected to MT5")
            self.connection_success.emit(success_msg)
            self.connection_status.emit(True)
            return True
            
        except Exception as e:
            error_msg = f"Error connecting to MT5: {str(e)}"
            self.logger.error(error_msg)
            self.connection_error.emit(error_msg)
            self.connection_status.emit(False)
            try:
                mt5_shutdown()
            except Exception:
                pass
            return False
            
    def disconnect(self):
        """Disconnect from MT5 terminal"""
        try:
            self.logger.info("Disconnecting from MT5...")
            if self.is_connected:
                mt5_shutdown()
                self.is_connected = False
                self.connection_status.emit(False)
                self.logger.info("Successfully disconnected from MT5")
                return True
            return True  # Already disconnected
        except Exception as e:
            error = f"Error disconnecting from MT5: {str(e)}"
            self.logger.error(error)
            self.connection_error.emit(error)
            return False
            
    def check_connection(self):
        """Check if MT5 is still connected"""
        try:
            if not MT5_AVAILABLE or not mt5.terminal_info():
                self.is_connected = False
                self.connection_status.emit(False)
                return False
            return True
        except Exception:
            self.is_connected = False
            self.connection_status.emit(False)
            return False
            
    def get_symbols(self):
        """Get available symbols"""
        if not self.is_connected or not MT5_AVAILABLE:
            return []
        return mt5.symbols_get()
        
    def get_timeframes(self):
        """Get available timeframes"""
        if not MT5_AVAILABLE:
            return {}
        return {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }
        
    def get_historical_data(self, symbol, timeframe, from_date, to_date=None):
        """
        Get historical data for a symbol
        Args:
            symbol: The trading symbol (e.g., "EURUSD")
            timeframe: The timeframe from mt5.TIMEFRAME_*
            from_date: Start date for historical data
            to_date: Optional end date (defaults to now)
        """
        if not self.is_connected or not MT5_AVAILABLE:
            return None
            
        if to_date is None:
            to_date = datetime.now()
            
        rates = mt5.copy_rates_range(symbol, timeframe, from_date, to_date)
        if rates is None:
            self.logger.error(f"Failed to get historical data for {symbol}")
            return None
            
        return pd.DataFrame(rates)

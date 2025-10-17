# MDPS - Multi-Dimensional Prediction System

## 🚀 Enhanced Trading System with Advanced PyQt Interface

**MDPS v2.0** is a comprehensive trading system that combines advanced machine learning models, real-time market analysis, and sophisticated risk management in a powerful PyQt desktop application.

![MDPS System Overview](https://img.shields.io/badge/Version-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-green)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Key Features

### 🎯 Core System Components
- **Multi-Model Prediction Engine**: LSTM, XGBoost, Random Forest, SVM, and Neural Networks
- **Real-time Market Data Processing**: Direct MetaTrader 5 integration
- **Advanced Technical Analysis**: Chart patterns, indicators, and market structure analysis
- **Risk Management System**: Portfolio optimization and position sizing
- **Strategy Backtesting**: Historical performance evaluation and optimization
- **Live Performance Monitoring**: System resources and trading metrics

### 🖥️ Enhanced PyQt Interface
- **Professional Trading Dashboard**: Multi-tab interface with real-time updates
- **Advanced Charts**: Interactive PyQtGraph-based visualization
- **System Monitoring**: Real-time CPU, memory, and network monitoring
- **Model Management**: Train, test, and deploy ML models with performance tracking
- **Connection Manager**: Enhanced MT5 connection with auto-reconnect and monitoring
- **Customizable Settings**: Comprehensive configuration management

### 📊 Analysis Capabilities
- **Chart Pattern Recognition**: Automated detection of key patterns
- **Market Structure Analysis**: Support/resistance levels and trend analysis
- **External Factors Integration**: Economic indicators and market sentiment
- **Data Quality Monitoring**: Real-time data validation and cleaning
- **Knowledge Graph Visualization**: Relationship mapping between market factors

## 🛠️ Installation

### Prerequisites
- **Python 3.9 or higher**
- **MetaTrader 5** (for live trading)
- **Windows/Linux/macOS** (tested on all platforms)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/mdps.git
   cd mdps
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch MDPS**
   ```bash
   # Preferred unified entrypoint
   python -m mdps

   # Or legacy UI launcher
   python launch_mdps.py
   ```

### Manual Installation

If you prefer to install dependencies manually:

```bash
# Core dependencies
pip install PyQt5>=5.15.0 numpy>=1.21.0 pandas>=1.3.0 scikit-learn>=1.3.0

# UI and visualization
pip install pyqtgraph>=0.13.0 matplotlib>=3.4.0 plotly>=5.0.0

# Trading and data
pip install MetaTrader5>=5.0.45 ccxt>=3.1.0 yfinance>=0.2.0

# Machine learning
pip install tensorflow>=2.13.0 torch>=2.0.0 xgboost>=1.7.0 lightgbm>=4.0.0

# System monitoring
pip install psutil>=5.9.0

# Additional utilities
pip install python-dotenv loguru aiohttp websockets
```

## 🚀 Getting Started

### 1. First Launch
Run the enhanced launcher with splash screen:
```bash
python launch_mdps.py
```

### 2. MetaTrader 5 Setup
1. Open the **MT5 Connection & Control** tab
2. Enter your MT5 credentials:
   - Login ID
   - Password
   - Server name
3. Click **Connect to MT5**
4. Monitor connection status in the **Monitoring** tab

### 3. Start MDPS Processing
1. Use the menu: **File → Start MDPS** (Ctrl+S)
2. Or click the **Start MDPS** button in the toolbar
3. Monitor system status in the **System Monitor** tab

### 4. Configure Predictions
1. Go to the **Model Comparison** tab
2. Navigate to **Live Predictions** → **Settings**
3. Configure:
   - Prediction interval
   - Confidence threshold
   - Active models
   - Ensemble method

## 📋 System Architecture

### Core Components

```
MDPS System
├── Data Collection & Acquisition
│   ├── MT5 Connection Manager
│   ├── External Data Feeds
│   └── Real-time Data Streams
├── Data Processing Pipeline
│   ├── Data Cleaning & Validation
│   ├── Feature Engineering
│   └── Signal Processing
├── Analysis Engines
│   ├── Technical Analysis
│   ├── Chart Pattern Recognition
│   ├── Market Structure Analysis
│   └── External Factors Integration
├── Prediction Engine
│   ├── Machine Learning Models
│   ├── Model Ensemble
│   └── Performance Tracking
├── Strategy & Decision Layer
│   ├── Signal Generation
│   ├── Risk Management
│   └── Position Sizing
└── User Interface
    ├── Real-time Dashboard
    ├── Analysis Tools
    ├── Model Management
    └── System Monitoring
```

### PyQt UI Components

- **Main Window**: Central control hub with tabbed interface
- **MT5 Connection Widget**: Enhanced connection management with monitoring
- **System Monitor**: Real-time system resources and MDPS status
- **Prediction Engine**: Live predictions with model comparison
- **Trading Interface**: Order management and position tracking
- **Analytics Dashboard**: Performance metrics and visualizations

## 🎮 Using the Interface

### Main Navigation
- **File Menu**: Start/stop MDPS, configuration, exit
- **View Menu**: Full screen, refresh all views
- **Tools Menu**: Quick access to system monitor and data quality
- **Help Menu**: About information

### Key Shortcuts
- `Ctrl+S`: Start MDPS
- `Ctrl+T`: Stop MDPS
- `Ctrl+P`: Configuration
- `F5`: Refresh all views
- `F11`: Toggle full screen
- `Ctrl+Q`: Exit application

### Tab Overview

1. **MT5 Connection & Control**
   - Connection management
   - Account monitoring
   - Symbol tracking
   - Connection logs

2. **Market**
   - Real-time price data
   - Market overview
   - Symbol selection

3. **Technical**
   - Technical indicators
   - Chart analysis
   - Pattern recognition

4. **Trading**
   - Order entry
   - Position management
   - Risk controls

5. **Analytics**
   - Performance metrics
   - Strategy analysis
   - Reporting tools

6. **System Monitor**
   - CPU, memory, disk usage
   - MDPS component status
   - Performance metrics
   - System controls

7. **Model Comparison**
   - Live predictions
   - Model management
   - Performance analysis
   - Settings

8. **Additional Tabs**
   - Knowledge Graph
   - External Factors
   - Market Structure
   - Pattern Recognition
   - Strategy Simulator
   - Risk Management
   - Data Quality

## ⚙️ Configuration

### Basic Configuration (`config.py`)
```python
# MT5 Settings
mt5_settings = {
    "server": "MetaQuotes-Demo",
    "timeout": 60000,
    "reconnect_attempts": 3
}

# Trading Settings
strategy_settings = {
    "risk_per_trade": 0.02,
    "max_open_positions": 3,
    "stop_loss_atr_factor": 2.0
}
```

### Advanced Settings
Access through: **File → Configuration** or use the Settings tabs in each component.

## 🤖 Machine Learning Models

### Supported Models
- **LSTM Neural Networks**: Time series prediction
- **XGBoost**: Gradient boosting for classification
- **Random Forest**: Ensemble decision trees
- **Support Vector Machines**: Pattern classification
- **Deep Neural Networks**: Multi-layer perceptrons
- **Transformer Models**: Attention-based architectures

### Model Management
1. **Training**: Automated training on historical data
2. **Testing**: Backtesting with performance metrics
3. **Deployment**: Live prediction deployment
4. **Monitoring**: Real-time performance tracking
5. **Comparison**: Side-by-side model analysis

## 📈 Performance Monitoring

### System Metrics
- CPU and memory usage
- Network I/O
- Disk utilization
- Process monitoring

### Trading Metrics
- Prediction accuracy
- Signal success rate
- Processing time
- Error tracking

### Real-time Updates
- Live performance charts
- Component status indicators
- Connection health monitoring
- Resource utilization graphs

## 🔧 Troubleshooting

### Common Issues

**1. MT5 Connection Failed**
```
Solution: 
- Check credentials
- Verify server name
- Ensure MT5 is running
- Check network connection
```

**2. Missing Dependencies**
```
Solution:
pip install -r requirements.txt
```

**3. PyQt5 Import Error**
```
Solution:
pip install PyQt5>=5.15.0
# or
conda install pyqt
```

**4. System Monitor Not Working**
```
Solution:
pip install psutil>=5.9.0
```

### Debug Mode
Enable detailed logging by setting the log level in `launch_mdps.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🏗️ Development

### Project Structure
```
repo-root/
├── mdps/
│   ├── __init__.py         # Aggregates all MDPS sections
│   ├── __main__.py         # python -m mdps entrypoint
│   └── main.py             # Pipeline driver
├── config.py               # Root configuration (reused)
├── run_mdps.py             # Convenience runner
├── launch_mdps.py          # PyQt UI launcher
├── trading_ui/             # PyQt interface (unchanged)
├── Data_Collection_and_Acquisition/
├── Data Cleaning & Signal Processing/
├── Preprocessing & Feature Engineering/
├── Advanced Chart Analysis Tools/
├── Market_Context_Structural_Analysis/
├── Labeling & Target Engineering/
├── Prediction Engine (MLDL Models)/
└── Strategy & Decision Layer/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### Coding Standards
- Follow PEP 8 style guidelines
- Use type hints where applicable
- Add docstrings to all functions
- Include unit tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

### Getting Help
- **Documentation**: Check this README and inline documentation
- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions

### Contact
- **Email**: mdps-support@example.com
- **Website**: https://mdps-trading.com
- **Documentation**: https://docs.mdps-trading.com

## 🚀 FastAPI Wrapper

MDPS now includes a FastAPI wrapper for running MDPS jobs via REST API!

### Quick Start

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Set the entrypoint** (optional, can be set per-request):
   ```bash
   export MDPS_ENTRYPOINT="module:callable"
   ```

3. **Start the API server**:
   ```bash
   # Using the startup script
   ./app/start.sh

   # Or directly with uvicorn
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Create a job**:
   ```bash
   curl -X POST http://localhost:8000/jobs \
     -H "Content-Type: application/json" \
     -d '{"parameters": {"symbol": "EURUSD"}}'
   ```

5. **Check job status**:
   ```bash
   curl http://localhost:8000/jobs/{job_id}
   ```

### Features

- **Dynamic Entrypoint Loading**: Configure via `MDPS_ENTRYPOINT` environment variable
- **Asynchronous Job Execution**: Non-blocking background task execution
- **Job Status Tracking**: Real-time status updates in `.quant_runs/` directory
- **RESTful API**: Standard HTTP endpoints for job management
- **Interactive Docs**: Swagger UI at `http://localhost:8000/docs`

For detailed API documentation, see [app/README.md](app/README.md)

### DevContainer Support

Open in VS Code with Dev Containers extension for automatic setup:
1. Command Palette → "Dev Containers: Reopen in Container"
2. Wait for setup to complete
3. Run `./app/start.sh` or `python app/main.py`

## 🎯 Roadmap

### v2.1 (Next Release)
- [ ] Enhanced chart analysis tools
- [ ] Advanced strategy optimization
- [ ] Portfolio management features
- [ ] Cloud deployment options

### v2.2 (Future)
- [ ] Mobile companion app
- [ ] Web-based interface
- [ ] Advanced AI models
- [ ] Multi-broker support

### v3.0 (Long-term)
- [ ] Distributed processing
- [ ] Real-time collaboration
- [ ] Advanced risk analytics
- [ ] Institutional features

---

**MDPS v2.0** - Bringing professional-grade trading technology to desktop applications with the power and flexibility of PyQt5.

*Happy Trading! 📈* 

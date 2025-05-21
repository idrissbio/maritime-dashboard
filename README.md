# Maritime Freight Algorithmic Trading System

This system uses maritime freight data and port congestion metrics to predict energy futures prices and generate trading signals for an Apex Trader Funding account.

## Overview

The Maritime Freight Algorithmic Trading System is designed to exploit correlations between maritime shipping markets and energy futures. By analyzing data from shipping indices, port congestion, and vessel tracking alongside energy futures prices, the system identifies trading opportunities and executes trades on the Apex Trader Funding platform.

## Key Features

- **Data Collection**: Gathers data from multiple sources including energy futures prices, Baltic Dry Index (BDI), Freightos Baltic Index (FBX), and port congestion metrics
- **TwelveData API Integration**: Provides real-time market data, quotes, and interactive charts for energy futures
- **Correlation Analysis**: Identifies relationships between maritime shipping metrics and energy futures prices
- **Price Prediction**: Uses machine learning models to forecast price movements in energy futures
- **Signal Generation**: Creates trading signals based on predictions and correlations
- **Automated Trading**: Executes trades through the Apex Trader Funding platform
- **Performance Monitoring**: Tracks trade performance, account metrics, and system health
- **Interactive Dashboard**: Visualizes data, correlations, predictions, and trading performance

## System Architecture

The system is organized into several components:

1. **Data Layer**
   - Data collection from multiple sources
   - Time-series database storage
   - Data preprocessing and cleaning

2. **Analysis Layer**
   - Correlation analysis between maritime and energy data
   - Machine learning models for price prediction
   - Signal generation based on predictions

3. **Trading Layer**
   - Strategy implementation and risk management
   - Order execution and position management
   - Performance tracking and reporting

4. **Dashboard Layer**
   - Interactive visualization of data and analysis
   - Real-time monitoring of signals and trades
   - Performance metrics and account status

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- API access to data sources (optional - system works with mock data)
- Datalastic API key (optional - for real vessel tracking data)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/maritime_trading_project.git
   cd maritime_trading_project
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables by copying the example file:
   ```
   cp .env.example .env
   ```
   Then edit `.env` to add your API keys and configuration.

### Usage

The system can be run in different modes using the command-line interface:

#### Running with Mock Data

```
python run_with_mock.py --dashboard
```

This runs the system with synthetic data for development and testing.

#### Running with Real Vessel Tracking Data

```
python install_vessel_tracking_api.py --key YOUR_DATALASTIC_API_KEY --test
python run_with_real_data.py --dashboard --ports Shanghai Singapore "Los Angeles"
```

This sets up your API key and runs the system with real vessel tracking data. See [USING_REAL_DATA.md](USING_REAL_DATA.md) for more details on working with real data.

#### Checking Datalastic API Usage

```
python check_api_usage.py
```

Shows your current Datalastic API usage, remaining credits, and account status.

```
python check_api_usage.py --format json
```

Outputs the API statistics in JSON format for further processing.

For a complete guide to using the Datalastic API in this system, see [DATALASTIC_API_GUIDE.md](DATALASTIC_API_GUIDE.md).

#### Vessel Tracking Visualization

```
python vessel_map_visualization.py --port Singapore --heatmap
```

Generate interactive maps showing vessel positions around major ports.

#### Other Modes

#### Running the Complete System

```
python main.py system --dashboard --data-interval 60 --trading-interval 60
```

This starts data collection, trading, and the dashboard all at once.

#### Data Collection Only

```
python main.py collect --historical --days 90
```

Collects 90 days of historical data, or:

```
python main.py collect --continuous --interval 60
```

Continuously collects data every 60 minutes.

#### Correlation Analysis

```
python main.py analyze --symbol CL --index BDI --lag 2 --plot
```

Analyzes correlation between Crude Oil (CL) and Baltic Dry Index (BDI) with a 2-day lag and generates a plot.

#### Model Training

```
python main.py train --symbol CL --days 180
```

Trains a prediction model for Crude Oil using 180 days of historical data.

#### Signal Generation

```
python main.py signals --update-models --export
```

Generates trading signals, updates models first, and exports the signals to a JSON file.

#### Trading Execution

```
python main.py trading --continuous --interval 60
```

Runs continuous trading with a 60-minute interval between cycles.

#### Dashboard

```
python main.py dashboard --port 8501
```

Launches the interactive dashboard on port 8501.

## Dashboard

The dashboard provides real-time monitoring and visualization of:

- Account performance and balance
- Open positions and trade history
- Correlation analysis between maritime and energy markets
- Price predictions and model performance
- Vessel tracking and port congestion data
- Data source metrics and system status

### Running the Dashboard Locally

Access the dashboard by running:

```
python main.py dashboard
```

Or use Streamlit directly:

```
streamlit run src/dashboard/app.py
```

Then open your browser to http://localhost:8501

### Streamlit Cloud Deployment

The dashboard can be deployed to Streamlit Cloud for easy access from anywhere:

1. Use the simplified Streamlit app for deployment:
   ```
   streamlit run streamlit_app.py
   ```

2. To deploy to Streamlit Cloud:
   - Create a GitHub repository and push the code:
     ```
     git remote add origin <your-github-repo-url>
     git push -u origin main
     ```

   - Go to [Streamlit Cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account
   - Click "New app" and select your repository
   - In the deploy settings:
     * Main file path: `deploy-streamlit.py`
     * Requirements file: `requirements.txt`
   - Click "Deploy"

   > **Important**: For compatibility with Streamlit Cloud, we've updated the dependencies in `requirements.txt` to versions that are compatible with the Streamlit Cloud environment.

The cloud-deployed version uses the TwelveData API for real-time market data and includes simplified versions of the dashboard pages focused on Energy Futures and their correlation with maritime shipping data. The `deploy-streamlit.py` file is a self-contained version of the dashboard specifically designed for Streamlit Cloud deployment.

## Configuration

System configuration is managed through the `config/config.py` file, which includes:

- Trading instruments and parameters
- Risk management settings
- Data source configuration
- Model parameters
- Dashboard settings

## Project Structure

```
maritime_trading_project/
├── config/                  # Configuration files
├── data/                    # Data storage
├── logs/                    # Log files
├── src/
│   ├── data/                # Data collection and storage
│   ├── models/              # Analysis and prediction models
│   ├── trading/             # Trading execution and management
│   ├── dashboard/           # Streamlit dashboard
│   └── utils/               # Utility functions
├── tests/                   # Unit and integration tests
├── .env.example             # Example environment variables
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Maritime data providers
- Apex Trader Funding for the trading platform
- Contributors and maintainers
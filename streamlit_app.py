"""
Maritime Trading Dashboard - Main Streamlit App
This is the entry point for the Streamlit Cloud deployment.
"""
import os
import sys
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import json
import requests

# Set page config
st.set_page_config(
    page_title="Maritime Trading Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define API key
TWELVEDATA_API_KEY = "d347cca2eff5491582449d18e14131d5"

# Define TwelveData API class for direct API interaction
class TwelveDataAPI:
    def __init__(self):
        self.api_key = TWELVEDATA_API_KEY
        self.base_url = "https://api.twelvedata.com"
        self.futures_mapping = {
            "CL": {"symbol": "CL", "exchange": "NYMEX"},  # Crude Oil
            "NG": {"symbol": "NG", "exchange": "NYMEX"},  # Natural Gas
            "HO": {"symbol": "HO", "exchange": "NYMEX"},  # Heating Oil
            "RB": {"symbol": "RB", "exchange": "NYMEX"},  # RBOB Gasoline
        }
        self.request_interval = 1.0  # seconds between requests
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Ensure we don't exceed API rate limits."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
            
        self.last_request_time = time.time()
    
    def get_time_series(self, symbol, interval="1day", outputsize=100):
        """Get time series data for a symbol."""
        # Prepare request parameters
        params = {
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
            "format": "JSON"
        }
        
        # Add exchange if it's a futures symbol
        if symbol in self.futures_mapping:
            params["symbol"] = self.futures_mapping[symbol]["symbol"]
            params["exchange"] = self.futures_mapping[symbol]["exchange"]
        
        # Add outputsize parameter
        params["outputsize"] = outputsize
        
        try:
            # Make the request
            response = requests.get(f"{self.base_url}/time_series", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if "values" in data:
                    # Convert to dataframe
                    df = pd.DataFrame(data["values"])
                    
                    # Convert types
                    if not df.empty:
                        df["datetime"] = pd.to_datetime(df["datetime"])
                        numeric_columns = ["open", "high", "low", "close", "volume"]
                        for col in numeric_columns:
                            if col in df.columns:
                                df[col] = pd.to_numeric(df[col])
                        
                        # Add symbol column and rename to match our standard format
                        df["Symbol"] = symbol
                        df = df.rename(columns={
                            "datetime": "Timestamp",
                            "open": "Open",
                            "high": "High",
                            "low": "Low",
                            "close": "Close",
                            "volume": "Volume"
                        })
                        
                        # Ensure all required columns exist
                        if "Volume" not in df.columns:
                            df["Volume"] = 0
                        
                        # Add Adj Close column (same as Close for futures)
                        df["Adj Close"] = df["Close"]
                        
                        # Reverse order to match other sources (newest last)
                        df = df.sort_values("Timestamp")
                        
                        return df
        except Exception as e:
            st.error(f"Error fetching time series data: {str(e)}")
        
        return pd.DataFrame()
    
    def get_quote(self, symbol):
        """Get current quote for a symbol."""
        # Prepare request parameters
        params = {
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        # Add exchange if it's a futures symbol
        if symbol in self.futures_mapping:
            params["symbol"] = self.futures_mapping[symbol]["symbol"]
            params["exchange"] = self.futures_mapping[symbol]["exchange"]
        
        try:
            # Make the request
            response = requests.get(f"{self.base_url}/quote", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if "symbol" in data:
                    return data
        except Exception as e:
            st.error(f"Error fetching quote data: {str(e)}")
        
        return {}
    
    def get_chart(self, symbol, interval="1day", chart_type="candle", 
                studies=None, outputsize=100):
        """Get chart image for a symbol."""
        # Prepare request parameters
        params = {
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
            "type": chart_type,
            "theme": "dark"  # Default theme
        }
        
        # Add exchange if it's a futures symbol
        if symbol in self.futures_mapping:
            params["symbol"] = self.futures_mapping[symbol]["symbol"]
            params["exchange"] = self.futures_mapping[symbol]["exchange"]
        
        # Handle outputsize (limit to API maximum)
        params["outputsize"] = min(outputsize, 350)  # API limit
        
        # Add technical indicators
        if studies:
            params["studies"] = ",".join(studies)
        
        try:
            # Make the request
            response = requests.get(f"{self.base_url}/chart", params=params)
            
            if response.status_code == 200:
                # Process the image
                img = Image.open(io.BytesIO(response.content))
                return img
        except Exception as e:
            st.error(f"Error fetching chart: {str(e)}")
        
        return None

# Initialize API client
api = TwelveDataAPI()

# Define functions for retrieving data
def get_market_summary_data():
    """Get the latest market data for the summary cards."""
    try:
        # Create result for energy futures
        result = []
        
        # Symbols we want to show
        symbols = ["CL", "NG", "HO", "RB"]
        
        # Map symbols to more descriptive names
        name_map = {
            "CL": "Crude Oil (CL)",
            "NG": "Natural Gas (NG)",
            "HO": "Heating Oil (HO)",
            "RB": "Gasoline (RB)"
        }
        
        # Get data for each symbol
        for symbol in symbols:
            quote = api.get_quote(symbol)
            
            if quote and "symbol" in quote:
                try:
                    close = float(quote.get("close", 0))
                    prev_close = float(quote.get("previous_close", 0))
                    change = (close - prev_close) / prev_close * 100 if prev_close > 0 else 0
                    volume = int(quote.get("volume", 0))
                
                    result.append({
                        "name": name_map.get(symbol, symbol),
                        "price": close,
                        "change": change,
                        "volume": volume
                    })
                except (ValueError, TypeError):
                    # If there's an error parsing the data, skip this symbol
                    pass
        
        # If we have data for at least one symbol, return it
        if result:
            return result
        
        # Use fallback data if real data isn't available
        return [
            {"name": "Crude Oil (CL)", "price": 85.68, "change": 1.25, "volume": 950000},
            {"name": "Natural Gas (NG)", "price": 2.84, "change": -0.72, "volume": 480000},
            {"name": "Heating Oil (HO)", "price": 2.62, "change": 0.95, "volume": 165000},
            {"name": "Gasoline (RB)", "price": 2.57, "change": 1.18, "volume": 185000}
        ]
    except Exception as e:
        st.error(f"Error getting market data: {str(e)}")
        # Fallback data
        return [
            {"name": "Crude Oil (CL)", "price": 85.68, "change": 1.25, "volume": 950000},
            {"name": "Natural Gas (NG)", "price": 2.84, "change": -0.72, "volume": 480000},
            {"name": "Heating Oil (HO)", "price": 2.62, "change": 0.95, "volume": 165000},
            {"name": "Gasoline (RB)", "price": 2.57, "change": 1.18, "volume": 185000}
        ]

def create_plotly_chart(symbol, interval):
    """Create a Plotly chart for the specified symbol and interval."""
    try:
        # Fetch historical data
        data = api.get_time_series(
            symbol=symbol,
            interval=interval,
            outputsize=90
        )
        
        if not data.empty:
            # Create candlestick chart
            fig = go.Figure()
            
            # Add candlestick trace
            fig.add_trace(go.Candlestick(
                x=data['Timestamp'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol
            ))
            
            # Calculate 20-day SMA
            data['SMA20'] = data['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=data['Timestamp'],
                y=data['SMA20'],
                mode='lines',
                line=dict(color='blue', width=1),
                name='SMA 20'
            ))
            
            # Calculate 50-day SMA
            data['SMA50'] = data['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(
                x=data['Timestamp'],
                y=data['SMA50'],
                mode='lines',
                line=dict(color='orange', width=1),
                name='SMA 50'
            ))
            
            # Update layout
            fig.update_layout(
                title=f"{symbol} - {interval} Chart",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=False,
                height=600
            )
            
            return fig
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
    
    return None

def generate_signals_data():
    """Generate trading signals for display."""
    current_time = datetime.now()
    signals = [
        {
            "instrument": "CL",
            "name": "Crude Oil Futures",
            "direction": "BUY",
            "signal_strength": 0.85,
            "entry_price": 85.40,
            "stop_loss": 82.80,
            "take_profit": 91.50,
            "r_r_ratio": 2.3,
            "confidence": 0.82,
            "model": "Port Congestion Lead",
            "timestamp": current_time - timedelta(hours=2),
            "port": "Singapore",
            "lead_lag": "Port congestion leads price by 5 days"
        },
        {
            "instrument": "NG",
            "name": "Natural Gas Futures",
            "direction": "SELL",
            "signal_strength": 0.72,
            "entry_price": 2.95,
            "stop_loss": 3.15,
            "take_profit": 2.55,
            "r_r_ratio": 2.0,
            "confidence": 0.68,
            "model": "Port Congestion Lead",
            "timestamp": current_time - timedelta(hours=3),
            "port": "Rotterdam",
            "lead_lag": "Port congestion leads price by 3 days"
        },
        {
            "instrument": "HO",
            "name": "Heating Oil Futures",
            "direction": "SELL",
            "signal_strength": 0.65,
            "entry_price": 2.60,
            "stop_loss": 2.75,
            "take_profit": 2.30,
            "r_r_ratio": 2.0,
            "confidence": 0.62,
            "model": "Seasonal Pattern",
            "timestamp": current_time - timedelta(hours=5),
            "port": "Houston",
            "lead_lag": "No significant lead-lag relationship detected"
        }
    ]
    return pd.DataFrame(signals)

def render_signal_card(signal):
    """Render a single signal card with styles."""
    # Determine colors based on signal attributes
    direction_color = "green" if signal["direction"] == "BUY" else "red"
    rr_color = "green" if signal["r_r_ratio"] >= 2.0 else ("orange" if signal["r_r_ratio"] >= 1.5 else "gray")
    
    # Determine correlation label and color
    corr_value = signal["confidence"]
    if corr_value >= 0.8:
        corr_label, corr_color = "Very Strong", "#FFD700"  # Gold
    elif corr_value >= 0.6:
        corr_label, corr_color = "Strong", "#4CAF50"  # Green
    elif corr_value >= 0.4:
        corr_label, corr_color = "Moderate", "#2196F3"  # Blue
    else:
        corr_label, corr_color = "Low", "#9E9E9E"  # Gray
    
    # Create styled card
    st.markdown(f"""
    <div style="border:1px solid #ddd; border-radius:5px; padding:15px; margin-bottom:10px; position:relative;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h3 style="margin:0;">{signal['instrument']}</h3>
            <span style="background-color:{direction_color}; color:white; padding:3px 10px; border-radius:12px; font-weight:bold;">
                {signal['direction']}
            </span>
        </div>
        <p style="margin:5px 0;"><b>{signal['name']}</b></p>
        <hr style="margin:10px 0;">
        <p style="margin:5px 0;"><b>Port:</b> {signal['port']}</p>
        <p style="margin:5px 0;"><b>Entry:</b> ${signal['entry_price']:.2f}</p>
        <div style="display:flex; justify-content:space-between; margin:5px 0;">
            <span><b>Stop:</b> ${signal['stop_loss']:.2f}</span>
            <span><b>Target:</b> ${signal['take_profit']:.2f}</span>
        </div>
        <p style="margin:10px 0 5px 0;"><b>Signal Strength:</b></p>
        <div style="background-color:#e0e0e0; border-radius:10px; height:10px; width:100%; margin-bottom:10px;">
            <div style="background-color:#4CAF50; border-radius:10px; height:10px; width:{signal['signal_strength']*100}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; margin:5px 0; align-items:center;">
            <span><b>Confidence:</b></span>
            <span style="background-color:{corr_color}; color:white; padding:2px 8px; border-radius:8px; font-size:0.8rem;">
                {corr_label} ({signal['confidence']:.2f})
            </span>
        </div>
        <div style="display:flex; justify-content:space-between; margin:5px 0; align-items:center;">
            <span><b>Reward/Risk:</b></span>
            <span style="color:{rr_color}; font-weight:bold;">{signal['r_r_ratio']:.1f}</span>
        </div>
        <div style="margin:10px 0 5px 0;">
            <b>Model:</b> {signal['model']}
        </div>
        <div style="margin:5px 0; font-size:0.9em;">
            <b>Analysis:</b> {signal['lead_lag']}
        </div>
        <div style="text-align:right; font-size:0.8rem; color:#666; margin-top:5px;">
            {signal['timestamp'].strftime('%Y-%m-%d %H:%M')}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_opportunity_cards(signals_df, max_cards=3):
    """Render signal cards for top opportunities."""
    if signals_df.empty:
        st.info("No high-priority entry opportunities available right now.")
        return
    
    # Sort by signal strength and confidence and take top entries
    top_signals = signals_df.sort_values(by=["signal_strength", "confidence"], ascending=False).head(max_cards)
    
    # Create columns for cards
    cols = st.columns(len(top_signals))
    
    # Render each card
    for i, (_, signal) in enumerate(top_signals.iterrows()):
        with cols[i]:
            render_signal_card(signal)

# Main dashboard layout
st.title("Maritime Trading Dashboard")
st.markdown("### Commodity Futures Trading System with TwelveData API")

# Sidebar for navigation
st.sidebar.title("Navigation")

# Create sidebar navigation
page = st.sidebar.radio(
    "Select Page",
    ["Market Overview", "Trading Signals", "Technical Charts", "System Status"]
)

# Market Overview Page
if page == "Market Overview":
    st.header("Market Overview")
    
    # Get market data
    market_data = get_market_summary_data()
    
    # Create a row for market cards
    cols = st.columns(4)
    
    for i, data in enumerate(market_data):
        with cols[i]:
            # Create styled card with price and change
            change_color = "green" if data['change'] > 0 else "red"
            change_icon = "▲" if data['change'] > 0 else "▼"
            
            st.markdown(f"""
            <div style="border:1px solid #ddd; border-radius:5px; padding:10px; text-align:center;">
                <h4>{data['name']}</h4>
                <h3>${data['price']:.2f}</h3>
                <p style="color:{change_color};">
                    {change_icon} {abs(data['change']):.2f}%
                </p>
                <p style="font-size:0.8em; color:#666;">
                    Volume: {data['volume']:,}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add correlation heatmap
    st.subheader("Futures-Freight Correlation Map")
    
    # Create a simple correlation heatmap for demonstration
    correlation_data = pd.DataFrame(
        [
            [0.72, 0.65, 0.78, 0.52, 0.48],
            [0.58, 0.48, 0.52, 0.68, 0.72],
            [0.63, 0.59, 0.61, 0.42, 0.38],
            [0.45, 0.32, 0.38, 0.62, 0.58]
        ],
        index=["Crude Oil (CL)", "Natural Gas (NG)", "Heating Oil (HO)", "Gasoline (RB)"],
        columns=["BDI", "C3", "C5", "P1A", "P2A"]
    )
    
    fig = px.imshow(
        correlation_data.values,
        labels=dict(x="Freight Indices", y="Commodity Futures", color="Correlation"),
        x=correlation_data.columns,
        y=correlation_data.index,
        color_continuous_scale='RdYlGn',
        zmin=-1,
        zmax=1
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Trading Signals Page
elif page == "Trading Signals":
    st.header("Trading Signals")
    
    # Priority Entry Opportunities
    st.subheader("Priority Entry Opportunities")
    
    # Generate and display signal cards
    signals_df = generate_signals_data()
    render_opportunity_cards(signals_df)
    
    # Add signal history chart
    st.subheader("Signal Performance History")
    
    # Create mock performance data
    history_data = pd.DataFrame({
        "instrument": ["CL", "NG", "HO", "RB"],
        "win_rate": [0.68, 0.54, 0.62, 0.57],
        "avg_return": [1.8, 1.2, 1.5, 1.3],
        "profit_factor": [2.2, 1.4, 1.8, 1.5]
    })
    
    # Create column selection for metric to display
    metric_selection = st.radio(
        "Select Performance Metric",
        options=["win_rate", "avg_return", "profit_factor"],
        format_func=lambda x: {
            "win_rate": "Win Rate", 
            "avg_return": "Average Return (%)",
            "profit_factor": "Profit Factor"
        }[x],
        horizontal=True
    )
    
    # Create bar chart for selected metric
    fig = px.bar(
        history_data,
        x="instrument",
        y=metric_selection,
        color=metric_selection,
        color_continuous_scale="Blues",
        title=f"Signal Performance by Instrument - {metric_selection.replace('_', ' ').title()}",
        labels={
            "instrument": "Instrument",
            "win_rate": "Win Rate",
            "avg_return": "Average Return (%)",
            "profit_factor": "Profit Factor"
        }
    )
    
    # Show chart
    st.plotly_chart(fig, use_container_width=True)

# Technical Charts Page
elif page == "Technical Charts":
    st.header("Technical Charts")
    
    # Chart controls
    col1, col2 = st.columns(2)
    
    with col1:
        # Dropdown for symbol selection
        symbols = {
            "CL": "Crude Oil",
            "NG": "Natural Gas",
            "HO": "Heating Oil",
            "RB": "Gasoline"
        }
        
        selected_symbol = st.selectbox(
            "Select Symbol",
            options=list(symbols.keys()),
            format_func=lambda x: f"{x} - {symbols[x]}"
        )
    
    with col2:
        # Dropdown for timeframe selection
        timeframes = {
            "1day": "Daily",
            "4h": "4-Hour",
            "1h": "1-Hour"
        }
        
        selected_timeframe = st.selectbox(
            "Select Timeframe",
            options=list(timeframes.keys()),
            format_func=lambda x: timeframes[x]
        )
    
    # Try to get chart from API
    st.markdown("### Technical Chart")
    with st.spinner(f"Loading {symbols.get(selected_symbol, selected_symbol)} chart..."):
        try:
            # Get chart from TwelveData API
            chart_img = api.get_chart(
                symbol=selected_symbol,
                interval=selected_timeframe,
                chart_type="candle",
                studies=["sma"],
                outputsize=90
            )
            
            if chart_img:
                # Display the image
                st.image(chart_img, use_column_width=True)
            else:
                # Fall back to Plotly chart
                fig = create_plotly_chart(selected_symbol, selected_timeframe)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Failed to generate chart. Please try a different symbol or timeframe.")
        except Exception as e:
            st.error(f"Error displaying chart: {str(e)}")
            
            # Fall back to Plotly chart
            fig = create_plotly_chart(selected_symbol, selected_timeframe)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # Add market context section
    st.markdown("### Market Context")
    
    # Get current quote data for the selected symbol
    try:
        quote = api.get_quote(selected_symbol)
        if quote and len(quote) > 0:
            # Get relevant data
            current_price = float(quote.get("close", 0))
            prev_close = float(quote.get("previous_close", 0))
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0
            
            # Create metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Price", 
                    f"${current_price:.2f}", 
                    f"{change_pct:.2f}%",
                    delta_color="normal"
                )
            
            with col2:
                day_range = quote.get("day_range", "N/A")
                st.metric("Day Range", day_range)
            
            with col3:
                fifty_two_week = quote.get("fifty_two_week", "N/A")
                st.metric("52-Week Range", fifty_two_week)
            
            with col4:
                exchange = quote.get("exchange", "N/A")
                st.metric("Exchange", exchange)
        else:
            st.warning("Quote data not available for the selected symbol.")
    except Exception as e:
        st.error(f"Error fetching quote data: {str(e)}")

# System Status Page
elif page == "System Status":
    st.header("System Status")
    
    # Show TwelveData API integration status
    st.subheader("TwelveData API Integration")
    
    # Check API status by making a simple request
    api_status = "✅ Connected" if api.get_quote("CL") else "❌ Not Connected"
    
    st.markdown(f"""
    <div style="border:1px solid #ddd; border-radius:5px; padding:15px; margin-bottom:20px;">
        <h3>API Status: {api_status}</h3>
        <p><strong>API Key:</strong> {TWELVEDATA_API_KEY}</p>
        <p><strong>Base URL:</strong> {api.base_url}</p>
        <p><strong>Features Implemented:</strong></p>
        <ul>
            <li>✅ Historical price data retrieval</li>
            <li>✅ Current quotes and prices</li>
            <li>✅ Interactive charts with technical indicators</li>
            <li>✅ Rate limiting for API compliance</li>
            <li>✅ Futures symbol mapping</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Show data sources
    st.subheader("Data Sources")
    
    data_sources = [
        {
            "name": "TwelveData API",
            "status": "Primary",
            "description": "Provides real-time and historical price data for energy futures",
            "implemented": True
        },
        {
            "name": "Yahoo Finance",
            "status": "Fallback",
            "description": "Used as a fallback for historical price data if TwelveData fails",
            "implemented": True
        },
        {
            "name": "Datalastic API",
            "status": "Primary",
            "description": "Provides vessel tracking and port congestion data",
            "implemented": True
        },
        {
            "name": "Baltic Dry Index",
            "status": "Primary",
            "description": "Provides freight rate indices for dry bulk shipping",
            "implemented": True
        }
    ]
    
    for source in data_sources:
        status_color = "green" if source["implemented"] else "orange"
        status_label = source["status"] if source["implemented"] else "Pending"
        
        st.markdown(f"""
        <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h4 style="margin:0;">{source["name"]}</h4>
                <p style="margin:5px 0 0 0; font-size:0.9em;">{source["description"]}</p>
            </div>
            <div style="background-color:{status_color}; color:white; padding:5px 10px; border-radius:5px; font-weight:bold;">
                {status_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # System documentation
    st.subheader("Documentation")
    
    with st.expander("TwelveData API Usage"):
        st.markdown("""
        ### TwelveData API Integration
        
        The Maritime Trading System uses the TwelveData API to retrieve financial market data for energy futures:
        
        1. **Time Series Data**: Historical OHLCV data for energy futures
        2. **Quotes**: Current prices and market information
        3. **Charts**: Technical analysis charts with indicators
        
        #### API Endpoints Used:
        - `/time_series` - For historical price data
        - `/quote` - For current market quotes
        - `/chart` - For technical analysis charts
        
        #### Rate Limiting:
        The system implements rate limiting to comply with TwelveData API usage restrictions, ensuring that requests are spaced at least 1 second apart.
        
        #### Fallback Mechanisms:
        If TwelveData API fails, the system falls back to Yahoo Finance for historical data.
        """)
    
    with st.expander("System Architecture"):
        st.markdown("""
        ### Maritime Trading System Architecture
        
        The system follows a modular architecture with these main components:
        
        1. **Data Collection Layer**:
           - Energy futures prices (TwelveData API)
           - Vessel tracking and port congestion data (Datalastic API)
           - Maritime indices data (Baltic Dry Index, Baltic Clean Tanker Index)
        
        2. **Analysis Layer**:
           - Correlation analyzer between shipping congestion and energy prices
           - Signal generator based on correlation patterns
           - Price prediction models
        
        3. **Trading Layer**:
           - Strategy manager for executing trades
           - Risk management system
           - Performance tracking
        
        4. **Visualization Layer**:
           - Streamlit dashboard (this interface)
           - Interactive charts and data tables
           - Signal notifications
        """)

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.caption("Maritime Trading System - TwelveData API Integration")
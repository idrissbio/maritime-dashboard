"""
Maritime Trading Dashboard - Standalone Streamlit App
This is a simplified version that can be deployed directly to Streamlit sharing.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import requests
from PIL import Image
import io

# Set page config
st.set_page_config(
    page_title="Maritime Trading Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# TwelveData API Key
TWELVEDATA_API_KEY = "d347cca2eff5491582449d18e14131d5"

class TwelveDataAPI:
    """Simple client for TwelveData API."""
    
    def __init__(self):
        self.api_key = TWELVEDATA_API_KEY
        self.base_url = "https://api.twelvedata.com"
        self.futures_mapping = {
            "CL": {"symbol": "CL", "exchange": "NYMEX"},  # Crude Oil
            "NG": {"symbol": "NG", "exchange": "NYMEX"},  # Natural Gas
            "HO": {"symbol": "HO", "exchange": "NYMEX"},  # Heating Oil
            "RB": {"symbol": "RB", "exchange": "NYMEX"},  # RBOB Gasoline
        }
        
    def get_quote(self, symbol):
        """Get current quote for a symbol."""
        params = {
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        # Add exchange if it's a futures symbol
        if symbol in self.futures_mapping:
            params["symbol"] = self.futures_mapping[symbol]["symbol"]
            params["exchange"] = self.futures_mapping[symbol]["exchange"]
        
        try:
            response = requests.get(f"{self.base_url}/quote", params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Error getting quote: {str(e)}")
        
        return {}
    
    def get_time_series(self, symbol, interval="1day", outputsize=30):
        """Get time series data for a symbol."""
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.api_key,
            "format": "JSON"
        }
        
        # Add exchange if it's a futures symbol
        if symbol in self.futures_mapping:
            params["symbol"] = self.futures_mapping[symbol]["symbol"]
            params["exchange"] = self.futures_mapping[symbol]["exchange"]
        
        try:
            response = requests.get(f"{self.base_url}/time_series", params=params)
            if response.status_code == 200:
                data = response.json()
                if "values" in data:
                    df = pd.DataFrame(data["values"])
                    df["datetime"] = pd.to_datetime(df["datetime"])
                    
                    # Convert numeric columns
                    for col in ["open", "high", "low", "close", "volume"]:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col])
                    
                    # Rename columns to match our standard
                    df["Symbol"] = symbol
                    df = df.rename(columns={
                        "datetime": "Timestamp",
                        "open": "Open",
                        "high": "High",
                        "low": "Low",
                        "close": "Close",
                        "volume": "Volume"
                    })
                    
                    return df
        except Exception as e:
            st.error(f"Error getting time series: {str(e)}")
        
        return pd.DataFrame()
    
    def get_chart(self, symbol, interval="1day", studies=None, outputsize=100):
        """Get chart image from the API."""
        params = {
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
            "type": "candle",
            "theme": "dark",
            "width": 900,
            "height": 500
        }
        
        # Add exchange if it's a futures symbol
        if symbol in self.futures_mapping:
            params["symbol"] = self.futures_mapping[symbol]["symbol"]
            params["exchange"] = self.futures_mapping[symbol]["exchange"]
        
        # Add studies if provided
        if studies:
            params["studies"] = ",".join(studies)
        
        try:
            response = requests.get(f"{self.base_url}/chart", params=params)
            if response.status_code == 200:
                try:
                    img = Image.open(io.BytesIO(response.content))
                    return img
                except Exception as img_error:
                    st.error(f"Error processing chart image: {str(img_error)}")
        except Exception as e:
            st.error(f"Error getting chart: {str(e)}")
        
        return None

# Initialize the API client
api = TwelveDataAPI()

# Create sidebar for navigation
st.sidebar.title("Maritime Trading Dashboard")
page = st.sidebar.radio("Navigate", ["Market Overview", "Trading Signals", "Technical Charts"])

# Add information about TwelveData API
st.sidebar.markdown("---")
st.sidebar.info("This dashboard uses the TwelveData API for real-time market data.")

# ---------- MARKET OVERVIEW PAGE ----------
if page == "Market Overview":
    st.title("Market Overview")
    st.markdown("### Energy Futures Market Summary")
    
    # Function to get market summary data
    def get_market_data():
        symbols = ["CL", "NG", "HO", "RB"]
        name_map = {
            "CL": "Crude Oil",
            "NG": "Natural Gas",
            "HO": "Heating Oil",
            "RB": "Gasoline"
        }
        
        market_data = []
        for symbol in symbols:
            quote = api.get_quote(symbol)
            
            if quote and "symbol" in quote:
                try:
                    price = float(quote.get("close", 0))
                    prev_close = float(quote.get("previous_close", 0))
                    change = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0
                    volume = quote.get("volume", "N/A")
                    
                    market_data.append({
                        "name": name_map.get(symbol, symbol),
                        "price": price,
                        "change": change,
                        "volume": volume
                    })
                except (ValueError, TypeError):
                    pass
        
        # If no data from API, use mock data
        if not market_data:
            market_data = [
                {"name": "Crude Oil", "price": 85.68, "change": 1.25, "volume": 950000},
                {"name": "Natural Gas", "price": 2.84, "change": -0.72, "volume": 480000},
                {"name": "Heating Oil", "price": 2.62, "change": 0.95, "volume": 165000},
                {"name": "Gasoline", "price": 2.57, "change": 1.18, "volume": 185000}
            ]
        
        return market_data
    
    # Get market data with loading indicator
    with st.spinner("Fetching market data..."):
        market_data = get_market_data()
    
    # Display market summary cards
    cols = st.columns(4)
    for i, data in enumerate(market_data):
        with cols[i]:
            change_color = "green" if data["change"] > 0 else "red"
            change_icon = "▲" if data["change"] > 0 else "▼"
            
            st.markdown(f"""
            <div style="border:1px solid #ddd; border-radius:5px; padding:15px; text-align:center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3>{data["name"]}</h3>
                <h2 style="margin:10px 0;">${data["price"]:.2f}</h2>
                <p style="color:{change_color}; font-weight:bold;">
                    {change_icon} {abs(data["change"]):.2f}%
                </p>
                <p style="color:#666; font-size:0.9em;">
                    Volume: {data["volume"]:,}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add correlation heatmap
    st.subheader("Shipping-Energy Correlation Matrix")
    
    # Generate a sample correlation matrix
    correlation_data = pd.DataFrame(
        [
            [1.00, 0.72, 0.65, 0.78, 0.52, 0.48],
            [0.72, 1.00, 0.58, 0.48, 0.52, 0.68],
            [0.65, 0.58, 1.00, 0.63, 0.59, 0.61],
            [0.78, 0.48, 0.63, 1.00, 0.42, 0.38],
            [0.52, 0.52, 0.59, 0.42, 1.00, 0.62],
            [0.48, 0.68, 0.61, 0.38, 0.62, 1.00]
        ],
        index=["Crude Oil", "Natural Gas", "Heating Oil", "Gasoline", "Baltic Dry", "Port Cong."],
        columns=["Crude Oil", "Natural Gas", "Heating Oil", "Gasoline", "Baltic Dry", "Port Cong."]
    )
    
    # Create heatmap
    fig = px.imshow(
        correlation_data,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto"
    )
    
    fig.update_layout(
        title="Correlation Between Energy Futures and Shipping Metrics",
        height=500,
        margin=dict(l=40, r=40, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation
    with st.expander("Understanding the Correlation Matrix"):
        st.markdown("""
        This heatmap shows the correlation coefficients between different energy futures contracts and shipping metrics:
        
        - **Strong positive correlation (dark blue)**: The two variables move together
        - **No correlation (white)**: No relationship between movements
        - **Negative correlation (dark red)**: The variables move in opposite directions
        
        Strong correlations between shipping metrics (Baltic Dry Index, Port Congestion) and energy futures indicate potential trading opportunities.
        """)

# ---------- TRADING SIGNALS PAGE ----------
elif page == "Trading Signals":
    st.title("Trading Signals")
    st.markdown("### Signal Dashboard for Commodity Futures Trading")
    
    # Generate some mock signals
    def generate_signals():
        current_time = datetime.now()
        signals = [
            {
                "instrument": "CL",
                "name": "Crude Oil",
                "direction": "BUY",
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
                "name": "Natural Gas",
                "direction": "SELL",
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
                "name": "Heating Oil",
                "direction": "SELL",
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
        return signals
    
    # Get signals
    signals = generate_signals()
    
    # Display signal cards
    cols = st.columns(3)
    for i, signal in enumerate(signals):
        with cols[i]:
            direction_color = "green" if signal["direction"] == "BUY" else "red"
            
            st.markdown(f"""
            <div style="border:1px solid #ddd; border-radius:5px; padding:15px; margin-bottom:10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h3 style="margin:0;">{signal['name']} ({signal['instrument']})</h3>
                    <span style="background-color:{direction_color}; color:white; padding:3px 10px; border-radius:12px; font-weight:bold;">
                        {signal['direction']}
                    </span>
                </div>
                <p style="margin:5px 0;"><b>Port:</b> {signal['port']}</p>
                <p style="margin:5px 0;"><b>Entry:</b> ${signal['entry_price']:.2f}</p>
                <div style="display:flex; justify-content:space-between; margin:5px 0;">
                    <span><b>Stop:</b> ${signal['stop_loss']:.2f}</span>
                    <span><b>Target:</b> ${signal['take_profit']:.2f}</span>
                </div>
                <p style="margin:5px 0;"><b>R:R Ratio:</b> {signal['r_r_ratio']:.1f}</p>
                <div style="margin:10px 0;">
                    <b>Confidence:</b> {signal['confidence']:.2f}
                    <div style="background-color:#e0e0e0; border-radius:10px; height:8px; width:100%; margin-top:5px;">
                        <div style="background-color:#4CAF50; border-radius:10px; height:100%; width:{signal['confidence']*100}%;"></div>
                    </div>
                </div>
                <p style="margin:5px 0; font-size:0.9em;">
                    <b>Model:</b> {signal['model']}<br>
                    <b>Analysis:</b> {signal['lead_lag']}
                </p>
                <div style="text-align:right; font-size:0.8rem; color:#666; margin-top:5px;">
                    {signal['timestamp'].strftime('%Y-%m-%d %H:%M')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Add performance metrics
    st.subheader("Signal Performance Metrics")
    
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric("Win Rate", "68%", "5%")
    with metrics_cols[1]:
        st.metric("Avg. Return", "2.1%", "0.3%") 
    with metrics_cols[2]:
        st.metric("Profit Factor", "2.3", "0.2")
    with metrics_cols[3]:
        st.metric("Correlation Strength", "0.78", "0.05")

# ---------- TECHNICAL CHARTS PAGE ----------
elif page == "Technical Charts":
    st.title("Technical Charts")
    
    # Chart controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.selectbox(
            "Select Symbol",
            options=["CL", "NG", "HO", "RB"],
            format_func=lambda x: {
                "CL": "Crude Oil (CL)",
                "NG": "Natural Gas (NG)",
                "HO": "Heating Oil (HO)",
                "RB": "Gasoline (RB)"
            }.get(x, x)
        )
    
    with col2:
        interval = st.selectbox(
            "Select Timeframe",
            options=["1day", "4h", "1h", "1week"],
            format_func=lambda x: {
                "1day": "Daily",
                "4h": "4-Hour",
                "1h": "Hourly",
                "1week": "Weekly"
            }.get(x, x)
        )
    
    with col3:
        indicators = st.multiselect(
            "Select Indicators",
            options=["sma", "ema", "macd", "rsi"],
            default=["sma"],
            format_func=lambda x: {
                "sma": "Simple MA",
                "ema": "Exponential MA",
                "macd": "MACD",
                "rsi": "RSI"
            }.get(x, x)
        )
    
    # Display chart
    st.subheader(f"{symbol} - {interval} Chart")
    
    with st.spinner("Loading chart..."):
        # Try to get chart from API
        chart_img = api.get_chart(symbol, interval, indicators)
        
        if chart_img:
            st.image(chart_img, use_column_width=True)
        else:
            # Create fallback chart with plotly
            data = api.get_time_series(symbol, interval)
            
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
                
                # Add SMA if selected
                if "sma" in indicators:
                    data['SMA20'] = data['Close'].rolling(window=20).mean()
                    fig.add_trace(go.Scatter(
                        x=data['Timestamp'],
                        y=data['SMA20'],
                        mode='lines',
                        line=dict(color='blue', width=1),
                        name='SMA 20'
                    ))
                
                # Add EMA if selected
                if "ema" in indicators:
                    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
                    fig.add_trace(go.Scatter(
                        x=data['Timestamp'],
                        y=data['EMA20'],
                        mode='lines',
                        line=dict(color='orange', width=1),
                        name='EMA 20'
                    ))
                
                # Update layout
                fig.update_layout(
                    title=f"{symbol} - {interval} Chart",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    xaxis_rangeslider_visible=False,
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Could not retrieve chart data. Please try a different symbol or timeframe.")
    
    # Display current quote data
    quote = api.get_quote(symbol)
    
    if quote:
        # Extract data
        try:
            price = float(quote.get("close", 0))
            prev_close = float(quote.get("previous_close", 0))
            change = price - prev_close
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0
            
            # Display metrics
            metrics_cols = st.columns(4)
            
            with metrics_cols[0]:
                st.metric("Current Price", f"${price:.2f}", f"{change_pct:.2f}%")
            
            with metrics_cols[1]:
                day_range = quote.get("day_range", "N/A")
                st.metric("Day Range", day_range)
            
            with metrics_cols[2]:
                fifty_two_week = quote.get("fifty_two_week", "N/A")
                st.metric("52-Week Range", fifty_two_week)
            
            with metrics_cols[3]:
                exchange = quote.get("exchange", "N/A")
                st.metric("Exchange", exchange)
        except:
            st.warning("Could not parse quote data for metrics.")

# Footer
st.markdown("---")
st.markdown("Powered by TwelveData API")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
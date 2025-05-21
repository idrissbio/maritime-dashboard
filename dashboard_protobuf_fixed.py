"""
Maritime Trading Dashboard - With Protobuf Compatibility Fix
For Streamlit Cloud deployment
"""
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import plotly.express as px

# Set protobuf environment variable for compatibility
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# Set page config
st.set_page_config(
    page_title="Maritime Trading Dashboard",
    page_icon="🚢",
    layout="wide"
)

# TwelveData API Key
TWELVEDATA_API_KEY = "d347cca2eff5491582449d18e14131d5"

# Create sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Market Overview", "Trading Signals"]
)

st.sidebar.markdown("---")
st.sidebar.info("Maritime Trading System with TwelveData API")

# Basic functions for TwelveData API
def get_quote(symbol):
    """Get quote for a symbol."""
    # Map energy futures symbols to correct exchange
    futures_symbols = {
        "CL": "NYMEX",  # Crude Oil
        "NG": "NYMEX",  # Natural Gas
        "HO": "NYMEX",  # Heating Oil
        "RB": "NYMEX",  # Gasoline
    }
    
    params = {"apikey": TWELVEDATA_API_KEY}
    
    if symbol in futures_symbols:
        params["symbol"] = symbol
        params["exchange"] = futures_symbols[symbol]
    else:
        params["symbol"] = symbol
    
    try:
        response = requests.get("https://api.twelvedata.com/quote", params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error getting quote: {str(e)}")
    
    return {}

def get_market_data():
    """Get market data for energy futures."""
    symbols = ["CL", "NG", "HO", "RB"]
    name_map = {
        "CL": "Crude Oil",
        "NG": "Natural Gas",
        "HO": "Heating Oil",
        "RB": "Gasoline"
    }
    
    market_data = []
    
    for symbol in symbols:
        quote = get_quote(symbol)
        
        if quote and "symbol" in quote:
            try:
                price = float(quote.get("close", 0))
                prev_close = float(quote.get("previous_close", 0))
                change = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0
                volume = int(quote.get("volume", 0)) if quote.get("volume") else "N/A"
                
                market_data.append({
                    "name": name_map.get(symbol, symbol),
                    "price": price,
                    "change": change,
                    "volume": volume
                })
            except (ValueError, TypeError):
                pass
    
    # If no data from API, use fallback data
    if not market_data:
        market_data = [
            {"name": "Crude Oil", "price": 85.68, "change": 1.25, "volume": 950000},
            {"name": "Natural Gas", "price": 2.84, "change": -0.72, "volume": 480000},
            {"name": "Heating Oil", "price": 2.62, "change": 0.95, "volume": 165000},
            {"name": "Gasoline", "price": 2.57, "change": 1.18, "volume": 185000}
        ]
    
    return market_data

# Market Overview Page
if page == "Market Overview":
    st.title("Market Overview")
    st.markdown("### Energy Futures Market Summary")
    
    # Display market data cards
    with st.spinner("Fetching market data..."):
        market_data = get_market_data()
    
    cols = st.columns(4)
    for i, data in enumerate(market_data):
        with cols[i]:
            change_color = "green" if data["change"] > 0 else "red"
            change_icon = "▲" if data["change"] > 0 else "▼"
            
            st.markdown(f"""
            <div style="border:1px solid #ddd; border-radius:5px; padding:15px; text-align:center;">
                <h3>{data["name"]}</h3>
                <h2>${data["price"]:.2f}</h2>
                <p style="color:{change_color}; font-weight:bold;">
                    {change_icon} {abs(data["change"]):.2f}%
                </p>
                <p style="font-size:0.8em; color:#666;">
                    Volume: {data["volume"]:,}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add correlation heatmap
    st.subheader("Shipping-Energy Correlation Heatmap")
    
    # Sample correlation data
    correlation_data = pd.DataFrame(
        [
            [0.72, 0.65, 0.78, 0.52, 0.48],
            [0.58, 0.48, 0.52, 0.68, 0.72],
            [0.63, 0.59, 0.61, 0.42, 0.38],
            [0.45, 0.32, 0.38, 0.62, 0.58]
        ],
        index=["Crude Oil", "Natural Gas", "Heating Oil", "Gasoline"],
        columns=["BDI", "C3", "C5", "P1A", "P2A"]
    )
    
    # Create heatmap
    fig = px.imshow(
        correlation_data,
        text_auto=".2f",
        color_continuous_scale="RdYlGn",
        zmin=-1,
        zmax=1,
        labels=dict(x="Freight Indices", y="Energy Futures", color="Correlation")
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Trading Signals Page
elif page == "Trading Signals":
    st.title("Trading Signals")
    st.markdown("### Priority Entry Opportunities")
    
    # Generate sample signals
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
    
    # Display signal cards
    cols = st.columns(3)
    for i, signal in enumerate(signals):
        with cols[i]:
            direction_color = "green" if signal["direction"] == "BUY" else "red"
            
            st.markdown(f"""
            <div style="border:1px solid #ddd; border-radius:5px; padding:15px; margin-bottom:10px; position:relative;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h3 style="margin:0;">{signal["instrument"]}</h3>
                    <span style="background-color:{direction_color}; color:white; padding:3px 10px; border-radius:12px; font-weight:bold;">
                        {signal["direction"]}
                    </span>
                </div>
                <p style="margin:5px 0;"><b>{signal["name"]}</b></p>
                <hr style="margin:10px 0;">
                <p style="margin:5px 0;"><b>Port:</b> {signal["port"]}</p>
                <p style="margin:5px 0;"><b>Entry:</b> ${signal["entry_price"]:.2f}</p>
                <div style="display:flex; justify-content:space-between; margin:5px 0;">
                    <span><b>Stop:</b> ${signal["stop_loss"]:.2f}</span>
                    <span><b>Target:</b> ${signal["take_profit"]:.2f}</span>
                </div>
                <p style="margin:10px 0 5px 0;"><b>Signal Strength:</b></p>
                <div style="background-color:#e0e0e0; border-radius:10px; height:10px; width:100%; margin-bottom:10px;">
                    <div style="background-color:#4CAF50; border-radius:10px; height:10px; width:{signal["confidence"]*100}%;"></div>
                </div>
                <div style="margin:10px 0 5px 0;">
                    <b>Model:</b> {signal["model"]}
                </div>
                <div style="margin:5px 0; font-size:0.9em;">
                    <b>Analysis:</b> {signal["lead_lag"]}
                </div>
                <div style="text-align:right; font-size:0.8rem; color:#666; margin-top:5px;">
                    {signal["timestamp"].strftime("%Y-%m-%d %H:%M")}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption(f"Maritime Trading Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Debug section
st.sidebar.markdown("---")
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.write("### Environment Info")
    st.sidebar.write(f"Protobuf Implementation: {os.environ.get('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION', 'Unknown')}")
    st.sidebar.write(f"Streamlit version: {st.__version__}")
    st.sidebar.write(f"Pandas version: {pd.__version__}")
    st.sidebar.write(f"TwelveData API Key: {TWELVEDATA_API_KEY}")
    
    # Test API Connection
    if st.sidebar.button("Test API Connection"):
        with st.sidebar:
            with st.spinner("Testing API connection..."):
                test_result = get_quote("CL")
                if test_result:
                    st.success("API connection successful!")
                else:
                    st.error("API connection failed.")
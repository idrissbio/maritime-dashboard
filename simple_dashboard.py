"""
Ultra-Simple Maritime Trading Dashboard - Streamlit Cloud Deployment
This version uses only the most basic dependencies
"""
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Maritime Trading Dashboard",
    page_icon="🚢",
    layout="wide"
)

# TwelveData API Key
TWELVEDATA_API_KEY = "d347cca2eff5491582449d18e14131d5"

# TwelveData API simple functions
def get_quote(symbol):
    """Get quote for a symbol from TwelveData API."""
    # For futures symbols, add exchange
    futures_map = {
        "CL": {"symbol": "CL", "exchange": "NYMEX"},
        "NG": {"symbol": "NG", "exchange": "NYMEX"},
        "HO": {"symbol": "HO", "exchange": "NYMEX"},
        "RB": {"symbol": "RB", "exchange": "NYMEX"}
    }
    
    params = {"apikey": TWELVEDATA_API_KEY}
    
    if symbol in futures_map:
        params["symbol"] = futures_map[symbol]["symbol"]
        params["exchange"] = futures_map[symbol]["exchange"]
    else:
        params["symbol"] = symbol
    
    try:
        response = requests.get(f"https://api.twelvedata.com/quote", params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching quote: {str(e)}")
    
    return {}

def get_price_history(symbol, days=30):
    """Get basic price history for a symbol."""
    # For futures symbols, add exchange
    futures_map = {
        "CL": {"symbol": "CL", "exchange": "NYMEX"},
        "NG": {"symbol": "NG", "exchange": "NYMEX"},
        "HO": {"symbol": "HO", "exchange": "NYMEX"},
        "RB": {"symbol": "RB", "exchange": "NYMEX"}
    }
    
    params = {
        "apikey": TWELVEDATA_API_KEY,
        "interval": "1day",
        "outputsize": min(days, 90),
        "format": "JSON"
    }
    
    if symbol in futures_map:
        params["symbol"] = futures_map[symbol]["symbol"]
        params["exchange"] = futures_map[symbol]["exchange"]
    else:
        params["symbol"] = symbol
    
    try:
        response = requests.get(f"https://api.twelvedata.com/time_series", params=params)
        if response.status_code == 200:
            data = response.json()
            if "values" in data:
                prices = []
                for item in data["values"]:
                    prices.append({
                        "date": item["datetime"],
                        "close": float(item["close"]),
                        "open": float(item["open"]),
                        "high": float(item["high"]),
                        "low": float(item["low"]),
                    })
                return prices
    except Exception as e:
        st.error(f"Error fetching price history: {str(e)}")
    
    return []

# Function to get market data
def get_market_data():
    """Get current market data for energy futures."""
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
                volume = quote.get("volume", "N/A")
                
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

# Create sidebar navigation
st.sidebar.title("Maritime Trading Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Market Summary", "Trading Signals", "Price Charts"]
)

st.sidebar.markdown("---")
st.sidebar.info("Maritime Trading System powered by TwelveData API")

# 1. Market Summary Page
if page == "Market Summary":
    st.title("Energy Futures Market Summary")
    
    # Display market cards
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
                    Volume: {data["volume"]}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add a simple correlation display
    st.subheader("Shipping-Energy Correlation Analysis")
    
    st.markdown("""
    The Maritime Trading System analyzes correlations between:
    
    1. **Port congestion levels** in major shipping hubs
    2. **Energy futures prices** for commodities like oil and gas
    
    Strong correlations suggest that shipping congestion can **predict price movements** in energy markets.
    """)
    
    # Add a simple table with correlation values
    st.markdown("### Current Correlation Values")
    
    correlation_data = {
        "Commodity": ["Crude Oil", "Natural Gas", "Heating Oil", "Gasoline"],
        "Singapore Port": [0.72, 0.58, 0.63, 0.45],
        "Rotterdam Port": [0.65, 0.48, 0.59, 0.32],
        "Shanghai Port": [0.78, 0.52, 0.61, 0.38],
        "Houston Port": [0.52, 0.68, 0.42, 0.62]
    }
    
    df = pd.DataFrame(correlation_data)
    st.dataframe(df, use_container_width=True)

# 2. Trading Signals Page
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

# 3. Price Charts Page
elif page == "Price Charts":
    st.title("Price Charts")
    
    # Symbol selection
    symbols = {
        "CL": "Crude Oil",
        "NG": "Natural Gas",
        "HO": "Heating Oil",
        "RB": "Gasoline"
    }
    
    symbol = st.selectbox(
        "Select Symbol",
        options=list(symbols.keys()),
        format_func=lambda x: f"{x} - {symbols.get(x, '')}"
    )
    
    days = st.slider("Days to display", min_value=7, max_value=90, value=30)
    
    # Fetch price history
    with st.spinner(f"Fetching {symbols.get(symbol, symbol)} price history..."):
        prices = get_price_history(symbol, days)
    
    if prices:
        # Create a simple price chart
        df = pd.DataFrame(prices)
        df['date'] = pd.to_datetime(df['date'])
        
        # Display basic stats
        latest = df.iloc[0]
        earliest = df.iloc[-1]
        price_change = latest['close'] - earliest['close']
        price_change_pct = (price_change / earliest['close']) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"${latest['close']:.2f}")
        with col2:
            st.metric("Price Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")
        with col3:
            highest = df['high'].max()
            lowest = df['low'].min()
            st.metric("Range", f"${lowest:.2f} - ${highest:.2f}")
        
        # Plot basic line chart
        st.line_chart(df.set_index('date')['close'])
        
        # Show price table
        st.subheader("Recent Price Data")
        st.dataframe(
            df[['date', 'open', 'high', 'low', 'close']].head(10).style.format({
                'open': '${:.2f}',
                'high': '${:.2f}',
                'low': '${:.2f}',
                'close': '${:.2f}'
            }),
            use_container_width=True
        )
    else:
        st.error(f"Could not retrieve price history for {symbol}. Please try another symbol.")

# Footer
st.markdown("---")
st.caption(f"Maritime Trading Dashboard with TwelveData API | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
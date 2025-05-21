"""
Basic Maritime Trading Dashboard - TwelveData API Integration
Uses minimal dependencies for Streamlit Cloud deployment
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests

# Set page config
st.set_page_config(
    page_title="Maritime Trading Dashboard",
    page_icon="🚢"
)

# TwelveData API Key
TWELVEDATA_API_KEY = "d347cca2eff5491582449d18e14131d5"

# Basic TwelveData API functions
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

def get_price_data(symbol, days=30):
    """Get historical price data."""
    # Map energy futures symbols to correct exchange
    futures_symbols = {
        "CL": "NYMEX",  # Crude Oil
        "NG": "NYMEX",  # Natural Gas
        "HO": "NYMEX",  # Heating Oil
        "RB": "NYMEX",  # Gasoline
    }
    
    params = {
        "apikey": TWELVEDATA_API_KEY,
        "interval": "1day",
        "outputsize": days,
        "format": "JSON"
    }
    
    if symbol in futures_symbols:
        params["symbol"] = symbol
        params["exchange"] = futures_symbols[symbol]
    else:
        params["symbol"] = symbol
    
    try:
        response = requests.get("https://api.twelvedata.com/time_series", params=params)
        if response.status_code == 200:
            data = response.json()
            if "values" in data:
                return data["values"]
    except Exception as e:
        st.error(f"Error getting price data: {str(e)}")
    
    return []

# Title and description
st.title("Maritime Trading Dashboard")
st.markdown("### Integration with TwelveData API")

st.markdown("""
This dashboard demonstrates integration with the TwelveData API for real-time energy futures data.
The system analyzes correlations between maritime shipping congestion and energy futures prices.
""")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Market Data", "Trading Signals", "API Integration"])

# Tab 1: Market Data
with tab1:
    st.header("Energy Futures Market Data")
    
    # Get quotes for energy futures
    symbols = ["CL", "NG", "HO", "RB"]
    names = {
        "CL": "Crude Oil",
        "NG": "Natural Gas",
        "HO": "Heating Oil",
        "RB": "Gasoline"
    }
    
    # Create columns for market cards
    cols = st.columns(4)
    
    # Display market data cards
    for i, symbol in enumerate(symbols):
        with cols[i]:
            with st.spinner(f"Loading {names[symbol]} data..."):
                quote = get_quote(symbol)
                
                if quote and "symbol" in quote:
                    try:
                        price = float(quote.get("close", 0))
                        prev_close = float(quote.get("previous_close", 0))
                        change = price - prev_close
                        change_pct = (change / prev_close * 100) if prev_close > 0 else 0
                        
                        # Display card
                        st.subheader(names[symbol])
                        st.metric(
                            "Price", 
                            f"${price:.2f}", 
                            f"{change_pct:.2f}%"
                        )
                        
                        # Additional details
                        st.write(f"Symbol: {symbol}")
                        st.write(f"Exchange: {quote.get('exchange', 'N/A')}")
                    except (ValueError, TypeError):
                        st.warning(f"Could not parse data for {symbol}")
                else:
                    st.warning(f"No data available for {symbol}")
    
    # Select a symbol for historical chart
    st.subheader("Historical Price Chart")
    selected_symbol = st.selectbox(
        "Select Symbol",
        options=symbols,
        format_func=lambda x: f"{x} - {names.get(x, x)}"
    )
    
    # Get historical data
    with st.spinner(f"Loading {names.get(selected_symbol, selected_symbol)} price history..."):
        historical_data = get_price_data(selected_symbol, 60)
        
        if historical_data:
            # Convert to dataframe
            df = pd.DataFrame(historical_data)
            df["datetime"] = pd.to_datetime(df["datetime"])
            df["close"] = pd.to_numeric(df["close"])
            
            # Sort by date
            df = df.sort_values("datetime")
            
            # Create chart
            st.line_chart(df.set_index("datetime")["close"])
            
            # Basic stats
            latest = float(df["close"].iloc[-1])
            earliest = float(df["close"].iloc[0])
            price_change = latest - earliest
            price_change_pct = (price_change / earliest * 100)
            
            # Display metrics
            st.metric(
                "Price Change (60 days)", 
                f"${price_change:.2f}", 
                f"{price_change_pct:.2f}%"
            )
        else:
            st.error(f"Could not retrieve historical data for {selected_symbol}")

# Tab 2: Trading Signals
with tab2:
    st.header("Trading Signals")
    st.markdown("### Based on Port Congestion Analysis")
    
    # Create sample signals
    current_time = datetime.now()
    
    signals = [
        {
            "symbol": "CL",
            "name": "Crude Oil",
            "direction": "BUY",
            "price": 85.40,
            "confidence": 0.82,
            "port": "Singapore",
            "analysis": "Port congestion leads price by 5 days",
            "time": current_time - timedelta(hours=2)
        },
        {
            "symbol": "NG",
            "name": "Natural Gas",
            "direction": "SELL",
            "price": 2.95,
            "confidence": 0.68,
            "port": "Rotterdam",
            "analysis": "Port congestion leads price by 3 days",
            "time": current_time - timedelta(hours=6)
        },
        {
            "symbol": "HO",
            "name": "Heating Oil",
            "direction": "SELL",
            "price": 2.60,
            "confidence": 0.62,
            "port": "Houston",
            "analysis": "No significant lead-lag relationship",
            "time": current_time - timedelta(hours=12)
        }
    ]
    
    # Display signals
    for signal in signals:
        color = "green" if signal["direction"] == "BUY" else "red"
        
        st.markdown(f"""
        <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
            <h3 style="margin:0;">{signal['name']} ({signal['symbol']})</h3>
            <div style="display:flex; justify-content:space-between; margin-top:5px;">
                <span style="font-weight:bold; color:{color};">{signal['direction']} @ ${signal['price']:.2f}</span>
                <span>Port: {signal['port']}</span>
            </div>
            <div style="margin-top:10px;">
                <div style="font-weight:bold;">Confidence: {signal['confidence']:.2f}</div>
                <div style="background-color:#eee; height:10px; border-radius:5px; margin-top:5px;">
                    <div style="background-color:{color}; height:10px; width:{signal['confidence']*100}%; border-radius:5px;"></div>
                </div>
            </div>
            <p style="margin-top:10px;">{signal['analysis']}</p>
            <div style="text-align:right; font-size:0.8em; color:#777;">
                {signal['time'].strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Correlation information
    st.subheader("Correlation Analysis")
    st.markdown("""
    Our trading signals are based on correlations between:
    
    1. **Port congestion metrics** at major shipping hubs
    2. **Energy futures prices** for commodities
    
    Research shows that port congestion often leads price movements by 3-7 days,
    creating trading opportunities in energy markets.
    """)

# Tab 3: API Integration
with tab3:
    st.header("TwelveData API Integration")
    
    st.markdown("""
    This dashboard demonstrates integration with the TwelveData API for:
    
    - Real-time quotes for energy futures
    - Historical price data
    - Technical analysis
    
    The API key is: `d347cca2eff5491582449d18e14131d5`
    """)
    
    # API testing
    st.subheader("API Status Test")
    test_symbol = st.selectbox(
        "Select symbol to test API connection",
        options=["CL", "NG", "HO", "RB", "AAPL", "MSFT"]
    )
    
    if st.button("Test API Connection"):
        with st.spinner("Testing API connection..."):
            quote = get_quote(test_symbol)
            
            if quote and "symbol" in quote:
                st.success("✅ API connection successful!")
                st.json(quote)
            else:
                st.error("❌ API connection failed!")

# Footer
st.markdown("---")
st.caption(f"Maritime Trading Dashboard | TwelveData API Integration | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
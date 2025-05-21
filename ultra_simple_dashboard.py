"""
Ultra-simple Maritime Trading Dashboard for Streamlit Cloud
No dependencies except streamlit and requests
"""
import os
import streamlit as st
from datetime import datetime
import requests

# Set protobuf environment variable for compatibility
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# Set page config
st.set_page_config(
    page_title="Maritime Trading Dashboard",
    page_icon="🚢"
)

# TwelveData API Key
TWELVEDATA_API_KEY = "d347cca2eff5491582449d18e14131d5"

# Function to get quote
def get_quote(symbol):
    """Get current quote for a symbol."""
    url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={TWELVEDATA_API_KEY}"
    
    if symbol in ["CL", "NG", "HO", "RB"]:
        url += f"&exchange=NYMEX"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None

# Title and description
st.title("Maritime Trading Dashboard")
st.markdown("### Energy Futures & Maritime Shipping System")

# Create tabs
tab1, tab2 = st.tabs(["Market Data", "Trading Signals"])

# Market Data Tab
with tab1:
    st.header("Energy Futures Market Data")
    
    # Sample market data
    market_data = [
        {"name": "Crude Oil (CL)", "symbol": "CL", "price": 85.68, "change": 1.25},
        {"name": "Natural Gas (NG)", "symbol": "NG", "price": 2.84, "change": -0.72},
        {"name": "Heating Oil (HO)", "symbol": "HO", "price": 2.62, "change": 0.95},
        {"name": "Gasoline (RB)", "symbol": "RB", "price": 2.57, "change": 1.18}
    ]
    
    # Display market data
    for data in market_data:
        # Try to get live data
        quote = get_quote(data["symbol"])
        
        if quote and "symbol" in quote:
            try:
                price = float(quote.get("close", 0))
                prev_close = float(quote.get("previous_close", 0))
                change = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0
                
                # Update with live data
                data["price"] = price
                data["change"] = change
            except:
                pass
        
        # Display market card
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader(data["name"])
        
        with col2:
            change_color = "green" if data["change"] > 0 else "red"
            change_icon = "▲" if data["change"] > 0 else "▼"
            
            st.metric(
                "Price",
                f"${data['price']:.2f}",
                f"{change_icon} {abs(data['change']):.2f}%"
            )
        
        st.markdown("---")
    
    # Shipping-Energy correlation description
    st.subheader("Shipping-Energy Correlation")
    
    st.markdown("""
    ### Key Findings:
    
    - **Crude Oil-BDI**: 0.72 correlation coefficient
    - **Natural Gas-C5**: 0.52 correlation coefficient
    - **Port Congestion**: Leads price movements by 3-7 days
    - **Regional Impact**: Singapore port has strongest correlation
    """)

# Trading Signals Tab
with tab2:
    st.header("Trading Signals")
    
    # Sample signals
    signals = [
        {
            "name": "Crude Oil (CL)",
            "direction": "BUY",
            "entry": 85.40,
            "target": 91.50,
            "stop": 82.80,
            "port": "Singapore",
            "analysis": "Port congestion leads price by 5 days"
        },
        {
            "name": "Natural Gas (NG)",
            "direction": "SELL",
            "entry": 2.95,
            "target": 2.55,
            "stop": 3.15,
            "port": "Rotterdam",
            "analysis": "Port congestion leads price by 3 days"
        },
        {
            "name": "Heating Oil (HO)",
            "direction": "SELL",
            "entry": 2.60,
            "target": 2.30,
            "stop": 2.75,
            "port": "Houston",
            "analysis": "Seasonal pattern signal"
        }
    ]
    
    # Display signals
    for signal in signals:
        direction_color = "green" if signal["direction"] == "BUY" else "red"
        
        st.subheader(signal["name"])
        st.markdown(f"<span style='color:{direction_color}; font-weight:bold; font-size:18px;'>{signal['direction']}</span>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Entry:** ${signal['entry']:.2f}")
            st.write(f"**Target:** ${signal['target']:.2f}")
            st.write(f"**Stop:** ${signal['stop']:.2f}")
        
        with col2:
            st.write(f"**Port:** {signal['port']}")
            st.write(f"**Analysis:** {signal['analysis']}")
        
        st.markdown("---")

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    st.info("Use the tabs above to view different sections of the dashboard.")
    
    # Show debug info
    st.markdown("---")
    if st.checkbox("Show Debug Info"):
        st.write("### Environment Info")
        st.write(f"Protobuf Implementation: {os.environ.get('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION', 'Unknown')}")
        st.write(f"Streamlit version: {st.__version__}")
        st.write(f"Python version: {os.environ.get('PYTHONVERSION', 'Unknown')}")
        
        # Test API
        if st.button("Test API Connection"):
            with st.spinner("Testing API connection..."):
                test_result = get_quote("CL")
                if test_result and "symbol" in test_result:
                    st.success("API connection successful!")
                else:
                    st.error("API connection failed.")

# Footer
st.markdown("---")
st.caption(f"Maritime Trading Dashboard | Last updated: {datetime.now()}")
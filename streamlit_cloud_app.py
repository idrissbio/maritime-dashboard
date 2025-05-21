"""
Maritime Trading Dashboard - Ultra-simple version for Streamlit Cloud
This is a minimal version specifically for Streamlit Cloud deployment.

Dependencies:
streamlit==1.20.0
pandas==1.3.0
numpy==1.21.0
plotly==5.10.0
requests==2.25.1
Pillow==9.0.0
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Maritime Trading Dashboard",
    page_icon="🚢",
    layout="wide"
)

# Create sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Market Overview", "Trading Signals"]
)

st.sidebar.markdown("---")
st.sidebar.info("Maritime Trading System - Simplified Version")

# Market Overview Page
if page == "Market Overview":
    st.title("Market Overview")
    st.markdown("### Energy Futures Market Summary")
    
    # Sample market data (static for simplicity)
    market_data = [
        {"name": "Crude Oil", "price": 85.68, "change": 1.25, "volume": 950000},
        {"name": "Natural Gas", "price": 2.84, "change": -0.72, "volume": 480000},
        {"name": "Heating Oil", "price": 2.62, "change": 0.95, "volume": 165000},
        {"name": "Gasoline", "price": 2.57, "change": 1.18, "volume": 185000}
    ]
    
    # Display market data cards
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
            "model": "Port Congestion Lead",
            "port": "Singapore",
            "lead_lag": "Port congestion leads price by 5 days"
        },
        {
            "instrument": "NG",
            "name": "Natural Gas",
            "direction": "SELL",
            "entry_price": 2.95,
            "model": "Port Congestion Lead",
            "port": "Rotterdam",
            "lead_lag": "Port congestion leads price by 3 days"
        },
        {
            "instrument": "HO",
            "name": "Heating Oil",
            "direction": "SELL",
            "entry_price": 2.60,
            "model": "Seasonal Pattern",
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
                <div style="margin:10px 0 5px 0;">
                    <b>Model:</b> {signal["model"]}
                </div>
                <div style="margin:5px 0; font-size:0.9em;">
                    <b>Analysis:</b> {signal["lead_lag"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption(f"Maritime Trading Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
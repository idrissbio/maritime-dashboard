"""
Bare minimum Streamlit app - Uses only the simplest Streamlit features
"""
import streamlit as st

# Title
st.title("Maritime Trading Dashboard")

# Description
st.write("This is a minimal dashboard for the Maritime Trading System.")

# Sample data
st.write("### Energy Futures Market Data")

# Display sample market data using pure Streamlit
data = [
    {"name": "Crude Oil", "price": 85.68, "change": 1.25},
    {"name": "Natural Gas", "price": 2.84, "change": -0.72},
    {"name": "Heating Oil", "price": 2.62, "change": 0.95},
    {"name": "Gasoline", "price": 2.57, "change": 1.18}
]

# Display data
for item in data:
    st.write(f"**{item['name']}:** ${item['price']:.2f} ({item['change']:.2f}%)")

# Add a simple visualization
st.write("### Sample Visualization")
chart_data = {
    "Dates": ["Jan", "Feb", "Mar", "Apr", "May"],
    "Crude Oil": [82.5, 83.2, 84.1, 85.0, 85.7]
}

st.write("Crude Oil Prices (Last 5 Months):")
st.line_chart(
    {"Crude Oil": chart_data["Crude Oil"]}
)

# Add a button
if st.button("Show Trading Signals"):
    st.write("### Trading Signals")
    
    signals = [
        {"instrument": "Crude Oil", "direction": "BUY", "price": 85.40},
        {"instrument": "Natural Gas", "direction": "SELL", "price": 2.95}
    ]
    
    for signal in signals:
        direction_color = "green" if signal["direction"] == "BUY" else "red"
        st.markdown(f"{signal['instrument']}: <span style='color:{direction_color};'>{signal['direction']}</span> at ${signal['price']:.2f}", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Navigation")
    st.write("This is a minimal example dashboard.")
    
    # Add a simple dropdown
    view = st.selectbox(
        "Select View",
        ["Market Data", "Trading Signals", "Analysis"]
    )
    
    st.write(f"Selected: {view}")

# Footer
st.write("---")
st.write("Maritime Trading System - Minimal Demo")
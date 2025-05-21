"""
Minimal Streamlit app with protobuf compatibility fix
"""
import os
import streamlit as st

# This is a workaround for protobuf compatibility issues
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# Page content
st.title("Maritime Trading Dashboard")
st.write("Protobuf compatibility test")

# Simple interactive element
if st.button("Click me"):
    st.success("It works!")
else:
    st.write("Click the button to test basic Streamlit functionality.")

# Display environment information
st.write("## Environment Information")
st.code(f"""
Python version: {os.environ.get('PYTHONVERSION', 'Unknown')}
Protobuf implementation: {os.environ.get('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION', 'Unknown')}
""")

# Footer
st.write("---")
st.caption("Maritime Trading System - Compatibility Test")
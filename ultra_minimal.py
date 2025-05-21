import streamlit as st

st.title("Hello Streamlit")
st.write("This is a minimal test app.")

if st.button("Click me"):
    st.success("It works!")
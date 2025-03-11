import streamlit as st
def display_sidebar():
    model_options = ["Home"]
    st.sidebar.selectbox("Page", options=model_options, key="model")
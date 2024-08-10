import streamlit as st
from chat import run_chat

# Set page configuration first
st.set_page_config(page_title="Query-Response Chatbox")

if __name__ == "__main__":
    st.title("Apple Financial Insights Chatbot")
    st.write("Welcome to the Apple Financial Insights Chatbot! Ask any financial questions related to Apple, and I'll provide insights based on SEC filings.")
    st.write("---")
    run_chat()

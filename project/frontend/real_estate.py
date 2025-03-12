import streamlit as st
import requests
import pandas as pd
from streamlit_extras.add_vertical_space import add_vertical_space

# FastAPI Server URL
API_URL = "http://127.0.0.1:8000/ask"

# Set Streamlit Page Config
st.set_page_config(
    page_title="🏡 AI Real Estate Advisor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Styling
st.markdown(
    """
    <style>
        .stTextArea textarea {
            height: 100px !important; /* Increase input box height */
        }
        .st-emotion-cache-16idsys { /* Remove Streamlit top padding */
            padding-top: 10px;
        }
        .chat-container {
            padding: 15px;
            border-radius: 10px;
        }
        .chat-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .summary-box {
            padding: 10px;
            border-radius: 10px;
        }
        .floating-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            color: white;
            padding: 15px;
            cursor: pointer;
        }
  
    </style>
    """,
    unsafe_allow_html=True
)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["🏡 Home", "📜 Chat History", "ℹ️ About"])

# Initialize Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to call FastAPI
def get_ai_response(query):
    try:
        response = requests.post(API_URL, json={"query": query})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"🚨 Connection Error: {str(e)}"}
#home
with tab1:
    # Custom Header with Emoji & Subtitle
    st.markdown("<h1 style='text-align: center;'>🏡 AI-Powered Real Estate Advisor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; color: grey;'>Find the best real estate insights effortlessly</p>", unsafe_allow_html=True)
    
    # st.markdown("---")  # A subtle divider

    # # Input Section in a Centered Layout
    # st.markdown("<h3 style='text-align: center;'>🔍 Ask Me Anything About Real Estate</h3>", unsafe_allow_html=True)
    
    user_query = st.text_area(
        "",  # Removed extra label text
        placeholder="E.g., 'Available houses in Maitama Abuja?'", 
        height=80
    )

    # Centered Button
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        submit_button = st.button("💡 Get Insights", use_container_width=True)

    # Result Handling
    if submit_button and user_query.strip():
        with st.spinner("🤖 Generating response..."):
            response_data = get_ai_response(user_query)

        if "error" in response_data:
            st.error(response_data["error"])
        else:
            st.markdown("### 📌 AI Response")
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 10px;">
                {response_data["response"]}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🔍 Summary")
            st.markdown(f"""
            <div style="padding: 10px; border-radius: 10px;">
                {response_data["summary"]}
            </div>
            """, unsafe_allow_html=True)

    elif submit_button:
        st.warning("⚠️ Please enter a question.")


# Chat History Tab
with tab2:
    st.title("📜 Chat History")

    if st.session_state.chat_history:
        search_query = st.text_input("🔎 Search past queries", placeholder="E.g., 'Maitama Abuja'")

        for chat in reversed(st.session_state.chat_history):
            if search_query.lower() in chat["question"].lower():
                with st.expander(f"📌 {chat['question']}"):
                    st.markdown(f"**AI Response:** {chat['response']}")
                    st.markdown(f"**🔍 Summary:** {chat['summary']}")
    else:
        st.info("No chat history available.")

# About Tab
with tab3:
    st.title("ℹ️ About This App")
    st.markdown("""
    - **🔹 Powered by LLMs (Large Language Models)**
    - **🔹 Uses FastAPI as the Backend**
    - **🔹 Helps users find real estate insights**
    - **🔹 Built with ❤️ using Streamlit**
    """)

    add_vertical_space(2)
    st.caption("📢 Created by an AI Enthusiast 🚀")

# Floating Action Button (FAB)
st.markdown("""
    <button class="floating-button" onclick="window.scrollTo(0, 0)">🔝</button>
""", unsafe_allow_html=True)

# Run with: `streamlit run real_estate.py`

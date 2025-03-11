import streamlit as st
from streamlit_extras.app_logo import add_logo
from sidebar import display_sidebar
import requests
import json


st.markdown("""
    <style>
        body {
            background-color: #000035 !important;
        }
        .main {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .stButton button {
            background-color: #000068 !important;
            color: white !important;
            font-size: 18px !important;
            border-radius: 10px !important;
            padding: 10px 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/predict_price/"

# Streamlit App Title
st.title("🏡 Property Price Prediction Tool")
st.markdown('For the Nigerian housing and real-estate Market')

prediction_placeholder = st.empty()

display_sidebar()

with open("locations.json", "r") as file:
    location_data = json.load(file)

location_map = {loc["location"]: loc["location_code"] for loc in location_data}
location_names = list(location_map.keys())

location_name = st.selectbox("🔍 Search & Select Location", options=location_names)
location_code = location_map[location_name] 

sqm = st.number_input("Enter Property Size (sqm)", min_value=0.0, step=10.0)
bedrooms = st.slider("Number of Bedrooms", 1, 10, 3)
bathrooms = st.slider("Number of Bathrooms", 1, 10, 2)
furnishing_code = st.radio("Furnishing Type", ["Unfurnished", "Semi-Furnished", "Furnished"])

furnishing_map = {"Unfurnished": 0, "Semi-Furnished": 1, "Furnished": 2}
furnishing = furnishing_map[furnishing_code]

if st.button("🔮 Predict Price"):
    
    data = {
        "location_code": location_code,
        "sqm": sqm,
        "bathrooms": bathrooms,
        "bedrooms": bedrooms,
        "furnishing_code": furnishing
    }

    
    response = requests.post(API_URL, json=data)

    # Display prediction result if successful response code is 200, otherwise display error message.
    if response.status_code == 200:
        predicted_price = response.json()["predicted_price"]
        prediction_placeholder.success(f"🏠 Estimated Property Price: {predicted_price}")
    else:
        prediction_placeholder.error("Error in prediction. Please try again!")

st.markdown('</div>', unsafe_allow_html=True)
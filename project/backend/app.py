from fastapi import FastAPI
import joblib
import pandas as pd

model = joblib.load("./model/price_prediction_model.pkl")

app = FastAPI()

from pydantic import BaseModel

class PropertyInput(BaseModel):
    location_code: int  # Location code (e.g., 5 for Ikoyi)
    sqm: float     # Property size in square meters
    bathrooms: int # Number of bathrooms
    bedrooms: int  # Number of bedrooms
    furnishing_code: int  # 0 = Unfurnished, 1 = Semi-Furnished, 2 = Furnished

@app.post("/predict_price/")
def predict_price(data: PropertyInput):
    input_data = pd.DataFrame([data.model_dump()])

    predicted_price = model.predict(input_data)[0]

    return {"predicted_price": f"₦{predicted_price:,.2f}"}


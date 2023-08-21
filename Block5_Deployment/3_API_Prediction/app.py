import gc
import uvicorn
import numpy as np
import pandas as pd
from pydantic import BaseModel
from typing import Literal, List, Union
import joblib
import json
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse 

description = """
Welcome to my rental price predictor API !\n
Submit the characteristics of your car and a Machine Learning model, trained on GetAround data, will recommend you a price per day for your rental. 

**Use the endpoint `/predict` to estimate the daily rental price of your car !**
"""

app = FastAPI(
    title="💸 Car Rental Price Predictor",
    description=description,
    version="0.1",
    ocontact={"name": "Céline Tang"}
)

def load_model():
    model_file = joblib.load('CatBoost_model.joblib')
    model = model_file['model']
    feature_encoder = model_file['feature_encoder']
    scaler = model_file['scaler']   
    return model, feature_encoder, scaler

def preprocess_data(input_data,feature_encoder):
    # Create the list that will contain the preprocessed options:
    preprocessed_data = [] 
    for option in input_data:
        # Put each option of criteria into a dataframe
        option_df = pd.DataFrame([option.dict()])
        # Preprocess this dataframe
        preprocessed_option_df = feature_encoder.transform(option_df)
        preprocessed_option_array = preprocessed_option_df.toarray()
        # Add preprocessed option to the final list:
        preprocessed_data.append(preprocessed_option_array)
    # Convert the list of preprocessed data to a numpy array
    preprocessed_data = np.concatenate(preprocessed_data, axis=0)
    return preprocessed_data


def predict_data(model, preprocessed_data, scaler):
    normalized_predictions = model.predict(preprocessed_data)
    # Reshape the normalized predictions if needed
    if len(normalized_predictions.shape) == 1:
        normalized_predictions = normalized_predictions.reshape(-1, 1)   
    # Inverse transform the predictions to the original scale
    predictions = scaler.inverse_transform(normalized_predictions)
    return predictions.tolist()

class Car(BaseModel):
    model_key: Literal['Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford',
       'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors',
       'Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati',
       'Lexus', 'Honda', 'Mazda', 'Mini', 'Mitsubishi', 'Nissan', 'SEAT',
       'Subaru', 'Suzuki', 'Toyota', 'Yamaha'] 
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: Literal['diesel', 'petrol', 'hybrid_petrol', 'electro']
    paint_color: Literal['black', 'grey', 'white', 'red', 'silver', 'blue', 'orange',
       'beige', 'brown', 'green']
    car_type: Literal['convertible','coupe','estate','hatchback','sedan','subcompact','suv','van']
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

class CarFeatures(BaseModel):
    car_features: List[Car]

# Redirect automatically to /docs (without showing this endpoint in /docs)
@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


@app.post("/predict", tags=["Machine Learning"])
async def predict(car_features: CarFeatures):
    model, feature_encoder, scaler = load_model()
    preprocessed_data = preprocess_data(car_features.car_features, feature_encoder)
    predictions = predict_data(model, preprocessed_data, scaler)
    formatted_predictions = [round(pred[0]) for pred in predictions]
    return {"predictions": formatted_predictions}


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, debug=True, reload=True)


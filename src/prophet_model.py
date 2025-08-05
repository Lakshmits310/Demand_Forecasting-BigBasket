import pandas as pd
from prophet import Prophet
import os

DATA_PATH = "data/processed/products"

def load_product_sales(product_id: str):
    path = os.path.join(DATA_PATH, f"{product_id}.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df = df.rename(columns={"date": "ds", "units_sold": "y"})
    return df[['ds', 'y']]

def forecast_sales(product_id: str, days: int):
    df = load_product_sales(product_id)
    if df is None:
        return {"error": "404: Product data not found"}

    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)

    return result.to_dict(orient="records")

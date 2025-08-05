# app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from prophet import Prophet
from datetime import datetime, timedelta

app = FastAPI(title="E-Commerce Demand Forecasting API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
DATA_DIR = os.path.join("data", "processed")
COMBINED_FILE = os.path.join(DATA_DIR, "historical_sales.csv")
PRODUCT_DIR = os.path.join(DATA_DIR, "products")


def load_product_data(product_id: str):
    """Load per-product CSV if exists, else filter from combined CSV."""
    per_file = os.path.join(PRODUCT_DIR, f"{product_id}.csv")

    if os.path.exists(per_file):
        df = pd.read_csv(per_file)
    elif os.path.exists(COMBINED_FILE):
        df = pd.read_csv(COMBINED_FILE)
        df = df[df["product_id"] == product_id]
    else:
        return None

    if df.empty:
        return None

    return df


@app.get("/forecast/prophet")
def forecast_prophet(
    product_id: str = Query(..., description="Product ID (e.g., BB0001)"),
    days: int = Query(30, ge=1, le=180, description="Number of days to forecast"),
    current_stock: int = Query(0, ge=0, description="Current stock for urgency calculation")
):
    """Generate Prophet forecast for given product ID and forecast period."""

    df = load_product_data(product_id)
    if df is None:
        return {"error": "404: Product data not found"}

    # Prepare data
    df = df[["date", "units_sold", "product"]].copy()
    df.rename(columns={"date": "ds", "units_sold": "y"}, inplace=True)
    df["ds"] = pd.to_datetime(df["ds"])
    product_name = df["product"].iloc[0]

    # Train Prophet
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df)

    # Forecast
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    # Slice only future days
    forecast_future = forecast.tail(days)

    # Calculate metrics
    avg_sales = float(forecast_future["yhat"].mean())
    reorder_point = int(avg_sales * 1.2)
    total_sales = int(forecast_future["yhat"].sum())

    # Dynamic date range (today → today+N)
    start_date = datetime.today().strftime("%Y-%m-%d")
    end_date = (datetime.today() + timedelta(days=days - 1)).strftime("%Y-%m-%d")

    # Urgency status
    status = "critical" if current_stock < reorder_point else "safe"

    # Prepare response
    result = forecast_future[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_dict(orient="records")

    return {
        "product_id": product_id,
        "product_name": product_name,
        "forecast": result,
        "average_sales": avg_sales,
        "total_sales": total_sales,
        "reorder_point": reorder_point,
        "start_date": start_date,
        "end_date": end_date,
        "status": status
    }

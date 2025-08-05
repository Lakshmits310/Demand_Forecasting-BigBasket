import pandas as pd
import os
from fastapi import HTTPException
from .utils import get_data_path

def load_product_sales(product_id: str) -> pd.DataFrame:
    """Load historical sales for one product"""
    file_path = get_data_path(f"products/{product_id}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Product data not found")

    df = pd.read_csv(file_path, parse_dates=["date"])
    df = df.rename(columns={"date": "ds", "units_sold": "y"})
    return df

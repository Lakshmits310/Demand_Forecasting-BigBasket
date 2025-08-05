import pandas as pd
import os

# Paths
processed_path = "data/processed/historical_sales.csv"
meta_path = "data/processed/product_metadata.csv"

# Ensure file exists
if not os.path.exists(processed_path):
    raise FileNotFoundError(f"{processed_path} not found. Generate sales data first.")

# Load only product_id + product columns (faster)
df = pd.read_csv(processed_path, usecols=['product_id', 'product']).drop_duplicates()

# Save metadata
df.to_csv(meta_path, index=False)
print(f"Metadata saved to {meta_path} ({len(df)} products)")

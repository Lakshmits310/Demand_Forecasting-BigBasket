# 📦 E-Commerce Demand Forecasting
Predict future product sales and get reorder recommendations to avoid stock-outs using **Facebook Prophet** and an interactive **Streamlit dashboard**.

## **Features**
- Forecast daily sales for each product
- Reorder point recommendations (20% buffer)
- Interactive dashboard with Plotly charts
- FastAPI backend serving Prophet forecasts
- Power BI integration for executive reporting

## **Project Structure**
ecommerce-demand-forecasting/
│
├── api/
│   └── app.py                     # FastAPI backend (forecast API)
├── dashboard/
│   └── streamlit_app.py       # Streamlit frontend (user-facing UI)
├── data/
│   ├── raw/                   # Raw input data (e.g., BigBasket_Products.csv)
│   └── processed/             # Processed data & per-product CSVs
│       ├── historical\_sales.csv
│       ├── products/
│       │   └── BB0001.csv
|       |   └── BB0002.csv
|       |   └── BB0003.csv
|       |   └── BB0004.csv
|       |   └── BB0005.csv
│       └── product_metadata.csv
├── src/
│   └── generate\_metadata.py   # Script to create product metadata and other preprocessing and feature engineering files
├── requirements.txt
└── README.md

## **Implementation Steps**
### **1. Setup Environment**
```bash
git clone https://github.com/<username>/ecommerce-demand-forecasting.git
cd ecommerce-demand-forecasting
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
````

### **2. Prepare Data**
* Place `BigBasket_Products.csv` in `data/raw/`.
* Run preprocessing notebook/script to generate:
  * `historical_sales.csv`
  * `products/*.csv`
  * `product_metadata.csv`

### **3. Run FastAPI Backend**
```bash
uvicorn app:app --reload
```
API available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### **4. Run Streamlit Frontend**
```bash
streamlit run dashboard/streamlit_app.py
```
Access dashboard: [http://localhost:8501](http://localhost:8501)

## **Tech Stack**
* **Backend:** FastAPI, Prophet
* **Frontend:** Streamlit, Plotly
* **Data:** Dask, Pandas
* **Visualization:** Power BI

## **Future Enhancements**
* Integrate LSTM for deep learning forecasts
* Deploy API on GCP Cloud Run
* Automate Power BI refresh from API


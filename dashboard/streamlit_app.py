import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import os

st.set_page_config(page_title="E-Commerce Demand Forecasting", layout="wide")

# -------------------------------
# Load product metadata
# -------------------------------
@st.cache_data
def load_product_details():
    meta_path = "data/processed/product_metadata.csv"
    if os.path.exists(meta_path):
        df = pd.read_csv(meta_path)
        return [f"{row.product} ({row.product_id})" for row in df.itertuples()]
    else:
        return []

# Extract product_id from dropdown text
def extract_product_id(selection_text):
    if "(" in selection_text and ")" in selection_text:
        return selection_text.split("(")[-1].strip(")")
    return selection_text.strip()

# -------------------------------
# Forecast API call
# -------------------------------
def get_forecast(product_id, days, current_stock):
    url = f"http://127.0.0.1:8000/forecast/prophet?product_id={product_id}&days={days}&current_stock={current_stock}"
    try:
        response = requests.get(url)
        data = response.json()
        if "error" in data:
            st.error(data["error"])
            return None
        return data
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

# -------------------------------
# Plot forecast chart
# -------------------------------
def plot_forecast(forecast_df, product_name, reorder_point):
    df = pd.DataFrame(forecast_df)

    fig = go.Figure()

    # Forecast line
    fig.add_trace(go.Scatter(
        x=df['ds'], y=df['yhat'],
        mode='lines', name='Forecasted daily sales',
        line=dict(color='blue')
    ))

    # Confidence interval
    fig.add_trace(go.Scatter(
        x=pd.concat([df['ds'], df['ds'][::-1]]),
        y=pd.concat([df['yhat_upper'], df['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(0, 100, 255, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Best/Worst case'
    ))

    # Reorder point horizontal line
    fig.add_trace(go.Scatter(
        x=df['ds'], y=[reorder_point] * len(df),
        mode='lines', name='Reorder point',
        line=dict(color='red', dash='dash')
    ))

    fig.update_layout(
        title=f"Forecast for {product_name}",
        xaxis_title="Date",
        yaxis_title="Units Sold",
        template="plotly_dark",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1
        )
    )
    return fig

# -------------------------------
# UI Layout
# -------------------------------
st.title("📦 E-Commerce Demand Forecasting")
st.markdown("Predict future product sales and get reorder recommendations to avoid stock-outs.")

products = load_product_details()

if not products:
    st.warning("No products found. Please generate sales data and run `generate_metadata.py` first.")
else:
    # Dropdown
    product_choice = st.selectbox("Choose a product", products)

    # Extract product_id + name separately
    product_id = extract_product_id(product_choice)
    product_name = product_choice.replace(f" ({product_id})", "")

    # Days slider
    days = st.slider("Forecast period (days ahead)", 7, 90, 30)

    # Stock input
    current_stock = st.number_input("Enter your current stock (units)", min_value=0, value=0)

    if st.button("Generate Forecast"):
        with st.spinner("Generating forecast..."):
            result = get_forecast(product_id, days, current_stock)
            if result is not None:
                forecast = result["forecast"]
                reorder_point = result["reorder_point"]

                # Show summary
                st.subheader(f"📊 Forecast Summary ({result['start_date']} → {result['end_date']})")
                st.write(f"**Product:** {result['product_name']} ({result['product_id']})")
                st.write(f"**Average daily sales expected:** ~{round(result['average_sales'], 1)} units/day")
                st.write(f"**Total sales over {days} days:** ~{result['total_sales']} units")
                st.write(f"**Reorder point (20% buffer):** {reorder_point} units")

                # Stock urgency badge
                if result["status"] == "critical":
                    st.markdown(
                        f"<span style='background-color:#ff4d4d;color:white;padding:5px 10px;border-radius:5px;'>CRITICAL: Stock {current_stock} < {reorder_point}. Reorder now!</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<span style='background-color:#28a745;color:white;padding:5px 10px;border-radius:5px;'>SAFE: Stock {current_stock} ≥ {reorder_point}.</span>",
                        unsafe_allow_html=True
                    )

                # Plot chart
                fig = plot_forecast(forecast, result["product_name"], reorder_point)
                st.plotly_chart(fig, use_container_width=True)

                # Explanation
                st.markdown("""
### How to understand this forecast?
- **Blue line:** Predicted daily sales for the future.
- **Shaded area:** Best and worst case sales range (confidence).
- **Red dashed line:** Recommended minimum stock (reorder threshold).

### What should you do?
- If your current stock is **below** this line, place a restock order.
- If it is **above**, you're safe — but check again in a few days.
- **Tip:** Hover over the blue line to see daily predictions.
""")

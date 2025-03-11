import streamlit as st

# ✅ Set page config (Must be first Streamlit command)
st.set_page_config(page_title="Sales Streamlit Dashboard", layout="wide")

import pandas as pd
import mysql.connector
import json
import os
import plotly.express as px

# ✅ Include CSS for better design
st.markdown('<style>{}</style>'.format(open("styles.css").read()), unsafe_allow_html=True)

# ✅ Load database credentials from config.json
config_file = "config.json"
if os.path.exists(config_file):
    with open(config_file, "r") as file:
        db_config = json.load(file)
else:
    db_config = None  # No database config available

# ✅ Function to fetch data from MySQL
def fetch_from_mysql():
    if not db_config:
        return None, "⚠ No database configuration found."
    try:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT * FROM sales"
        df = pd.read_sql(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, f"❌ Error fetching data from MySQL: {e}"

# ✅ Function to fetch data from CSV
def fetch_from_csv(csv_path="C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/sales_data.csv"):
    try:
        df = pd.read_csv(csv_path)
        return df, None
    except Exception as e:
        return None, f"❌ Error reading CSV file: {e}"

# ✅ Load data: Try MySQL first, then CSV
df, error = fetch_from_mysql()
if df is None:
    df, error = fetch_from_csv()

# ✅ Streamlit UI
st.sidebar.header("🔍 Filters")
st.title("📊 Sales Streamlit Dashboard")

if df is not None and not df.empty:
    st.success("✅ Data loaded successfully!")

    # Sidebar Filters
    if 'product' in df.columns:
        selected_product = st.sidebar.selectbox("Select Product", options=["All"] + list(df['product'].unique()))
        if selected_product != "All":
            df = df[df['product'] == selected_product]

    if 'customer_segment' in df.columns:
        selected_segment = st.sidebar.selectbox("Select Customer Segment", options=["All"] + list(df['customer_segment'].unique()))
        if selected_segment != "All":
            df = df[df['customer_segment'] == selected_segment]

    # ✅ KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Total Revenue", f"${df['revenue'].sum():,.2f}")
    if 'profit' in df.columns:
        col2.metric("📈 Total Profit", f"${df['profit'].sum():,.2f}")
    if 'quantity' in df.columns:
        col3.metric("📦 Total Quantity Sold", f"{df['quantity'].sum():,.0f}")
    if 'discount' in df.columns:
        col4.metric("🔖 Avg Discount", f"{df['discount'].mean():.2f}%")

    # ✅ Revenue by Product (Interactive Plotly Chart)
    st.subheader("💰 Revenue by Product")
    if 'product' in df.columns and 'revenue' in df.columns:
        product_sales = df.groupby("product")["revenue"].sum().reset_index()
        fig = px.bar(product_sales, x='product', y='revenue', text_auto=True, title="Revenue by Product", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # ✅ Sales by Category
    st.subheader("📦 Sales by Category")
    if 'category' in df.columns and 'revenue' in df.columns:
        category_sales = df.groupby("category")["revenue"].sum().reset_index()
        fig = px.pie(category_sales, names='category', values='revenue', title="Sales by Category", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # ✅ Time-Series Analysis
    if 'date' in df.columns:
        st.subheader("📅 Sales Over Time")
        df['date'] = pd.to_datetime(df['date'])
        time_series = df.groupby("date")["revenue"].sum().reset_index()
        fig = px.line(time_series, x='date', y='revenue', title="Revenue Over Time", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # ✅ Data Table & Download Option
    st.subheader("📋 Filtered Data")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Data", data=csv, file_name="filtered_sales_data.csv", mime='text/csv')

else:
    st.error(error or "⚠ No data available.")


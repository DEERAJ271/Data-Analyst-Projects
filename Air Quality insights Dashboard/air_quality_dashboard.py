import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #0F1117;
        color: white;
    }
    .stApp {
        background-color: #0F1117;
    }
    .block-container {
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Air Quality Dashboard (CSV-Based)")

# File uploader
uploaded_file = st.file_uploader("📂 Upload Air Quality CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = ["City", "Location", "Parameter", "Value", "Unit", "Date", "Latitude", "Longitude"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ CSV must contain: {', '.join(required_cols)}")
        st.stop()

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Sidebar Filters
    with st.sidebar:
        st.markdown("## 🔎 Filters")
        cities = sorted(df["City"].dropna().unique().tolist())
        selected_cities = st.multiselect("Select Cities", cities, default=cities)

        all_params = df["Parameter"].dropna().unique().tolist()
        selected_params = st.multiselect("Select Pollutants", all_params, default=all_params[:2])

    filtered_df = df[(df["City"].isin(selected_cities)) & (df["Parameter"].isin(selected_params))]

    # Summary Cards
    st.markdown("### 📊 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average", round(filtered_df["Value"].mean(), 2))
    col2.metric("Maximum", round(filtered_df["Value"].max(), 2))
    col3.metric("Minimum", round(filtered_df["Value"].min(), 2))

    # Charts Section
    st.markdown("### 📈 Visualizations")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 📊 Average Values by City")
        avg_city = filtered_df.groupby("City")["Value"].mean().reset_index()
        bar_fig = px.bar(avg_city, x="City", y="Value", color="City", title="Average Pollutant Levels",
                         template="plotly_dark", text_auto=True)
        st.plotly_chart(bar_fig, use_container_width=True)

    with chart_col2:
        st.markdown("#### 🧁 Pollutant Contribution")
        pie_df = df["Parameter"].value_counts().reset_index()
        pie_df.columns = ["Parameter", "Count"]
        pie_fig = px.pie(pie_df, values="Count", names="Parameter", title="Pollutant Distribution",
                         template="plotly_dark", hole=0.3)
        st.plotly_chart(pie_fig, use_container_width=True)

    st.markdown("#### 📉 Trends Over Time (Multi-Pollutant)")
    trend_fig = px.line(filtered_df, x="Date", y="Value", color="Parameter",
                        markers=True, template="plotly_dark", title="Pollutant Levels Over Time")
    st.plotly_chart(trend_fig, use_container_width=True)

    # Map View with Value Info
    st.markdown("### 📍 Monitoring Stations Map")
    map_df = filtered_df.dropna(subset=["Latitude", "Longitude"])
    map_fig = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        color="Parameter",
        size="Value",
        hover_name="City",
        hover_data={"Value": True, "Unit": True, "Location": True},
        zoom=4,
        height=500,
        title="Station Locations with Pollutant Levels"
    )
    map_fig.update_layout(mapbox_style="carto-positron", template="plotly_dark")
    st.plotly_chart(map_fig, use_container_width=True)

    # Alerts
    st.markdown("### 🚨 High Pollution Alerts (> 100)")
    alerts = filtered_df[filtered_df["Value"] > 100]
    if not alerts.empty:
        for _, row in alerts.iterrows():
            st.error(f"{row['City']} at {row['Location']}: {row['Value']} {row['Unit']}")
    else:
        st.success("✅ All levels are safe.")

    # Download filtered data
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False),
        file_name=f"filtered_air_quality_data.csv",
        mime="text/csv"
    )
else:
    st.info("📌 Upload a CSV file to get started.")
    st.markdown("Try this [**sample CSV**](sandbox:/mnt/data/large_air_quality_data.csv)")









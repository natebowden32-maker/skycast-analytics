import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# 1. Setup Page
st.set_page_config(page_title="SkyCast Analytics", layout="wide")

# 2. Helper Functions (The "Logic")
def get_coords(city_name):
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
        response = requests.get(url).json()
        if "results" in response:
            return response["results"][0]["latitude"], response["results"][0]["longitude"]
        return None, None
    except Exception as e:
        return None, None

def get_weather(lat, lon, start_date, end_date):
    try:
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max&timezone=auto"
        return requests.get(url).json()
    except Exception as e:
        return None

# 3. The UI Layout
st.title("⚡ SkyCast Analytics")

# Sidebar for inputs
with st.sidebar:
    st.header("Configuration")
    default_start = datetime.now() - timedelta(days=30)
    default_end = datetime.now()
    
    date_range = st.date_input(
        "Select Date Range",
        (default_start, default_end),
        format="YYYY-MM-DD"
    )
    
    # Handle if user selects only one date
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = default_start, default_end

col1, col2 = st.columns(2)
with col1:
    city_a = st.text_input("City A", "New York")
with col2:
    city_b = st.text_input("City B", "Tokyo")

if st.button("Analyze Vibe"):
    if not city_a or not city_b:
        st.error("Please enter both cities.")
    else:
        with st.spinner("Fetching data..."):
            # Get Coordinates
            lat_a, lon_a = get_coords(city_a)
            lat_b, lon_b = get_coords(city_b)
            
            if lat_a is None:
                st.error(f"Could not find coordinates for {city_a}")
            elif lat_b is None:
                st.error(f"Could not find coordinates for {city_b}")
            else:
                # Get Weather Data
                data_a = get_weather(lat_a, lon_a, start_date, end_date)
                data_b = get_weather(lat_b, lon_b, start_date, end_date)
                
                if data_a and data_b and "daily" in data_a and "daily" in data_b:
                    # Process Data
                    df_a = pd.DataFrame({
                        "Date": data_a["daily"]["time"],
                        "Max Temp": data_a["daily"]["temperature_2m_max"],
                        "City": city_a
                    })
                    
                    df_b = pd.DataFrame({
                        "Date": data_b["daily"]["time"],
                        "Max Temp": data_b["daily"]["temperature_2m_max"],
                        "City": city_b
                    })
                    
                    df = pd.concat([df_a, df_b])
                    
                    # Calculate Metrics
                    avg_a = df_a["Max Temp"].mean()
                    avg_b = df_b["Max Temp"].mean()
                    
                    # Display Metrics
                    m_col1, m_col2 = st.columns(2)
                    m_col1.metric(f"Avg Max Temp ({city_a})", f"{avg_a:.1f}°C")
                    m_col2.metric(f"Avg Max Temp ({city_b})", f"{avg_b:.1f}°C")
                    
                    # Display Line Chart
                    fig = px.line(
                        df, 
                        x="Date", 
                        y="Max Temp", 
                        color="City", 
                        title="Max Daily Temperature Comparison",
                        color_discrete_map={city_a: "#00FFFF", city_b: "#FF4500"} # Neon Blue & Sunset Orange
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display Raw Data
                    with st.expander("View Raw Data"):
                        st.dataframe(df)
                        
                else:
                    st.error("Error fetching weather data.")
import streamlit as st
import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add project root to python path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.ui import apply_premium_style, render_header, render_footer, render_glass_card
from src.utils.db import get_clean_data
from src.forecasting.forecaster import TrafficForecaster

# Apply styling
apply_premium_style()

# Header
render_header("Traffic Volume Forecasting", "Time-series predictive timelines and seasonality decomposition")

# Load data
df_clean = get_clean_data()

# Sidebar options
st.sidebar.header("📈 Forecast Settings")
junction_id = st.sidebar.selectbox("Target Junction Sensor", [1, 2, 3, 4], index=2,
                                   help="Select the junction to forecast.")
horizon_days = st.sidebar.slider("Forecast Horizon (Days)", min_value=1, max_value=7, value=7,
                                 help="How many days into the future to project traffic volumes.")

# Run forecast computation
forecaster = TrafficForecaster()
forecaster.fit(df_clean, int(junction_id))

# Horizon days to hours conversion
horizon_hours = horizon_days * 24
df_forecast = forecaster.forecast(horizon_hours)

# Render Forecaster status
st.markdown(
    f"**Active Forecaster Core**: `{forecaster.model_type}` &nbsp; | &nbsp; **Forecast Period**: `{horizon_days} Days ({horizon_hours} hours)`", 
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

# Main layout: Plotly chart of forecast
st.markdown("### 🔮 Traffic Volume Forecast Timeline")

# Filter history for plotting (take last 7 days of history to compare visually, avoiding overcrowding the chart)
history_days = 7
j_history = df_clean[df_clean["junction_id"] == int(junction_id)].sort_values("timestamp")
last_hist_time = j_history["timestamp"].max()
cutoff_time = last_hist_time - pd.Timedelta(days=history_days)
j_history_plot = j_history[j_history["timestamp"] >= cutoff_time]

# Build Plotly Trace
fig_fc = go.Figure()

# Historical Trace
fig_fc.add_trace(go.Scatter(
    x=j_history_plot["timestamp"], y=j_history_plot["traffic_volume"],
    name="Historical Actuals", line=dict(color="#94a3b8", width=2)
))

# Forecasted Trace
fig_fc.add_trace(go.Scatter(
    x=df_forecast["timestamp"], y=df_forecast["forecasted_volume"],
    name="Forecasted Volume", line=dict(color="#ec4899", width=3)
))

# Upper / Lower Bound Shading
fig_fc.add_trace(go.Scatter(
    x=pd.concat([df_forecast["timestamp"], df_forecast["timestamp"].iloc[::-1]]),
    y=pd.concat([df_forecast["upper_bound"], df_forecast["lower_bound"].iloc[::-1]]),
    fill='toself',
    fillcolor='rgba(236, 72, 153, 0.15)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=True,
    name="95% Confidence Interval"
))

fig_fc.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(title="Traffic Volume (vehicles/hour)"),
    xaxis=dict(title="Date & Time"),
    hovermode="x unified",
    margin=dict(l=40, r=40, t=20, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_fc, use_container_width=True)

# Forecast Subsections
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### 🧩 Forecast Seasonal Decomposition")

# Check if model has seasonality profiles (fallback has profiles, prophet has components)
col_comp1, col_comp2, col_comp3 = st.columns(3)

with col_comp1:
    # 1. Overall trend (slope direction)
    st.write("**Overall Traffic Trend**")
    
    fig_tr = px.line(
        df_forecast, x="timestamp", y="trend",
        labels={"trend": "Detrended Volume", "timestamp": "Timeline"},
        color_discrete_sequence=["#818cf8"]
    )
    fig_tr.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=30),
        height=180
    )
    st.plotly_chart(fig_tr, use_container_width=True)
    
with col_comp2:
    # 2. Daily seasonality (hourly profile)
    st.write("**Hourly Commuter Seasonality**")
    
    if forecaster.prophet_model is not None:
        # Extract daily seasonality from forecast DataFrame
        # Prophet does not output a simple dictionary, but we can plot seasonality values across hours
        df_forecast["_hour"] = df_forecast["timestamp"].dt.hour
        daily_season = df_forecast.groupby("_hour")["seasonal_daily"].mean().reset_index()
        fig_dl = px.line(daily_season, x="_hour", y="seasonal_daily", color_discrete_sequence=["#c084fc"])
    else:
        # Custom fallback profiles are already hourly dict
        hours = list(range(24))
        vals = [forecaster.hourly_profile.get(h, 0.0) for h in hours]
        fig_dl = px.line(x=hours, y=vals, labels={"x": "Hour", "y": "Deviation"}, color_discrete_sequence=["#c084fc"])
        
    fig_dl.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=30),
        height=180,
        xaxis=dict(tickmode="linear", tick0=0, dtick=4)
    )
    st.plotly_chart(fig_dl, use_container_width=True)

with col_comp3:
    # 3. Weekly seasonality (day of week profile)
    st.write("**Weekly Day-of-Week Seasonality**")
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if forecaster.prophet_model is not None:
        df_forecast["_day"] = df_forecast["timestamp"].dt.weekday
        weekly_season = df_forecast.groupby("_day")["seasonal_weekly"].mean().reset_index()
        weekly_season["day_name"] = weekly_season["_day"].map(dict(enumerate(days)))
        fig_wk = px.line(weekly_season, x="day_name", y="seasonal_weekly", color_discrete_sequence=["#f472b6"])
    else:
        vals = [forecaster.weekly_profile.get(d, 0.0) for d in range(7)]
        fig_wk = px.line(x=days, y=vals, labels={"x": "Day", "y": "Deviation"}, color_discrete_sequence=["#f472b6"])
        
    fig_wk.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=30),
        height=180
    )
    st.plotly_chart(fig_wk, use_container_width=True)

# Export forecast option
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 💾 Export Generated Forecasts")
export_df = df_forecast[["timestamp", "forecasted_volume", "lower_bound", "upper_bound"]].copy()
export_df["junction_id"] = int(junction_id)

csv_data = export_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Forecast CSV",
    data=csv_data,
    file_name=f"junction_{junction_id}_traffic_forecast_horizon_{horizon_days}d.csv",
    mime="text/csv",
    help="Export forecasted point estimations and interval bounds for down-stream operations."
)

render_footer()

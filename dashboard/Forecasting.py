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

# Import from the new modular forecasting engine
from src.forecasting.train import train_forecaster
from src.forecasting.predict import predict_future_timeline

# Apply styling
apply_premium_style()

# Header
render_header("Traffic Volume Forecasting", "Time-series predictive timelines and seasonality decomposition")

# Objects
df_clean = None
df_forecast = None
forecaster = None
data_load_error = None
forecast_error = None

# Try loading cleaned data
try:
    df_clean = get_clean_data()
except NotImplementedError as e:
    data_load_error = str(e)

# Sidebar settings (will render for UI consistency)
st.sidebar.header("📈 Forecast Settings")
junction_id = st.sidebar.selectbox("Target Junction Sensor", [1, 2, 3, 4], index=2)
horizon_days = st.sidebar.slider("Forecast Horizon (Days)", min_value=1, max_value=7, value=7)
horizon_hours = horizon_days * 24

# Try running forecast if data loaded
if df_clean is not None:
    try:
        # Filter training data for selected junction
        junc_df = df_clean[df_clean["junction_id"] == int(junction_id)].copy()
        
        # Fit the forecaster using new function
        forecaster = train_forecaster(junc_df)
        
        # Query predictions using new function
        df_forecast = predict_future_timeline(forecaster, horizon_hours)
    except NotImplementedError as e:
        forecast_error = str(e)

# Render Global Warnings
if data_load_error:
    st.warning(f"⚠️ **Ingestion Database Offline**: `{data_load_error}`")
elif forecast_error:
    st.warning(
        f"⚠️ **Forecasting Engine Offline**  \n"
        f"The forecasting engine raised the following instruction:  \n"
        f"`{forecast_error}`"
    )
    st.info(
        "💡 **Developer Note:**  \n"
        "To view active forecasts and seasonal components, implement:  \n"
        "1. `train_forecaster` in `src/forecasting/train.py`  \n"
        "2. `predict_future_timeline` in `src/forecasting/predict.py`"
    )

# Active forecaster description
core_type = "Meta Prophet / Holt-Winters Additive" if not forecast_error and df_forecast is not None else "PENDING IMPLEMENTATION"
st.markdown(
    f"**Active Forecaster Core**: `{core_type}` &nbsp; | &nbsp; **Forecast Period**: `{horizon_days} Days ({horizon_hours} hours)`", 
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

# Main Forecast timeline container
st.markdown("### 🔮 Traffic Volume Forecast Timeline")

# Helper to render time-series plot placeholder
def render_forecast_plot_placeholder():
    st.markdown(
        """
        <div style="background-color: rgba(30, 41, 59, 0.4); border: 1px dashed rgba(255,255,255,0.15); border-radius: 12px; padding: 70px 20px; text-align: center; margin: 15px 0;">
            <div style="font-size: 3rem; margin-bottom: 12px;">📈</div>
            <div style="font-family: Outfit; font-size: 1.35rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">Forecasting Timeline Graph Offline</div>
            <div style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px; max-width: 600px; margin-left: auto; margin-right: auto;">
                Once you implement train_forecaster() and predict_future_timeline() inside src/forecasting/, 
                this container will render an interactive Actuals vs. Forecast timeline with a 95% shaded confidence interval band.
            </div>
            <div style="background-color: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); display: inline-block; padding: 6px 12px; border-radius: 6px; font-family: monospace; font-size: 0.8rem; color: #a855f7;">
                Implement in src/forecasting/train.py and predict.py
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if df_forecast is not None and df_clean is not None:
    # Render actual forecast plot
    history_days = 7
    j_history = df_clean[df_clean["junction_id"] == int(junction_id)].sort_values("timestamp")
    last_hist_time = j_history["timestamp"].max()
    cutoff_time = last_hist_time - pd.Timedelta(days=history_days)
    j_history_plot = j_history[j_history["timestamp"] >= cutoff_time]
    
    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(x=j_history_plot["timestamp"], y=j_history_plot["traffic_volume"], name="Historical Actuals", line=dict(color="#94a3b8", width=2)))
    fig_fc.add_trace(go.Scatter(x=df_forecast["timestamp"], y=df_forecast["forecasted_volume"], name="Forecasted Volume", line=dict(color="#ec4899", width=3)))
    fig_fc.add_trace(go.Scatter(
        x=pd.concat([df_forecast["timestamp"], df_forecast["timestamp"].iloc[::-1]]),
        y=pd.concat([df_forecast["upper_bound"], df_forecast["lower_bound"].iloc[::-1]]),
        fill='toself', fillcolor='rgba(236, 72, 153, 0.15)', line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip", showlegend=True, name="95% Confidence Interval"
    ))
    fig_fc.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Traffic Volume (vehicles/hour)"), xaxis=dict(title="Date & Time"),
        hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_fc, use_container_width=True)
else:
    render_forecast_plot_placeholder()

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### 🧩 Forecast Seasonal Decomposition")

# Component columns
col_comp1, col_comp2, col_comp3 = st.columns(3)

with col_comp1:
    st.write("**Overall Traffic Trend**")
    trend_plotted = False
    if df_forecast is not None:
        try:
            fig_tr = px.line(df_forecast, x="timestamp", y="trend", color_discrete_sequence=["#818cf8"])
            fig_tr.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=10, b=30), height=180
            )
            st.plotly_chart(fig_tr, use_container_width=True)
            trend_plotted = True
        except KeyError:
            pass
            
    if not trend_plotted:
        st.info("📈 **Trend decomposition under development.**")
        
with col_comp2:
    st.write("**Hourly Commuter Seasonality**")
    hourly_plotted = False
    if df_forecast is not None:
        try:
            # Check for Prophet or custom components
            if "seasonal_daily" in df_forecast.columns:
                df_forecast["_hour"] = df_forecast["timestamp"].dt.hour
                daily_season = df_forecast.groupby("_hour")["seasonal_daily"].mean().reset_index()
                fig_dl = px.line(daily_season, x="_hour", y="seasonal_daily", color_discrete_sequence=["#c084fc"])
                fig_dl.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=10, b=30), height=180, xaxis=dict(tickmode="linear", tick0=0, dtick=4)
                )
                st.plotly_chart(fig_dl, use_container_width=True)
                hourly_plotted = True
        except (KeyError, AttributeError):
            pass
            
    if not hourly_plotted:
        st.info("🕒 **Hourly cycles under development.**")

with col_comp3:
    st.write("**Weekly Day-of-Week Seasonality**")
    weekly_plotted = False
    if df_forecast is not None:
        try:
            if "seasonal_weekly" in df_forecast.columns:
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                df_forecast["_day"] = df_forecast["timestamp"].dt.weekday
                weekly_season = df_forecast.groupby("_day")["seasonal_weekly"].mean().reset_index()
                weekly_season["day_name"] = weekly_season["_day"].map(dict(enumerate(days)))
                fig_wk = px.line(weekly_season, x="day_name", y="seasonal_weekly", color_discrete_sequence=["#f472b6"])
                fig_wk.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=10, b=30), height=180
                )
                st.plotly_chart(fig_wk, use_container_width=True)
                weekly_plotted = True
        except (KeyError, AttributeError):
            pass
            
    if not weekly_plotted:
        st.info("🗓️ **Weekly cycles under development.**")

# CSV exports rendering check
if df_forecast is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💾 Export Generated Forecasts")
    export_df = df_forecast[["timestamp", "forecasted_volume", "lower_bound", "upper_bound"]].copy()
    export_df["junction_id"] = int(junction_id)
    csv_data = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Forecast CSV",
        data=csv_data,
        file_name=f"junction_{junction_id}_traffic_forecast_horizon_{horizon_days}d.csv",
        mime="text/csv"
    )
else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("📥 **CSV downloads are disabled.** (Requires forecasting engine fit output)")

render_footer()

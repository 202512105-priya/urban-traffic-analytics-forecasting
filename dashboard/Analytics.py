import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to python path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.ui import apply_premium_style, render_header, render_footer, render_metric_card
from src.utils.db import get_clean_data

# Import from the new modular analytics engine
from src.analytics.temporal import peak_hour_analysis, weekday_vs_weekend_analysis, monthly_trend_analysis
from src.analytics.weather import weather_impact_analysis, temperature_correlation_analysis
from src.analytics.holiday import holiday_impact_analysis
from src.analytics.traffic import get_traffic_peaks
from src.analytics.statistics import correlation_matrix, traffic_variance_analysis
from src.analytics.congestion import calculate_custom_congestion_score
from src.analytics.insights import generate_insights_report

# Apply page config & styling
apply_premium_style()

# Title
render_header("Traffic Analytics Dashboard", "Exploratory analysis and behavioral profiles across junctions")

# Initialize objects
df = None
data_load_error = None

# Try to load clean data
try:
    df = get_clean_data()
except NotImplementedError as e:
    data_load_error = str(e)

# --- Sidebar Filters (Will always render for UI completeness) ---
st.sidebar.header("🔍 Analytical Filters")

junction_options = ["All Junctions", 1, 2, 3, 4]
selected_junction = st.sidebar.selectbox("Select Junction", junction_options)
junction_filter = None if selected_junction == "All Junctions" else int(selected_junction)

weather_options = ["All Weather", "Clear", "Rainy", "Snowy", "Foggy"]
selected_weather = st.sidebar.selectbox("Weather Condition", weather_options)

holiday_options = ["All Days", "Holidays Only", "Regular Days Only"]
selected_holiday = st.sidebar.selectbox("Holiday Status", holiday_options)

# Date filter inputs (with static default dates since data is not loaded yet)
min_date = pd.to_datetime("2025-01-01").date()
max_date = pd.to_datetime("2025-12-31").date()
selected_date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Global data error handling
if data_load_error is not None:
    st.warning(
        f"⚠️ **Data Engine Offline**  \n"
        f"Could not load cleaned traffic records. Detail:  \n"
        f"`{data_load_error}`"
    )
    st.info(
        "💡 **Developer Note:**  \n"
        "To view active telemetry, first implement:  \n"
        "1. `generate_sample_data` in `src/utils/data_generator.py`  \n"
        "2. `get_clean_data` in `src/utils/db.py`  \n"
        "3. `run_cleaning_pipeline` in `src/cleaning/pipeline.py`"
    )

# Filter data if available
filtered_df = None
if df is not None:
    filtered_df = df.copy()
    if junction_filter is not None:
        filtered_df = filtered_df[filtered_df["junction_id"] == junction_filter]
    if selected_weather != "All Weather":
        filtered_df = filtered_df[filtered_df["weather_condition"] == selected_weather]
    if selected_holiday == "Holidays Only":
        filtered_df = filtered_df[filtered_df["is_holiday"] == 1]
    elif selected_holiday == "Regular Days Only":
        filtered_df = filtered_df[filtered_df["is_holiday"] == 0]
    if len(selected_date_range) == 2:
        start_dt = pd.to_datetime(selected_date_range[0])
        end_dt = pd.to_datetime(selected_date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        filtered_df = filtered_df[(filtered_df["timestamp"] >= start_dt) & (filtered_df["timestamp"] <= end_dt)]

# KPI Computations
kpis = None
kpi_error = None
if filtered_df is not None:
    try:
        # Resolve metrics using new statistics/traffic modules
        variance_data = traffic_variance_analysis(filtered_df)
        peaks_data = get_traffic_peaks(filtered_df)
        
        kpis = {
            "total_records": len(filtered_df),
            "avg_volume": int(filtered_df["traffic_volume"].mean()),
            "avg_speed": round(filtered_df["average_speed"].mean(), 1),
            "max_volume": int(filtered_df["traffic_volume"].max()),
        }
    except NotImplementedError as e:
        kpi_error = str(e)

# Render KPI metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    val = f"{kpis['total_records']:,}" if kpis is not None else "TBD"
    render_metric_card("Telemetry Records", val, "Total count")
with col2:
    val = f"{kpis['avg_volume']} veh/hr" if kpis is not None else "TBD"
    render_metric_card("Average Volume", val, "Average hourly flow")
with col3:
    val = f"{kpis['avg_speed']} km/h" if kpis is not None else "TBD"
    render_metric_card("Average Speed", val, "Average system velocity")
with col4:
    val = f"{kpis['max_volume']:,} veh" if kpis is not None else "TBD"
    render_metric_card("Peak Traffic Volume", val, "Max volume logged")

if kpi_error:
    st.info(f"💡 **KPI Computation Status:** `traffic_variance_analysis()` and `get_traffic_peaks()` in `src/analytics/` are under development.")

st.markdown("<br>", unsafe_allow_html=True)

# Main layout tabs
tab_temporal, tab_weather, tab_holidays, tab_junctions = st.tabs([
    "📈 Temporal Profiles", 
    "🌦️ Weather Influences", 
    "🎉 Holiday Comparisons", 
    "🔀 Junction Benchmarks"
])

# Utility helper to render standard placeholder boxes for unimplemented chart functions
def render_chart_placeholder(title: str, file_name: str, function_name: str, explanation: str):
    st.markdown(
        f"""
        <div style="background-color: rgba(30, 41, 59, 0.4); border: 1px dashed rgba(255,255,255,0.15); border-radius: 12px; padding: 40px 20px; text-align: center; margin: 15px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 12px;">📊</div>
            <div style="font-family: Outfit; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">{title} Chart Placeholder</div>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 16px; max-width: 500px; margin-left: auto; margin-right: auto;">
                {explanation}
            </div>
            <div style="background-color: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); display: inline-block; padding: 6px 12px; border-radius: 6px; font-family: monospace; font-size: 0.8rem; color: #a855f7;">
                Implement {function_name}() in src/analytics/{file_name}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# TAB 1: TEMPORAL PROFILES
with tab_temporal:
    st.markdown("### Hourly and Monthly Seasonal Patterns")
    col_hr, col_mth = st.columns(2)
    
    with col_hr:
        st.write("**Hourly Traffic & Speed Distribution**")
        hourly_peaks_plotted = False
        if filtered_df is not None:
            try:
                hourly_df = peak_hour_analysis(filtered_df)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hourly_df["hour"], y=hourly_df["avg_volume"],
                    name="Traffic Volume (LHS)", line=dict(color="#6366f1", width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=hourly_df["hour"], y=hourly_df["avg_speed"],
                    name="Average Speed (RHS)", line=dict(color="#ec4899", width=3, dash="dash"),
                    yaxis="y2"
                ))
                fig.update_layout(
                    yaxis=dict(title="Traffic Volume (vehicles/hour)", titlefont=dict(color="#6366f1")),
                    yaxis2=dict(title="Average Speed (km/h)", titlefont=dict(color="#ec4899"), overlaying="y", side="right"),
                    xaxis=dict(title="Hour of Day", tickmode="linear", tick0=0, dtick=2),
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=40, t=20, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                hourly_peaks_plotted = True
            except NotImplementedError:
                pass
        
        if not hourly_peaks_plotted:
            render_chart_placeholder(
                "Hourly Peaks", 
                "temporal.py",
                "peak_hour_analysis", 
                "Visualizes vehicle densities and speed drops during rush hours (08:00 and 17:00)."
            )
        
    with col_mth:
        st.write("**Monthly Average Volume & Congestion**")
        monthly_trends_plotted = False
        if filtered_df is not None:
            try:
                monthly_df = monthly_trend_analysis(filtered_df)
                fig_mth = px.bar(
                    monthly_df, x="month_name", y="avg_volume",
                    color="avg_congestion", color_continuous_scale="Viridis",
                    labels={"avg_volume": "Avg Volume", "month_name": "Month", "avg_congestion": "Congestion Index"}
                )
                fig_mth.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=20, b=40)
                )
                st.plotly_chart(fig_mth, use_container_width=True)
                monthly_trends_plotted = True
            except NotImplementedError:
                pass
                
        if not monthly_trends_plotted:
            render_chart_placeholder(
                "Monthly Trends", 
                "temporal.py",
                "monthly_trend_analysis", 
                "Shows traffic volumes and monthly congestion fluctuations throughout the seasonal year."
            )

# TAB 2: WEATHER INFLUENCES
with tab_weather:
    st.markdown("### Impact of Weather on Speed and Flow")
    col_w1, col_w2 = st.columns(2)
    
    weather_impact_plotted = False
    if filtered_df is not None:
        try:
            weather_df = weather_impact_analysis(filtered_df)
            
            with col_w1:
                st.write("**Traffic Volume by Weather Condition**")
                fig_w1 = px.bar(
                    weather_df, x="weather_condition", y="avg_volume",
                    color="weather_condition",
                    color_discrete_map={"Clear": "#818cf8", "Rainy": "#60a5fa", "Snowy": "#94a3b8", "Foggy": "#fbbf24"},
                    labels={"avg_volume": "Avg Volume (vehicles/hr)", "weather_condition": "Weather"}
                )
                fig_w1.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False, margin=dict(l=20, r=20, t=20, b=40)
                )
                st.plotly_chart(fig_w1, use_container_width=True)
                
            with col_w2:
                st.write("**Average Speed & Congestion Rate**")
                fig_w2 = go.Figure()
                fig_w2.add_trace(go.Bar(
                    x=weather_df["weather_condition"], y=weather_df["avg_speed"],
                    name="Avg Speed (km/h)", marker_color="#f43f5e", opacity=0.8
                ))
                fig_w2.add_trace(go.Scatter(
                    x=weather_df["weather_condition"], y=weather_df["avg_congestion"],
                    name="Avg Congestion Index", marker=dict(color="#f59e0b", size=10),
                    line=dict(color="#f59e0b", width=3), yaxis="y2"
                ))
                fig_w2.update_layout(
                    yaxis=dict(title="Speed (km/h)"), yaxis2=dict(title="Congestion Index (0-10)", overlaying="y", side="right"),
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=40, r=40, t=20, b=40)
                )
                st.plotly_chart(fig_w2, use_container_width=True)
                
            weather_impact_plotted = True
        except NotImplementedError:
            pass
            
    if not weather_impact_plotted:
        with col_w1:
            render_chart_placeholder("Weather Volume Impact", "weather.py", "weather_impact_analysis", "Analyzes traffic volume reductions during rainy/snowy conditions.")
        with col_w2:
            render_chart_placeholder("Weather Speed Impact", "weather.py", "weather_impact_analysis", "Graphs speed declines and congestion index rises during poor weather.")

# TAB 3: HOLIDAY COMPARISONS
with tab_holidays:
    st.markdown("### Holiday vs. Regular Day Traffic Behavior")
    
    holiday_plotted = False
    if filtered_df is not None:
        try:
            holiday_comp = holiday_impact_analysis(filtered_df)
            fig_hol = px.line(
                holiday_comp, x="hour", y="avg_volume", color="day_type",
                color_discrete_map={"Regular Day": "#6366f1", "Holiday": "#a855f7"},
                labels={"avg_volume": "Avg Traffic Volume", "hour": "Hour of Day", "day_type": "Day Classification"},
                title="Hourly Volume Profile Comparison"
            )
            fig_hol.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_hol, use_container_width=True)
            holiday_plotted = True
        except NotImplementedError:
            pass
            
    if not holiday_plotted:
        render_chart_placeholder(
            "Holiday Comparison", 
            "holiday.py",
            "holiday_impact_analysis", 
            "Illustrates the daily shift from weekday peak commuter windows to holiday afternoon travel profiles."
        )

# TAB 4: JUNCTION BENCHMARKS
with tab_junctions:
    st.markdown("### Performance Benchmark Across Monitored Junctions")
    col_j1, col_j2 = st.columns(2)
    
    junction_summary_plotted = False
    if filtered_df is not None:
        try:
            # We can use the correlation matrix stats or junction summaries here
            junc_df = get_traffic_peaks(filtered_df)
            
            with col_j1:
                st.write("**Junction Traffic Benchmarks**")
                fig_j1 = px.bar(
                    junc_df, x="junction_id", y="traffic_volume",
                    color="average_speed", color_continuous_scale="YlOrRd",
                    labels={"traffic_volume": "Volume", "junction_id": "Junction ID", "average_speed": "Speed"}
                )
                fig_j1.update_layout(
                    xaxis=dict(tickmode="linear"), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=20, b=40)
                )
                st.plotly_chart(fig_j1, use_container_width=True)
                
            with col_j2:
                st.write("**Speed vs. Volume Correlation**")
                corr_df = correlation_matrix(filtered_df)
                fig_j2 = px.imshow(corr_df, text_auto=True, color_continuous_scale="RdBu_r")
                fig_j2.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=20, b=40)
                )
                st.plotly_chart(fig_j2, use_container_width=True)
                
            junction_summary_plotted = True
        except NotImplementedError:
            pass
            
    if not junction_summary_plotted:
        with col_j1:
            render_chart_placeholder("Junction Benchmark Bar", "traffic.py", "get_traffic_peaks", "Renders average volumes and congestion indices for all junctions side by side.")
        with col_j2:
            render_chart_placeholder("Correlation Matrix", "statistics.py", "correlation_matrix", "Calculates a correlation matrix showing linear relations between variables.")

st.markdown("<hr>", unsafe_allow_html=True)

# Actionable Business Insights Section
st.markdown("### 💡 Actionable Business Insights")

insights_report = None
if filtered_df is not None:
    try:
        insights_report = generate_insights_report(filtered_df)
    except NotImplementedError:
        pass

if insights_report is not None:
    for idx, insight in enumerate(insights_report):
        st.info(f"💡 **Insight {idx+1}:** {insight}")
else:
    st.info(
        "ℹ/📊 **Actionable insights are currently under development.**  \n"
        "Business insights require the insights query engine (`src/analytics/insights.py`) "
        "and corresponding analysis scripts to be implemented."
    )

render_footer()

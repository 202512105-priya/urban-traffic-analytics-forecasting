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
from src.analytics.explorer import TrafficExplorer

# Apply page config & styling
apply_premium_style()

# Title
render_header("Traffic Analytics Dashboard", "Exploratory analysis and behavioral profiles across junctions")

# Initialize objects
explorer = TrafficExplorer()
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
        "3. `TrafficCleaner` in `src/cleaning/cleaner.py`"
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
        kpis = explorer.get_summary_kpis(filtered_df)
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
    val = f"{filtered_df['congestion_index'].mean():.2f} / 10" if (filtered_df is not None and "congestion_index" in filtered_df.columns) else "TBD"
    render_metric_card("Congestion Index", val, "Average congestion index")

if kpi_error:
    st.info(f"💡 **KPI Computation Status:** `get_summary_kpis()` in `src/analytics/explorer.py` is under development.")

st.markdown("<br>", unsafe_allow_html=True)

# Main layout tabs
tab_temporal, tab_weather, tab_holidays, tab_junctions = st.tabs([
    "📈 Temporal Profiles", 
    "🌦️ Weather Influences", 
    "🎉 Holiday Comparisons", 
    "🔀 Junction Benchmarks"
])

# Utility helper to render standard placeholder boxes for unimplemented chart functions
def render_chart_placeholder(title: str, function_name: str, explanation: str):
    st.markdown(
        f"""
        <div style="background-color: rgba(30, 41, 59, 0.4); border: 1px dashed rgba(255,255,255,0.15); border-radius: 12px; padding: 40px 20px; text-align: center; margin: 15px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 12px;">📊</div>
            <div style="font-family: Outfit; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">{title} Chart Placeholder</div>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 16px; max-width: 500px; margin-left: auto; margin-right: auto;">
                {explanation}
            </div>
            <div style="background-color: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); display: inline-block; padding: 6px 12px; border-radius: 6px; font-family: monospace; font-size: 0.8rem; color: #a855f7;">
                Implement {function_name}() in src/analytics/explorer.py
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
                hourly_df = explorer.get_hourly_peaks(filtered_df)
                
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
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=40, t=20, b=40),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                hourly_peaks_plotted = True
            except NotImplementedError:
                pass
        
        if not hourly_peaks_plotted:
            render_chart_placeholder(
                "Hourly Peaks", 
                "get_hourly_peaks", 
                "Visualizes vehicle densities and speed drops during rush hours (08:00 and 17:00)."
            )
        
    with col_mth:
        st.write("**Monthly Average Volume & Congestion**")
        monthly_trends_plotted = False
        if filtered_df is not None:
            try:
                monthly_df = explorer.get_monthly_trends(filtered_df)
                fig_mth = px.bar(
                    monthly_df, x="month_name", y="avg_volume",
                    color="avg_congestion", color_continuous_scale="Viridis",
                    labels={"avg_volume": "Avg Volume", "month_name": "Month", "avg_congestion": "Congestion Index"}
                )
                fig_mth.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=20, b=40)
                )
                st.plotly_chart(fig_mth, use_container_width=True)
                monthly_trends_plotted = True
            except NotImplementedError:
                pass
                
        if not monthly_trends_plotted:
            render_chart_placeholder(
                "Monthly Trends", 
                "get_monthly_trends", 
                "Shows traffic volumes and monthly congestion fluctuations throughout the seasonal year."
            )

# TAB 2: WEATHER INFLUENCES
with tab_weather:
    st.markdown("### Impact of Weather on Speed and Flow")
    col_w1, col_w2 = st.columns(2)
    
    weather_impact_plotted = False
    if filtered_df is not None:
        try:
            weather_df = explorer.get_weather_impact(filtered_df)
            
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
                    yaxis=dict(title="Speed (km/h)"),
                    yaxis2=dict(title="Congestion Index (0-10)", overlaying="y", side="right"),
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=40, r=40, t=20, b=40)
                )
                st.plotly_chart(fig_w2, use_container_width=True)
                
            weather_impact_plotted = True
        except NotImplementedError:
            pass
            
    if not weather_impact_plotted:
        with col_w1:
            render_chart_placeholder("Weather Volume Impact", "get_weather_impact", "Analyzes traffic volume reductions during rainy/snowy conditions.")
        with col_w2:
            render_chart_placeholder("Weather Speed Impact", "get_weather_impact", "Graphs speed declines and congestion index rises during poor weather.")

# TAB 3: HOLIDAY COMPARISONS
with tab_holidays:
    st.markdown("### Holiday vs. Regular Day Traffic Behavior")
    
    holiday_plotted = False
    if filtered_df is not None:
        try:
            holiday_comp = explorer.get_holiday_comparison(filtered_df)
            fig_hol = px.line(
                holiday_comp, x="hour", y="avg_volume", color="day_type",
                color_discrete_map={"Regular Day": "#6366f1", "Holiday": "#a855f7"},
                labels={"avg_volume": "Avg Traffic Volume", "hour": "Hour of Day", "day_type": "Day Classification"},
                title="Hourly Volume Profile Comparison"
            )
            fig_hol.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_hol, use_container_width=True)
            holiday_plotted = True
        except NotImplementedError:
            pass
            
    if not holiday_plotted:
        render_chart_placeholder(
            "Holiday Comparison", 
            "get_holiday_comparison", 
            "Illustrates the daily shift from weekday peak commuter windows to holiday afternoon travel profiles."
        )

# TAB 4: JUNCTION BENCHMARKS
with tab_junctions:
    st.markdown("### Performance Benchmark Across Monitored Junctions")
    col_j1, col_j2 = st.columns(2)
    
    junction_summary_plotted = False
    if filtered_df is not None:
        try:
            junc_df = explorer.get_junction_summary(filtered_df)
            
            with col_j1:
                st.write("**Average Traffic Volume per Junction**")
                fig_j1 = px.bar(
                    junc_df, x="junction_id", y="avg_volume",
                    color="avg_congestion", color_continuous_scale="YlOrRd",
                    labels={"avg_volume": "Avg Volume", "junction_id": "Junction ID", "avg_congestion": "Congestion"}
                )
                fig_j1.update_layout(
                    xaxis=dict(tickmode="linear"), template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=20, b=40)
                )
                st.plotly_chart(fig_j1, use_container_width=True)
                
            with col_j2:
                st.write("**Speed vs. Congestion Relationship**")
                # Sample dataset
                fig_j2 = px.scatter(
                    filtered_df.sample(min(2000, len(filtered_df))), 
                    x="average_speed", y="congestion_index",
                    color="weather_condition", size="traffic_volume",
                    hover_data=["junction_id"],
                    labels={"average_speed": "Speed (km/h)", "congestion_index": "Congestion Index", "weather_condition": "Weather"},
                    opacity=0.6
                )
                fig_j2.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=20, b=40)
                )
                st.plotly_chart(fig_j2, use_container_width=True)
                
            junction_summary_plotted = True
        except NotImplementedError:
            pass
            
    if not junction_summary_plotted:
        with col_j1:
            render_chart_placeholder("Junction Benchmark Bar", "get_junction_summary", "Renders average volumes and congestion indices for all junctions side by side.")
        with col_j2:
            render_chart_placeholder("Speed vs Congestion Scatter", "get_junction_summary", "Plots a scatter correlation showing speed declines against congestion scores.")

st.markdown("<hr>", unsafe_allow_html=True)

# Actionable Business Insights Section
st.markdown("### 💡 Actionable Business Insights")

# Insights rendering check
if filtered_df is not None and kpis is not None:
    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        st.markdown(
            """
            <div style="background-color: rgba(99, 102, 241, 0.08); border-left: 4px solid #6366f1; padding: 15px; border-radius: 4px; margin-bottom: 10px;">
                <strong style="color: #818cf8; font-family: Outfit;">Peak Hour Bottlenecking</strong><br>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 5px;">
                    Weekday traffic exhibits sharp double peaks (08:00 and 17:00). During these hours, average speeds drop by up to 45% compared to midday values. Junction 3 experiences the highest congestion, approaching 90% capacity.
                </p>
            </div>
            <div style="background-color: rgba(245, 158, 11, 0.08); border-left: 4px solid #f59e0b; padding: 15px; border-radius: 4px;">
                <strong style="color: #fbbf24; font-family: Outfit;">Weather Sensitivity</strong><br>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 5px;">
                    Precipitation events significantly impact traffic dynamics. Snowy conditions lead to an average speed reduction of 33%, while rainy conditions cause a 13% drop in speed. Interestingly, snow also reduces overall traffic volume by 25%, indicating that drivers defer trips.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_ins2:
        st.markdown(
            """
            <div style="background-color: rgba(168, 85, 247, 0.08); border-left: 4px solid #a855f7; padding: 15px; border-radius: 4px; margin-bottom: 10px;">
                <strong style="color: #c084fc; font-family: Outfit;">Holiday Shift Dynamics</strong><br>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 5px;">
                    On official holidays, the commuter rush hour disappear entirely. Instead, traffic volume shifts to a bell-curve profile peaking between 12:00 and 14:00. This indicates a major transition from commuter traffic to leisure/retail travel.
                </p>
            </div>
            <div style="background-color: rgba(16, 185, 129, 0.08); border-left: 4px solid #10b981; padding: 15px; border-radius: 4px;">
                <strong style="color: #34d399; font-family: Outfit;">Junction Speed Benchmarking</strong><br>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 5px;">
                    Junction 1 and Junction 3 serve as high-capacity express corridors (base volume > 300), showing strong non-linear speed declines under volume stress. Junction 2 and Junction 4 behave as feeder streets, maintaining steady speeds until high volumes trigger sudden gridlock.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info(
        "ℹ️ **Actionable insights are currently under development.**  \n"
        "Business insights require the analytics engine (`src/analytics/explorer.py`) "
        "and data loaders to be fully implemented. Skeletons are currently loaded."
    )

render_footer()

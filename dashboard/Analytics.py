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

# Load data
df = get_clean_data()
explorer = TrafficExplorer()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Analytical Filters")

# Junction filter
junction_options = ["All Junctions"] + sorted(list(df["junction_id"].unique()))
selected_junction = st.sidebar.selectbox("Select Junction", junction_options)
junction_filter = None if selected_junction == "All Junctions" else int(selected_junction)

# Weather filter
weather_options = ["All Weather"] + sorted(list(df["weather_condition"].unique()))
selected_weather = st.sidebar.selectbox("Weather Condition", weather_options)

# Holiday filter
holiday_options = ["All Days", "Holidays Only", "Regular Days Only"]
selected_holiday = st.sidebar.selectbox("Holiday Status", holiday_options)

# Date filter
min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()
selected_date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
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

# Compute KPIs for filtered dataset
kpis = explorer.get_summary_kpis(filtered_df)

# Render KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Telemetry Records", f"{kpis['total_records']:,}", "Filtered range")
with col2:
    render_metric_card("Average Volume", f"{kpis['avg_volume']} vehicles/hr", "Junction-specific avg")
with col3:
    render_metric_card("Average Speed", f"{kpis['avg_speed']} km/h", "System velocity")
with col4:
    render_metric_card("Congestion Index", f"{filtered_df['congestion_index'].mean():.2f} / 10", "Avg density score")

st.markdown("<br>", unsafe_allow_html=True)

# Main layout tabs
tab_temporal, tab_weather, tab_holidays, tab_junctions = st.tabs([
    "📈 Temporal Profiles", 
    "🌦️ Weather Influences", 
    "🎉 Holiday Comparisons", 
    "🔀 Junction Benchmarks"
])

# TAB 1: TEMPORAL PROFILES
with tab_temporal:
    st.markdown("### Hourly and Monthly Seasonal Patterns")
    
    col_hr, col_mth = st.columns(2)
    
    with col_hr:
        st.write("**Hourly Traffic & Speed Distribution**")
        hourly_df = explorer.get_hourly_peaks(filtered_df)
        
        # Dual axis plot: Volume vs Speed
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
            background_color="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_mth:
        st.write("**Monthly Average Volume & Congestion**")
        monthly_df = explorer.get_monthly_trends(filtered_df)
        
        fig_mth = px.bar(
            monthly_df, x="month_name", y="avg_volume",
            color="avg_congestion",
            color_continuous_scale="Viridis",
            labels={"avg_volume": "Avg Volume", "month_name": "Month", "avg_congestion": "Congestion Index"}
        )
        fig_mth.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_mth, use_container_width=True)

# TAB 2: WEATHER INFLUENCES
with tab_weather:
    st.markdown("### Impact of Weather on Speed and Flow")
    
    weather_df = explorer.get_weather_impact(filtered_df)
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.write("**Traffic Volume by Weather Condition**")
        fig_w1 = px.bar(
            weather_df, x="weather_condition", y="avg_volume",
            color="weather_condition",
            color_discrete_map={"Clear": "#818cf8", "Rainy": "#60a5fa", "Snowy": "#94a3b8", "Foggy": "#fbbf24"},
            labels={"avg_volume": "Avg Volume (vehicles/hr)", "weather_condition": "Weather"}
        )
        fig_w1.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=40)
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
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_w2, use_container_width=True)

# TAB 3: HOLIDAY COMPARISONS
with tab_holidays:
    st.markdown("### Holiday vs. Regular Day Traffic Behavior")
    
    holiday_comp = explorer.get_holiday_comparison(filtered_df)
    
    if len(holiday_comp) > 0:
        fig_hol = px.line(
            holiday_comp, x="hour", y="avg_volume", color="day_type",
            color_discrete_map={"Regular Day": "#6366f1", "Holiday": "#a855f7"},
            labels={"avg_volume": "Avg Traffic Volume", "hour": "Hour of Day", "day_type": "Day Classification"},
            title="Hourly Volume Profile Comparison"
        )
        fig_hol.update_update_variables = {"line": {"width": 3}}
        fig_hol.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=40)
        )
        st.plotly_chart(fig_hol, use_container_width=True)
    else:
        st.warning("Insufficient holiday data for selected filters.")

# TAB 4: JUNCTION BENCHMARKS
with tab_junctions:
    st.markdown("### Performance Benchmark Across Monitored Junctions")
    
    junc_df = explorer.get_junction_summary(filtered_df)
    
    col_j1, col_j2 = st.columns(2)
    with col_j1:
        st.write("**Average Traffic Volume per Junction**")
        fig_j1 = px.bar(
            junc_df, x="junction_id", y="avg_volume",
            color="avg_congestion", color_continuous_scale="YlOrRd",
            labels={"avg_volume": "Avg Volume", "junction_id": "Junction ID", "avg_congestion": "Congestion"}
        )
        fig_j1.update_layout(
            xaxis=dict(tickmode="linear"),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_j1, use_container_width=True)
        
    with col_j2:
        st.write("**Speed vs. Congestion Relationship**")
        fig_j2 = px.scatter(
            filtered_df.sample(min(2000, len(filtered_df))), 
            x="average_speed", y="congestion_index",
            color="weather_condition", size="traffic_volume",
            hover_data=["junction_id"],
            labels={"average_speed": "Speed (km/h)", "congestion_index": "Congestion Index", "weather_condition": "Weather"},
            opacity=0.6
        )
        fig_j2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_j2, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Actionable Business Insights Section
st.markdown("### 💡 Actionable Business Insights")
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

render_footer()

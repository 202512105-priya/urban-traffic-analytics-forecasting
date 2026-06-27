import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to python path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.ui import apply_premium_style, render_header, render_footer, render_metric_card, render_status_badge
from src.utils.db import get_raw_data, get_clean_data
from src.validation.validator import TrafficValidator
from src.cleaning.cleaner import TrafficCleaner

# Apply styling
apply_premium_style()

# Header
render_header("Data Quality Dashboard", "Telemetry health tracking and schema validation audit logs")

# Load raw dataset for analysis
df_raw = get_raw_data()
validator = TrafficValidator()

# Run validation report on raw data
raw_report = validator.get_quality_report(df_raw)

# Sidebar actions
st.sidebar.header("🛠️ Pipeline Controls")
st.sidebar.write("Simulate the ingestion and cleaning pipeline in real-time.")

# Trigger cleaning session state
if "pipeline_cleaned" not in st.session_state:
    st.session_state["pipeline_cleaned"] = False

def run_cleaning_pipeline():
    st.session_state["pipeline_cleaned"] = True
    st.sidebar.success("ETL Cleaning Pipeline Completed!")

if st.sidebar.button("⚙️ Run Ingestion Cleaning", on_click=run_cleaning_pipeline):
    pass

if st.sidebar.button("🔄 Reset to Raw Stream"):
    st.session_state["pipeline_cleaned"] = False
    st.rerun()

# Determine active dataset based on state
if st.session_state["pipeline_cleaned"]:
    # Run cleaning pipeline
    cleaner = TrafficCleaner()
    df_active = cleaner.fit_transform(df_raw)
    report = validator.get_quality_report(df_active)
    data_label = "CLEANED DATASET"
    badge_html = render_status_badge("PROCESSED - OK", "good")
else:
    df_active = df_raw
    report = raw_report
    data_label = "RAW TELEMETRY STREAM"
    badge_html = render_status_badge("RAW - AUDIT REQUIRED", "warning")

# Header state display
col_lbl, col_btn = st.columns([8, 2])
with col_lbl:
    st.markdown(f"**Current Pipeline State:** {badge_html} &nbsp; | &nbsp; **Dataset**: `{data_label}` (`{len(df_active):,}` rows)", unsafe_allow_html=True)
    
st.markdown("<br>", unsafe_allow_html=True)

# Quality Score Gauge
score = report["quality_score"]
score_color = "#34d399" if score >= 85 else ("#fbbf24" if score >= 70 else "#f87171")
score_type = "good" if score >= 85 else ("warning" if score >= 70 else "danger")

col_gauge, col_quality_summary = st.columns([4, 8])

with col_gauge:
    # Plotly Gauge Chart for Data Quality Score
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Telemetry Health Index", 'font': {'size': 18, 'family': 'Outfit'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': score_color},
            'bgcolor': "rgba(30, 41, 59, 0.3)",
            'borderwidth': 1,
            'bordercolor': "rgba(255,255,255,0.08)",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [60, 85], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [85, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ]
        }
    ))
    fig_gauge.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=10),
        height=200
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_quality_summary:
    st.markdown("### 🔍 Telemetry Audit Summary")
    
    # Render KPI subcards
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        missing_count = sum([col_info["total_missing"] for col_info in report["missing_values"].values()])
        render_metric_card("Missing Elements", f"{missing_count:,}", "To be imputed" if not st.session_state["pipeline_cleaned"] else "Resolved", "down" if missing_count > 0 else "up")
    with col_kpi2:
        dup_count = report["duplicates"]["duplicate_count"]
        render_metric_card("Duplicate Rows", f"{dup_count:,}", "To be purged" if not st.session_state["pipeline_cleaned"] else "Resolved", "down" if dup_count > 0 else "up")
    with col_kpi3:
        corrupt_count = report["corrupted_columns_count"]
        render_metric_card("Type Mismatches", f"{corrupt_count}", "Corrupted string types" if not st.session_state["pipeline_cleaned"] else "Resolved", "down" if corrupt_count > 0 else "up")

st.markdown("<br><hr>", unsafe_allow_html=True)

# Detailed Audits Tab
tab_missing, tab_duplicates, tab_schema, tab_outliers = st.tabs([
    "🧩 Null & Missingness Audit",
    "👯 Duplicate Records",
    "📋 Schema Datatype Audit",
    "📈 Outlier Distributions"
])

# 1. MISSINGNESS AUDIT
with tab_missing:
    st.write("### Missing Values Per Column")
    missing_data = []
    for col, info in report["missing_values"].items():
        missing_data.append({
            "Column": col,
            "Null Count": info["null_count"],
            "Sentinel Count": info["sentinel_count"],
            "Total Missing": info["total_missing"],
            "Percentage (%)": info["percentage"]
        })
    df_missing = pd.DataFrame(missing_data)
    
    # Plot missingness
    fig_miss = px.bar(
        df_missing, x="Column", y="Percentage (%)",
        color="Percentage (%)", color_continuous_scale="Reds",
        labels={"Percentage (%)": "Missing Percentage (%)"},
        text="Percentage (%)"
    )
    fig_miss.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=40),
        yaxis=dict(range=[0, max(15, df_missing["Percentage (%)"].max() + 5)])
    )
    fig_miss.update_traces(textposition="outside", texttemplate='%{y:.1f}%')
    
    col_m1, col_m2 = st.columns([7, 5])
    with col_m1:
        st.plotly_chart(fig_miss, use_container_width=True)
    with col_m2:
        st.dataframe(df_missing.sort_values(by="Percentage (%)", ascending=False), use_container_width=True, hide_index=True)
        st.info("Imputation Policy: Traffic volumes and average speeds are imputed using median values grouped by hour and junction. Weather categories are imputed using the mode.")

# 2. DUPLICATES AUDIT
with tab_duplicates:
    st.write("### Record Duplication Check")
    dup_info = report["duplicates"]
    
    if dup_info["duplicate_count"] > 0:
        st.warning(f"Audited {dup_info['duplicate_count']} exact duplicate records ({dup_info['percentage']}% of total dataset).")
        
        # Display duplicates sample
        st.write("Sample Duplicate Records:")
        dups_sample = df_active[df_active.duplicated(keep=False)].head(10)
        st.dataframe(dups_sample, use_container_width=True)
    else:
        st.success("Success: No duplicate records detected in the active stream.")

# 3. SCHEMA DATATYPE AUDIT
with tab_schema:
    st.write("### Target Schema Validation Audit")
    
    schema_report = report["schema"]
    
    schema_data = []
    for col, exp_type in validator.target_schema.items():
        if col in df_active.columns:
            actual_type = str(df_active[col].dtype)
            
            # Check if this column has a type mismatch in this report
            has_mismatch = col in schema_report["type_discrepancies"]
            status = "Mismatch ❌" if has_mismatch else "Pass Check  "
        else:
            actual_type = "Missing"
            status = "Missing ❌"
            
        schema_data.append({
            "Column Name": col,
            "Target Schema Type": exp_type,
            "Actual Ingested Type": actual_type,
            "Audit Status": status
        })
        
    df_schema = pd.DataFrame(schema_data)
    st.dataframe(df_schema, use_container_width=True, hide_index=True)
    
    if not schema_report["is_schema_ok"]:
        st.error("Schema Audit failed due to mismatches or missing columns.")
        if schema_report["type_discrepancies"]:
            for col, details in schema_report["type_discrepancies"].items():
                st.write(f"- Column `{col}`: Expected `{details['expected']}` but parsed as `{details['actual']}`.")
    else:
        st.success("Target schema validation checklist passed successfully.")

# 4. OUTLIERS AUDIT
with tab_outliers:
    st.write("### Outlier Detection (Z-Score > 3.0)")
    
    outliers_data = []
    for col, info in report["outliers"].items():
        outliers_data.append({
            "Numeric Column": col,
            "Outlier Count": info["outlier_count"],
            "Percentage (%)": info["percentage"],
            "Statistical Bound (99.7%)": f"{info['bounds'][0]} to {info['bounds'][1]}"
        })
    df_outliers = pd.DataFrame(outliers_data)
    st.dataframe(df_outliers, use_container_width=True, hide_index=True)
    
    # Plot boxplot for outliers
    numeric_col = st.selectbox("Select Column to Inspect Outliers", ["traffic_volume", "average_speed", "congestion_index"])
    
    # Coerce to numeric for plotting
    plot_series = pd.to_numeric(df_active[numeric_col], errors="coerce").dropna()
    
    fig_box = px.box(
        df_active, y=numeric_col, 
        color_discrete_sequence=["#a855f7"],
        labels={numeric_col: f"Distribution of {numeric_col}"}
    )
    fig_box.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=10, b=40)
    )
    st.plotly_chart(fig_box, use_container_width=True)

render_footer()

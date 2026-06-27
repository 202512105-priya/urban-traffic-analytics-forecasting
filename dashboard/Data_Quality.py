import streamlit as st
import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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

# Objects
validator = TrafficValidator()
df_raw = None
raw_report = None
data_load_error = None
validator_error = None

# Try loading raw data
try:
    df_raw = get_raw_data()
except NotImplementedError as e:
    data_load_error = str(e)

# Try running validation reports on raw data if loaded
if df_raw is not None:
    try:
        raw_report = validator.get_quality_report(df_raw)
    except NotImplementedError as e:
        validator_error = str(e)

# Sidebar actions (UI controls)
st.sidebar.header("🛠️ Pipeline Controls")
st.sidebar.write("Simulate the ingestion and cleaning pipeline in real-time.")

# Pipeline session states
if "pipeline_cleaned" not in st.session_state:
    st.session_state["pipeline_cleaned"] = False

# Trigger cleaner actions
cleaning_error = None
if st.sidebar.button("⚙️ Run Ingestion Cleaning"):
    if df_raw is None:
        st.sidebar.error("Error: Raw telemetry stream is unavailable (db.py not implemented).")
    else:
        try:
            cleaner = TrafficCleaner()
            # Try to clean the data to verify implementation
            df_test = cleaner.fit_transform(df_raw)
            st.session_state["pipeline_cleaned"] = True
            st.sidebar.success("ETL Cleaning Pipeline Completed!")
        except NotImplementedError as e:
            cleaning_error = str(e)
            st.session_state["pipeline_cleaned"] = False

if st.sidebar.button("🔄 Reset to Raw Stream"):
    st.session_state["pipeline_cleaned"] = False
    st.rerun()

# Global warning reports
if data_load_error:
    st.warning(f"⚠️ **Ingestion Database Offline**: `{data_load_error}`")
elif validator_error:
    st.warning(f"⚠️ **Validator Engine Incomplete**: `{validator_error}`")
    
if cleaning_error:
    st.sidebar.error(f"Execution Failed: {cleaning_error}")

# Set Active state and report values
df_active = None
report = None
data_label = "TBD"
badge_html = render_status_badge("UNINITIALIZED", "danger")

if df_raw is not None:
    if st.session_state["pipeline_cleaned"]:
        try:
            cleaner = TrafficCleaner()
            df_active = cleaner.fit_transform(df_raw)
            report = validator.get_quality_report(df_active)
            data_label = "CLEANED DATASET"
            badge_html = render_status_badge("PROCESSED - OK", "good")
        except Exception:
            # Fallback if cleaner failed but state was set
            df_active = df_raw
            report = raw_report
            data_label = "RAW TELEMETRY STREAM"
            badge_html = render_status_badge("RAW - AUDIT REQUIRED", "warning")
    else:
        df_active = df_raw
        report = raw_report
        data_label = "RAW TELEMETRY STREAM"
        badge_html = render_status_badge("RAW - AUDIT REQUIRED", "warning")

# Header status display
col_lbl, col_btn = st.columns([8, 2])
with col_lbl:
    st.markdown(f"**Current Pipeline State:** {badge_html} &nbsp; | &nbsp; **Dataset**: `{data_label}` (`{len(df_active) if df_active is not None else 0}` rows)", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Quality Score Gauge
score = report["quality_score"] if report is not None else 0
score_color = "#34d399" if score >= 85 else ("#fbbf24" if score >= 70 else "#f87171")

col_gauge, col_quality_summary = st.columns([4, 8])

with col_gauge:
    # Gauge rendering
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
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=10), height=200
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_quality_summary:
    st.markdown("### 🔍 Telemetry Audit Summary")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    with col_kpi1:
        missing_count = sum([col_info["total_missing"] for col_info in report["missing_values"].values()]) if report is not None else "TBD"
        render_metric_card("Missing Elements", f"{missing_count}" if isinstance(missing_count, str) else f"{missing_count:,}", "To be imputed", "down")
    with col_kpi2:
        dup_count = report["duplicates"]["duplicate_count"] if report is not None else "TBD"
        render_metric_card("Duplicate Rows", f"{dup_count}" if isinstance(dup_count, str) else f"{dup_count:,}", "To be purged", "down")
    with col_kpi3:
        corrupt_count = report["corrupted_columns_count"] if report is not None else "TBD"
        render_metric_card("Type Mismatches", f"{corrupt_count}", "Corrupted string types", "down")

st.markdown("<br><hr>", unsafe_allow_html=True)

# Tabs
tab_missing, tab_duplicates, tab_schema, tab_outliers = st.tabs([
    "🧩 Null & Missingness Audit",
    "👯 Duplicate Records",
    "📋 Schema Datatype Audit",
    "📈 Outlier Distributions"
])

# Utility placeholder
def render_audit_placeholder(title: str, function_name: str, explanation: str):
    st.markdown(
        f"""
        <div style="background-color: rgba(30, 41, 59, 0.45); border: 1px dashed rgba(255,255,255,0.15); border-radius: 12px; padding: 40px; text-align: center; margin: 15px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 12px;">🧹</div>
            <div style="font-family: Outfit; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">{title} Audit Log Offline</div>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 16px; max-width: 500px; margin-left: auto; margin-right: auto;">
                {explanation}
            </div>
            <div style="background-color: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); display: inline-block; padding: 6px 12px; border-radius: 6px; font-family: monospace; font-size: 0.8rem; color: #a855f7;">
                Implement {function_name}() in src/validation/validator.py
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 1. MISSINGNESS AUDIT
with tab_missing:
    st.write("### Missing Values Per Column")
    missing_rendered = False
    if report is not None:
        try:
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
            
            fig_miss = px.bar(
                df_missing, x="Column", y="Percentage (%)",
                color="Percentage (%)", color_continuous_scale="Reds",
                text="Percentage (%)"
            )
            fig_miss.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=40), yaxis=dict(range=[0, max(15, df_missing["Percentage (%)"].max() + 5)])
            )
            fig_miss.update_traces(textposition="outside", texttemplate='%{y:.1f}%')
            
            col_m1, col_m2 = st.columns([7, 5])
            with col_m1:
                st.plotly_chart(fig_miss, use_container_width=True)
            with col_m2:
                st.dataframe(df_missing.sort_values(by="Percentage (%)", ascending=False), use_container_width=True, hide_index=True)
                st.info("Imputation Policy: Missing traffic volumes and speeds should be imputed using group medians. Weather should be imputed using mode.")
            missing_rendered = True
        except KeyError:
            pass
            
    if not missing_rendered:
        render_audit_placeholder(
            "Missingness Analysis", 
            "check_missing_values", 
            "Analyzes raw null counts, empty string sentinels, and percentage of missing indices for all telemetry columns."
        )

# 2. DUPLICATES AUDIT
with tab_duplicates:
    st.write("### Record Duplication Check")
    dup_rendered = False
    if report is not None:
        try:
            dup_info = report["duplicates"]
            if dup_info["duplicate_count"] > 0:
                st.warning(f"Audited {dup_info['duplicate_count']} exact duplicate records ({dup_info['percentage']}% of total dataset).")
                st.write("Sample Duplicate Records:")
                dups_sample = df_active[df_active.duplicated(keep=False)].head(10)
                st.dataframe(dups_sample, use_container_width=True)
            else:
                st.success("Success: No duplicate records detected in the active stream.")
            dup_rendered = True
        except KeyError:
            pass
            
    if not dup_rendered:
        render_audit_placeholder(
            "Duplicate Row Checker", 
            "check_duplicates", 
            "Detects exact row duplicates across timestamps and sensors, highlighting data pipeline ingestion redundancy."
        )

# 3. SCHEMA DATATYPE AUDIT
with tab_schema:
    st.write("### Target Schema Validation Audit")
    schema_rendered = False
    if report is not None:
        try:
            schema_report = report["schema"]
            schema_data = []
            for col, exp_type in validator.target_schema.items():
                if col in df_active.columns:
                    actual_type = str(df_active[col].dtype)
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
            schema_rendered = True
        except KeyError:
            pass
            
    if not schema_rendered:
        render_audit_placeholder(
            "Schema Datatype Audit", 
            "validate_schema", 
            "Compares columns and datatypes against a target schema definition, identifying corruptions."
        )

# 4. OUTLIERS AUDIT
with tab_outliers:
    st.write("### Outlier Detection (Z-Score > 3.0)")
    outliers_rendered = False
    if report is not None:
        try:
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
            
            numeric_col = st.selectbox("Select Column to Inspect Outliers", ["traffic_volume", "average_speed", "congestion_index"])
            fig_box = px.box(df_active, y=numeric_col, color_discrete_sequence=["#a855f7"])
            fig_box.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=40, r=40, t=10, b=40)
            )
            st.plotly_chart(fig_box, use_container_width=True)
            outliers_rendered = True
        except KeyError:
            pass
            
    if not outliers_rendered:
        render_audit_placeholder(
            "Outlier Scanner", 
            "check_outliers", 
            "Finds extreme values using Z-score or IQR techniques, determining statistical boundaries for sensor anomalies."
        )

render_footer()

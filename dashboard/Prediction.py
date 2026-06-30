import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px

# Add project root to python path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.ui import apply_premium_style, render_header, render_footer, render_glass_card
from src.utils.db import load_model_artifact

# Import from the new modular structure
from src.models.predict import predict_congestion
from src.models.explain import explain_features

# Apply styling
apply_premium_style()

# Header
render_header("Traffic Congestion Prediction", "Interactive machine learning inference registry interface")

# Initialize registry model
model = None
model_loaded = False
load_error = None

try:
    model = load_model_artifact("traffic_volume_rf.joblib")
    model_loaded = True
except NotImplementedError as e:
    load_error = str(e)

# Create layout columns: Form on left, Prediction Results on right
col_form, col_res = st.columns([5, 7])

with col_form:
    st.markdown("### 🎛️ Telemetry Conditions")
    
    with st.form("prediction_form"):
        # Junction Input
        junction_id = st.selectbox("Select Traffic Junction", [1, 2, 3, 4], index=0, 
                                   help="Select the specific monitored sensor grid.")
        
        # Temporal Inputs
        hour = st.slider("Hour of Day", min_value=0, max_value=23, value=8, 
                         help="Hour in 24-hour format (e.g., 8 = 8:00 AM, 17 = 5:00 PM).")
        
        day_mapping = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, 
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        day_name = st.selectbox("Day of the Week", list(day_mapping.keys()), index=0)
        day_of_week = day_mapping[day_name]
        
        month_mapping = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
        }
        month_name = st.selectbox("Month of Year", list(month_mapping.keys()), value="October")
        month = month_mapping[month_name]
        
        # Weather & Environment Inputs
        weather_condition = st.selectbox("Weather Condition", ["Clear", "Rainy", "Snowy", "Foggy"], index=0)
        temperature = st.slider("Temperature (°C)", min_value=-15.0, max_value=40.0, value=18.0)
        
        # Holiday Indicator
        is_holiday = st.checkbox("Is Public Holiday?", value=False)
        
        # Submit Button
        submit_btn = st.form_submit_button("🔮 Predict Congestion Profile")

# Compile inputs
inputs = {
    "junction_id": int(junction_id),
    "hour": int(hour),
    "day_of_week": int(day_of_week),
    "month": int(month),
    "temperature": float(temperature),
    "is_holiday": 1 if is_holiday else 0,
    "weather_condition": str(weather_condition)
}

# Run prediction if model is loaded and user submits
results = None
predict_error = None

# If model artifact was loaded, run prediction
if submit_btn or model_loaded:
    try:
        # Wrap inputs in a DataFrame as expected by the backend function contracts
        X_pred = pd.DataFrame([inputs])
        results = predict_congestion(model, X_pred)
    except NotImplementedError as e:
        predict_error = str(e)
    except Exception as e:
        predict_error = f"Model execution failed. Ensure model registry has a valid model artifact."

with col_res:
    st.markdown("### 📊 Inference Predictions")
    
    if predict_error or load_error or results is None:
        # Render clean warning banner instead of results
        st.warning(
            f"⚠️ **Inference Engine Offline**  \n"
            f"The predictor module raised the following instruction:  \n"
            f"`{predict_error or load_error or 'Prediction interface uninitialized.'}`"
        )
        
        # Display structural placeholders for UI consistency without fake metrics
        st.markdown(
            """
            <div style="padding: 16px; border-radius: 12px; margin-bottom: 20px; background-color: rgba(255,255,255,0.03); color: #94a3b8; border: 1px dashed rgba(255,255,255,0.1);">
                <div style="font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.8;">Predicted Congestion Level</div>
                <div style="font-family: Outfit; font-size: 2.2rem; font-weight: 800; margin: 4px 0; color: #64748b;">TBD</div>
                <div style="font-size: 0.85rem; font-weight: 600;">No prediction model active in registry.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col_v, col_c = st.columns(2)
        with col_v:
            st.metric(label="Predicted Traffic Volume", value="TBD")
        with col_c:
            st.metric(label="Prediction Confidence", value="TBD")
            
        st.write("**95% Confidence Interval Band**")
        st.markdown(
            """
            <div style="position: relative; width: 100%; height: 35px; background: rgba(255,255,255,0.02); border-radius: 18px; margin: 15px 0 35px 0; border: 1px dashed rgba(255,255,255,0.08); text-align: center; line-height: 33px; font-size: 0.75rem; color: #64748b;">
                Prediction interval band offline.
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("### 🧬 Explainable AI: Feature Importances")
        st.info("🧬 **XAI weights display is under development.** Implement explain_features() in src/models/explain.py.")
        
    else:
        # Renders if the user has implemented the predictor code
        congest_lvl = results.get("congestion_level", "TBD")
        congest_col = results.get("congestion_color", "warning")
        
        if congest_col == "green":
            badge_style = "background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);"
            status_text = "LOW DENSITY - FREE FLOW"
        elif congest_col == "warning":
            badge_style = "background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);"
            status_text = "MODERATE DENSITY - SLOW DISSIPATION"
        else:
            badge_style = "background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3);"
            status_text = "CRITICAL DENSITY - HEAVY GRIDLOCK"
            
        st.markdown(
            f"""
            <div style="padding: 16px; border-radius: 12px; margin-bottom: 20px; {badge_style}">
                <div style="font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.8;">Predicted Congestion Level</div>
                <div style="font-family: Outfit; font-size: 2.2rem; font-weight: 800; margin: 4px 0;">{congest_lvl}</div>
                <div style="font-size: 0.85rem; font-weight: 600;">{status_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col_v, col_c = st.columns(2)
        with col_v:
            st.metric(label="Predicted Traffic Volume", value=f"{results.get('predicted_volume', 'TBD')} vehicles/hr")
        with col_c:
            st.metric(label="Prediction Confidence", value=f"{results.get('confidence_score', 'TBD')}%")
            
        st.write("**95% Confidence Interval Band**")
        lower = results.get("lower_bound", 0)
        upper = results.get("upper_bound", 100)
        pred = results.get("predicted_volume", 50)
        max_range = max(100, upper * 1.2)
        lower_pct = min(90, (lower / max_range) * 100)
        pred_pct = min(95, (pred / max_range) * 100)
        upper_pct = min(100, (upper / max_range) * 100)
        
        st.markdown(
            f"""
            <div style="position: relative; width: 100%; height: 35px; background: rgba(255,255,255,0.05); border-radius: 18px; margin: 15px 0 35px 0; border: 1px solid rgba(255,255,255,0.05);">
                <div style="position: absolute; left: {lower_pct}%; width: {upper_pct - lower_pct}%; height: 100%; background: rgba(99, 102, 241, 0.25); border-radius: 4px; border-left: 2px solid #6366f1; border-right: 2px solid #6366f1;"></div>
                <div style="position: absolute; left: {pred_pct}%; top: 50%; transform: translate(-50%, -50%); width: 14px; height: 14px; background: #ec4899; border-radius: 50%; box-shadow: 0 0 8px #ec4899;"></div>
                <div style="position: absolute; left: {lower_pct}%; top: 38px; transform: translateX(-50%); font-size: 0.75rem; color: #94a3b8; font-weight: 500;">{lower} (min)</div>
                <div style="position: absolute; left: {pred_pct}%; top: -20px; transform: translateX(-50%); font-size: 0.8rem; color: #ec4899; font-weight: 700;">{pred} (est)</div>
                <div style="position: absolute; left: {upper_pct}%; top: 38px; transform: translateX(-50%); font-size: 0.75rem; color: #94a3b8; font-weight: 500;">{upper} (max)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("### 🧬 Explainable AI: Feature Importances")
        try:
            # We map model name to feature explainers
            feature_names = ["junction_id", "hour", "day_of_week", "month", "temperature", "is_holiday", "weather_condition"]
            importances = explain_features(model, feature_names)
            df_imp = pd.DataFrame(list(importances.items()), columns=["Feature", "Importance"])
            df_imp = df_imp.sort_values(by="Importance", ascending=True)
            
            fig_imp = px.bar(
                df_imp, x="Importance", y="Feature", orientation="h",
                color="Importance", color_continuous_scale="Purples"
            )
            fig_imp.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=10, b=10), height=220, coloraxis_showscale=False
            )
            st.plotly_chart(fig_imp, use_container_width=True)
        except NotImplementedError:
            st.info("🧬 **Feature importance weights check is under development.**")

render_footer()

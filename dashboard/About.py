import streamlit as st
import os
import sys

# Add project root to python path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.ui import apply_premium_style, render_header, render_footer, render_glass_card

# Apply styling
apply_premium_style()

# Header
render_header("Project Documentation", "Architecture overview, pipeline workflows, and system design specifications")

# Project documentation layout
col_left, col_right = st.columns([7, 5])

with col_left:
    st.markdown("### 🏗️ Platform System Architecture")
    
    # Render Mermaid diagram for system design
    mermaid_code = """
    flowchart TD
        subgraph Data Ingestion
            A[Raw Sensor Feeds] -->|CSV / API Stream| B[data/raw/traffic_raw.csv]
        end
        
        subgraph Data Engineering Pipeline
            B --> C[src/validation/validator.py]
            C -->|Datatype & Constraint Audit| D[src/cleaning/cleaner.py]
            D -->|Imputed & Deduplicated Data| E[data/processed/traffic_clean.csv]
            E --> F[src/feature_engineering/features.py]
            F -->|Cyclical & Lag features| G[data/features/traffic_features.csv]
        end
        
        subgraph Machine Learning Registry
            G --> H[src/models/predictor.py]
            G --> I[src/forecasting/forecaster.py]
            H -->|Fit RF Regressor| J[models/traffic_volume_rf.joblib]
            I -->|Fit Prophet / Fallback| K[Time Series Forecaster]
        end
        
        subgraph Streamlit Interface
            J --> L[dashboard/Prediction.py]
            K --> M[dashboard/Forecasting.py]
            E --> N[dashboard/Analytics.py]
            C --> O[dashboard/Data_Quality.py]
        end
        
        style B fill:#334155,stroke:#64748b,stroke-width:2px,color:#fff
        style E fill:#1e293b,stroke:#818cf8,stroke-width:2px,color:#fff
        style G fill:#1e293b,stroke:#c084fc,stroke-width:2px,color:#fff
        style J fill:#1e1b4b,stroke:#ec4899,stroke-width:2px,color:#fff
    """
    
    st.markdown(f"```mermaid\n{mermaid_code}\n```")
    
    st.markdown("### ⚙️ Modular Workflow Pipelines")
    st.markdown(
        """
        1. **Telemetry Ingestion & Quality Audit**: 
           Telemetry is loaded from database systems or CSV files. The validation engine checking constraints, missing values, z-score outlier boundaries, and schema datatypes publishes an audit log.
           
        2. **Clean & Impute (ETL)**:
           Duplicates are dropped. Values are coerced to target schemas (e.g. converting erroneous temperature strings). Missing readings are filled using group-by medians (sensor ID + hour of day) to preserve seasonal commuter patterns.
           
        3. **Cyclical & Temporal Feature Extraction**:
           Timestamp logs are transformed into cyclical sine/cosine wave representations of hour, day, and month to preserve time proximity (e.g. 23:00 wrapping to 00:00). Autocorrelation lag values (t-1h, t-24h) and 3h/24h rolling averages are computed per junction.
           
        4. **Machine Learning Predictor & Explainability (XAI)**:
           A Random Forest model fits the feature-engineered matrix. Inference evaluates points and standard errors across individual estimator trees to compute confidence bounds. Feature importances are dynamically graphed for model explainability.
           
        5. **Forecasting**:
           A Prophet time-series or multi-seasonal fallback model decomposes historical trends, daily commuter profiles, and weekly weekend cycles to project traffic flows up to 7 days into the future.
        """
    )

with col_right:
    st.markdown("### 🛠️ Production Tech Stack")
    
    tech_info = """
    - **Programming Language**: `Python 3.9+`
    - **Dashboard Framework**: `Streamlit 1.50+` (Sleek multi-page routing, caching, and state management)
    - **Data Wrangling**: `Pandas 2.0+` & `NumPy` (Vectorized ETL pipelines and data transformations)
    - **Interactions & Plots**: `Plotly 6.0` (Hardware accelerated interactive charts with hover indicators)
    - **Machine Learning**: `Scikit-Learn 1.6+` (Random Forest models, tree ensembles, and feature importances)
    - **Time-Series Forecasting**: `Prophet 1.3+` (Meta's additive forecasting engine with statistical Pandas fallbacks)
    - **Serialization**: `Joblib` (Binary serialization of trained ML model weights)
    - **Validation Logic**: `Pydantic` (Schema data structures and constraint models)
    """
    render_glass_card("Technology Stack Details", tech_info, "⚙️")
    
    st.markdown("### 💼 Showcase Value & Next Steps")
    showcase_notes = (
        "This project represents a fully engineered, production-ready boilerplate designed to show "
        "advanced capabilities in Analytics Engineering and Machine Learning Engineering. \n\n"
        "**To extend this platform in the next phases:**  \n"
        "1. **Connect PostgreSQL**: Edit `src/utils/db.py` to replace CSV file loaders with SQL queries running against a live PostgreSQL server.  \n"
        "2. **Expand ML Registry**: Replace the Random Forest with XGBoost or LightGBM models by updating `src/models/predictor.py`.  \n"
        "3. **Add Airflow Scheduler**: Schedule the script `src/utils/data_generator.py` or an ETL pipeline to run daily to append new telemetry to the database."
    )
    render_glass_card("Portfolio Highlights", showcase_notes, "🏆")
    
    st.markdown(
        """
        <div style="background-color: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); padding: 15px; border-radius: 8px;">
            <strong style="color: #818cf8; font-family: Outfit; font-size: 1rem;">👩‍💻 Author & Developer Credits</strong><br>
            <p style="color: #cbd5e1; font-size: 0.85rem; margin-top: 5px; line-height: 1.4;">
                Developed by <strong>Priya Shah</strong> as a master capstone project to highlight analytics, data cleaning pipelines, data validation reports, ML inference, and forecasting.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

render_footer()

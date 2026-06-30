# Project Engineering Decisions

This document logs the critical engineering, architectural, and mathematical decisions made during the development of the Urban Traffic Analytics and Forecasting Platform.

---

## Decision 1: Separation of Business Logic from the UI

### Context
In Streamlit applications, it is common to mix UI layout code with data manipulation (e.g. using `df.shape[0]`, `df.groupby()`, or `.mean()` directly inside the rendering scripts). This couples the frontend to the data structure and schema, leading to brittle code that is difficult to test, reuse, or adapt.

### Decision
Dashboard pages will never perform data calculations, schemas audits, or modeling operations directly. Instead, all business logic, statistics, and calculations are encapsulated within helper functions inside `src/`. Dashboard pages are strictly responsible for:
1. Collecting user input via sidebar sliders, buttons, or forms.
2. Invoking the appropriate backend functions from `src/`.
3. Displaying the returned results using Streamlit visual components.

### Benefits
- **Testability**: Backend logic can be isolated and unit-tested via scripts without requiring the Streamlit server to run.
- **Reusability**: Multiple pages (e.g. Home, Analytics, and Data Quality) can query the same underlying analytical modules without repeating code.
- **Maintainability**: Refactoring a backend formula or changing columns will only require modifying one file in `src/`, rather than updating multiple dashboard scripts.
- **Loose Coupling**: Allows parallel development between UI elements and underlying algorithms.

---

## Decision 2: Return Type and Function Design Constraints

### Context
When writing analytical functions, developers often return varied data types (e.g., custom nested dictionaries, tuples, lists, or custom dataclasses). This makes chaining operations together difficult and increases the learning curve for developers joining the project.

### Decision
Every analytics, engineering, and preprocessing function must satisfy these four design rules:
1. **DataFrame Input & Output**: Accept a `pd.DataFrame` as the primary argument and return a `pd.DataFrame` (or a clearly documented scalar when appropriate, such as a quality score).
2. **No Streamlit Dependency**: Backend modules must never import or call Streamlit methods.
3. **No I/O Side Effects**: Backend modules must never execute `print()` or `plt.show()`.
4. **Loose Coupling**: Frontend is only responsible for rendering inputs and displaying outputs.

### Benefits
- **Interoperability**: DataFrames are universally understood by Streamlit widgets (`st.dataframe`, `st.plotly_chart`), CSV export functions, and statistical libraries.
- **Portability**: Functions can be run in Jupyter notebooks, unit tests, or web APIs (like FastAPI) without modifications.
- **Chaining**: Promotes piping and compounding pandas transformations easily.

---

## Decision 3: Modular Package Architecture (v1.0)

### Context
A single large `validator.py` or `cleaner.py` file is hard to navigate, edit, and scale as validation constraints or modeling requirements grow.

### Decision
We organize the project into 8 core packages with highly specialized concerns:
1. `core/`: Core infrastructure (loaders, paths, custom exceptions).
2. `validation/`: Answers "Is this dataset trustworthy?" without modifying data.
3. `cleaning/`: Modifies data to resolve validation errors.
4. `analytics/`: Performs grouping, statistical summaries, and insights.
5. `feature_engineering/`: Generates mathematical features for machine learning models.
6. `models/`: Wraps ML model training, prediction, evaluation, and explainability.
7. `forecasting/`: Completely independent time-series forecasting.
8. `recommendations/`: Translates analytical facts into business actions.

### Benefits
- **High Cohesion & Single Responsibility**: Every file is focused on solving one exact problem (e.g., `duplicates.py` is only responsible for duplicate detection).
- **Scalability**: New models or forecasting features can be added by creating files in respective directories, without touching unrelated files.

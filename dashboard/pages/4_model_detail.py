import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.db import get_connection
from core.scorer import compute_model_scores

st.header("Model Detail")

conn = get_connection()
models = conn.execute("SELECT * FROM models WHERE active = 1 ORDER BY id").fetchall()
conn.close()

if not models:
    st.info("No models registered.")
    st.stop()

model_id = st.selectbox("Select Model", [m["id"] for m in models])
model = next((dict(m) for m in models if m["id"] == model_id), None)

if model:
    st.subheader(model["name"])
    st.markdown(f"**Type**: {model['model_type']} | **Phase**: {model['phase']}")
    if model.get("description"):
        st.markdown(model["description"])

conn = get_connection()
scores = compute_model_scores(conn, model_id, "rainfall_mumbai", 90)
conn.close()

if scores:
    df = pd.DataFrame(scores)

    col1, col2, col3 = st.columns(3)
    col1.metric("MAE", f"{df['abs_error'].mean():.2f} mm")
    col2.metric("RMSE", f"{(df['abs_error'] ** 2).mean() ** 0.5:.2f} mm")
    col3.metric("Bias", f"{df['error'].mean():+.2f} mm")

    st.subheader("Error Distribution")
    fig = go.Figure(go.Histogram(x=df["error"], nbinsx=20, marker_color="#3498db"))
    fig.update_layout(template="plotly_dark", height=300,
                      xaxis_title="Error (mm)", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Predicted vs Actual Scatter")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["actual_value"], y=df["predicted_value"],
        mode="markers", marker=dict(color="#e74c3c", size=8),
    ))
    min_val = min(df["actual_value"].min(), df["predicted_value"].min())
    max_val = max(df["actual_value"].max(), df["predicted_value"].max())
    fig2.add_trace(go.Scatter(
        x=[min_val, max_val], y=[min_val, max_val],
        mode="lines", line=dict(color="white", dash="dash"), name="Perfect",
    ))
    fig2.update_layout(template="plotly_dark", height=400,
                       xaxis_title="Actual (mm)", yaxis_title="Predicted (mm)")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No scores for this model yet.")

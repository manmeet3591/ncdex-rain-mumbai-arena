import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
from core.db import get_connection
from core.scorer import compute_model_scores
from dashboard.components.charts import prediction_vs_actual_chart, error_over_time_chart

st.header("Predictions — Rain Mumbai")

conn = get_connection()
models = conn.execute("SELECT id, name FROM models WHERE active = 1 ORDER BY id").fetchall()
model_ids = [m["id"] for m in models]
conn.close()

if not model_ids:
    st.info("No models registered yet.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    model_id = st.selectbox("Model", model_ids)
with col2:
    days = st.slider("Lookback (days)", 7, 365, 30, key="pred_days")

conn = get_connection()
scores = compute_model_scores(conn, model_id, "rainfall_mumbai", days)
conn.close()

if scores:
    st.plotly_chart(prediction_vs_actual_chart(scores), width="stretch")
    st.plotly_chart(error_over_time_chart(scores), width="stretch")
    st.subheader("Score Details")
    st.dataframe(pd.DataFrame(scores), width="stretch")
else:
    st.info("No scored predictions for this selection.")

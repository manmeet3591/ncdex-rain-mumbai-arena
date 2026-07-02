import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
from core.db import get_connection
from dashboard.components.charts import rainfall_history_chart

st.header("Data Explorer — Mumbai Rainfall")

col1, col2 = st.columns(2)
with col1:
    date_from = st.date_input("From", value=pd.Timestamp("2026-06-01"))
with col2:
    date_to = st.date_input("To", value=pd.Timestamp.now())

conn = get_connection()
rows = conn.execute(
    """SELECT * FROM actuals
       WHERE market = 'rainfall_mumbai' AND location = 'mumbai'
         AND target_date >= ? AND target_date <= ?
       ORDER BY target_date DESC LIMIT 1000""",
    (str(date_from), str(date_to)),
).fetchall()
conn.close()
actuals = [dict(r) for r in rows]

if actuals:
    df = pd.DataFrame(actuals)
    st.plotly_chart(rainfall_history_chart(actuals), use_container_width=True)

    col_a, col_b, col_c = st.columns(3)
    values = df["value"].dropna()
    col_a.metric("Records", len(df))
    col_b.metric("Mean", f"{values.mean():.1f} mm")
    col_c.metric("Max", f"{values.max():.1f} mm")

    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "mumbai_rainfall.csv", "text/csv")
else:
    st.info("No data for this date range.")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
from core.db import get_connection
from core.scorer import compute_leaderboard
from dashboard.components.charts import leaderboard_bar_chart

st.header("Leaderboard — Rain Mumbai")

days = st.slider("Lookback (days)", 7, 365, 30)

conn = get_connection()
data = compute_leaderboard(conn, "rainfall_mumbai", days)
conn.close()

if data:
    df = pd.DataFrame(data)
    st.plotly_chart(leaderboard_bar_chart(data, "mae"), use_container_width=True)

    st.subheader("Rankings")
    display_df = df[["model_id", "name", "n_predictions", "mae", "rmse", "bias"]].copy()
    display_df.index = range(1, len(display_df) + 1)
    display_df.index.name = "Rank"
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No scores yet.")

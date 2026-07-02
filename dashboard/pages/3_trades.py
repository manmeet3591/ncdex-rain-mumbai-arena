import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import streamlit as st
import pandas as pd
from core.db import get_connection
from dashboard.components.charts import pnl_equity_curve

st.header("Paper Trades — Rain Mumbai")

conn = get_connection()
rows = conn.execute(
    "SELECT * FROM trades WHERE market = 'rainfall_mumbai' ORDER BY target_date DESC LIMIT 200"
).fetchall()
conn.close()
trades = [dict(r) for r in rows]

if trades:
    resolved = [t for t in trades if t["status"] == "resolved" and t.get("pnl") is not None]
    if resolved:
        total_pnl = sum(t["pnl"] for t in resolved)
        wins = sum(1 for t in resolved if t["pnl"] > 0)
        st.plotly_chart(pnl_equity_curve(resolved), width="stretch")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Trades", len(resolved))
        m2.metric("Total P&L", f"₹{total_pnl:.2f}")
        m3.metric("Win Rate", f"{wins / len(resolved) * 100:.0f}%")
        m4.metric("Avg P&L", f"₹{total_pnl / len(resolved):.2f}")

    st.subheader("Trade Log")
    for t in trades:
        meta = {}
        if t.get("trade_metadata"):
            try:
                meta = json.loads(t["trade_metadata"])
            except (json.JSONDecodeError, TypeError):
                pass
        t["justification"] = meta.get("justification", "")
        t["confidence"] = meta.get("confidence", "")

    df = pd.DataFrame(trades)
    display_cols = [c for c in ["model_id", "target_date", "direction",
                                 "position_size", "pnl", "status", "justification"] if c in df.columns]
    st.dataframe(df[display_cols], width="stretch")
else:
    st.info("No trades yet. Models trade selectively — only when they see an edge.")

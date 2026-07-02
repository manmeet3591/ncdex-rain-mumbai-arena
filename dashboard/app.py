import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.db import get_connection, init_db
from core.paper_trader import get_equity_curves, STARTING_CAPITAL
from core.scorer import compute_leaderboard

st.set_page_config(
    page_title="Rain Mumbai Arena",
    page_icon="🌧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODEL_COLORS = {
    "persistence": "#e74c3c",
    "sma_7": "#3498db",
    "exp_smooth": "#2ecc71",
}
MODEL_LABELS = {
    "persistence": "Persistence (Naive)",
    "sma_7": "SMA 7-day",
    "exp_smooth": "Exp Smoothing",
}

st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    h1 { text-align: center; }
    .stMetric { text-align: center; }
</style>
""", unsafe_allow_html=True)

col_logo, col_title, col_status = st.columns([1, 4, 1])
with col_title:
    st.markdown("# Rain Mumbai Arena")
    st.markdown("<p style='text-align:center; color: #888;'>Models compete on NCDEX Rain Mumbai — daily rainfall prediction arena</p>",
                unsafe_allow_html=True)
with col_status:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("🟢 **LIVE**")

st.markdown("---")

try:
    init_db()
    conn = get_connection()
    equity_data = get_equity_curves(conn, "rainfall_mumbai")
    leaderboard = compute_leaderboard(conn, "rainfall_mumbai", days=30)
    conn.close()

    if equity_data:
        fig = go.Figure()

        fig.add_hline(y=STARTING_CAPITAL, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                      annotation_text=f"Starting Capital ₹{STARTING_CAPITAL:,.0f}",
                      annotation_position="bottom left",
                      annotation_font_color="rgba(255,255,255,0.5)")

        sorted_models = sorted(equity_data.items(),
                                key=lambda x: x[1][-1]["account_value"] if x[1] else 0,
                                reverse=True)

        for model_id, entries in sorted_models:
            dates = [e["date"] for e in entries]
            values = [e["account_value"] for e in entries]
            color = MODEL_COLORS.get(model_id, "#ffffff")
            label = MODEL_LABELS.get(model_id, model_id)
            final_val = values[-1] if values else STARTING_CAPITAL

            fig.add_trace(go.Scatter(
                x=dates, y=values,
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=3),
                marker=dict(size=4),
                hovertemplate=f"<b>{label}</b><br>Date: %{{x}}<br>Value: ₹%{{y:,.2f}}<extra></extra>",
            ))

            fig.add_annotation(
                x=dates[-1], y=final_val,
                text=f"  ₹{final_val:,.0f}",
                showarrow=False,
                xanchor="left",
                font=dict(color=color, size=14, family="monospace"),
            )

        fig.update_layout(
            title=dict(text="TOTAL ACCOUNT VALUE", x=0.5, font=dict(size=20)),
            template="plotly_dark",
            height=500,
            xaxis=dict(title="", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(title="Account Value (₹)", tickprefix="₹", tickformat=",",
                       gridcolor="rgba(255,255,255,0.1)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="center", x=0.5, font=dict(size=13)),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(r=100),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Standings")
        cols = st.columns(len(sorted_models))
        for i, (model_id, entries) in enumerate(sorted_models):
            final = entries[-1]["account_value"] if entries else STARTING_CAPITAL
            pnl = final - STARTING_CAPITAL
            pct = (pnl / STARTING_CAPITAL) * 100
            label = MODEL_LABELS.get(model_id, model_id)
            color = MODEL_COLORS.get(model_id, "#fff")
            with cols[i]:
                st.markdown(f"<h3 style='color:{color}; text-align:center;'>#{i+1}</h3>",
                            unsafe_allow_html=True)
                st.metric(label, f"₹{final:,.0f}", delta=f"{pct:+.1f}%")

        if leaderboard:
            st.markdown("### Prediction Accuracy (Rainfall mm)")
            lb_cols = st.columns(len(leaderboard))
            for i, entry in enumerate(leaderboard):
                with lb_cols[i]:
                    color = MODEL_COLORS.get(entry["model_id"], "#fff")
                    st.markdown(f"<p style='color:{color}; text-align:center; font-weight:bold;'>{MODEL_LABELS.get(entry['model_id'], entry['model_id'])}</p>",
                                unsafe_allow_html=True)
                    st.metric("MAE", f"{entry['mae']:.2f} mm")
                    st.metric("RMSE", f"{entry['rmse']:.2f} mm")
                    st.metric("Predictions", entry["n_predictions"])

    else:
        st.info("No trading data yet. Run `python scripts/run_daily.py` to generate data.")

except Exception as e:
    st.error(f"Error loading data: {e}")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#555;'>Season 1 — June 2026 | Starting capital: ₹10,000 per model | Data: Open-Meteo</p>",
            unsafe_allow_html=True)

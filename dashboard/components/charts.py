import plotly.graph_objects as go
import pandas as pd


def leaderboard_bar_chart(data: list[dict], metric: str = "mae") -> go.Figure:
    df = pd.DataFrame(data)
    if df.empty:
        return go.Figure()
    colors = ["#2ecc71" if i == 0 else "#3498db" for i in range(len(df))]
    fig = go.Figure(go.Bar(
        x=df["name"],
        y=df[metric],
        marker_color=colors,
        text=df[metric].round(2),
        textposition="auto",
    ))
    fig.update_layout(
        title=f"Model Comparison — {metric.upper()}",
        xaxis_title="Model",
        yaxis_title=metric.upper(),
        template="plotly_dark",
        height=400,
    )
    return fig


def prediction_vs_actual_chart(scores: list[dict]) -> go.Figure:
    df = pd.DataFrame(scores)
    if df.empty:
        return go.Figure()
    df = df.sort_values("target_date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["target_date"], y=df["actual_value"],
        mode="lines+markers", name="Actual",
        line=dict(color="#2ecc71", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df["target_date"], y=df["predicted_value"],
        mode="lines+markers", name="Predicted",
        line=dict(color="#e74c3c", width=2, dash="dash"),
    ))
    fig.update_layout(
        title="Predicted vs Actual",
        xaxis_title="Date",
        yaxis_title="Value",
        template="plotly_dark",
        height=400,
    )
    return fig


def error_over_time_chart(scores: list[dict]) -> go.Figure:
    df = pd.DataFrame(scores)
    if df.empty:
        return go.Figure()
    df = df.sort_values("target_date")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["target_date"], y=df["error"],
        marker_color=df["error"].apply(lambda x: "#2ecc71" if x >= 0 else "#e74c3c"),
        name="Error",
    ))
    fig.update_layout(
        title="Prediction Error Over Time",
        xaxis_title="Date",
        yaxis_title="Error (Predicted - Actual)",
        template="plotly_dark",
        height=300,
    )
    return fig


def pnl_equity_curve(trades: list[dict]) -> go.Figure:
    df = pd.DataFrame(trades)
    if df.empty:
        return go.Figure()
    df = df.sort_values("target_date")
    df["cumulative_pnl"] = df["pnl"].cumsum()
    fig = go.Figure(go.Scatter(
        x=df["target_date"], y=df["cumulative_pnl"],
        mode="lines+markers",
        line=dict(color="#f39c12", width=2),
        fill="tozeroy",
        fillcolor="rgba(243, 156, 18, 0.1)",
    ))
    fig.update_layout(
        title="Cumulative P&L",
        xaxis_title="Date",
        yaxis_title="P&L ($)",
        template="plotly_dark",
        height=350,
    )
    return fig


def rainfall_history_chart(actuals: list[dict]) -> go.Figure:
    df = pd.DataFrame(actuals)
    if df.empty:
        return go.Figure()
    df = df.sort_values("target_date")
    fig = go.Figure(go.Bar(
        x=df["target_date"], y=df["value"],
        marker_color="#3498db",
    ))
    fig.update_layout(
        title="Daily Rainfall (mm)",
        xaxis_title="Date",
        yaxis_title="Precipitation (mm)",
        template="plotly_dark",
        height=350,
    )
    return fig

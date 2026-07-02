from pydantic import BaseModel
from typing import Optional


class ModelOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    model_type: str
    phase: int = 1
    config_json: Optional[str] = None


class LeaderboardEntry(BaseModel):
    model_id: str
    name: str
    model_type: str
    n_predictions: int
    mae: float
    rmse: float
    bias: float
    first_date: Optional[str] = None
    last_date: Optional[str] = None


class PredictionOut(BaseModel):
    id: int
    model_id: str
    market: str
    location: str
    target_date: str
    variable: str
    value: float
    confidence: Optional[float] = None
    predicted_at: Optional[str] = None


class ScoreOut(BaseModel):
    target_date: str
    market: str
    location: str
    variable: str
    predicted_value: float
    actual_value: float
    error: float
    abs_error: float


class TradeOut(BaseModel):
    id: int
    model_id: str
    market: str
    location: str
    target_date: str
    direction: str
    entry_price: float
    predicted_value: float
    position_size: float
    shares: Optional[float] = None
    status: str
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    resolved_at: Optional[str] = None
    created_at: Optional[str] = None


class TradeSummary(BaseModel):
    model_id: str
    total_trades: int
    wins: int
    total_pnl: float
    avg_pnl: float
    win_rate: float


class RunArenaRequest(BaseModel):
    target_date: str
    markets: Optional[list[str]] = None


class ActualOut(BaseModel):
    target_date: str
    market: str
    location: str
    variable: str
    value: Optional[float] = None
    source: Optional[str] = None

import numpy as np
from models.base import BaseModel, Prediction


class MovingAverageModel(BaseModel):
    id = "sma_7"
    name = "Simple Moving Average (7-day)"
    description = "Predicts the mean of the last 7 days."
    model_type = "statistical"
    phase = 1

    def __init__(self, window: int = 7):
        self.window = window

    def predict(self, history: list[float], target_date: str, variable: str, location: str) -> Prediction:
        if not history:
            return Prediction(value=0.0)
        window = min(self.window, len(history))
        recent = history[-window:]
        mean = float(np.mean(recent))
        std = float(np.std(recent)) if len(recent) > 1 else 0.0
        return Prediction(
            value=mean,
            lower=mean - 1.96 * std,
            upper=mean + 1.96 * std,
            confidence=1.0 / (1.0 + std),
        )

    def get_config(self) -> dict:
        cfg = super().get_config()
        cfg["window"] = self.window
        return cfg

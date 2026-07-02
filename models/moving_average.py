import numpy as np
from models.base import BaseModel, Prediction, TradeDecision


class MovingAverageModel(BaseModel):
    id = "sma_7"
    name = "Simple Moving Average (7-day)"
    description = "Predicts the 7-day mean. Trades when the trend diverges from yesterday."
    model_type = "statistical"
    phase = 1

    def __init__(self, window: int = 7):
        self.window = window

    def predict(self, history: list[float], target_date: str, variable: str, location: str) -> Prediction:
        if not history:
            return Prediction(value=0.0, trade=TradeDecision("hold", 0.0, "No data"))

        window = min(self.window, len(history))
        recent = history[-window:]
        mean = float(np.mean(recent))
        std = float(np.std(recent)) if len(recent) > 1 else 0.0

        prediction = Prediction(
            value=mean,
            lower=mean - 1.96 * std,
            upper=mean + 1.96 * std,
            confidence=1.0 / (1.0 + std),
        )

        yesterday = history[-1]
        diff = mean - yesterday
        threshold = max(5.0, std * 0.8)

        if abs(diff) < threshold:
            prediction.trade = TradeDecision(
                "hold", 0.2,
                f"SMA {mean:.0f}mm close to yesterday {yesterday:.0f}mm — no clear trend"
            )
        elif diff > 0:
            confidence = min(0.9, abs(diff) / (threshold * 2.5))
            prediction.trade = TradeDecision(
                "long", confidence,
                f"7d avg {mean:.0f}mm above yesterday {yesterday:.0f}mm — upward trend"
            )
        else:
            confidence = min(0.9, abs(diff) / (threshold * 2.5))
            prediction.trade = TradeDecision(
                "short", confidence,
                f"7d avg {mean:.0f}mm below yesterday {yesterday:.0f}mm — downward trend"
            )

        return prediction

    def get_config(self) -> dict:
        cfg = super().get_config()
        cfg["window"] = self.window
        return cfg

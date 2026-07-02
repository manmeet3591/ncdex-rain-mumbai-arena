import numpy as np
from models.base import BaseModel, Prediction, TradeDecision


class ExponentialSmoothingModel(BaseModel):
    id = "exp_smooth"
    name = "Exponential Smoothing (alpha=0.3)"
    description = "Trend-following with exponential weighting. Trades on momentum shifts."
    model_type = "statistical"
    phase = 1

    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha

    def predict(self, history: list[float], target_date: str, variable: str, location: str) -> Prediction:
        if not history:
            return Prediction(value=0.0, trade=TradeDecision("hold", 0.0, "No data"))

        smoothed = history[0]
        for val in history[1:]:
            smoothed = self.alpha * val + (1 - self.alpha) * smoothed

        prediction = Prediction(value=smoothed)

        yesterday = history[-1]
        diff = smoothed - yesterday

        window = min(7, len(history))
        recent_std = float(np.std(history[-window:])) if window > 1 else 5.0
        threshold = max(4.0, recent_std * 0.6)

        if abs(diff) < threshold:
            prediction.trade = TradeDecision(
                "hold", 0.15,
                f"Smoothed {smoothed:.0f}mm near yesterday {yesterday:.0f}mm — trend flat"
            )
        elif diff > 0:
            confidence = min(0.85, abs(diff) / (threshold * 2.5))
            prediction.trade = TradeDecision(
                "long", confidence,
                f"Trend {smoothed:.0f}mm rising above yesterday {yesterday:.0f}mm — momentum up"
            )
        else:
            confidence = min(0.85, abs(diff) / (threshold * 2.5))
            prediction.trade = TradeDecision(
                "short", confidence,
                f"Trend {smoothed:.0f}mm falling below yesterday {yesterday:.0f}mm — momentum down"
            )

        return prediction

    def get_config(self) -> dict:
        cfg = super().get_config()
        cfg["alpha"] = self.alpha
        return cfg

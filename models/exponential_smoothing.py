from models.base import BaseModel, Prediction


class ExponentialSmoothingModel(BaseModel):
    id = "exp_smooth"
    name = "Exponential Smoothing (alpha=0.3)"
    description = "Simple exponential smoothing with configurable alpha."
    model_type = "statistical"
    phase = 1

    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha

    def predict(self, history: list[float], target_date: str, variable: str, location: str) -> Prediction:
        if not history:
            return Prediction(value=0.0)
        smoothed = history[0]
        for val in history[1:]:
            smoothed = self.alpha * val + (1 - self.alpha) * smoothed
        return Prediction(value=smoothed)

    def get_config(self) -> dict:
        cfg = super().get_config()
        cfg["alpha"] = self.alpha
        return cfg

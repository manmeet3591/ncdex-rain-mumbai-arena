import numpy as np
from models.base import BaseModel, Prediction, TradeDecision


class PersistenceModel(BaseModel):
    id = "persistence"
    name = "Persistence (Naive)"
    description = "Predicts tomorrow = today. Trades on mean-reversion when rainfall is extreme."
    model_type = "statistical"
    phase = 1

    def predict(self, history: list[float], target_date: str, variable: str, location: str) -> Prediction:
        if not history:
            return Prediction(value=0.0, trade=TradeDecision("hold", 0.0, "No data"))

        yesterday = history[-1]
        prediction = Prediction(value=yesterday)

        window = min(14, len(history))
        recent = history[-window:]
        avg = float(np.mean(recent))
        deviation = yesterday - avg

        threshold = max(8.0, avg * 0.5)

        if abs(deviation) < threshold:
            prediction.trade = TradeDecision(
                "hold", 0.2,
                f"Rain {yesterday:.0f}mm near 14d avg {avg:.0f}mm — no edge"
            )
        elif deviation > 0:
            confidence = min(0.9, abs(deviation) / (threshold * 3))
            prediction.trade = TradeDecision(
                "short", confidence,
                f"Rain {yesterday:.0f}mm well above 14d avg {avg:.0f}mm — expect reversion"
            )
        else:
            confidence = min(0.9, abs(deviation) / (threshold * 3))
            prediction.trade = TradeDecision(
                "long", confidence,
                f"Rain {yesterday:.0f}mm well below 14d avg {avg:.0f}mm — expect reversion"
            )

        return prediction

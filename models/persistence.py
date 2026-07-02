from models.base import BaseModel, Prediction


class PersistenceModel(BaseModel):
    id = "persistence"
    name = "Persistence (Naive)"
    description = "Predicts tomorrow = today. The simplest possible baseline."
    model_type = "statistical"
    phase = 1

    def predict(self, history: list[float], target_date: str, variable: str, location: str) -> Prediction:
        if not history:
            return Prediction(value=0.0)
        return Prediction(value=history[-1])

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TradeDecision:
    signal: str  # "long", "short", "hold"
    confidence: float  # 0.0 to 1.0
    justification: str


@dataclass
class Prediction:
    value: float
    lower: float | None = None
    upper: float | None = None
    confidence: float | None = None
    metadata: dict | None = field(default=None, repr=False)
    trade: TradeDecision | None = None


class BaseModel(ABC):
    id: str
    name: str
    description: str
    model_type: str
    phase: int = 1

    @abstractmethod
    def predict(
        self,
        history: list[float],
        target_date: str,
        variable: str,
        location: str,
    ) -> Prediction:
        ...

    def fit(self, history: list[float]) -> None:
        pass

    def get_config(self) -> dict:
        return {"id": self.id, "name": self.name, "type": self.model_type, "phase": self.phase}

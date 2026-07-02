import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.persistence import PersistenceModel
from models.base import Prediction


def test_persistence_returns_last_value():
    model = PersistenceModel()
    pred = model.predict([1.0, 2.0, 3.0], "2026-07-02", "precipitation_mm", "mumbai")
    assert pred.value == 3.0


def test_persistence_single_value():
    model = PersistenceModel()
    pred = model.predict([42.5], "2026-07-02", "precipitation_mm", "mumbai")
    assert pred.value == 42.5


def test_persistence_empty_history():
    model = PersistenceModel()
    pred = model.predict([], "2026-07-02", "precipitation_mm", "mumbai")
    assert pred.value == 0.0


def test_persistence_metadata():
    model = PersistenceModel()
    assert model.id == "persistence"
    assert model.phase == 1
    cfg = model.get_config()
    assert cfg["id"] == "persistence"
    assert cfg["type"] == "statistical"


def test_prediction_dataclass():
    p = Prediction(value=5.0, lower=3.0, upper=7.0, confidence=0.8)
    assert p.value == 5.0
    assert p.lower == 3.0
    assert p.upper == 7.0

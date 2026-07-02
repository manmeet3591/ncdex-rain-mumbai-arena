import importlib
import pkgutil
from pathlib import Path

from models.base import BaseModel

_REGISTRY: dict[str, BaseModel] = {}


def discover_models() -> dict[str, BaseModel]:
    global _REGISTRY
    models_dir = Path(__file__).parent.parent / "models"
    for _, modname, _ in pkgutil.iter_modules([str(models_dir)]):
        if modname == "base":
            continue
        module = importlib.import_module(f"models.{modname}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type)
                    and issubclass(attr, BaseModel)
                    and attr is not BaseModel):
                instance = attr()
                _REGISTRY[instance.id] = instance
    return _REGISTRY


def get_model(model_id: str) -> BaseModel:
    if not _REGISTRY:
        discover_models()
    return _REGISTRY[model_id]


def list_models() -> list[BaseModel]:
    if not _REGISTRY:
        discover_models()
    return list(_REGISTRY.values())

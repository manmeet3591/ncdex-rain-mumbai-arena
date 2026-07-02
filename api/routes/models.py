from fastapi import APIRouter
from core.db import get_connection

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
def list_models():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM models WHERE active = 1 ORDER BY phase, id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{model_id}")
def get_model(model_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM models WHERE id = ?", (model_id,)).fetchone()
    conn.close()
    if not row:
        return {"error": "Model not found"}
    return dict(row)

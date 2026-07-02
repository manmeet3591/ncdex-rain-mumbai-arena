from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.db import init_db
from api.routes import leaderboard, predictions, trades, models, markets


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Weather Forecasting Arena", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leaderboard.router)
app.include_router(predictions.router)
app.include_router(trades.router)
app.include_router(models.router)
app.include_router(markets.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

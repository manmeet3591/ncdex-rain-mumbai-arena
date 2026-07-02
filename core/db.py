import sqlite3
from pathlib import Path

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS models (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    model_type  TEXT NOT NULL,
    phase       INTEGER DEFAULT 1,
    config_json TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    active      INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS actuals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    market      TEXT NOT NULL,
    location    TEXT NOT NULL,
    target_date TEXT NOT NULL,
    variable    TEXT NOT NULL,
    value       REAL,
    source      TEXT,
    fetched_at  TEXT DEFAULT (datetime('now')),
    UNIQUE(market, location, target_date, variable)
);

CREATE TABLE IF NOT EXISTS predictions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id      TEXT NOT NULL REFERENCES models(id),
    market        TEXT NOT NULL,
    location      TEXT NOT NULL,
    target_date   TEXT NOT NULL,
    variable      TEXT NOT NULL,
    value         REAL NOT NULL,
    confidence    REAL,
    metadata_json TEXT,
    predicted_at  TEXT DEFAULT (datetime('now')),
    UNIQUE(model_id, market, location, target_date, variable)
);

CREATE TABLE IF NOT EXISTS scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id        TEXT NOT NULL REFERENCES models(id),
    market          TEXT NOT NULL,
    location        TEXT NOT NULL,
    target_date     TEXT NOT NULL,
    variable        TEXT NOT NULL,
    predicted_value REAL NOT NULL,
    actual_value    REAL NOT NULL,
    error           REAL NOT NULL,
    abs_error       REAL NOT NULL,
    squared_error   REAL NOT NULL,
    scored_at       TEXT DEFAULT (datetime('now')),
    UNIQUE(model_id, market, location, target_date, variable)
);

CREATE TABLE IF NOT EXISTS trades (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id        TEXT NOT NULL REFERENCES models(id),
    market          TEXT NOT NULL,
    location        TEXT NOT NULL,
    target_date     TEXT NOT NULL,
    direction       TEXT NOT NULL,
    entry_price     REAL NOT NULL,
    predicted_value REAL NOT NULL,
    position_size   REAL DEFAULT 10.0,
    shares          REAL,
    status          TEXT DEFAULT 'open',
    exit_price      REAL,
    pnl             REAL,
    resolved_at     TEXT,
    trade_metadata  TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(model_id, market, location, target_date, direction)
);

CREATE TABLE IF NOT EXISTS market_snapshots (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    market        TEXT NOT NULL,
    location      TEXT NOT NULL,
    target_date   TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    fetched_at    TEXT DEFAULT (datetime('now'))
);
"""


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str | None = None) -> None:
    conn = get_connection(db_path)
    conn.executescript(SCHEMA)
    conn.close()


def store_prediction(conn, model_id, market, location, target_date, variable, value, confidence=None, metadata=None):
    import json
    conn.execute(
        """INSERT OR REPLACE INTO predictions
           (model_id, market, location, target_date, variable, value, confidence, metadata_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (model_id, market, location, target_date, variable, value, confidence,
         json.dumps(metadata) if metadata else None),
    )
    conn.commit()


def store_actual(conn, market, location, target_date, variable, value, source=None):
    conn.execute(
        """INSERT OR REPLACE INTO actuals
           (market, location, target_date, variable, value, source)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (market, location, target_date, variable, value, source),
    )
    conn.commit()


def get_history(conn, market, location, variable, end_date, lookback_days=90):
    rows = conn.execute(
        """SELECT value FROM actuals
           WHERE market = ? AND location = ? AND variable = ?
             AND target_date <= ? AND value IS NOT NULL
           ORDER BY target_date DESC
           LIMIT ?""",
        (market, location, variable, end_date, lookback_days),
    ).fetchall()
    return [r["value"] for r in reversed(rows)]


def get_unscored_predictions(conn):
    return conn.execute(
        """SELECT p.id, p.model_id, p.market, p.location, p.target_date,
                  p.variable, p.value as predicted_value, a.value as actual_value
           FROM predictions p
           JOIN actuals a ON p.market = a.market
                         AND p.location = a.location
                         AND p.target_date = a.target_date
                         AND p.variable = a.variable
           LEFT JOIN scores s ON p.model_id = s.model_id
                             AND p.market = s.market
                             AND p.location = s.location
                             AND p.target_date = s.target_date
                             AND p.variable = s.variable
           WHERE a.value IS NOT NULL AND s.id IS NULL"""
    ).fetchall()


def store_score(conn, model_id, market, location, target_date, variable, predicted, actual):
    error = predicted - actual
    conn.execute(
        """INSERT OR REPLACE INTO scores
           (model_id, market, location, target_date, variable,
            predicted_value, actual_value, error, abs_error, squared_error)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (model_id, market, location, target_date, variable,
         predicted, actual, error, abs(error), error ** 2),
    )
    conn.commit()


def register_model(conn, model_id, name, description, model_type, phase=1, config=None):
    import json
    conn.execute(
        """INSERT OR REPLACE INTO models (id, name, description, model_type, phase, config_json)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (model_id, name, description, model_type, phase,
         json.dumps(config) if config else None),
    )
    conn.commit()

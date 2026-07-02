import logging
from core.db import get_unscored_predictions, store_score

log = logging.getLogger(__name__)


def resolve_pending(conn) -> int:
    unscored = get_unscored_predictions(conn)
    count = 0
    for row in unscored:
        store_score(
            conn,
            model_id=row["model_id"],
            market=row["market"],
            location=row["location"],
            target_date=row["target_date"],
            variable=row["variable"],
            predicted=row["predicted_value"],
            actual=row["actual_value"],
        )
        count += 1
    if count:
        log.info(f"Scored {count} pending predictions")
    return count

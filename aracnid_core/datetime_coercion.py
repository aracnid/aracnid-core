from __future__ import annotations

from datetime import datetime, timezone

from .timezone_config import DateTimeTZConfig, DateTimeTZMode


def parse_iso_datetime(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("Naive datetimes are not supported")
    return dt


def coerce_datetime_timezone(dt: datetime, cfg: DateTimeTZConfig) -> datetime:
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("Naive datetimes are not supported")

    if cfg.mode is DateTimeTZMode.KEEP:
        return dt
    if cfg.mode is DateTimeTZMode.UTC:
        return dt.astimezone(timezone.utc)

    # LOCAL mode (guaranteed non-None by config validation)
    return dt.astimezone(cfg.local_timezone)
"""Contract tests for datetime timezone coercion.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from aracnid_core.datetime_coercion import coerce_datetime_timezone, parse_iso_datetime
from aracnid_core.timezone_config import DateTimeTZConfig, DateTimeTZMode


def test_parse_iso_datetime_accepts_z_suffix() -> None:
    dt = parse_iso_datetime("2026-07-22T12:34:56.000Z")
    assert dt.tzinfo is not None
    assert dt.astimezone(timezone.utc) == datetime(2026, 7, 22, 12, 34, 56, tzinfo=timezone.utc)


def test_parse_iso_datetime_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError, match="Naive datetimes are not supported"):
        parse_iso_datetime("2026-07-22T12:34:56")


def test_coerce_datetime_timezone_keep_mode_preserves_offset() -> None:
    src = datetime(2026, 7, 22, 12, 34, 56, tzinfo=timezone(timedelta(hours=-4)))
    cfg = DateTimeTZConfig(mode=DateTimeTZMode.KEEP, local_timezone=None)

    out = coerce_datetime_timezone(src, cfg)

    assert out is src


def test_coerce_datetime_timezone_utc_mode_converts_to_utc() -> None:
    src = datetime(2026, 7, 22, 12, 34, 56, tzinfo=timezone(timedelta(hours=-4)))
    cfg = DateTimeTZConfig(mode=DateTimeTZMode.UTC, local_timezone=None)

    out = coerce_datetime_timezone(src, cfg)

    assert out.tzinfo is not None
    assert out.astimezone(timezone.utc) == datetime(2026, 7, 22, 16, 34, 56, tzinfo=timezone.utc)


def test_coerce_datetime_timezone_local_mode_uses_explicit_zone() -> None:
    src = datetime(2026, 7, 22, 12, 0, 0, tzinfo=timezone.utc)
    cfg = DateTimeTZConfig(mode=DateTimeTZMode.LOCAL, local_timezone=ZoneInfo("America/New_York"))

    out = coerce_datetime_timezone(src, cfg)

    assert out.tzinfo is not None
    # July in New York is EDT (UTC-4)
    assert out.hour == 8


def test_coerce_datetime_timezone_rejects_naive_input() -> None:
    src = datetime(2026, 7, 22, 12, 0, 0)  # naive
    cfg = DateTimeTZConfig(mode=DateTimeTZMode.UTC, local_timezone=None)

    with pytest.raises(ValueError, match="Naive datetimes are not supported"):
        coerce_datetime_timezone(src, cfg)
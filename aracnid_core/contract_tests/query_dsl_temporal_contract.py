from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from aracnid_core.exceptions import QueryValidationError
from aracnid_core.query_dsl import normalize_query


def _walk_values(node):
    """Yield all scalar values in a normalized query dict/list structure."""
    if isinstance(node, dict):
        for v in node.values():
            yield from _walk_values(v)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_values(item)
    else:
        yield node


def test_normalize_query_accepts_timezone_aware_datetime_local_tz():
    # Local timezone aware datetime (example: America/New_York)
    dt_local = datetime(2026, 7, 19, 9, 30, tzinfo=ZoneInfo("America/New_York"))
    query = {"ts": {"$eq": dt_local}}

    normalized = normalize_query(query)

    # Should normalize successfully and preserve the same instant.
    # We assert by finding at least one datetime equal by instant.
    datetimes = [v for v in _walk_values(normalized) if isinstance(v, datetime)]
    assert datetimes, "Expected normalized query to contain datetime value(s)."
    assert any(d.astimezone(timezone.utc) == dt_local.astimezone(timezone.utc) for d in datetimes)


def test_normalize_query_accepts_timezone_aware_datetime_utc():
    dt_utc = datetime(2026, 7, 19, 13, 30, tzinfo=timezone.utc)
    query = {"ts": {"$eq": dt_utc}}

    normalized = normalize_query(query)

    datetimes = [v for v in _walk_values(normalized) if isinstance(v, datetime)]
    assert datetimes, "Expected normalized query to contain datetime value(s)."
    assert any(d.astimezone(timezone.utc) == dt_utc for d in datetimes)


def test_normalize_query_rejects_naive_datetime():
    dt_naive = datetime(2026, 7, 19, 9, 30)  # tzinfo=None
    query = {"ts": {"$eq": dt_naive}}

    with pytest.raises(QueryValidationError, match=r"datetime|timezone|naive|tzinfo"):
        normalize_query(query)


def test_normalize_query_date_literal_still_valid():
    d = date(2026, 7, 19)
    query = {"as_of": {"$eq": d}}

    normalized = normalize_query(query)

    dates = [v for v in _walk_values(normalized) if isinstance(v, date) and not isinstance(v, datetime)]
    assert dates, "Expected normalized query to contain date value(s)."
    assert d in dates
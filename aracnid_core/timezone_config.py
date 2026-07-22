from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class DateTimeTZMode(str, Enum):
    UTC = "utc"
    LOCAL = "local"
    KEEP = "keep"


@dataclass(frozen=True)
class DateTimeTZConfig:
    mode: DateTimeTZMode
    local_timezone: ZoneInfo | None


def _parse_mode(raw: str | None) -> DateTimeTZMode:
    if raw is None or raw.strip() == "":
        return DateTimeTZMode.UTC
    normalized = raw.strip().lower()
    try:
        return DateTimeTZMode(normalized)
    except ValueError as exc:
        valid = ", ".join(m.value for m in DateTimeTZMode)
        raise ValueError(
            f"Invalid ARACNID_DATETIME_TZ_MODE={raw!r}. Expected one of: {valid}"
        ) from exc


def _parse_local_tz(raw: str | None) -> ZoneInfo | None:
    if raw is None or raw.strip() == "":
        return None
    try:
        return ZoneInfo(raw.strip())
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f"Invalid ARACNID_LOCAL_TIMEZONE={raw!r}. "
            "Expected IANA timezone, e.g. 'America/New_York'."
        ) from exc


def load_datetime_tz_config_from_env(
    *,
    mode_env_var: str = "ARACNID_DATETIME_TZ_MODE",
    local_tz_env_var: str = "ARACNID_LOCAL_TIMEZONE",
) -> DateTimeTZConfig:
    mode = _parse_mode(os.getenv(mode_env_var))
    local_tz = _parse_local_tz(os.getenv(local_tz_env_var))

    if mode is DateTimeTZMode.LOCAL and local_tz is None:
        raise ValueError(
            "ARACNID_LOCAL_TIMEZONE is required when "
            "ARACNID_DATETIME_TZ_MODE=local "
            "(example: ARACNID_LOCAL_TIMEZONE=America/New_York)."
        )

    return DateTimeTZConfig(mode=mode, local_timezone=local_tz)
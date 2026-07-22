"""Contract tests for timezone configuration loaded from environment variables.
"""
import pytest

from aracnid_core.timezone_config import (
    DateTimeTZMode,
    load_datetime_tz_config_from_env,
)


def test_env_default_mode_is_utc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARACNID_DATETIME_TZ_MODE", raising=False)
    monkeypatch.delenv("ARACNID_LOCAL_TIMEZONE", raising=False)

    cfg = load_datetime_tz_config_from_env()

    assert cfg.mode is DateTimeTZMode.UTC
    assert cfg.local_timezone is None


def test_env_invalid_mode_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARACNID_DATETIME_TZ_MODE", "naive")

    with pytest.raises(ValueError, match="Invalid ARACNID_DATETIME_TZ_MODE"):
        load_datetime_tz_config_from_env()


def test_env_local_mode_requires_explicit_timezone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARACNID_DATETIME_TZ_MODE", "local")
    monkeypatch.delenv("ARACNID_LOCAL_TIMEZONE", raising=False)

    with pytest.raises(ValueError, match="ARACNID_LOCAL_TIMEZONE is required"):
        load_datetime_tz_config_from_env()


def test_env_invalid_local_timezone_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARACNID_DATETIME_TZ_MODE", "local")
    monkeypatch.setenv("ARACNID_LOCAL_TIMEZONE", "Mars/Phobos")

    with pytest.raises(ValueError, match="Invalid ARACNID_LOCAL_TIMEZONE"):
        load_datetime_tz_config_from_env()


def test_env_local_mode_with_valid_timezone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARACNID_DATETIME_TZ_MODE", "local")
    monkeypatch.setenv("ARACNID_LOCAL_TIMEZONE", "America/New_York")

    cfg = load_datetime_tz_config_from_env()

    assert cfg.mode is DateTimeTZMode.LOCAL
    assert str(cfg.local_timezone) == "America/New_York"
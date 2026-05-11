from __future__ import annotations

import json
from pathlib import Path

from geektime_exporter import cli


def test_main_calls_runtime_with_config(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"username": "user", "password": "pass", "log_file": "run.log"}),
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_export(options, config):  # type: ignore[no-untyped-def]
        captured["options"] = options
        captured["config"] = config
        return 0

    monkeypatch.setattr(cli, "run_export", fake_run_export)
    exit_code = cli.main(
        [
            "export",
            "--article",
            "https://time.geekbang.org/column/article/123",
            "--output",
            str(tmp_path / "out"),
            "--images-dir",
            str(tmp_path / "out" / "images"),
            "--config",
            str(config_path),
        ]
    )

    assert exit_code == 0
    assert captured["config"] == {"username": "user", "password": "pass", "log_file": "run.log"}


def test_main_run_interactive_uses_start_article_id(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"log_file": "run.log"}), encoding="utf-8")
    captured: dict[str, object] = {}

    answers = iter(
        [
            "2",  # mode: batch
            "https://time.geekbang.org/column/intro/101113501?tab=catalog",
            "article_id",
            "967091",
            "",  # output default
            "",  # images default
            "",  # naming default
            "",  # retries default
            str(config_path),
        ]
    )

    def fake_input(_prompt: str) -> str:
        return next(answers)

    def fake_run_export(options, config):  # type: ignore[no-untyped-def]
        captured["options"] = options
        captured["config"] = config
        return 0

    monkeypatch.setattr(cli, "input", fake_input)
    monkeypatch.setattr(cli, "run_export", fake_run_export)
    exit_code = cli.main(["run"])

    assert exit_code == 0
    assert captured["config"] == {"log_file": "run.log"}
    assert captured["options"].batch == "https://time.geekbang.org/column/intro/101113501?tab=catalog"
    assert captured["options"].article is None
    assert captured["options"].start_mode == "article_id"
    assert captured["options"].start_value == "967091"


def test_main_run_preflight_allows_auto_switch_when_cdp_required_unavailable(
    monkeypatch, tmp_path: Path
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "auth_mode": "browser",
                "browser_cdp_required": True,
                "browser_cdp_url": "http://127.0.0.1:9222",
                "log_file": "run.log",
            }
        ),
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    answers = iter(
        [
            "1",  # mode: article
            "967091",
            "",  # output default
            "",  # images default
            "",  # naming default
            "",  # retries default
            str(config_path),
            "y",  # preflight switch to non-required
        ]
    )

    def fake_input(_prompt: str) -> str:
        return next(answers)

    def fake_check(_cdp_url: str) -> tuple[bool, str]:
        return (False, "status=404")

    def fake_run_export(options, config):  # type: ignore[no-untyped-def]
        captured["options"] = options
        captured["config"] = config
        return 0

    monkeypatch.setattr(cli, "input", fake_input)
    monkeypatch.setattr(cli, "_check_cdp_endpoint_health", fake_check)
    monkeypatch.setattr(cli, "run_export", fake_run_export)
    exit_code = cli.main(["run"])

    assert exit_code == 0
    assert captured["config"]["browser_cdp_required"] is False

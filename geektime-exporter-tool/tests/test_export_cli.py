from __future__ import annotations

import json

import pytest

from geektime_exporter.cli import ExportOptions, parse_args


def test_parse_export_single_article_defaults() -> None:
    args = parse_args(["export", "--article", "article-001"])
    assert args == ExportOptions(
        article="article-001",
        batch=None,
        output="./output",
        images_dir="./output/images",
        naming="slug",
        retries=3,
        config=None,
        start_mode="index",
        start_value=None,
    )


def test_parse_export_uses_config_values(tmp_path: pytest.TempPathFactory) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "article": "article-from-config",
                "output": "./dist",
                "images_dir": "./dist/img",
                "naming": "title",
                "retries": 5,
            }
        ),
        encoding="utf-8",
    )

    args = parse_args(["export", "--config", str(config_path)])
    assert args == ExportOptions(
        article="article-from-config",
        batch=None,
        output="./dist",
        images_dir="./dist/img",
        naming="title",
        retries=5,
        config=str(config_path),
        start_mode="index",
        start_value=None,
    )


def test_parse_export_cli_overrides_config(tmp_path: pytest.TempPathFactory) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "article": "article-from-config",
                "output": "./dist",
                "images_dir": "./dist/img",
                "naming": "title",
                "retries": 5,
            }
        ),
        encoding="utf-8",
    )

    args = parse_args(
        [
            "export",
            "--config",
            str(config_path),
            "--article",
            "article-from-cli",
            "--output",
            "./override",
            "--images-dir",
            "./override/images",
            "--naming",
            "id",
            "--retries",
            "2",
        ]
    )
    assert args == ExportOptions(
        article="article-from-cli",
        batch=None,
        output="./override",
        images_dir="./override/images",
        naming="id",
        retries=2,
        config=str(config_path),
        start_mode="index",
        start_value=None,
    )


def test_export_requires_article_or_batch() -> None:
    args = parse_args(["export"])
    assert args.batch == "专栏URL"
    assert args.article is None


def test_parse_run_defaults_for_batch() -> None:
    args = parse_args(["run"])
    assert args == ExportOptions(
        article=None,
        batch="专栏URL",
        output="./output",
        images_dir="./output/images",
        naming="slug",
        retries=3,
        config=None,
        start_mode="index",
        start_value=None,
    )

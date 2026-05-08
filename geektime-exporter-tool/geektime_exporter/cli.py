from __future__ import annotations

import argparse
import builtins
from dataclasses import dataclass, replace
from typing import Sequence

from .config import ConfigError, load_config
from .runtime import RuntimeOptions, run_export

input = builtins.input


@dataclass(frozen=True)
class ExportOptions:
    article: str | None
    batch: str | None
    output: str
    images_dir: str
    naming: str
    retries: int
    config: str | None
    start_mode: str = "index"
    start_value: str | None = None


def _bootstrap_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geektime-exporter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export = subparsers.add_parser("export", help="Export article(s) to Markdown")
    export.add_argument("--config", type=str, default=None, help="Path to JSON config")
    run = subparsers.add_parser("run", help="Run interactive export wizard")
    run.add_argument("--config", type=str, default=None, help="Path to JSON config")
    return parser


def _build_main_parser(config: dict[str, object]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geektime-exporter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export = subparsers.add_parser("export", help="Export article(s) to Markdown")
    mode = export.add_mutually_exclusive_group(required=False)
    mode.add_argument("--article", type=str, default=config.get("article"))
    mode.add_argument("--batch", type=str, default=config.get("batch"))

    export.add_argument("--config", type=str, default=None, help="Path to JSON config")
    export.add_argument("--output", type=str, default=config.get("output", "./output"))
    export.add_argument(
        "--images-dir",
        type=str,
        default=config.get("images_dir", "./output/images"),
    )
    export.add_argument(
        "--naming",
        choices=["slug", "id", "title"],
        default=config.get("naming", "slug"),
    )
    export.add_argument("--retries", type=int, default=int(config.get("retries", 3)))

    run = subparsers.add_parser("run", help="Run interactive export wizard")
    run.add_argument("--config", type=str, default=None, help="Path to JSON config")

    return parser


def _prompt(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    if raw:
        return raw
    return default or ""


def _normalize_article(value: str) -> str:
    text = value.strip()
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return f"https://time.geekbang.org/column/article/{text}"


def _normalize_column(value: str) -> str:
    text = value.strip()
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return f"https://time.geekbang.org/column/intro/{text}?tab=catalog"


def _interactive_options(config_hint: dict[str, object], config_arg: str | None) -> ExportOptions:
    output_default = str(config_hint.get("output", "./output"))
    images_default = str(config_hint.get("images_dir", "./output/images"))
    naming_default = str(config_hint.get("naming", "slug"))
    retries_default = str(config_hint.get("retries", 3))
    config_default = config_arg or ""

    mode = _prompt("选择导出模式：1) 单篇文章 2) 专栏批量", "2")
    is_article = mode == "1"

    article: str | None = None
    batch: str | None = None
    start_mode = "index"
    start_value: str | None = None

    if is_article:
        article_input = _prompt("输入文章 ID 或完整文章 URL", "")
        article = _normalize_article(article_input)
    else:
        batch_input = _prompt("输入专栏 ID 或完整专栏 URL", "")
        batch = _normalize_column(batch_input)
        start_mode_input = _prompt("起始方式：index（目录序号）/article_id（文章ID）", "index").lower()
        if start_mode_input not in {"index", "article_id"}:
            start_mode_input = "index"
        start_mode = start_mode_input
        if start_mode == "index":
            raw_index = _prompt("起始目录序号（留空默认从第 1 篇）", "")
            if raw_index:
                start_value = raw_index
        else:
            raw_article_id = _prompt("起始文章 ID", "")
            start_value = raw_article_id or None

    output = _prompt("输出目录", output_default)
    images_dir = _prompt("图片目录", images_default)
    naming = _prompt("命名规则（slug/id/title）", naming_default)
    retries = int(_prompt("重试次数", retries_default))
    config = _prompt("配置文件路径（可留空）", config_default) or None

    return ExportOptions(
        article=article,
        batch=batch,
        output=output,
        images_dir=images_dir,
        naming=naming,
        retries=retries,
        config=config,
        start_mode=start_mode,
        start_value=start_value,
    )


def parse_args(argv: Sequence[str] | None = None) -> ExportOptions:
    bootstrap, _ = _bootstrap_parser().parse_known_args(argv)

    config: dict[str, object] = {}
    if bootstrap.command in {"export", "run"}:
        try:
            config = load_config(getattr(bootstrap, "config", None))
        except ConfigError as exc:
            raise SystemExit(str(exc)) from exc

    args = _build_main_parser(config).parse_args(argv)

    if bootstrap.command == "run":
        return ExportOptions(
            article=None,
            batch="专栏URL",
            output=str(config.get("output", "./output")),
            images_dir=str(config.get("images_dir", "./output/images")),
            naming=str(config.get("naming", "slug")),
            retries=int(config.get("retries", 3)),
            config=args.config,
            start_mode="index",
            start_value=None,
        )

    options = ExportOptions(
        article=getattr(args, "article", None),
        batch=getattr(args, "batch", None),
        output=args.output,
        images_dir=args.images_dir,
        naming=args.naming,
        retries=args.retries,
        config=args.config,
        start_mode="index",
        start_value=None,
    )
    if not options.article and not options.batch:
        options = replace(options, batch="专栏URL")

    if options.article and options.batch:
        raise SystemExit("Exactly one of --article or --batch must be provided")

    return options


def main(argv: Sequence[str] | None = None) -> int:
    bootstrap, _ = _bootstrap_parser().parse_known_args(argv)
    options = parse_args(argv)
    if bootstrap.command == "run":
        base_config: dict[str, object] = {}
        if options.config:
            try:
                base_config = load_config(options.config)
            except ConfigError as exc:
                raise SystemExit(str(exc)) from exc
        options = _interactive_options(base_config, options.config)

    try:
        config = load_config(options.config)
    except ConfigError as exc:
        raise SystemExit(str(exc)) from exc
    return run_export(
        RuntimeOptions(
            article=options.article,
            batch=options.batch,
            output=options.output,
            images_dir=options.images_dir,
            naming=options.naming,
            retries=options.retries,
            start_mode=options.start_mode,
            start_value=options.start_value,
        ),
        config,
    )

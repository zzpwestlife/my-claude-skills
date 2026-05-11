from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qsl, urlencode, urlparse

from .article_parser import (
    Block,
    CodeBlock,
    HeadingBlock,
    ImageBlock,
    ListBlock,
    ParagraphBlock,
    QuoteBlock,
    discover_column_article_urls,
    fetch_article_page,
    parse_article_dom,
)
from .image_localizer import Downloader, localize_markdown_images

_ARTICLE_ID_RE = re.compile(r"/column/article/(\d+)/?$")
_COLUMN_ID_RE = re.compile(r"/column/intro/(\d+)/?$")
_INVALID_FILENAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_SPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^A-Za-z0-9\u4e00-\u9fff_-]+")

Fetcher = Callable[[str, dict[str, str]], str]


@dataclass(frozen=True)
class ExportedArticle:
    article_url: str
    file_path: Path


def _slugify(text: str) -> str:
    normalized = _SPACE_RE.sub("-", text.strip())
    normalized = _PUNCT_RE.sub("-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-._")
    return normalized or "article"


def _sanitize_title_filename(text: str) -> str:
    normalized = _INVALID_FILENAME_RE.sub("-", text.strip())
    normalized = _SPACE_RE.sub("-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-._")
    return normalized or "article"


def _article_id(article_url: str) -> str | None:
    matched = _ARTICLE_ID_RE.search(urlparse(article_url).path)
    if not matched:
        return None
    return matched.group(1)


def _column_id(column_url: str) -> str | None:
    matched = _COLUMN_ID_RE.search(urlparse(column_url).path)
    if not matched:
        return None
    return matched.group(1)


def _build_column_articles_api_url(column_url: str, column_id: str) -> str:
    parsed = urlparse(column_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.pop("tab", None)
    query.update({"cid": column_id, "size": "500", "prev": "0", "order": "earliest"})
    return f"{parsed.scheme}://{parsed.netloc}/serv/v1/column/articles?{urlencode(query)}"


def _discover_column_article_urls_via_api(
    *,
    column_url: str,
    session_token: str,
    fetcher: Fetcher | None,
) -> list[str]:
    column_id = _column_id(column_url)
    if not column_id:
        return []

    api_url = _build_column_articles_api_url(column_url, column_id)
    api_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": column_url,
        "Origin": f"{urlparse(column_url).scheme}://{urlparse(column_url).netloc}",
        "X-Requested-With": "XMLHttpRequest",
    }
    body = fetch_article_page(
        api_url,
        session_token,
        fetcher=fetcher,
        extra_headers=api_headers,
    )
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return []

    items: list[object] = []
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict):
            raw_items = data.get("list", [])
            if isinstance(raw_items, list):
                items = raw_items
        elif isinstance(data, list):
            items = data
        elif isinstance(payload.get("list"), list):
            items = payload.get("list", [])

    if not isinstance(items, list):
        return []

    urls: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        article_id = str(item.get("article_id", "")).strip()
        if not article_id:
            continue
        urls.append(f"https://time.geekbang.org/column/article/{article_id}")
    return urls


def render_gfm_markdown(blocks: list[Block]) -> str:
    chunks: list[str] = []
    for block in blocks:
        if isinstance(block, HeadingBlock):
            level = min(max(block.level, 1), 6)
            chunks.append(f'{"#" * level} {block.text}')
            continue
        if isinstance(block, ParagraphBlock):
            chunks.append(block.text)
            continue
        if isinstance(block, CodeBlock):
            language = block.language or ""
            chunks.append(f"```{language}\n{block.code}\n```")
            continue
        if isinstance(block, QuoteBlock):
            quote_lines = block.text.splitlines() or [block.text]
            chunks.append("\n".join(f"> {line}" for line in quote_lines))
            continue
        if isinstance(block, ListBlock):
            if block.ordered:
                chunks.append("\n".join(f"{idx}. {item}" for idx, item in enumerate(block.items, start=1)))
            else:
                chunks.append("\n".join(f"- {item}" for item in block.items))
            continue
        if isinstance(block, ImageBlock):
            chunks.append(f"![{block.alt}]({block.url})")
            continue
    return "\n\n".join(chunks).strip() + "\n"


def build_markdown_path(
    output_dir: Path,
    title: str,
    article_id: str | None,
    naming: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    if naming == "id":
        stem = article_id or _slugify(title)
    elif naming == "title":
        stem = _sanitize_title_filename(title)
    else:
        stem = _slugify(title)

    candidate = output_dir / f"{stem}.md"
    suffix = 1
    while candidate.exists():
        candidate = output_dir / f"{stem}-{suffix}.md"
        suffix += 1
    return candidate


def _article_title(blocks: list[Block], article_url: str) -> str:
    for block in blocks:
        if isinstance(block, HeadingBlock):
            return block.text
    article_id = _article_id(article_url)
    if article_id:
        return f"article-{article_id}"
    return "article"


_STOP_HEADINGS = ("全部留言", "精选留言", "全部评论", "评论区", "推荐阅读", "相关文章")


def _looks_like_speed_menu(block: ListBlock) -> bool:
    if not block.items:
        return False
    normalized = [item.strip().lower().replace(" ", "") for item in block.items]
    return all(re.fullmatch(r"\d+(\.\d+)?x(\ue698)?", item) for item in normalized if item)


def _filter_main_content_blocks(blocks: list[Block]) -> list[Block]:
    if not blocks:
        return []

    start_index = 0
    for idx, block in enumerate(blocks):
        if isinstance(block, HeadingBlock):
            start_index = idx
            break

    filtered: list[Block] = []
    for block in blocks[start_index:]:
        if isinstance(block, HeadingBlock):
            heading_text = block.text.strip()
            if any(stop in heading_text for stop in _STOP_HEADINGS):
                break
        if isinstance(block, ListBlock) and _looks_like_speed_menu(block):
            continue
        filtered.append(block)
    return filtered


def export_single_article(
    article_url: str,
    session_token: str,
    output_dir: Path,
    images_dir: Path,
    naming: str,
    fetcher: Fetcher | None = None,
    downloader: Downloader | None = None,
) -> ExportedArticle:
    html = fetch_article_page(article_url, session_token, fetcher=fetcher)
    blocks = _filter_main_content_blocks(parse_article_dom(html))
    markdown = render_gfm_markdown(blocks)

    metadata_name = f".image-progress-{_article_id(article_url) or 'default'}.json"
    markdown_with_local_images = localize_markdown_images(
        markdown=markdown,
        image_urls=[],
        images_dir=images_dir,
        metadata_path=output_dir / metadata_name,
        downloader=downloader,
    )

    title = _article_title(blocks, article_url=article_url)
    target = build_markdown_path(
        output_dir=output_dir,
        title=title,
        article_id=_article_id(article_url),
        naming=naming,
    )
    target.write_text(markdown_with_local_images, encoding="utf-8")
    return ExportedArticle(article_url=article_url, file_path=target)


def export_batch_articles(
    column_url: str,
    session_token: str,
    output_dir: Path,
    images_dir: Path,
    naming: str,
    fetcher: Fetcher | None = None,
    downloader: Downloader | None = None,
    start_index: int = 1,
    start_article_id: str | None = None,
) -> list[ExportedArticle]:
    column_html = fetch_article_page(column_url, session_token, fetcher=fetcher)
    article_urls = discover_column_article_urls(html=column_html, base_url=column_url)
    if not article_urls:
        article_urls = _discover_column_article_urls_via_api(
            column_url=column_url,
            session_token=session_token,
            fetcher=fetcher,
        )

    filtered_urls = article_urls
    if start_article_id:
        matched_index = next(
            (idx for idx, url in enumerate(article_urls) if _article_id(url) == start_article_id),
            None,
        )
        if matched_index is not None:
            filtered_urls = article_urls[matched_index:]
        else:
            filtered_urls = []
    else:
        normalized_start = max(start_index, 1)
        filtered_urls = article_urls[normalized_start - 1 :]

    exported: list[ExportedArticle] = []
    for article_url in filtered_urls:
        exported.append(
            export_single_article(
                article_url=article_url,
                session_token=session_token,
                output_dir=output_dir,
                images_dir=images_dir,
                naming=naming,
                fetcher=fetcher,
                downloader=downloader,
            )
        )
    return exported

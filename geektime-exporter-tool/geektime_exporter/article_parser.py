from __future__ import annotations

import re
import urllib.request
from urllib.error import HTTPError
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable
from urllib.parse import urljoin

from .auth import SessionInvalidError

ARTICLE_URL_RE = re.compile(r"/column/article/\d+/?$")


@dataclass(frozen=True)
class HeadingBlock:
    level: int
    text: str


@dataclass(frozen=True)
class ParagraphBlock:
    text: str


@dataclass(frozen=True)
class CodeBlock:
    code: str
    language: str | None = None


@dataclass(frozen=True)
class QuoteBlock:
    text: str


@dataclass(frozen=True)
class ListBlock:
    ordered: bool
    items: list[str]


@dataclass(frozen=True)
class ImageBlock:
    url: str
    alt: str = ""


Block = HeadingBlock | ParagraphBlock | CodeBlock | QuoteBlock | ListBlock | ImageBlock
Fetcher = Callable[[str, dict[str, str]], str]


def _default_fetcher(url: str, headers: dict[str, str]) -> str:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:  # noqa: S310
        return response.read().decode("utf-8")


def fetch_article_page(
    article_url: str,
    session_token: str,
    fetcher: Fetcher | None = None,
) -> str:
    http_fetcher = fetcher or _default_fetcher
    headers = {"User-Agent": "geektime-exporter/0.1"}
    if session_token.startswith("cookie:"):
        headers["Cookie"] = session_token.removeprefix("cookie:")
    else:
        headers["Authorization"] = f"Bearer {session_token}"
    try:
        return http_fetcher(article_url, headers)
    except HTTPError as exc:
        if exc.code in {401, 403}:
            raise SessionInvalidError(f"http unauthorized: {exc.code}") from exc
        raise


class _ArticleLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return

        for key, value in attrs:
            if key == "href" and value:
                self.links.append(value)
                return


def discover_column_article_urls(html: str, base_url: str) -> list[str]:
    parser = _ArticleLinkParser()
    parser.feed(html)

    urls: list[str] = []
    seen: set[str] = set()
    for href in parser.links:
        url = urljoin(base_url, href)
        if not ARTICLE_URL_RE.search(url):
            continue
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)

    return urls


def _normalize_text(text: str) -> str:
    return " ".join(text.split())


class _DOMToBlocksParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self._heading_level: int | None = None
        self._heading_parts: list[str] = []
        self._paragraph_parts: list[str] = []
        self._code_parts: list[str] = []
        self._quote_parts: list[str] = []
        self._list_ordered: bool | None = None
        self._list_items: list[str] = []
        self._list_item_parts: list[str] = []
        self._in_pre = False
        self._in_paragraph = False
        self._in_blockquote = False
        self._in_list_item = False
        self._code_language: str | None = None
        self._has_slate_content = False
        self._div_roles: list[str | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_name = tag.lower()
        attr_map = dict(attrs)
        slate_type = (attr_map.get("data-slate-type") or "").strip().lower()

        if slate_type:
            self._has_slate_content = True

        if tag_name == "div":
            role: str | None = None
            if slate_type == "paragraph":
                self._in_paragraph = True
                self._paragraph_parts = []
                role = "paragraph"
            elif slate_type == "list":
                self._list_ordered = False
                self._list_items = []
                role = "list"
            elif slate_type == "list-line" and self._list_ordered is not None:
                self._in_list_item = True
                self._list_item_parts = []
                role = "list-line"
            self._div_roles.append(role)
            return

        if tag_name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if self._has_slate_content and slate_type and slate_type != "heading":
                return
            if self._has_slate_content and not slate_type:
                return
            self._heading_level = int(tag_name[1:])
            self._heading_parts = []
            return

        if tag_name == "p":
            if self._has_slate_content:
                return
            if not self._in_blockquote and not self._in_list_item:
                self._in_paragraph = True
                self._paragraph_parts = []
            return

        if tag_name == "pre":
            if self._has_slate_content:
                return
            self._in_pre = True
            self._code_parts = []
            self._code_language = None
            return

        if tag_name == "code" and self._in_pre:
            class_name = dict(attrs).get("class") or ""
            for part in class_name.split():
                if part.startswith("language-"):
                    self._code_language = part.split("-", 1)[1] or None
                    break
            return

        if tag_name == "blockquote":
            if self._has_slate_content:
                return
            self._in_blockquote = True
            self._quote_parts = []
            return

        if tag_name in {"ul", "ol"}:
            if self._has_slate_content:
                return
            self._list_ordered = tag_name == "ol"
            self._list_items = []
            return

        if tag_name == "li" and self._list_ordered is not None:
            if self._has_slate_content:
                return
            self._in_list_item = True
            self._list_item_parts = []
            return

        if tag_name == "br":
            self._append_text("\n")
            return

        if tag_name == "img":
            src = (attr_map.get("src") or "").strip()
            if src:
                self.blocks.append(ImageBlock(url=src, alt=(attr_map.get("alt") or "").strip()))

    def handle_data(self, data: str) -> None:
        self._append_text(data)

    def handle_endtag(self, tag: str) -> None:
        tag_name = tag.lower()

        if tag_name == "div":
            role = self._div_roles.pop() if self._div_roles else None
            if role == "paragraph" and self._in_paragraph:
                text = _normalize_text("".join(self._paragraph_parts))
                if text:
                    self.blocks.append(ParagraphBlock(text=text))
                self._in_paragraph = False
                self._paragraph_parts = []
                return
            if role == "list-line" and self._in_list_item:
                item = _normalize_text("".join(self._list_item_parts))
                if item:
                    self._list_items.append(item)
                self._in_list_item = False
                self._list_item_parts = []
                return
            if role == "list" and self._list_ordered is not None:
                if self._list_items:
                    self.blocks.append(
                        ListBlock(
                            ordered=bool(self._list_ordered),
                            items=list(self._list_items),
                        )
                    )
                self._list_ordered = None
                self._list_items = []
                return

        if tag_name in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading_level:
            text = _normalize_text("".join(self._heading_parts))
            if text:
                self.blocks.append(HeadingBlock(level=self._heading_level, text=text))
            self._heading_level = None
            self._heading_parts = []
            return

        if tag_name == "p" and self._in_paragraph:
            if self._has_slate_content:
                return
            text = _normalize_text("".join(self._paragraph_parts))
            if text:
                self.blocks.append(ParagraphBlock(text=text))
            self._in_paragraph = False
            self._paragraph_parts = []
            return

        if tag_name == "pre" and self._in_pre:
            if self._has_slate_content:
                return
            code = "".join(self._code_parts).strip()
            if code:
                self.blocks.append(CodeBlock(code=code, language=self._code_language))
            self._in_pre = False
            self._code_parts = []
            self._code_language = None
            return

        if tag_name == "blockquote" and self._in_blockquote:
            if self._has_slate_content:
                return
            text = _normalize_text("".join(self._quote_parts))
            if text:
                self.blocks.append(QuoteBlock(text=text))
            self._in_blockquote = False
            self._quote_parts = []
            return

        if tag_name == "li" and self._in_list_item:
            if self._has_slate_content:
                return
            item = _normalize_text("".join(self._list_item_parts))
            if item:
                self._list_items.append(item)
            self._in_list_item = False
            self._list_item_parts = []
            return

        if tag_name in {"ul", "ol"} and self._list_ordered is not None:
            if self._has_slate_content:
                return
            if self._list_items:
                self.blocks.append(
                    ListBlock(
                        ordered=bool(self._list_ordered),
                        items=list(self._list_items),
                    )
                )
            self._list_ordered = None
            self._list_items = []

    def _append_text(self, text: str) -> None:
        if self._heading_level is not None:
            self._heading_parts.append(text)
        if self._in_paragraph:
            self._paragraph_parts.append(text)
        if self._in_pre:
            self._code_parts.append(text)
        if self._in_blockquote:
            self._quote_parts.append(text)
        if self._in_list_item:
            self._list_item_parts.append(text)


def parse_article_dom(html: str) -> list[Block]:
    parser = _DOMToBlocksParser()
    parser.feed(html)
    return parser.blocks

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.parse import urljoin, urlparse

Downloader = Callable[[str], bytes]
_MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)\s]+)\)")


class _ImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        for key, value in attrs:
            if key == "src" and value:
                self.urls.append(value)
                return


def _default_downloader(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "geektime-exporter/0.1"})
    with urllib.request.urlopen(request) as response:  # noqa: S310
        return response.read()


def _deduplicate(items: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        output.append(item)
    return output


def _extract_markdown_image_urls(markdown: str) -> list[str]:
    return _deduplicate([url.strip() for url in _MARKDOWN_IMAGE_RE.findall(markdown) if url.strip()])


def extract_article_image_urls(html: str, base_url: str) -> list[str]:
    parser = _ImageParser()
    parser.feed(html)
    normalized = [urljoin(base_url, raw_url) for raw_url in parser.urls]
    return _deduplicate(normalized)


def _initial_metadata() -> dict[str, object]:
    return {
        "completed_count": 0,
        "url_status": {},
        "url_to_file": {},
        "hash_to_file": {},
    }


def _load_metadata(metadata_path: Path) -> dict[str, object]:
    if not metadata_path.exists():
        return _initial_metadata()
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def _save_metadata(metadata_path: Path, metadata: dict[str, object]) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=True, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _relative_path(from_dir: Path, target: Path) -> str:
    return target.relative_to(from_dir).as_posix()


def _pick_extension(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 10:
        return suffix
    return ".img"


def _replace_markdown_urls(markdown: str, url_to_file: dict[str, str]) -> str:
    updated = markdown
    for url, local_path in url_to_file.items():
        updated = updated.replace(f"({url})", f"({local_path})")
    return updated


def localize_markdown_images(
    markdown: str,
    image_urls: list[str],
    images_dir: Path,
    metadata_path: Path,
    downloader: Downloader | None = None,
) -> str:
    fetch = downloader or _default_downloader
    images_dir.mkdir(parents=True, exist_ok=True)

    metadata = _load_metadata(metadata_path)
    url_status = dict(metadata.get("url_status", {}))
    url_to_file = dict(metadata.get("url_to_file", {}))
    hash_to_file = dict(metadata.get("hash_to_file", {}))
    queue = _deduplicate(list(image_urls) + _extract_markdown_image_urls(markdown))

    for url in queue:
        existing_path = url_to_file.get(url)
        if (
            url_status.get(url) == "done"
            and isinstance(existing_path, str)
            and (metadata_path.parent / existing_path).exists()
        ):
            continue

        url_status[url] = "in_progress"
        metadata["url_status"] = url_status
        metadata["url_to_file"] = url_to_file
        metadata["hash_to_file"] = hash_to_file
        metadata["completed_count"] = sum(1 for item in queue if url_status.get(item) == "done")
        _save_metadata(metadata_path, metadata)

        content = fetch(url)
        digest = hashlib.sha256(content).hexdigest()
        dedup_relative = hash_to_file.get(digest)
        if isinstance(dedup_relative, str) and (metadata_path.parent / dedup_relative).exists():
            local_relative = dedup_relative
        else:
            filename = f"{digest[:16]}{_pick_extension(url)}"
            target_file = images_dir / filename
            target_file.write_bytes(content)
            local_relative = _relative_path(metadata_path.parent, target_file)
            hash_to_file[digest] = local_relative

        url_to_file[url] = local_relative
        url_status[url] = "done"
        metadata["url_status"] = url_status
        metadata["url_to_file"] = url_to_file
        metadata["hash_to_file"] = hash_to_file
        metadata["completed_count"] = sum(1 for item in queue if url_status.get(item) == "done")
        _save_metadata(metadata_path, metadata)

    final_url_to_file = {url: path for url, path in url_to_file.items() if isinstance(path, str)}
    return _replace_markdown_urls(markdown=markdown, url_to_file=final_url_to_file)

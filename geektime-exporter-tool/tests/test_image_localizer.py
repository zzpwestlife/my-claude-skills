from __future__ import annotations

import json
from pathlib import Path

import pytest

from geektime_exporter.image_localizer import (
    extract_article_image_urls,
    localize_markdown_images,
)


def test_extract_article_image_urls_deduplicates_and_normalizes() -> None:
    html = """
    <article>
      <img src="/assets/a.png" />
      <img src="https://img.example.com/b.jpg" />
      <img src="/assets/a.png" />
      <img />
    </article>
    """

    urls = extract_article_image_urls(
        html=html,
        base_url="https://time.geekbang.org/column/article/100",
    )

    assert urls == [
        "https://time.geekbang.org/assets/a.png",
        "https://img.example.com/b.jpg",
    ]


def test_localize_markdown_images_downloads_and_rewrites_relative_paths(
    tmp_path: Path,
) -> None:
    markdown = (
        "![a](https://img.example.com/a.png)\n"
        "正文\n"
        "![b](https://img.example.com/b.jpg)\n"
    )
    urls = ["https://img.example.com/a.png", "https://img.example.com/b.jpg"]

    payloads = {
        "https://img.example.com/a.png": b"img-a",
        "https://img.example.com/b.jpg": b"img-b",
    }

    def downloader(url: str) -> bytes:
        return payloads[url]

    images_dir = tmp_path / "assets"
    metadata_path = tmp_path / "progress.json"
    updated = localize_markdown_images(
        markdown=markdown,
        image_urls=urls,
        images_dir=images_dir,
        metadata_path=metadata_path,
        downloader=downloader,
    )

    assert "https://img.example.com/a.png" not in updated
    assert "https://img.example.com/b.jpg" not in updated
    assert "![a](assets/" in updated
    assert "![b](assets/" in updated
    assert len(list(images_dir.iterdir())) == 2

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["completed_count"] == 2
    assert set(metadata["url_to_file"]) == set(urls)


def test_localize_markdown_images_supports_resume_with_progress_metadata(
    tmp_path: Path,
) -> None:
    markdown = (
        "![a](https://img.example.com/a.png)\n"
        "![b](https://img.example.com/b.jpg)\n"
    )
    urls = ["https://img.example.com/a.png", "https://img.example.com/b.jpg"]

    attempts: dict[str, int] = {}
    payloads = {
        "https://img.example.com/a.png": b"img-a",
        "https://img.example.com/b.jpg": b"img-b",
    }

    def flaky_downloader(url: str) -> bytes:
        attempts[url] = attempts.get(url, 0) + 1
        if url.endswith("b.jpg") and attempts[url] == 1:
            raise RuntimeError("network down")
        return payloads[url]

    images_dir = tmp_path / "assets"
    metadata_path = tmp_path / "progress.json"

    with pytest.raises(RuntimeError):
        localize_markdown_images(
            markdown=markdown,
            image_urls=urls,
            images_dir=images_dir,
            metadata_path=metadata_path,
            downloader=flaky_downloader,
        )

    metadata_after_fail = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata_after_fail["completed_count"] == 1
    assert metadata_after_fail["url_status"]["https://img.example.com/a.png"] == "done"
    assert (
        metadata_after_fail["url_status"]["https://img.example.com/b.jpg"]
        == "in_progress"
    )

    updated = localize_markdown_images(
        markdown=markdown,
        image_urls=urls,
        images_dir=images_dir,
        metadata_path=metadata_path,
        downloader=flaky_downloader,
    )
    assert "https://img.example.com/a.png" not in updated
    assert "https://img.example.com/b.jpg" not in updated

    metadata_after_resume = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata_after_resume["completed_count"] == 2
    assert metadata_after_resume["url_status"]["https://img.example.com/b.jpg"] == "done"
    assert attempts["https://img.example.com/a.png"] == 1
    assert attempts["https://img.example.com/b.jpg"] == 2


def test_localize_markdown_images_deduplicates_by_content_hash(tmp_path: Path) -> None:
    markdown = (
        "![a](https://img.example.com/a.png)\n"
        "![dup](https://cdn.example.com/dup-a.png)\n"
    )
    urls = ["https://img.example.com/a.png", "https://cdn.example.com/dup-a.png"]

    def downloader(url: str) -> bytes:
        return b"same-content"

    images_dir = tmp_path / "assets"
    metadata_path = tmp_path / "progress.json"
    updated = localize_markdown_images(
        markdown=markdown,
        image_urls=urls,
        images_dir=images_dir,
        metadata_path=metadata_path,
        downloader=downloader,
    )

    stored = list(images_dir.iterdir())
    assert len(stored) == 1

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    path_a = metadata["url_to_file"]["https://img.example.com/a.png"]
    path_b = metadata["url_to_file"]["https://cdn.example.com/dup-a.png"]
    assert path_a == path_b
    assert f"![a]({path_a})" in updated
    assert f"![dup]({path_b})" in updated

from __future__ import annotations

from pathlib import Path

from geektime_exporter.article_parser import (
    CodeBlock,
    HeadingBlock,
    ListBlock,
    ParagraphBlock,
    QuoteBlock,
)
from geektime_exporter.markdown_export import (
    _filter_main_content_blocks,
    build_markdown_path,
    export_batch_articles,
    export_single_article,
    render_gfm_markdown,
)


def test_render_gfm_markdown_preserves_block_semantics() -> None:
    markdown = render_gfm_markdown(
        [
            HeadingBlock(level=2, text="标题"),
            ParagraphBlock(text="正文段落"),
            CodeBlock(code='print("hello")', language="python"),
            QuoteBlock(text="引用行1\n引用行2"),
            ListBlock(ordered=False, items=["一", "二"]),
            ListBlock(ordered=True, items=["甲", "乙"]),
        ]
    )

    assert "## 标题" in markdown
    assert "正文段落" in markdown
    assert "```python\nprint(\"hello\")\n```" in markdown
    assert "> 引用行1\n> 引用行2" in markdown
    assert "- 一\n- 二" in markdown
    assert "1. 甲\n2. 乙" in markdown


def test_build_markdown_path_handles_name_conflict(tmp_path: Path) -> None:
    first = build_markdown_path(
        output_dir=tmp_path,
        title="Task 5 标题",
        article_id="100",
        naming="title",
    )
    first.write_text("x", encoding="utf-8")

    second = build_markdown_path(
        output_dir=tmp_path,
        title="Task 5 标题",
        article_id="100",
        naming="title",
    )
    assert second.name == "Task-5-标题-1.md"


def test_export_single_article_writes_body_only_markdown(tmp_path: Path) -> None:
    html = """
    <article>
      <ul><li>0.75x</li><li>1.0x</li></ul>
      <h1>导出标题</h1>
      <p>正文内容</p>
      <h2>全部留言</h2>
      <p>这是评论区内容</p>
      <img src="https://img.example.com/a.png" />
    </article>
    """

    def fetcher(url: str, headers: dict[str, str]) -> str:
        return html

    def downloader(url: str) -> bytes:
        return b"image-a"

    result = export_single_article(
        article_url="https://time.geekbang.org/column/article/100",
        session_token="token-1",
        output_dir=tmp_path / "out",
        images_dir=tmp_path / "out" / "assets",
        naming="slug",
        fetcher=fetcher,
        downloader=downloader,
    )

    assert result.file_path.exists()
    content = result.file_path.read_text(encoding="utf-8")
    assert "# 导出标题" in content
    assert "正文内容" in content
    assert "0.75x" not in content
    assert "全部留言" not in content
    assert "评论区内容" not in content
    assert "assets/" not in content


def test_export_single_article_keeps_body_images_and_excludes_comment_images(tmp_path: Path) -> None:
    html = """
    <article>
      <h1>导出标题</h1>
      <p>正文内容</p>
      <img src="https://img.example.com/body.png" />
      <h2>全部留言</h2>
      <img src="https://img.example.com/comment.png" />
    </article>
    """
    downloaded: list[str] = []

    def fetcher(url: str, headers: dict[str, str]) -> str:
        return html

    def downloader(url: str) -> bytes:
        downloaded.append(url)
        return b"image-bytes"

    result = export_single_article(
        article_url="https://time.geekbang.org/column/article/100",
        session_token="token-1",
        output_dir=tmp_path / "out",
        images_dir=tmp_path / "out" / "assets",
        naming="id",
        fetcher=fetcher,
        downloader=downloader,
    )

    content = result.file_path.read_text(encoding="utf-8")
    assert "![](assets/" in content
    assert "comment.png" not in content
    assert downloaded == ["https://img.example.com/body.png"]


def test_filter_main_content_blocks_removes_noise() -> None:
    blocks = [
        ListBlock(ordered=False, items=["0.75x", "1.0x"]),
        HeadingBlock(level=1, text="文章标题"),
        ParagraphBlock(text="正文段落"),
        HeadingBlock(level=2, text="全部留言"),
        ParagraphBlock(text="不该保留"),
    ]
    filtered = _filter_main_content_blocks(blocks)
    assert filtered == [
        HeadingBlock(level=1, text="文章标题"),
        ParagraphBlock(text="正文段落"),
    ]


def test_export_batch_articles_orchestrates_multi_article_export(tmp_path: Path) -> None:
    column_html = """
    <a href="/column/article/100">A</a>
    <a href="/column/article/101">B</a>
    """
    article_html = """
    <article>
      <h1>批量标题</h1>
      <p>正文</p>
    </article>
    """

    def fetcher(url: str, headers: dict[str, str]) -> str:
        if "article" in url:
            return article_html
        return column_html

    results = export_batch_articles(
        column_url="https://time.geekbang.org/column/intro/123",
        session_token="token-1",
        output_dir=tmp_path / "out",
        images_dir=tmp_path / "out" / "assets",
        naming="id",
        fetcher=fetcher,
        downloader=lambda url: b"image",
    )

    assert len(results) == 2
    names = sorted(item.file_path.name for item in results)
    assert names == ["100.md", "101.md"]


def test_export_batch_articles_supports_start_index(tmp_path: Path) -> None:
    column_html = """
    <a href="/column/article/100">A</a>
    <a href="/column/article/101">B</a>
    <a href="/column/article/102">C</a>
    """
    article_html = """
    <article>
      <h1>批量标题</h1>
      <p>正文</p>
    </article>
    """

    def fetcher(url: str, headers: dict[str, str]) -> str:
        if "article" in url:
            return article_html
        return column_html

    results = export_batch_articles(
        column_url="https://time.geekbang.org/column/intro/123",
        session_token="token-1",
        output_dir=tmp_path / "out",
        images_dir=tmp_path / "out" / "assets",
        naming="id",
        fetcher=fetcher,
        downloader=lambda url: b"image",
        start_index=2,
    )

    assert len(results) == 2
    names = sorted(item.file_path.name for item in results)
    assert names == ["101.md", "102.md"]


def test_export_batch_articles_supports_start_article_id(tmp_path: Path) -> None:
    column_html = """
    <a href="/column/article/100">A</a>
    <a href="/column/article/101">B</a>
    <a href="/column/article/102">C</a>
    """
    article_html = """
    <article>
      <h1>批量标题</h1>
      <p>正文</p>
    </article>
    """

    def fetcher(url: str, headers: dict[str, str]) -> str:
        if "article" in url:
            return article_html
        return column_html

    results = export_batch_articles(
        column_url="https://time.geekbang.org/column/intro/123",
        session_token="token-1",
        output_dir=tmp_path / "out",
        images_dir=tmp_path / "out" / "assets",
        naming="id",
        fetcher=fetcher,
        downloader=lambda url: b"image",
        start_article_id="101",
    )

    assert len(results) == 2
    names = sorted(item.file_path.name for item in results)
    assert names == ["101.md", "102.md"]


def test_export_batch_articles_falls_back_to_column_api_when_catalog_has_no_links(
    tmp_path: Path,
) -> None:
    column_html = '<html><body><div id="app"></div><script src="/main.js"></script></body></html>'
    article_html = """
    <article>
      <h1>批量标题</h1>
      <p>正文</p>
    </article>
    """
    api_body = (
        '{"data":{"list":['
        '{"article_id":963262},'
        '{"article_id":963273}'
        ']}}'
    )

    seen_headers: dict[str, str] = {}

    def fetcher(url: str, headers: dict[str, str]) -> str:
        if "/serv/v1/column/articles" in url:
            seen_headers.update(headers)
            return api_body
        if "article" in url:
            return article_html
        return column_html

    results = export_batch_articles(
        column_url="https://time.geekbang.org/column/intro/101132501?tab=catalog",
        session_token="cookie:session_id=abc",
        output_dir=tmp_path / "out",
        images_dir=tmp_path / "out" / "assets",
        naming="id",
        fetcher=fetcher,
        downloader=lambda url: b"image",
    )

    assert len(results) == 2
    names = sorted(item.file_path.name for item in results)
    assert names == ["963262.md", "963273.md"]
    assert seen_headers.get("X-Requested-With") == "XMLHttpRequest"
    assert "Mozilla/5.0" in seen_headers.get("User-Agent", "")


def test_export_batch_articles_supports_api_payload_data_as_list(tmp_path: Path) -> None:
    column_html = '<html><body><div id="app"></div><script src="/main.js"></script></body></html>'
    article_html = """
    <article>
      <h1>批量标题</h1>
      <p>正文</p>
    </article>
    """
    api_body = '{"data":[{"article_id":963262},{"article_id":963273}]}'

    def fetcher(url: str, headers: dict[str, str]) -> str:
        if "/serv/v1/column/articles" in url:
            return api_body
        if "article" in url:
            return article_html
        return column_html

    results = export_batch_articles(
        column_url="https://time.geekbang.org/column/intro/101132501?tab=catalog",
        session_token="cookie:session_id=abc",
        output_dir=tmp_path / "out",
        images_dir=tmp_path / "out" / "assets",
        naming="id",
        fetcher=fetcher,
        downloader=lambda url: b"image",
    )

    assert len(results) == 2

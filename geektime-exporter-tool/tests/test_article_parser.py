from __future__ import annotations

import urllib.error

import pytest

from geektime_exporter.auth import SessionInvalidError
from geektime_exporter.article_parser import (
    CodeBlock,
    HeadingBlock,
    ListBlock,
    ParagraphBlock,
    QuoteBlock,
    discover_column_article_urls,
    fetch_article_page,
    parse_article_dom,
)


def test_discover_column_article_urls_deduplicates_and_normalizes() -> None:
    html = """
    <html>
      <body>
        <a href="/column/article/100">A</a>
        <a href="https://time.geekbang.org/column/article/101">B</a>
        <a href="/column/article/100">A2</a>
        <a href="/not-article/999">X</a>
      </body>
    </html>
    """

    urls = discover_column_article_urls(
        html=html,
        base_url="https://time.geekbang.org/column/abc",
    )

    assert urls == [
        "https://time.geekbang.org/column/article/100",
        "https://time.geekbang.org/column/article/101",
    ]


def test_parse_article_dom_preserves_block_semantics() -> None:
    html = """
    <html>
      <body>
        <article class="article-content">
          <h2>小节标题</h2>
          <p>第一段内容</p>
          <pre><code>print("hello")\nprint("world")</code></pre>
          <blockquote><p>引用文本</p></blockquote>
          <ul><li>条目一</li><li>条目二</li></ul>
        </article>
      </body>
    </html>
    """

    blocks = parse_article_dom(html)

    assert blocks == [
        HeadingBlock(level=2, text="小节标题"),
        ParagraphBlock(text="第一段内容"),
        CodeBlock(code='print("hello")\nprint("world")', language=None),
        QuoteBlock(text="引用文本"),
        ListBlock(ordered=False, items=["条目一", "条目二"]),
    ]


def test_fetch_article_page_uses_token_and_bubbles_network_error() -> None:
    called: dict[str, str] = {}

    def fake_fetcher(url: str, headers: dict[str, str]) -> str:
        called["url"] = url
        called["auth"] = headers["Authorization"]
        return "<html>ok</html>"

    body = fetch_article_page(
        article_url="https://time.geekbang.org/column/article/100",
        session_token="token-123",
        fetcher=fake_fetcher,
    )
    assert body == "<html>ok</html>"
    assert called == {
        "url": "https://time.geekbang.org/column/article/100",
        "auth": "Bearer token-123",
    }

    def bad_fetcher(url: str, headers: dict[str, str]) -> str:
        raise urllib.error.URLError("network down")

    with pytest.raises(urllib.error.URLError):
        fetch_article_page(
            article_url="https://time.geekbang.org/column/article/100",
            session_token="token-123",
            fetcher=bad_fetcher,
        )


def test_fetch_article_page_supports_cookie_session() -> None:
    called: dict[str, str] = {}

    def fake_fetcher(url: str, headers: dict[str, str]) -> str:
        called["url"] = url
        called["cookie"] = headers["Cookie"]
        return "<html>ok</html>"

    body = fetch_article_page(
        article_url="https://time.geekbang.org/column/article/100",
        session_token="cookie:session_id=abc; uid=1",
        fetcher=fake_fetcher,
    )

    assert body == "<html>ok</html>"
    assert called["cookie"] == "session_id=abc; uid=1"


@pytest.mark.parametrize("status_code", [401, 403, 451])
def test_fetch_article_page_auth_related_http_errors_raise_session_invalid(status_code: int) -> None:
    def unauthorized_fetcher(url: str, headers: dict[str, str]) -> str:
        raise urllib.error.HTTPError(
            url=url,
            code=status_code,
            msg="unauthorized",
            hdrs=None,
            fp=None,
        )

    with pytest.raises(SessionInvalidError):
        fetch_article_page(
            article_url="https://time.geekbang.org/column/article/100",
            session_token="token-123",
            fetcher=unauthorized_fetcher,
        )


def test_parse_article_dom_supports_slate_blocks() -> None:
    html = """
    <div id="app">
      <div data-slate-type="paragraph"><span>第一段正文</span></div>
      <h3 data-slate-type="heading"><span>小节标题</span></h3>
      <div data-slate-type="paragraph"><span>第二段正文</span></div>
      <div data-slate-type="list">
        <div data-slate-type="list-line"><span>条目A</span></div>
        <div data-slate-type="list-line"><span>条目B</span></div>
      </div>
      <ul><li>播放器菜单</li></ul>
    </div>
    """

    blocks = parse_article_dom(html)

    assert blocks == [
        ParagraphBlock(text="第一段正文"),
        HeadingBlock(level=3, text="小节标题"),
        ParagraphBlock(text="第二段正文"),
        ListBlock(ordered=False, items=["条目A", "条目B"]),
    ]

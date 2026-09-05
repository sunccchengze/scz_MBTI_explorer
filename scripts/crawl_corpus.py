#!/usr/bin/env python3
"""crawl_corpus.py — 网页抓取入库（crawl4ai 适配器）

用法：
    python3 scripts/crawl_corpus.py https://example.com [更多URL...]
    python3 scripts/crawl_corpus.py --file urls.txt          # 每行一个 URL，# 注释
    python3 scripts/crawl_corpus.py --http URL               # 无浏览器模式（httpx 直取静态页）
    python3 scripts/crawl_corpus.py --no-robots URL          # 关闭 robots.txt 检查（慎用）

行为（对齐 corpus/ 协议）：
    1. 快照写入 corpus/sources/crawled/YYYY-MM-DD-HHMM-<slug>.md（带来源头）；
    2. 只追加、不覆盖：文件名冲突时自动加 -2 / -3 后缀；
    3. 抓取账本追加到 corpus/sources/crawled/INBOX.md（含失败记录）；
    4. 抓到的网页 = 外部材料：入 profile/ 之前必须人工过目并登记 sources/SOURCES.md。

安装（首次）：
    pip install -U crawl4ai
    crawl4ai-setup        # 下载 Chromium；无浏览器环境用 --http

依赖：crawl4ai >= 0.7（0.9.x 验证通过）。--http 模式不需要浏览器。
"""

import argparse
import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTDIR = REPO_ROOT / "corpus" / "sources" / "crawled"

try:
    import crawl4ai
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
except ImportError:
    sys.stderr.write("缺少依赖：先运行 `pip install -U crawl4ai && crawl4ai-setup`\n")
    sys.exit(1)

try:
    from crawl4ai.__version__ import __version__ as CRAWL4AI_VERSION
except ImportError:  # 老版本兼容
    CRAWL4AI_VERSION = "未知"
    v = getattr(crawl4ai, "__version__", None)
    CRAWL4AI_VERSION = getattr(v, "__version__", str(v)) if v else "未知"


class PlainHttpStrategy:
    """无浏览器策略：httpx 直取，交给 crawl4ai 做 HTML→Markdown。

    crawl4ai 0.7+ 的 AsyncCrawlerStrategy 是 ABC（只有一个 crawl 抽象方法），
    直接 duck-typing 即可——这样环境里没装 Chromium 也能跑静态页。
    需要登录态/JS 渲染的页面请走浏览器模式（不加 --http）。
    """

    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 scz-crawl/1.0"
    )

    async def crawl(self, url, **kwargs):
        import httpx

        from crawl4ai.models import AsyncCrawlResponse

        # 本地文件/裸 HTML：离线测试与重抓存档用（file:///path/to/page.html 或 raw:<html>）
        if url.startswith("file://"):
            from pathlib import Path as _P
            html = _P(url[7:]).read_text(encoding="utf-8", errors="replace")
            return AsyncCrawlResponse(html=html, response_headers={}, status_code=200)
        if url.startswith(("raw://", "raw:")):
            html = url[6:] if url.startswith("raw://") else url[4:]
            return AsyncCrawlResponse(html=html, response_headers={}, status_code=200)

        async with httpx.AsyncClient(
            follow_redirects=True, timeout=30.0, headers={"User-Agent": self.USER_AGENT}
        ) as client:
            resp = await client.get(url)
        return AsyncCrawlResponse(
            html=resp.text,
            response_headers={k: v for k, v in resp.headers.items()},
            status_code=resp.status_code,
            redirected_url=str(resp.url) if resp.url != url else None,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None


def _slugify(url: str) -> str:
    p = urlparse(url)
    raw = f"{p.netloc}{p.path}".strip("/") or "root"
    raw = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "-", raw)
    return raw[:80].strip("-") or "root"


def _unique_path(base: Path) -> Path:
    """只追加不覆盖：存在就加 -2、-3 …"""
    if not base.exists():
        return base
    i = 2
    while True:
        cand = base.with_name(f"{base.stem}-{i}{base.suffix}")
        if not cand.exists():
            return cand
        i += 1


def _read_urls(args) -> list[str]:
    urls: list[str] = list(args.urls)
    if args.file:
        for line in Path(args.file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _inbox_header() -> str:
    return (
        "# 抓取入库 · INBOX\n\n"
        "> 抓取快照统一落 `corpus/sources/crawled/`，本文件是只追加的入库账本。\n"
        "> **这里的内容是「外部材料」：不构成证据。** 过目确认后才可被 `profile/` 引用，\n"
        "> 且引用前须在 `corpus/sources/SOURCES.md` 登记一行（来源/位置/提供了什么/授权状态）。\n\n"
        "| 日期 | URL | 结果 | 快照 | 标题 | 字数 |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
    )


def _inbox_append(inbox: Path, row: str) -> None:
    if not inbox.exists():
        inbox.write_text(_inbox_header(), encoding="utf-8")
    with inbox.open("a", encoding="utf-8") as f:
        f.write(row + "\n")


async def _crawl_one(crawler, url: str, outdir: Path, check_robots: bool, mode_label: str) -> tuple[str, str, str, str]:
    """返回 (结果, 快照相对路径, 标题, 字数)。"""
    cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        check_robots_txt=check_robots,
        page_timeout=30000,
        excluded_tags=["nav", "footer", "script", "style", "noscript", "iframe", "svg"],
    )
    try:
        result = await crawler.arun(url=url, config=cfg)
    except Exception as e:  # 网络/浏览器异常
        return "失败", "", "", f"异常：{type(e).__name__}: {e}"

    if not result.success or not result.html:
        err = (result.error_message or "未知错误")[:120]
        return "失败", "", "", f"HTTP {getattr(result, 'status_code', '?')} {err}"

    md_obj = getattr(result, "markdown", None)
    md_text = getattr(md_obj, "raw_markdown", "") if md_obj else ""
    if not md_text and isinstance(result.markdown, str):
        md_text = result.markdown
    meta = getattr(result, "metadata", None) or {}
    title = str(meta.get("title", "")).strip()[:120]

    now = datetime.now().astimezone()
    target = _unique_path(outdir / f"{now:%Y-%m-%d-%H%M}-{_slugify(url)}.md")
    header = (
        "---\n"
        f"来源: {url}\n"
        f"抓取时间: {now:%Y-%m-%d %H:%M %z}\n"
        f"HTTP 状态: {result.status_code}\n"
        f"引擎: crawl4ai {CRAWL4AI_VERSION}（{mode_label}）\n"
        f"标题: {title or '(未提取到)'}\n"
        "---\n\n"
    )
    target.write_text(header + md_text, encoding="utf-8")
    rel = target.relative_to(REPO_ROOT)
    words = len(re.sub(r"\s", "", md_text))
    return "成功", str(rel), title, f"{words} 字"


async def _run(urls: list[str], args) -> int:
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    inbox = outdir / "INBOX.md"

    mode_label = "无浏览器 http 模式" if args.http else "浏览器模式"
    if args.http:
        crawler = AsyncWebCrawler(crawler_strategy=PlainHttpStrategy())
    else:
        crawler = AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False))

    ok, failed = 0, 0
    entered = False
    try:
        try:
            await crawler.__aenter__()
            entered = True
        except Exception as e:
            sys.stderr.write(
                f"浏览器启动失败（{type(e).__name__}: {e}）\n"
                "→ 先运行 `crawl4ai-setup` 安装 Chromium；\n"
                "→ 或加 --http 用无浏览器模式抓静态页。\n"
            )
            sys.exit(2)
        for i, url in enumerate(urls):
            print(f"[{i + 1}/{len(urls)}] {url}")
            status, snap, title, info = await _crawl_one(
                crawler, url, outdir, check_robots=not args.no_robots, mode_label=mode_label
            )
            when = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")
            if status == "成功":
                ok += 1
                print(f"    ✅ {snap}（{info}）")
                _inbox_append(
                    inbox,
                    f"| {when} | {url} | ✅ 成功 | `{snap}` | {title or '—'} | {info} |",
                )
            else:
                failed += 1
                print(f"    ❌ {info}")
                _inbox_append(
                    inbox,
                    f"| {when} | {url} | ❌ 失败 | — | — | {info} |",
                )
            if i < len(urls) - 1 and args.delay > 0:
                await asyncio.sleep(args.delay)
    finally:
        if entered:
            await crawler.__aexit__(None, None, None)

    print(f"\n完成：成功 {ok} / 失败 {failed}；快照目录 {outdir.relative_to(REPO_ROOT)}")
    print("提醒：抓到的内容是「外部材料」，入 profile/ 前必须过目并登记 sources/SOURCES.md。")
    return 1 if failed and not ok else 0


def main() -> None:
    ap = argparse.ArgumentParser(description="网页抓取入库（crawl4ai 适配器，快照+INBOX 只追加）")
    ap.add_argument("urls", nargs="*", help="要抓的 URL（可多个）")
    ap.add_argument("--file", help="从文件读 URL（每行一个，# 注释）")
    ap.add_argument("--http", action="store_true", help="无浏览器模式（httpx 直取静态页，不需 crawl4ai-setup）")
    ap.add_argument("--no-robots", action="store_true", help="跳过 robots.txt 检查（默认遵守）")
    ap.add_argument("--delay", type=float, default=1.0, help="页面间隔秒数（默认 1.0，礼貌抓取）")
    ap.add_argument("--outdir", default=str(DEFAULT_OUTDIR), help="快照输出目录")
    args = ap.parse_args()

    urls = _read_urls(args)
    if not urls:
        ap.error("没有 URL：直接传参或用 --file")
    sys.exit(asyncio.run(_run(urls, args)))


if __name__ == "__main__":
    main()

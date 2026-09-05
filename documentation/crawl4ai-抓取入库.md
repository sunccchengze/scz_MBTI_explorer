# 网页抓取入库 · crawl4ai 适配

> 工具层（不是语料）：把网页抓成 Markdown 快照，进 INBOX 待审队列。
> 建立：2026-09-05（Arena 会话，主人问"这种爬虫该怎样才能为我所用"）· 验证基线 crawl4ai 0.9.3
> 协议锚点：抓到的网页 = **外部材料**，不构成证据；被 `profile/` 引用前必须人工过目并在 `corpus/sources/SOURCES.md` 登记一行。

## 为什么引入

语料目前靠「口述 + AI 整理」进一手材料，但网页类材料（MBTI 长文、公开讨论、本人公开发布页）没有稳定入口：
复制粘贴进对话会丢原始结构与时间戳，逐条贴聊天又不可持续。
crawl4ai（[unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)，⭐81k，开源）负责「取页面 → 干净 Markdown」这一公里，
本仓 `scripts/crawl_corpus.py` 负责「快照 + 待审台账」这一公里。

## 一次性安装（本人机器）

```bash
pip install -U crawl4ai
crawl4ai-setup        # 下载 Chromium（浏览器模式才需要）
crawl4ai-doctor       # 自检
```

## 日常用法

```bash
python3 scripts/crawl_corpus.py https://某个/长文          # 单页，浏览器模式（默认）
python3 scripts/crawl_corpus.py --file urls.txt           # 批量，每行一个 URL，# 注释
python3 scripts/crawl_corpus.py --http URL                # 无浏览器模式：静态页最快，免 setup
python3 scripts/crawl_corpus.py --http "file:///path/p.html"  # 离线测管道/重抓存档
```

产出行为：

- 快照：`corpus/sources/crawled/<时间戳>-<名>.md`，头部带 来源/抓取时间/HTTP 状态/引擎/标题；
- 台账：`corpus/sources/crawled/INBOX.md` 自动追加一行（**失败也记录**，不留空）；
- 只追加不覆盖（文件名撞车自动 `-2`/`-3` 后缀）；默认遵守 robots.txt；页间 1s 礼貌间隔（`--delay` 可调）。

## 抓完之后（必须）

1. 过一遍 INBOX，逐份看快照是不是目标内容（登录墙/反爬提示/重定向页 = 作废，在 INBOX 注明原因）；
2. 值得引用的材料 → 在 `sources/SOURCES.md` 登记一行（ID/来源/位置/提供了什么/授权状态），`profile/` 里引用时带 ID；
3. 「像本人但非本人」的内容（网站转述、AI 代笔的"孙承泽观点"）→ 按语料协议标【待确认】/〔推断〕，不当一手。

## 边界（诚实写）

| 场景 | 判断 | 处理 |
| --- | --- | --- |
| 静态文章/博客/GitHub 页 | ✅ | `--http` 即可，最快 |
| JS 渲染页（SPA） | ✅ | 浏览器模式（默认），需 `crawl4ai-setup` |
| 登录墙（微博/微信/小红书/知乎专栏等） | ⛔ 不稳定 | 不硬抓：手动导出或官方导出，导出文件直接进 `corpus/` |
| 强反爬（验证码/封号风险） | ⛔ | 立即停，不破解；INBOX 记失败 |
| 大规模抓取（几十上百页） | ⚠️ | 先确认对方 robots/ToS；快照过大不进 Git，移到外部存储 |
| 他人私密页面 | ⛔ 红线 | 不抓。关系分析只分析**对方主动给**的材料（corpus 隐私红线第 6 条） |

## 验证记录

- 2026-09-05（本 Arena 沙盒，crawl4ai 0.9.3）：离线路径 `file:// → HTML→Markdown → 快照落盘 → INBOX 追加（含撞车 -2 后缀）` ✅ 跑通；nav/footer 过滤 ✅。
- **未验证**：沙盒无法下载 Chromium、无直连外网，真实 https 抓取与浏览器模式未在沙盒端到端验证。本人机器首跑自检：
  `python3 scripts/crawl_corpus.py --http https://example.com`（报浏览器错就先跑 `crawl4ai-setup`）。
- 沙盒调过的坑（留痕）：0.9.x 无 `BrowserlessConfig`（自定义 strategy 走 `PlainHttpStrategy`）；`exclude_tags` 改名 `excluded_tags`；`AsyncCrawlResponse` 在 `crawl4ai.models`；`crawl4ai.__version__` 是模块要取 `.__version__`。

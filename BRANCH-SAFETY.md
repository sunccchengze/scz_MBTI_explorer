# 分支与推送手册（Arena Agent 生存手册 · 本仓版）

> 来源：`sunccchengze/SCZ_Archived` → `BRANCH-SAFETY.md`
> （原文摘自 `sunccchengze/turbine-blade-ai-platform` 的 `HANDOFF.md`，由本人与历代 agent 实战踩坑积累）
> 落地本仓：2026-09-03
>
> **动手前先读完这一页。**

---

## 一、⭐ 快进推送：把内容送上 main 而不碰 PR

### 一行命令

```bash
git push origin <你的分支>:main
```

就这一条。**不开 PR、不合 PR、不关 PR**，`main` 直接前进到你分支的位置。

### 为什么需要它

Arena 会在 PR **合并或关闭**的瞬间**关闭本会话的远程通道**，之后所有 `push` / `gh` 全部失败；
而此时**尚未推送的提交会永久丢失**。快进推送走的是纯 Git 协议（refspec `<src>:<dst>`），
GitHub 只是把 `main` 这个 ref 往前挪一格，**压根没有"PR 被合并/关闭"这个事件**，自然不触发关闭。

| | PR 合并 | 快进推送 |
| --- | --- | --- |
| `main` 拿到你的内容 | ✅ | ✅ |
| 触发 Arena 关闭远程通道 | 🩸 **会** | ✅ 不会 |
| 之后还能 push / gh | ❌ | ✅ 能 |
| 留下 PR 记录 / code review | ✅ | ❌ 没有 |
| 产生 merge commit | 会 | 不会（线性历史） |

### 完整流程（照抄即可）

```bash
# 0. 工作区干净、提交都已 commit
git status --short

# 1. 自检：main 必须是你分支的祖先，否则不能快进
git fetch origin main
git merge-base --is-ancestor origin/main HEAD \
  && echo "✅ FF 安全，可以推" \
  || echo "❌ main 有你没有的提交，先 rebase"

# 2. 先推自己的分支（保命：绝不攒提交）
git push origin <你的分支>

# 3. 快进推送到 main
git push origin <你的分支>:main

# 4. 核对：两个 ref 应指向同一个 commit
git ls-remote --heads origin | sed 's#refs/heads/##'
```

### 第 1 步说"需要先 rebase"时

说明 `main` 上有你分支没有的提交，快进不成立。**不要用 `-f` 强推**——会覆盖 `main` 上别人的工作：

```bash
git fetch origin main
git rebase origin/main          # 把你的提交挪到 main 之上
# 解决冲突后
git push origin <你的分支>       # 自己的分支可以 -f
git push origin <你的分支>:main  # 再快进
```

### 边界与代价（诚实说明）

- **没有 PR 记录、没有 code review。** 对只读归档仓、单人项目很合适；依赖评审的团队需自行权衡。
- **要求线性历史**：`main` 必须是你分支的祖先。
- **不适用于受保护分支**：若 `main` 开了 branch protection 要求 PR，这条推送会被拒绝。
- 本仓现状（2026-09-03 核对）：`main` **未开启分支保护**，且 `main` 与当前会话分支同指向 `62d7d71`，
  即 `git push origin arena/01a06527-scz-mbti-explorer:main` 当前**技术上成立**。

> ⚠️ **会话约束**：Arena 会话与 `arena/01a06527-scz-mbti-explorer` 绑定——本次会话的所有工作
> 只提交并推送到该分支。上面那行快进推送**需要你在本地或下一个会话里执行**，
> 由本会话代推到 `main` 会让工作脱离会话追踪。命令就在上面，复制即用。

---

## 二、五条铁律（HANDOFF 原文）

### 1. 推送优先于一切

每完成一个可交付单元，立刻 `commit` + `push`。**绝不攒提交。未推送的提交 = 不存在的提交。**

### 2. 🩸 绝不主动合并 PR

Arena 会在 PR **合并/关闭**后立刻关闭本会话的远程通道。

```bash
gh pr create ...   # ✅ 开 PR 没问题
gh pr merge  ...   # 🩸 关闭远程通道
gh pr close  ...   # 🩸 同样关闭远程通道
```

三个易错点：
- 触发条件是「合并**或关闭**」，不只是合并；
- **别用"分支还在不在"判断**——分支通常好端端在，通道照样已关；
- 通道一关，**尚未推送的提交就永久丢失**。

要继续干活就让 PR 开着；合并只能是会话的最后一个动作，或留给本人在 GitHub 网页点。

### 3. 推不上去时，立刻导 patch 存档，然后如实上报

```bash
git format-patch origin/main..HEAD -o /tmp/patches/
git bundle create /tmp/backup.bundle HEAD
```

不要静默跳过、不要假装成功。

### 4. 引用任何数字前先自己复现，不许照抄

答不出口径，比数字低一点致命得多（"训练集还是测试集""怎么复现"是最基本一问）。

### 5. 遇到权限／网络／环境问题，直接说，不要绕过去假装完成

---

## 三、其他通用坑

| # | 坑 | 应对 |
| --- | --- | --- |
| 1 | `node_modules` 等不跨会话持久 | 重要产物别只放 `dist/build/cache/__pycache__/.venv` 等被排除目录 |
| 2 | 会话权限不确定 | 开工先 `git ls-remote` 探一次 |
| 3 | GitHub 身份被 clone 带成仓库主人 | 先 `git config user.name/user.email` 再提交 |
| 4 | 聊天里贴 patch 会被改坏（空白/HTML 实体） | 用「整篇覆盖 + 模糊匹配脚本」恢复，别依赖 `git apply` |
| 5 | 沙盒有出口白名单 | GitHub/PyPI/npm 通，很多外部域名 TLS 直接失败 |
| 6 | 测连通性用 GET | `curl -o /dev/null -w "%{http_code}"`；`HEAD` 返回 exit 0 可能是**假阳性** |
| 7 | 附件上传可能不落盘 | 让用户直接粘贴内容 |
| 8 | 🩸 GitHub App 无 `workflows` 权限 | 推送含 `.github/workflows/*.yml` 的提交会被 GitHub 拒绝 |
| 9 | 🩸 推送前反复 TLS 报错 | 看似抖动，**其实是会话将关闭的前兆**；别机械重试超 2–3 次，立刻 commit + 尝试推送 |

---

## 四、本仓相关操作速查

```bash
python3 scripts/validate_skill.py        # 提交前必跑（含链接、占位符、Skill 预算、mbti 工具自检）
bash scripts/fetch_reference_repos.sh    # 重建被 gitignore 的三个大体积参考仓库
```

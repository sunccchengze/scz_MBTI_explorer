#!/usr/bin/env bash
# 重建 reference-repos/ 下的外部参考仓库。
#
# 三个体积较大的仓库（ACGTI / Machine-Mindset / evolving_personality）
# 不进 Git（见 .gitignore），用本脚本按固定 commit 复现，保证任何人
# 拉下来的内容与本仓 reference-repos/REFERENCE-INDEX.md 描述一致。
#
# 用法：
#   bash scripts/fetch_reference_repos.sh          # 只补齐缺失的大仓
#   bash scripts/fetch_reference_repos.sh --all    # 全部重拉（会删除已有目录）

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/reference-repos"

# slug|commit|:sparse 规格（commit 为 2026-09-03 抓取时锁定的 HEAD）
REPOS=(
  "tianxingleo/ACGTI|298910de5992d64cfe95beae4af122e0226d2111|src public data docs"
  "PKU-YuanGroup/Machine-Mindset|5ee14c144fc59579a6c77e553acb2b6b56a54d7d|"
  "agent-topia/evolving_personality|517e357da483462a21a2a22cdcdccc0d110c55d4|"
)

ALL=0
[ "${1:-}" = "--all" ] && ALL=1

mkdir -p "$DEST"

for entry in "${REPOS[@]}"; do
  IFS='|' read -r slug commit sparse <<<"$entry"
  name="${slug##*/}"
  target="$DEST/$name"

  if [ -d "$target" ] && [ "$ALL" -eq 0 ]; then
    echo "skip  $name (已存在；用 --all 强制重拉)"
    continue
  fi

  rm -rf "$target"
  echo "fetch $name @ ${commit:0:8}"

  if [ -n "${sparse:-}" ]; then
    git clone --depth 1 --filter=blob:none --sparse \
      "https://github.com/${slug}.git" "$target" >/dev/null
    ( cd "$target" && git sparse-checkout set $sparse >/dev/null )
  else
    git clone --depth 1 "https://github.com/${slug}.git" "$target" >/dev/null
  fi

  ( cd "$target" && git checkout --quiet "$commit" ) 2>/dev/null \
    || echo "  warn: 无法切到 $commit（可能已被 force-push），保留默认分支 HEAD"

  # 裁剪体积：去掉历史与超大素材，只留可读的参考内容
  rm -rf "$target/.git"
  rm -rf "$target/public/images" 2>/dev/null || true
  find "$target" -type d -name node_modules -prune -exec rm -rf {} + 2>/dev/null || true
  find "$target" -type f -size +3M -delete 2>/dev/null || true

  echo "  done $name ($(du -sh "$target" | cut -f1))"
done

echo
echo "完成。索引说明见 reference-repos/REFERENCE-INDEX.md"

# S1 交接 · 去 turbine 仓跑「基准题库第一批」

> **给**：下一场 `sunccchengze/turbine-blade-ai-platform` 的 Arena 会话（本仓 **不改** turbine）。
> **来源**：`-SKILL-/四个月脚印计划-2026Sep-Dec.md` §2 S1；数字全部来自 turbine `evidence/`（2026-09-03 用 gh 拉过原文）。
> **时限**：≤3 小时。上一步没 commit 不开始下一步。
> **本文件建立**：2026-09-03 · MBTI 会话因监护 #6 把人推回主线。

## 0. 你是第几任

turbine HANDOFF 已到 v8。开工先读：`docs/BRANCH-SAFETY.md` → `HANDOFF.md` 十一条铁律 → `evidence/metrics.json` + `evidence/claims.yaml`。**引用数字前自己打开文件，不许信本交接里的抄写。**

## 1. S1 规格（原计划原文压缩）

- 在 turbine **会话分支**建 `bench/`（不要先碰 PR、不要合 PR）。
- 产出：`bench/v0-q1-20.json`
- 判据：20 题、每题**唯一**正确答案、每题能翻到出处（文件路径 + 字段/小节）。
- 计划举例要用论文页码。本交接 **v0 先用 `evidence/` 已冻结数字**（E2/E1/E3 已核）。论文页码题（SMO 2018/2021、KT-EGO、TNO）标为 Q21+ 槽位，**S1 三小时内若 PDF 不在工作区，不要编页码**——编了就违反铁律 4。

## 2. 建议 JSON schema

```json
{
  "schema": "turbine-bench/v0",
  "created": "YYYY-MM-DD",
  "rule": "答案必须能在 source.path 原文复现；禁止把 E2 写成 E4",
  "items": [
    {
      "id": "Q01",
      "question": "",
      "answer": "",
      "source": { "path": "evidence/metrics.json", "pointer": "split.n_test" },
      "grade": "E2"
    }
  ]
}
```

## 3. 已核 20 题草稿（落地前必须对照仓库原文）

完整草稿见同目录 `S1-v0-q1-20.draft.json`。摘要：

| ID | 题干要点 | 唯一答案 | 出处 |
| --- | --- | --- | --- |
| Q01 | 工程 holdout 测试集 n、seed | n=100, seed=42 | metrics.split |
| Q02 | 残差 ONNX 三通道 R² | 0.9844 / 0.9561 / 0.9827（压比/效率/流量） | surrogate_holdout.r2 |
| Q03 | 基线 MLP 效率 R² | 0.9132 | baseline_mlp_holdout |
| Q04 | 训练/验证/测试划分 | 800 / 100 / 100 | split |
| Q05 | η 上 MC Dropout 经验覆盖率 | 0.65 | empirical_coverage.Efficiency |
| Q06 | 压比 / 流量经验覆盖率 | 0.89 / 0.88 | 同上 |
| Q07 | η 的 mean_sigma | 0.0010 | mean_sigma.Efficiency |
| Q08 | 代理 Pareto 最高效率 | 0.9173097（对外约 0.9173） | nsga2_surrogate.max_eta |
| Q09 | 相对训练均值 Δη | 0.054（约 +5.4%，**对外不报**） | delta_eta_vs_train_mean |
| Q10 | 最大流量代理点 | 21.7379 kg/s | max_massflow |
| Q11 | NSGA-II 约束 | pi_min=1.8, eta_min=0.84 | constraints |
| Q12 | NSGA-II pop / ngen / seed | 100 / 200 / 42 | nsga2_surrogate |
| Q13 | SU2 粗网格 | 14 万格、relrms≈−3.39、未收敛 | su2_coarse |
| Q14 | 74 维是什么 | 表面统计量，不是可设计几何 | C06 |
| Q15 | 三个输出能否称 MDO | 不能，全是气动标量 | C07 |
| Q16 | C08（排序与 CFD 一致）状态 | empty，decision_metrics 全 null | claims C08 |
| Q17 | 禁止对外的短语举两例 | 「校准的 95% 置信区间」「可制造的 Pareto 最优叶片」 | claims.forbidden_phrases |
| Q18 | 名义 95% 带能否当校准 CI | 不能 | mc_dropout_heuristic.nominal |
| Q19 | TNO（郭 2025 CJA）先报什么再报性能 | 先报 T, p, ρ 场 | docs/guo-line §1（二次来源，S1 后补论文页） |
| Q20 | 和他路线能接上的接口 | 加点 infill（覆盖率 65% 当传感器） | guo-line §2–3 |

## 4. 三小时停点

1. 对照 `metrics.json` 逐题复现，改掉任何抄写误差。
2. `git add bench/ && commit && push` **会话分支**。
3. **不要**开/合 PR；上 main 用快进且须本人点头。
4. 收工写一行：S1 ☐ 20 题唯一答案 ☐ 出处可翻。然后停。S2 是裸答，本会话不做。

## 5. 明确不做

- 不编 SMO/KT-EGO 论文页码；
- 不把 5.4%、0.9173 写成 CFD 验证；
- 不在本 MBTI 仓提交 turbine 的 `bench/`（会脏错仓库）。

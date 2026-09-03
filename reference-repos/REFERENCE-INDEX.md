# 外部参考仓库索引（MBTI / 人格分析）

> 用途：给「scz_MBTI_explorer」从恋爱军师转型为**孙承泽专属 MBTI 探索者**提供参考与辅助材料。
> 本目录是**只读参考区**，不属于可分发的 Skill 运行时内容（`scripts/validate_skill.py` 已跳过校验）。
> 建立日期：2026-09-03 · 抓取方式：GitHub 搜索（star 排序）+ 浅克隆（去掉各自 `.git`）。

## 一、总表

| # | 仓库 | Star | 许可证 | 本仓用途 | 参考方式 |
| --- | --- | --- | --- | --- | --- |
| 1 | [shengjidaguai-china/goutoujunshi](https://github.com/shengjidaguai-china/goutoujunshi) | ⭐2736 | MIT | **本仓内容的真实上游**。用于 diff：看我们改了什么、丢掉了什么 | 可复用（MIT，且本仓就是其衍生品） |
| 2 | [agent-topia/evolving_personality](https://github.com/agent-topia/evolving_personality) | ⭐1146 | ⚠️ 未检测到 | Jung 八功能 → LLM Agent 动态人格（JPAF）：主辅协调、强化—补偿、反思三机制；含 93 题测评与人格演化实验 | **仅作公开事实观察，不复制内容**（无许可证） |
| 3 | [tianxingleo/ACGTI](https://github.com/tianxingleo/ACGTI) | ⭐1058 | Apache-2.0 | MBTI 化「二次元人格原型」测评站点：情境式题目设计、计分与结果页、前端工程范式 | 可借鉴题目措辞与结果呈现（Apache-2.0，需保留版权与 NOTICE） |
| 4 | [wordware-ai/twitter](https://github.com/wordware-ai/twitter) | ⭐1448 | ⚠️ 未检测到 | 从公开文本生成人格档案的 Agent 产品：抓取 → 结构化 prompt → 流式出报告 → OG 图分享 | **仅作公开事实观察，不复制内容**（无许可证） |
| 5 | [notdog1998/yourself-skill](https://github.com/notdog1998/yourself-skill) | ⭐3351 | MIT | 「与其蒸馏别人，不如蒸馏自己」：Self Memory + Persona 双件套，把自己的语料蒸馏成 Skill | 可复用（MIT）——**语料库工程范式直接对标 `corpus/`** |
| 6 | [therealXiaomanChu/ex-skill](https://github.com/therealXiaomanChu/ex-skill) | ⭐6186 | MIT | 把某个人的聊天记录 + 主观描述蒸馏成「像 ta 的 Skill」：原料 → 抽取 → persona → 校验 | 可复用（MIT）——抽取/校验流水线参考 |
| 7 | [PKU-YuanGroup/Machine-Mindset](https://github.com/PKU-YuanGroup/Machine-Mindset) | ⭐542 | Apache-2.0 | 《Machine Mindset: An MBTI Exploration of LLMs》：8 个 MBTI 维度各 60 条中英行为题 + 诱导方法 | 可复用（Apache-2.0）——**四维行为题库是最硬的题源** |

> 1–5 为「star > 1k」主线要求；6、7 为补充（6 是同族最高星的蒸馏工程范式，7 是本仓可直接引用题库的学术来源）。
> 三个大体积仓库（ACGTI / Machine-Mindset / evolving_personality）已在 `.gitignore` 中排除，用 `scripts/fetch_reference_repos.sh` 按需重建。

## 二、逐个说明与「能借什么」

### 1. goutoujunshi · 本仓的上游（⭐2736 · MIT）

**为什么放它**：本仓 71 个文件里有 67 个与它逐一同名，SKILL.md 的 `name: goutoujunshi`、README 的「狗头军师」、CONTRIBUTING 的贡献标准全部原样保留。它是「内容和仓库名不对应」的**物证**。

**diff 结论**（2026-09-03，上游 `6c32b8d` vs 本仓 `62d7d71`）：

- 本仓**独有** 3 份内容：`documentation/mbti-skill-research.md`、`references/practical/MBTI类型访谈与相邻类型辨析.md`、`references/practical/MBTI沟通适配与成长训练.md`、`scripts/mbti_case.py`——即「MBTI 增强包」；
- 其余文件（README / SKILL / 20 份 knowledge / 22 份 practical）与上游仅个别字句差异，**主题仍是恋爱军师**。

**能借**：上游后续版本的 MBTI 迭代（若上游更新）；更重要的是——**明确知道哪些是别人的、哪些是我们加的**，避免二次搬运时把恋爱话术又搬回来。

### 2. evolving_personality · JPAF（⭐1146 · ⚠️ 无许可证）

Jung 八功能驱动的 Agent 人格框架，三机制：主辅功能协调、强化—补偿、反思演化；论文 arXiv:2601.10025；含 `Personality_test/`（测评驱动）与 `Personality_changes/`（人格演化实验）。

**能借（只借思路，不复制代码/文本）**：
- 「人格随交互演化」的建模方式 → 可映射到本仓 `corpus/memory/MEMORY.md` 的活记忆机制；
- 93 题测评的**组织方式**（按维度分组、多轮取稳定值）。

**不能借**：仓库未声明许可证，按 `documentation/mbti-skill-research.md` 既有规则，只做公开事实观察。

### 3. ACGTI（⭐1058 · Apache-2.0）

MBTI 化的二次元角色原型测评：情境式题目 → 角色代码 → 原型结果页。含题目数据、计分逻辑、结果组件、测试。

**能借**：
- **情境式题干写法**（把抽象维度写成一个具体场景），比「你是否喜欢社交」信息量高一个量级；
- 结果页的信息架构（主型 + 分项 + 相邻型 + 反例）。

**注意**：Apache-2.0 要求保留 NOTICE 与版权声明；本仓仅借鉴写法，不整段搬运。

### 4. wordware-ai/twitter（⭐1448 · ⚠️ 无许可证）

从 X 账号公开帖子生成人格档案的完整产品链路：取数 → 结构化 prompt → LLM 流式出报告（roast / strengths / love life / spirit animal…）→ 缓存 → OG 分享图。

**能借（只借产品思路）**：
- 「一段公开文本 → 一份可分享的人格档案」的**输出契约**（固定章节 + 可缓存 + 可分享）；
- 报告里 roast 与 strengths 并置的语气设计。

**红线**：本仓原则明确「不默认扫描社交媒体给第三方建立心理档案」。这里只借输出形式，**不借其抓取第三方数据的做法**——我们的语料只能来自**孙承泽本人授权提供的一手材料**。

### 5. yourself-skill（⭐3351 · MIT）

「自己.skill」——把本人的聊天记录、日记、自我描述解构为 **Part A Self Memory + Part B Persona**，生成能用本人口头禅思考的数字副本。

**能借（直接对标）**：
- **Self Memory / Persona 二分** → 本仓 `corpus/memory/`（活记忆）与 `corpus/profile/`（人格档案）就是同一套切分；
- 语料目录约定、增量更新流程、隐私红线声明。

**为什么重要**：它是「把语料库做成可持续维护的工程」的现成范式，而不是一次性 prompt。

### 6. ex-skill（⭐6186 · MIT）

把某个人的聊天记录 + 主观描述蒸馏成「像 ta 的 Skill」，含 `docs/`、`prompts/`、`tools/` 三段式流水线。

**能借**：
- **原料 → 抽取 → persona → 校验** 的四阶段流水线（本仓 `corpus/` 的更新协议沿用此结构）；
- 抽取阶段对「口头禅 / 高频句式 / 情绪反应模式」的分类维度。

### 7. Machine-Mindset（⭐542 · Apache-2.0）

北大 Yuan Group 的 MBTI × LLM 研究。仓库内 `datasets/behaviour/zh/` 提供 **8 个维度（EI / SN / TF / JP 各两极）各一批中文行为题**，`datasets/self_awareness/` 提供自我意识题，`cli_inference.py` / `generate_mbti_res_images.py` 是评测与可视化脚本。

**能借（最硬的一项）**：现成的**中文行为题库**，可直接作为 `corpus/profile/01-MBTI证据账本.md` 后续自适应访谈的题源补充（需注明来源 Apache-2.0）。

> 已裁剪：`datasets/dpo/`、`images/`、`datasets/behaviour/en/` 为控制体积移除；`datasets/behaviour/zh/`（28 MB，8 个 json）随脚本完整重建。

## 三、使用边界（照抄本仓既有原则）

1. **不复制无许可证仓库的内容**（#2、#4 只做事实观察）。
2. **不把外部启发式数字当心理测量值**（沿用 `mbti-skill-research.md`：不产出未校准的功能百分比/匹配率/贝叶斯置信度）。
3. **不扫描第三方社交账号建立人格档案**（#4 的反模式）。
4. **直接移植代码或大段表达时**，必须补许可证全文与版权声明，不能只留链接。

## 四、体积与复现

- 随 Git 提交（纯文本、体积小）：`goutoujunshi/`、`yourself-skill/`、`ex-skill/`、`twitter/`
- 走脚本重建（体积大）：`ACGTI/`、`Machine-Mindset/`、`evolving_personality/`

```bash
bash scripts/fetch_reference_repos.sh          # 补齐三个大仓（锁定 commit，见脚本内 PINNED）
bash scripts/fetch_reference_repos.sh --all    # 全部重拉
```

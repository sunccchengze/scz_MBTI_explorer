# GitHub MBTI Agent Skills 调研与整合决策

- 调研日期：2026-08-11
- 目标：增强本项目的MBTI类型访谈、相邻类型辨析、沟通适配、成长训练与多视角分析能力（调研时项目名为「狗头军师」，现已正名为「MBTI 探索者」）
- 方法：GitHub仓库搜索、`SKILL.md`代码搜索、许可证检查、原始文件审阅及可用脚本自检

## 评估标准

1. **方法质量**：是否区分观察、解释和结论；是否有候选、反证、替代解释与不确定性。
2. **科学边界**：是否区分MBTI、认知功能、Big Five、A/T、依恋与临床诊断。
3. **实用性**：能否产生访谈问题、关系沟通、成长练习或可审计报告。
4. **安全与隐私**：是否避免第三方读心、高风险筛选和无授权人格画像。
5. **工程质量**：是否采用渐进加载、结构化状态、验证器和回归样例。
6. **许可证**：没有明确许可证的仓库只作公开事实观察，不复制内容。

## 候选项目

| 项目 | 审阅提交 | 许可证 | 主要价值 | 风险与决定 |
| --- | --- | --- | --- | --- |
| [Zaoqu-Liu/mbti-typing-skill](https://github.com/Zaoqu-Liu/mbti-typing-skill) | `995e241` | MIT | 证据账本、候选集、相邻类型对决、反证、Big Five校验、质量门槛、结构化会话和回归样例 | **首选方法源**。本地运行其skill scorecard为35/35，16个基准案例与golden regression通过。吸收方法，不照搬启发式贝叶斯数字为心理测量值。 |
| [ChangyuanYU/mbti-expert-skill](https://github.com/ChangyuanYU/mbti-expert-skill) | `8a5837a` | MIT | 多来源输入、充分性门槛、自适应追问、证据抽取和候选报告 | **选择性吸收**。自然追问和材料路由有价值；原方案的维度百分比、从照片审美或元数据推功能容易制造假精确与刻板推断，因此不采用。 |
| [ChangyuanYU/mbti-persona-skill](https://github.com/ChangyuanYU/mbti-persona-skill) | `8d3ca3d` | MIT | 八功能、功能轴、16类persona、基线／压力／恢复状态层 | **选择性吸收**。只用于用户明确要求的认知视角模拟，不把persona当真实群体规律，也不长期把代理固定为某类型。 |
| [share-skills/pi](https://github.com/share-skills/pi) | `eafbd6d` | Apache-2.0 | 把Ni/Ne/Te/Ti/Fe/Fi/Se/Si翻译为收敛、发散、执行、校验、共情、价值护栏、现场感知和经验检索等AI处理模式 | **吸收抽象方式**。用于能力训练和多视角审查，不宣称AI或用户因此拥有固定MBTI。 |
| [gaebalai/MBTI-16types](https://github.com/gaebalai/MBTI-16types) | `281ccac` | MIT | 单类型、双类型辩论和多类型面板的结构化工作流 | **选择性吸收**。保留“独立产出→相互反驳→中立综合”，但不机械生成16个刻板声音。 |
| [leilei926524-tech/samantha](https://github.com/leilei926524-tech/samantha) 的 `mbti-coach` | `56b4987` | MIT | 将功能偏好翻译成日常练习与进度复盘 | **只吸收训练理念**。拒绝“做练习给功能分数加点”、五题精确校准和把压力反应当真相验证；成长定义为扩展能力而非换类型。 |
| [smixs/osint-skill](https://github.com/smixs/osint-skill) | `94f382e` | MIT | 来源分级、行为证据、置信度提示 | **不并入人格画像流程**。以发帖频率、emoji、职业轨迹推MBTI/Big Five的效度不足，且针对第三方的OSINT心理画像存在隐私和误用风险。只保留“每个结论需证据、来源有等级”的一般原则。 |
| [infometa/workbuddyskills](https://github.com/infometa/workbuddyskills) 的 `agent-mbti` | `2bd6db6` | 未检测到仓库许可证 | 对AI Agent自身行为做26题偏好诊断并比较用户期待 | **不复制**。与“培养代理风格”相关，但无明确许可证；固定问卷也容易把宿主约束误写成稳定人格。 |
| [Fechin/sbti-now-skill](https://github.com/Fechin/sbti-now-skill) | `1127f0b` | 未检测到仓库许可证 | 自包含问卷、确定性本地计分和多语言运行 | **不采用内容**。SBTI明确是娱乐型互联网人格测试，不是MBTI严肃能力；工程上的自包含设计可作为一般参考。 |
| [Epsilondelta-ai/claw-mbti](https://github.com/Epsilondelta-ai/claw-mbti) | `f52aa76` | 未检测到仓库许可证 | 给AI Agent做60题人格测试及结果可视化 | **不复制**。偏娱乐、对象是AI代理，且缺少明确许可证。 |
| [YouMind-OpenLab/abti](https://github.com/YouMind-OpenLab/abti) | `35a8964` | CC-BY-NC-SA-4.0 | 依据聊天记忆生成28类AI人格结果 | **不采用内容**。娱乐和“roast”定位与严肃MBTI类型访谈不同，ShareAlike义务也不适合混入当前整体许可证。 |

## 最终整合策略

不把外部项目原样塞进根目录，而是按现有单Skill架构重新组织：

1. 扩充 `references/knowledge/04-MBTI人格与匹配.md`：四维、八功能、十六栈、Big Five、关系匹配和科学边界。
2. 新增 `references/practical/MBTI类型访谈与相邻类型辨析.md`：模式选择、材料门槛、候选集、证据账本、自适应访谈、15组常见相邻类型对决、报告契约与质量门槛。
3. 新增 `references/practical/MBTI沟通适配与成长训练.md`：偏好翻译、八功能沟通入口、关系场景、非量化训练和多类型视角模拟。
4. 新增 `scripts/mbti_case.py`：只管理结构化案例和报告审计，不计算“官方类型”或伪造功能分数。
5. 在根 `SKILL.md` 增加渐进路由：严肃定型读取知识入口+访谈指南；沟通与成长读取知识入口+适配指南。
6. 保留“行为证据优先”和“关系安全、互惠、同意优先于MBTI匹配”的原有内核。

## 明确不做

- 不从姓名、脸、照片审美、emoji、星座或职业直接推断类型。
- 不默认扫描社交媒体给第三方建立心理档案。
- 不把自定义问题的结果说成官方MBTI分数。
- 不给未经量表校准的功能百分比、匹配率或贝叶斯置信概率。
- 不用MBTI做招聘、升学、医疗、司法或关系淘汰的单一依据。
- 不把A/T当成官方MBTI第五维。
- 不声称某类型必然忠诚、聪明、成熟、会出轨或适合某类型。

## 归属说明

本次整合以重新组织和中文原创表述为主。方法设计受到上表所列MIT及Apache-2.0项目启发；学术性结论以知识文档列出的官方资料、独立研究与心理测量文献为依据。后续如直接移植外部源代码或大段表达，必须在仓库增加对应许可证全文与版权声明，而不能只保留本调研链接。

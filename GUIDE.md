# 考试系统与 Agent Skill 完整使用指南 (Exam Forge Usage Guide)

本指南指导学生、教师及 AI Agent 如何使用 `exam-practice-builder` 技能，将零散的考资转化为高仿真、可追踪、多主题、支持公式与编程题的**双语自适应备考网站**。

---

## 核心设计哲学：两大支柱 (Core Design Philosophy)

`exam_forge` 的本质价值并非简单的“题库展示网页”，而是解决备考中最重要的两个核心痛点：

### 支柱一：找准题目 / 按照大纲生成合适的题目（“准”与“严”）
- **考纲蓝图深度对齐 (Domain Weights Mapping)**：优先基于官方考纲（如 College Board CED、DECA Guide、AWS Exam Blueprint），提取官方各章节考点权重（如 Domain A: 30%, Domain B: 40%），严格按真实比例生成题目，杜绝偏科与盲目出题。
- **知识点颗粒度防同质 (`concept_id` 机制)**：杜绝机械套用模板换数字的“虚假题量”。每道题绑定独立的 `concept_id`，严格审计独立考点数与变式题比例，确保考点覆盖真实全面。
- **高信度干扰项与评分要点 (Distractor Rigor & Rubrics)**：
  - **客观题**：每个错误选项必须有明确的认知陷阱剖析（`why_wrong_en/zh`，如公式混淆、单位遗漏、概念偷换），让做错题目具有极高复盘价值。
  - **问答题/主观题**：必须配齐核心踩分点（`rubric`）和详尽参考答案，为自评与对照提供精确标尺。
- **认知层级递进 (Bloom's Taxonomy)**：严格按照认知层次分级（L1 基础概念记忆、L2 综合计算与应用、L3 陷阱辨析与高阶推理），保障试题信度与梯度。

### 支柱二：循序渐进、高效的复习改进方法（“效”与“闭环”）
- **五阶渐进式能力跃迁 (5-Stage Progressive Roadmap)**：
  1. **阶段 1：摸底诊断 (Diagnostic)** — 跨模块分层抽样，快速测出能力基线与薄弱板块，避免盲目刷题。
  2. **阶段 2：专题精练 (Topic Drilling)** — 按诊断结果对弱项模块专项攻坚，每题即时双语全解析吃透原理。
  3. **阶段 3：错题消灭 (Mistake Elimination)** — 错题动态池管理，做对移出、做错复现，直击高频盲区。
  4. **阶段 4：全真模考 (Timed Realistic Mock)** — 仿真官方时间限制与合格线（Passing Benchmark），训练配速与抗压。
  5. **阶段 5：自适应冲刺 (Adaptive Sprint)** — 算法动态组合最佳提分卷（60% 薄弱章节 + 25% 未做新题 + 15% 记忆保持）。
- **零摩擦与离线闭环 (Zero-Friction Offline Loop)**：单文件 HTML 纯离线运行，作答记录本地持久化并防意外刷新，随时导出/导入成绩，构建极简高效的备考复盘闭环。

---

## 零、 交互式需求前置调研问卷 (Intake Survey & One-Click Skip)

为了确保生成的练习系统与用户备考目标精准对齐，每次调用 `exam-practice-builder` 时，Agent **必须首先发起一个交互式问卷（Intake Survey）**。

> **💡 自由跳过机制 (One-Click Skip & Skip Remaining)**：
> - **完全跳过**：用户可直接点击界面的 **「Skip / 跳过」** 按钮或回复 *“让 AI 决定”*，由 AI 全程自主决策。
> - **主题给出后跳过剩余所有问题**：一旦明确了考试主题（例如用户输入 *“AP Physics”* 或 *“AMC 10”*），用户可以只填关心的某 1 项（如指定“只要 50 题”），并直接选择 **“跳过剩余所有问题 (Skip all remaining questions)”**。所有未填项均自动由 AI 联网检索官方考纲标准完成智能兜底配置。

### 问卷核心 4 题架构：
1. **题库来源 (Source Mode)**
   - `(推荐) 模式 B：零题库自主检索` — AI 联网抓取官方考纲，原创同构 scenario 试题。
   - `模式 A：已有材料导入` — 用户上传 PDF / 样卷 / 大纲文件。
2. **目标题目容量 (Target Bank Size)**
   - `(推荐) 标准全真模考样卷 (20–25 题)`
   - `完整大考标准卷 (40–50 题)`
   - `深度综合冲刺大题库 (80–100+ 题)`
   - `自定义题量：指定具体数字（如 15、30、60、120 题等）`
3. **考试时限与及格基准线 (Exam Rules)**
   - `(推荐) 官方规则自适应` — AI 自动探测官方时长与及格线。
   - `自定义时长与达标线` — 如 60 分钟 / 75% 及格。
   - `纯练习模式` — 不设时限，不设及格线。
4. **语言与题型偏好 (Language & Types)**
   - `(推荐) 中英双语完整对称` + 自动渲染 LaTeX 数学公式 / 代码块。
   - `纯英文 (English Only)`
   - `纯中文`

---

## 一、 考试配置档案 (Exam Profile)

在制作题库前，首先定义考试的基本属性与合格指标。可创建 `exam_profile.json`（参考 `examples/exam_profile.json`），包含以下关键字段：

```json
{
  "exam_name": "Innovation & Quantitative Competency Practice",
  "exam_code": "IQCP",
  "exam_category": "Business, Quantitative & Technology",
  "description": "自适应评测系统，考察量化财务分析、商业假设验证、单位经济学与算法逻辑。",
  "official_url": "https://example.org/exam-blueprint",
  "passing_score_pct": 75,
  "exam_duration_mins": 60,
  "mock_questions_count": 20,
  "target_bank_size": 100,
  "target_mock_tests": 5,
  "logo_monogram": "IQCP",
  "theme_default": "cyber",
  "verified_rules": false
}
```

### 字段说明
| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `exam_name` | String | 考试官方全称（中英文皆可） | `"AP Computer Science A"` |
| `exam_code` | String | 考试缩写或代号 | `"AP-CSA"` |
| `exam_category` | String | 学科或门类分类 | `"Computer Science"` |
| `description` | String | 考试背景与考察能力简述 | `"AP 大学先修计算机科学 A 模拟冲刺"` |
| `official_url` | String | 官方大纲/考纲网站链接 | `"https://apcentral.collegeboard.org/..."` |
| `passing_score_pct` | Number | 达标/及格百分比（0-100） | `75` (即 75% 判定合格) |
| `exam_duration_mins` | Number | 正式考试时长（分钟） | `90` |
| `mock_questions_count` | Number | 真实单套卷总题量 | `40` |
| `target_bank_size` | Number | 题库规划独立概念/题目总量 | `300` |
| `target_mock_tests` | Number | 推荐生成的自适应模考套数 | `8` |
| `logo_monogram` | String | 动态 LOGO 徽标中心字母/缩写 | `"CSA"` 或 `"DECA"` |
| `theme_default` | String | 默认配色主题 (`cyber`, `light`, `navy`, `forest`) | `"cyber"` |

---

## 二、 循序渐进的五阶学习进阶体系 (5-Stage Mastery Journey)

备考不能仅停留在“盲目做整套模考”，而应当通过结构化阶梯稳步提升：

```
[阶段 1: 摸底诊断] ──► [阶段 2: 专题精练] ──► [阶段 3: 错题消灭] ──► [阶段 4: 全真模考] ──► [阶段 5: 冲刺认证]
 (20-30题抽样)         (分模块各个击破)       (贝叶斯加权清零)       (限时限分仿真)        (达标发证冲刺)
```

1. **阶段 1：摸底诊断 (Diagnostic Baseline)**
   - **目标**：不限时抽取 20–30 道覆盖全模块的典型题。
   - **产出**：测出初始正确率与各知识模块长短板分布，建立基线。
2. **阶段 2：专题精讲突破 (Topic Competency Drill)**
   - **目标**：针对单一薄弱 Topic（例如：财务分析、递归树遍历），开展集中专项刷题。
   - **产出**：通过双语题干、选项反思解析（`why_wrong`）吃透核心概念。
3. **阶段 3：错题靶向清零 (Targeted Mistake Killer)**
   - **目标**：系统记录历史错题与低掌握度题目，采用贝叶斯平滑公式优先推送高频失分题。
   - **产出**：反复辨析易混淆选项，直到错题本完全清空。
4. **阶段 4：全真仿真模考 (Real-world Timed Simulation)**
   - **目标**：完全按照官方考试时间（倒计时）与真实题目数（如 70 分钟 100 题）进行闭卷压力测试。
   - **产出**：输出正式成绩单，对比 `passing_score_pct` 给出“合格 (Passed)”或“未达标 (Try Again)”判定。
5. **阶段 5：考前自适应冲刺 (Adaptive Sprint to Success)**
   - **目标**：生成 5–10 套自适应套卷（配比：60% 历史薄弱项 + 25% 未见题 + 15% 巩固题）。
   - **产出**：连续 3 套达到及格线以上，确立信心，达成 Exam-Ready 状态。

### 💡 学习操作指引：阶段闯关 vs 自由刷题 (How to Practice)
- **循序渐进闯关（推荐）：** 建议按 **Stage 01 ➔ 05** 顺序推进（摸底 ➔ 专项 ➔ 清错 ➔ 模考 ➔ 冲刺），形成认知闭环。
- **完全自由不锁死：** 各阶段**不设前置锁死门槛**。学生可在首页直接点击任意 Stage 卡片，或点击左侧具体考点模块针对性强化。
- **练习模式（即选即核） vs 模考模式（整卷交卷）：**
  - **日常练习（阶段 1/2/3/5）：** 提交后立即显示对错、详尽中英双语解析与 **A-D 干扰项逐项剖析 (`why_wrong`)**；支持 `A`–`D` 键盘快捷键。
  - **全真模考（阶段 4）：** 严格倒计时全卷测试，作答自动暂存 `sessionStorage` 防止刷新丢失；交卷后生成成绩单、及格判定与弱项突破建议。
- **离线持久化：** 所有答题数据、错题集与收藏题目完全保存在浏览器本地（`localStorage`），支持一键 JSON 导出与跨设备导入。

---

## 三、 题库格式与多题型规范 (`questions.json`)

题库支持 **单选 (Single)**、**多选 (Multiple)**、**判断题 (Boolean)**、**问答题 (Short)**，并原生支持 **数学公式 (LaTeX/MathML)** 与 **代码块 (Markdown Code Blocks)**：

### 1. 题目对象格式说明
```json
[
  {
    "id": "MATH-001",
    "concept_id": "quadratic-formula",
    "topic": "Algebra",
    "type": "single",
    "difficulty": 2,
    "en": "For the equation $ax^2 + bx + c = 0$, what is the discriminant?",
    "zh": "对于一元二次方程 $ax^2 + bx + c = 0$，其判别式是什么？",
    "choices_en": ["$b^2 - 4ac$", "$b^2 + 4ac$", "$\\sqrt{b^2 - 4ac}$", "$-b / (2a)$"],
    "choices_zh": ["$b^2 - 4ac$", "$b^2 + 4ac$", "$\\sqrt{b^2 - 4ac}$", "$-b / (2a)$"],
    "answer": 0,
    "explanation_en": "The discriminant $\\Delta = b^2 - 4ac$ determines the number and type of roots.",
    "explanation_zh": "判别式 $\\Delta = b^2 - 4ac$ 决定方程实根的个数与性质。",
    "why_wrong_en": [
      "Correct: $\\Delta = b^2 - 4ac$.",
      "Sign error: should be minus $4ac$, not plus.",
      "This is the radical term inside the quadratic formula.",
      "This is the axis of symmetry $x = -b/(2a)$."
    ],
    "why_wrong_zh": [
      "正确：判别式为 $\\Delta = b^2 - 4ac$。",
      "符号错误：应为减去 $4ac$ 而非加上。",
      "这是求根公式中的根号部分，而不是判别式本身。",
      "这是对称轴公式 $x = -b/(2a)$。"
    ]
  }
]
```

### 2. 题型与答案规范
- **单选 (`type`: "single" 或缺省)**：`answer` 为整数索引 `0, 1, 2, ...`。
- **多选 (`type`: "multiple")**：`answer` 为数组 `[0, 2]`。界面会自动呈现复选框并要求提交验证。
- **判断题 (`type`: "boolean")**：`choices_en` 填写 `["True", "False"]`，`answer` 为 `0` 或 `1`。
- **问答题 (`type`: "short")**：无选项；不需要 `choices_*`/`answer`，改填 `answer_en`/`answer_zh`（参考答案，字符串），可选 `rubric_en`/`rubric_zh`（得分要点列表）。练习模式下输入答案后显示参考答案，由学习者自评「答对了/需加强」并计入错题本；限时模考中问答题不计入自动评分，仅在复盘时对照参考答案。
- **数学公式**：使用 `$E = mc^2$` 或 `$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$`，前端自动渲染为优美的数学排版。
- **代码块**：使用 ```java ... ``` 包裹代码，前端自动进行等宽字体格式化。

---

## 四、 命令行操作指南

本项目不依赖任何外部 pip 包，仅使用 Python 3 标准库：

### 1. 校验题库与考试配置
```bash
python scripts/validate_bank.py examples/questions.json --profile examples/exam_profile.json
```
- 会校验所有 ID 唯一性、题干排重、中英完整性、错因归因匹配度以及各模块分布统计。

### 2. 生成离线自适应网站
```bash
python scripts/build_site.py examples/questions.json \
  --profile examples/exam_profile.json \
  --out practice.html
```
也可以直接在命令行覆盖部分参数：
```bash
python scripts/build_site.py examples/questions.json \
  --title "AP Computer Science A Mock" \
  --pass-score 75 \
  --mins 90 \
  --out ap_csa_practice.html
```

### 3. 打开与使用
直接在 Chrome、Safari、Edge 等主流现代浏览器双击打开生成的 `practice.html`。
- **完全离线**：断网可用，无 CDN 延迟。
- **主题切换**：支持 4 种风格（Cyber Dark 赛博黑、Academic Light 学院白、Midnight Navy 午夜深蓝、Forest Green 森林绿）。
- **动态防作弊**：支持一键开启 **🎲 选项乱序**（选项随机打乱且保证答案与错因精准对应）。
- **跨设备同步**：通过“导出进度 / 导入进度”迁移学习记录。

---

## 五、 零题库启动模式：自主搜索与原创重构 (Autonomous Search & Redesign)

很多实际场景中，用户手里**没有现成的题库文件或 PDF**，仅有考试名称和期望的题目数量（如：“帮我做 100 道题的 AP 宏观经济学刷题站”）。此时 Agent 会自动触发 **Mode B: 自主搜索与原创重构链路**：

```
[用户输入: 仅考试名+目标题量]
             │
             ▼
[Step 1: 联网检索官方蓝图] ──► 搜索官方考纲 (CED / Syllabus) 与模块分值权重
             │
             ▼
[Step 2: 拆解微能力矩阵]   ──► 将目标题量 (如 100 题) 按考纲权重分摊至各 Topic/Concept
             │
             ▼
[Step 3: 靶向原创命题重构] ──► 严禁侵权抄袭原题；基于考点情境化原创命题 (同构题/变体)
             │
             ▼
[Step 4: 双语精修与错因生成] ──► 自动补全中英文题干、详细解析与 4 个选项逐项错因剖析
             │
             ▼
[Step 5: 自动校验并编译交付] ──► 调用 validate_bank.py 校验后生成 practice.html
```

### 为什么必须是“重构 (Redesign)”而不是简单“爬取”？
1. **版权与合规红线**：商业考试与官方考卷（如 College Board、DECA、ETS）原题受严格版权保护，直接抓取原题存在侵权与下架风险。
2. **防过时与针对性**：官方题库往往年代跨度大、考纲已更新。通过 Agent 按**最新大纲能力点**重新命制现代情境题，效度更高。
3. **避免低质假膨胀**：Agent 在重构时必须为每道题分配独立的 `concept_id`，确保 100 道题覆盖 80~100 个真实微考点，杜绝用 5 个模板换数字刷水题。
4. **全量错因生成**：网上抓取的题库通常只有单字母答案（如“选 C”），而 Agent 原创重构能补齐关键的 **`why_wrong_en` / `why_wrong_zh`（干扰项为什么错）**，形成真正的自适应学习闭环。


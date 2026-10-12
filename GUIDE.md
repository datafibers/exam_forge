# 考试系统与 Agent Skill 完整使用指南 (Exam Forge Usage Guide)

本指南指导学生、教师及 AI Agent 如何使用 `exam-practice-builder` 技能，将零散的考资转化为高仿真、可追踪、多主题、支持公式与编程题的**双语自适应备考网站**。

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

---

## 三、 题库格式与多题型规范 (`questions.json`)

题库支持 **单选 (Single)**、**多选 (Multiple)**、**判断题 (Boolean)**，并原生支持 **数学公式 (LaTeX/MathML)** 与 **代码块 (Markdown Code Blocks)**：

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


# Exam Forge — Exam Practice Builder (Agent Skill)

Turn user-provided exam resources into a **bilingual adaptive practice website** with traceable questions, a 5-stage progressive mastery roadmap, realistic timed mocks, and modern multi-theme UI.

Zero external dependencies — pure standard Python 3. Works 100% offline with zero CDN dependencies.

---

## 🌟 核心特性 (Key Features)

1. **考试档案配置 (Exam Profile Integration)**：
   - 完整记录考试名称、官方大纲/考纲 URL、正式考试时长、官方及格达标线（如 75%）、目标题库规划量与模考套数。
2. **循序渐进的五阶学习体系 (5-Stage Progressive Learning)**：
   - 拒绝单一盲目刷题，提供清晰阶梯：**摸底诊断 ➔ 专题精练 ➔ 错题清零 ➔ 全真模考 ➔ 冲刺达标**。
   - 模考与练习后提供基于目标及格线的达标判定（Passed / Not Yet Passed）与考后深度复盘。
3. **多主题与专属考试徽标 (Multi-Theme & SVG Exam Crest)**：
   - 4 款内置现代主题：**Cyber Dark (赛博深色)**、**Academic Light (学院浅色)**、**Midnight Navy (午夜深蓝)**、**Forest Green (护眼森绿)**。
   - 根据考试代号/简称（如 DECA, AMC, AP）自动生成精致的矢量 SVG 考试勋章 Crest。
4. **数理公式与编程题支持 (Math LaTeX & Code Snippets)**：
   - 原生支持数学公式 `$E = mc^2$`、`$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$`（适用 AMC / AP 数理）。
   - 原生支持等宽代码块 ```` ```python ... ``` ```` 与行内代码 `` `code` ``（适用 AP CSA / 计算机认证）。
5. **多题型与动态防死记硬背 (Multi-types & Choice Shuffling)**：
   - 支持单选题 (`single`)、多选题 (`multiple`)、判断题 (`boolean`)。
   - 可一键开启 **🎲 选项动态乱序 (Shuffle Choices)**，打乱选项同时精准保持答案与每项错因分析（`why_wrong`）的 1:1 映射。
6. **零题库自主搜索与原创重构 (Autonomous Search & Redesign)**：
   - 当用户不提供任何现成题目或文件时，仅凭考试名称与目标题量，Agent 会自主联网检索官方考纲蓝图（CED / Syllabus），按考纲权重拆解微知识点矩阵，靶向原创重构高仿真试题与干扰项深度错因，严守版权合规并达标指定题量。


---

## 🚀 快速开始 (Quick Start)

只需系统自带 Python 3，无需安装任何 pip 包：

```bash
# 1. 校验题库与考试档案完整性
python scripts/validate_bank.py examples/questions.json --profile examples/exam_profile.json

# 2. 生成单文件离线备考网站
python scripts/build_site.py examples/questions.json --profile examples/exam_profile.json --out practice.html
```

直接在任何浏览器（Chrome, Safari, Edge）双击打开 `practice.html` 即可开始做题。学习记录保存在本地 `localStorage`，支持 JSON 导入/导出跨设备迁移。

---

## 📂 项目结构 (Project Structure)

- [`SKILL.md`](SKILL.md)：Agent Skill 核心规范指令（支持 Claude Code, Codex, Antigravity 等）。
- [`GUIDE.md`](GUIDE.md)：**详细使用指南**（考试档案 schema、五阶学习方法论、题型规范与操作指令）。
- [`scripts/validate_bank.py`](scripts/validate_bank.py)：题库与配置校验脚本（排重、双语对称、题型合法性）。
- [`scripts/build_site.py`](scripts/build_site.py)：离线单文件站点构建器（嵌入数据、多主题、SVG 徽标与逻辑）。
- [`examples/exam_profile.json`](examples/exam_profile.json)：考试配置模板（时长、及格线、官方链接、学习阶段）。
- [`examples/questions.json`](examples/questions.json)：支持公式、代码、多选、判断题的高质量题库范例。

---

## 🤖 Agent 提示词示例 (Prompt Template)

```text
Use the exam-practice-builder skill to create a bilingual English/Chinese adaptive training site from the resources I provide:
- Exam Name: [e.g. AP Computer Science A / Ontario DECA EIP / AMC 10]
- Official Syllabus URL: [Link]
- Target Duration: [e.g. 70 mins], Passing Score: [e.g. 75%]
- Target Bank Size: [e.g. 200 distinct concepts]
Produce verified questions.json, exam_profile.json, and the final offline practice.html.
```

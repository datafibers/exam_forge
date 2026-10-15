# Exam Forge — Adaptive Exam Practice Builder (Agent Skill)

[English](README.md) | [简体中文](README_zh.md) | [System Design](DESIGN.md) | [Usage Guide](GUIDE.md)

> Turn exam resources **or** autonomous web research into a standalone, **bilingual adaptive practice website** with traceable questions, a 5-stage progressive mastery roadmap, realistic timed mocks, and a modern multi-theme UI.

**Zero external dependencies** — built purely with standard Python 3. The generated single-file HTML runs 100% offline with no CDNs, credentials, or web servers required.

---

## 📸 System Preview

![Sample System Built - Exam Forge](assets/snapshot.png)

*Sample adaptive practice portal built with Exam Forge: featuring dynamic exam crest, domain mastery matrix, bilingual question stems with Math LaTeX, and interactive choice diagnostics.*

---

## 🎯 Core Architectural Pillars

Exam Forge is built on two foundational principles (see [DESIGN.md](DESIGN.md) for full design specifications):

1. **Authoring Authenticity & Syllabus Precision ("准")**
   - **Syllabus-Aligned Mapping**: Calibrates question quotas strictly against official testing authority domain weights (e.g., College Board CED, DECA Guide, AWS blueprints).
   - **Concept Atomicity (`concept_id`)**: Every question is tied to a discrete knowledge atom to prevent repetitive, superficial clones.
   - **In-Depth Distractor Analysis**: Every choice includes complete bilingual reasoning (`why_wrong_en/zh`) explaining why it is correct or incorrect.

2. **Progressive Cognitive Mastery ("效")**
   - **5-Stage Learning Roadmap**: Seamlessly guides learners through **Diagnostic Baseline ➔ Topic Competency Drilling ➔ Targeted Mistake Elimination ➔ Real-World Timed Mock ➔ Final Adaptive Sprint**.
   - **Adaptive Sprint Engine**: Dynamically synthesizes practice sets weighted with 60% weak domains, 25% unattempted items, and 15% spaced retention.
   - **Private & Resilient**: 100% client-side `localStorage` persistence with mock crash recovery (`sessionStorage`) and JSON export/import.

---

## 🌟 Key Highlights

- ⏱️ **Realistic Timed Mocks:** Official exam countdown, Pass/Fail benchmark verdicts (e.g., 75% cutoff), and session auto-recovery against accidental browser refreshes.
- 📐 **Math LaTeX & Code Snippets:** Native formula rendering (`$...$` and `$$...$$`) and monospace code blocks for STEM and CS examinations.
- 📝 **Multi-Question Types:** Native support for Single Choice, Multiple Choice (`type: "multiple"`), True/False (`type: "boolean"`), and Short Answer (`type: "short"`) with self-grading rubrics.
- 🎲 **Anti-Memorization Option Shuffling:** Randomizes choice order while keeping answer keys and distractor reasoning strictly synchronized.
- 🎨 **Multi-Theme UI & Dynamic Crest:** 4 built-in themes (Cyber Dark, Academic Light, Midnight Navy, Forest Green) with an auto-generated SVG monogram crest.
- 🖨️ **Printable Paper Mode (`@media print`):** Formats clean paper exam sheets with candidate header and an answer key appendix for offline classrooms.

---

## 🚀 Quick Start

Requires only standard Python 3. Zero `pip install` needed:

```bash
# 1. Validate question bank integrity and exam profile
python3 scripts/validate_bank.py examples/questions.json --profile examples/exam_profile.json

# 2. Build the single-file offline adaptive website
python3 scripts/build_site.py examples/questions.json --profile examples/exam_profile.json --out practice.html
```

Double-click `practice.html` in Chrome, Safari, or Edge to begin practicing immediately.

---

## 🤖 Dual Operating Modes

- **Mode A (Resource-Guided):** Provide past exam PDFs, notes, or syllabi. The Agent parses concepts, authors aligned scenario questions, and builds the portal.
- **Mode B (Autonomous Search & Redesign):** Provide only an exam title. The Agent autonomously searches official blueprints, maps competency weights, and authors 100% original, copyright-compliant scenario items.

---

## 📂 Repository Structure

```text
exam_forge/
├── SKILL.md                  # Agent Skill definition & operational guardrails
├── DESIGN.md                 # System architecture & cognitive design philosophy
├── GUIDE.md                  # Comprehensive user manual & syllabus authoring guide
├── README.md                 # English documentation
├── README_zh.md              # 简体中文说明文档
├── scripts/
│   ├── validate_bank.py      # Schema, translation, deduplication, & profile validator
│   └── build_site.py         # Multi-theme single-file HTML website compiler
├── examples/
│   ├── exam_profile.json     # Exam metadata profile (benchmark template)
│   ├── questions.json        # Verified bilingual test bank with Math, Code, & distractors
│   └── resources.json        # External resource tracking & licensing configuration
├── assets/
│   ├── snapshot.png          # Sample system screenshot
│   ├── roadmap.svg           # 5-stage progressive learning roadmap
│   └── workflow.svg          # Pipeline workflow diagram
└── practice.html             # Generated standalone offline mock testing portal
```

---

## 📖 Further Reading

- [System Design & Architecture (DESIGN.md)](DESIGN.md) — Cognitive models, pipeline mechanics, and client state machine.
- [Usage & Question Bank Guide (GUIDE.md)](GUIDE.md) — Intake survey protocol, question schema, and custom exam authoring.
- [Agent Skill Specification (SKILL.md)](SKILL.md) — Agent execution prompt and quality red lines.

# Exam Forge — System Design & Architecture (系统设计与架构文档)

[English](DESIGN.md) | [简体中文](GUIDE.md)

This document details the architectural principles, cognitive learning models, synthesis pipeline, and client-side runtime of **Exam Forge**.

---

## 1. Core Design Philosophy: The Two Pillars (核心双核架构)

Exam Forge is fundamentally engineered around two interdependent pillars: **Authoring Authenticity ("准")** and **Progressive Cognitive Mastery ("效")**.

```mermaid
flowchart TD
  subgraph P1["🎯 Pillar 1: Targeted & Syllabus-Aligned Authoring (准)"]
    A["Official Blueprint & Weight Mapping (CED / Syllabus)"] --> B["Concept Atomicity & Anti-Homogeneity (concept_id)"]
    B --> C["High-Rigor Distractors & Scoring Rubrics"]
    C --> D["Cognitive Tiering (Bloom L1/L2/L3)"]
  end
  subgraph P2["📈 Pillar 2: Progressive & Efficient Learning Feedback Loop (效)"]
    E["1. Diagnostic Baseline (Expose Blind Spots)"] --> F["2. Topic Drilling (Targeted Mastery)"]
    F --> G["3. Mistake Elimination (Active Clearing)"]
    G --> H["4. Real-world Timed Mock (Pacing & Passing Mark)"]
    H --> I["5. Adaptive Sprint (Dynamic Review Sets)"]
  end
  P1 ==>|High-Fidelity Question Bank| P2
```

### Pillar 1: Authoring Authenticity & Syllabus Precision ("准")
1. **Curriculum Weight Calibration (`domain_weights`):**
   - Instead of generating questions randomly, the engine analyzes official examination specifications (e.g., College Board CED, DECA Guide, AWS Exam Guides, AMC syllabi).
   - Domain percentages (`domain_weights` in `exam_profile.json`, e.g., Domain A: 30%, Domain B: 40%, Domain C: 30%) are validated against the actual question bank and drive proportional sampling in Timed Mocks.
2. **Concept Atomicity (`concept_id`):**
   - Each problem is tagged with an atomic `concept_id` representing a distinct, non-fungible syllabus skill.
   - Prevents AI hallucination and repetitive numerical clones (e.g., 50 questions that merely change numbers in the same formula).
3. **Cognitive Tiering (Bloom's Taxonomy):**
   - **Difficulty 1 (Recall & Definition):** Fundamental terms, core theorems, baseline assumptions.
   - **Difficulty 2 (Application & Calculation):** Multi-step problem solving, quantitative evaluations, scenario diagnosis.
   - **Difficulty 3 (Synthesis & Edge-Case Traps):** Boundary conditions, cross-topic integration, counter-intuitive distractor reasoning.
4. **5 Question Types, Distractor Rigor & Rubrics:**
   - Supports **Single-Choice** (`single`), **Multiple-Choice** (`multiple`), **True/False** (`boolean`), **Objective Fill-in-the-Blank / Numerical** (`fill` with fraction/percentage parsing and `tolerance`), and **Open-Ended Short Answer** (`short`).
   - Every choice-based distractor provides explicit diagnostic explanations (`why_wrong_en/zh`) pinpointing the underlying misconception.
   - Short-answer questions (`type: "short"`) include canonical reference answers (`answer_en/zh`), structured rubrics (`rubric_en/zh`), and interactive self-grading in Timed Mocks.

---

### Pillar 2: Progressive Mastery & Closed-Loop Efficiency ("效")

Rather than forcing learners into repetitive, static full-length mocks, Exam Forge implements a progressive 5-stage mastery framework:

```mermaid
flowchart LR
  classDef stage fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
  classDef goal fill:#0f172a,stroke:#10b981,stroke-width:2.5px,color:#34d399;

  S1["🎯 <b>Stage 1: Diagnostic</b><br/>Stratified Baseline Sample"]:::stage
  S2["📚 <b>Stage 2: Topic Drill</b><br/>Weighted Domain Deep-Dive"]:::stage
  S3["🔥 <b>Stage 3: Mistake Killer</b><br/>2-Streak Graduation"]:::stage
  S4["⏱️ <b>Stage 4: Timed Mock</b><br/>Syllabus-Weighted Simulation"]:::stage
  S5["🏆 <b>Stage 5: Adaptive Sprint</b><br/>Targeted Score Booster"]:::goal

  S1 -->|Weaknesses Identified| S2
  S2 -->|Error Patterns Captured| S3
  S3 -->|Mistakes Cleared| S4
  S4 -->|Benchmark Assessed| S5
```

1. **Stage 1 (Diagnostic Baseline):** Syllabus-weighted stratified sampling across all curriculum domains to map baseline competency without time pressure.
2. **Stage 2 (Topic Competency Drilling):** Weighted sampling (`computeQuestionWeight`) on selected domains prioritizing weak concepts, unattempted items, and spaced time decay.
3. **Stage 3 (Targeted Mistake Elimination):** Dynamic error queue requiring **2 consecutive correct attempts** (`streak >= 2`) before graduating an item out of the mistake bank.
4. **Stage 4 (Real-world Timed Simulation):** Strict exam countdown and official domain-weighted question volume, with interactive post-exam self-grading for short-answer items and accidental refresh recovery.
5. **Stage 5 (Adaptive Sprint to Certification):** Synthesizes optimized practice sets dynamically weighted:
   - **60% Weak Domains & Active Mistakes:** Concentrated weighted practice on areas with the lowest Bayesian-smoothed accuracy.
   - **25% Unattempted Items:** Fresh problems to eliminate blind spots.
   - **15% Spaced Retention:** Time-decay weighted review of previously answered items to prevent memory decay.

---

## 2. Pipeline & Workflow Architecture (管线架构与工作流)

![Exam Forge Pipeline & Usage Architecture](assets/workflow.svg)

```mermaid
flowchart TD
  subgraph Inputs["1. Exam Resources / Prompts"]
    M1["📄 <b>Mode A: User Resources</b><br/>PDFs, Syllabi, Study Notes, Past Papers"]
    M2["🔍 <b>Mode B: Autonomous Search</b><br/>Web Blueprint & CED Retrieval"]
  end

  subgraph Engine["2. Exam Forge Pipeline (Standard Python)"]
    E1["⚙️ <b>Concept Extraction & Batch Merger</b><br/><code>scripts/merge_bank.py</code>"]
    E2["🎲 <b>Single/Bilingual Normalization & Distractors</b><br/><code>normalize_question()</code>"]
    E3["🛡️ <b>Quality & Weight Validator</b><br/><code>scripts/validate_bank.py</code>"]
    E4["⚡ <b>Zero-Dependency Compiler</b><br/><code>scripts/build_site.py</code>"]
  end

  subgraph Output["3. Standalone Client: practice.html"]
    O1["🌐 <b>100% Offline Single-File Website</b><br/>Cyber / Light / Navy / Forest Themes"]
    O2["📈 <b>5-Stage Visual Learning Progression</b><br/>Interactive Timeline & Diagram Figures"]
    O3["🖨️ <b>PDF & Paper Print Mode</b><br/>Offline Exam Sheets with Answer Keys"]
  end

  M1 --> E1
  M2 --> E1
  E1 --> E2 --> E3 --> E4 --> O1
  O1 --> O2
  O1 --> O3
```

### Dual Operating Modes
- **Mode A (Resource-Guided):** Ingests raw inputs (PDFs, study notes, past papers), extracts core competencies, deduplicates knowledge points, and formats items into bilingual JSON.
- **Mode B (Autonomous Search & Redesign):** Triggered when no question bank is provided. The agent searches official authority portals, extracts the curriculum blueprint, and synthesizes 100% original, copyright-compliant scenario questions adhering to official domain weights.

---

## 3. Client-Side Runtime & State Machine (离线运行时设计)

### Zero-Dependency Architecture
The output `practice.html` is a standalone, single-file application requiring zero external network requests, CDNs, or server infrastructure.

```text
┌────────────────────────────────────────────────────────┐
│ practice.html (Standalone Client)                      │
│                                                        │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Embedded JSON   │  │ Math & Code     │              │
│  │ (Bank & Profile)│  │ Parser Engine   │              │
│  └─────────────────┘  └─────────────────┘              │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ 5-Stage Adaptive│  │ Timed Mock      │              │
│  │ Engine          │  │ Session Recovery│              │
│  └─────────────────┘  └─────────────────┘              │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ LocalStorage    │  │ @media print    │              │
│  │ State Sync      │  │ Paper Generator │              │
│  └─────────────────┘  └─────────────────┘              │
└────────────────────────────────────────────────────────┘
```

- **Offline Storage (`localStorage`):** Tracks question attempt histories, mistake banks, bookmarks (`⭐`), current stage, language preference (`en`/`zh`), and theme selection.
- **Crash Recovery (`sessionStorage`):** During timed mocks, question order, elapsed time, and entered answers are mirrored every second. Browser crashes or accidental page reloads restore the active mock state seamlessly.
- **Formula & Code Engine:** Native regex-based LaTeX parser supporting `$inline$` and `$$block$$` formulas without heavy external MathJax/KaTeX bundles. Code snippets support syntax indentation and dark-theme contrast.
- **Option Permutation:** When "Shuffle Choices" is enabled, options are randomized per question while preserving 1:1 mathematical alignment with the answer key and option-specific distractor explanations.

---

## 4. Quality Gates & System Guardrails (质量红线)

1. **Anti-Hallucination & Provenance:** Clearly demarcate original synthetic items from official practice materials. Never invent past-paper provenance.
2. **Concept Diversity Ratio:** Automated validator enforces a minimum unique `concept_id` count to prevent template redundancy.
3. **Bilingual Parity:** Both English and Chinese stems, choices, and explanations must maintain equivalent semantic fidelity and technical rigor.
4. **Data Privacy:** 100% local persistence ensures student study data and test scores never leave the local device.

---
name: exam-practice-builder
description: Turn user-provided exam resources OR autonomous web research into a bilingual adaptive practice website with traceable questions, progressive mastery stages, realistic timed mocks, and multi-theme UI.
---
# Exam Practice Builder

## Purpose
Build a **subject-agnostic English/Chinese progressive practice system** from either:
- **Mode A (Resource-Guided):** User-provided resources (PDFs, URLs, notes, sample exams, spreadsheets).
- **Mode B (Autonomous Search & Redesign):** Zero initial questions provided — Agent autonomously searches official syllabi, course blueprints, topic weights, and authors original exam-grade questions to reach the requested target quantity.

Produces a standalone, zero-dependency offline HTML site and editable source files. Suitable for DECA EIP, AMC, AP (CSA, Calc, Physics, Econ), Biology Olympiad, AWS/GCP, professional certifications, etc.

## Trigger
Use when asked to create, rebuild, expand, or curate exam-practice websites, mock testing portals, or question banks from study resources OR from an exam name alone. Do not trigger for simply answering one single practice question.

## Core Pillars & Features
1. **Exam Profile & Target Metrics:** Explicitly track exam identity, official syllabus URL, duration, official mock item count, passing score benchmark (e.g. 75%), and target concept bank size.
2. **Autonomous Search & Redesign Pipeline (零题库自主重构能力):**
   - When no questions are provided, Agent actively searches official testing authority blueprints (e.g., College Board CED, DECA Guide, AMC syllabus).
   - Generates an accurate competency weight matrix.
   - Authors 100% original, copyright-compliant scenario items up to the requested target count without scraping verbatim proprietary tests.
3. **5-Stage Progressive Learning Framework:**
   - **Stage 1 (Diagnostic Baseline):** Stratified sample to expose blind spots and establish baseline competency.
   - **Stage 2 (Topic Competency Drilling):** Focused domain practice with bilingual distractor analysis (`why_wrong_en/zh`).
   - **Stage 3 (Mistake Elimination):** Bayesian-smoothed mistake killer targeting high-frequency pitfalls until 100% resolved.
   - **Stage 4 (Real-world Timed Mock):** Official duration countdown with pass/fail threshold verdict against the benchmark.
   - **Stage 5 (Adaptive Sprint to Certification):** 5–10 personalized test sets balancing 60% weak domains, 25% unattempted, and 15% retention review.
4. **Multi-theme UI & Dynamic Exam Crest:**
   - 4 built-in themes: Cyber Dark, Academic Light, Midnight Navy, Forest Green.
   - Dynamic SVG Exam Crest logo generated from the exam monogram/initials (e.g. `DECA`, `AMC`, `AP`, `MATH`).
5. **Math, Code, & Multi-Question Types Support:**
   - Render inline and block formulas (`$...$` and `$$...$$`) via native lightweight Math formatting.
   - Render programming code blocks (`` `code` `` and ```` ```python ... ``` ````).
   - Support Single Choice, Multiple Choice (`type: "multiple"`), and True/False (`type: "boolean"`).
6. **Anti-Memorization Option Shuffling:** Toggleable option permutation that maintains strict 1:1 mapping with answer keys and distractor reasoning.

---

## Operating Workflow & Intake Protocol

### Step 0: Mandatory Intake Survey (Always Initiated, Skippable)
Whenever this skill is triggered, the Agent **MUST ALWAYS prompt the user with an interactive intake survey** (using the `ask_question` tool or structured prompt) before writing files.

The survey allows the user to quickly align requirements, or click **Skip** / choose default to let AI make autonomous decisions based on official research:

**Intake Survey Structure:**
1. **Resource Mode:**
   - `(Recommended) Mode B: Zero-Bank — Let AI autonomously research official blueprints & author original items`
   - `Mode A: User-Provided — I have PDFs / study URLs / past questions to parse`
2. **Target Question Capacity:**
   - `(Recommended) Quick Sample / Standard Mock (20–25 questions)`
   - `Full Competition / Comprehensive Exam (40–50 questions)`
   - `Deep Domain Bank (80–100+ questions)`
   - `Custom Count: User specifies exact number (e.g. 15, 30, 60, 120 questions)`
3. **Timer & Passing Benchmark:**
   - `(Recommended) Autonomous Research: Auto-detect official MAA/CollegeBoard/DECA duration and pass cutoff`
   - `Custom: 60 minutes, 75% passing mark`
   - `Practice Only: Untimed, no pass threshold`
4. **Language & Special Formats:**
   - `(Recommended) Bilingual Parity (EN/ZH) with auto Math LaTeX / Code snippets`
   - `English Only`
   - `Chinese Only`

**Handling Survey Outcomes & "Skip Remaining":**
- **Skip Entirely:** The user clicks Skip without answering ➔ The Agent automatically prompts for the exam topic (if not yet provided), then applies full AI Autonomous Defaults (Mode B, official timing/passing score, 20–25 questions, bilingual parity).
- **Skip All Remaining Questions (Once Topic is Given):** As soon as the exam topic is identified, the user can answer any single question they care about (e.g. only specify question count or only specify source documents) and **skip all remaining questions** (or say *"skip remaining / rest decided by AI"*). Any unanswered question seamlessly adopts AI smart defaults.
- **Customized Submissions:** The Agent preserves all explicit user preferences and fills any remaining unstated parameters via autonomous web research.

---

### Step 1: Mode Execution

#### Mode A: User-Provided Resources
Use when user provides PDFs, URLs, syllabi, or past paper files. Ingest, extract concepts, ensure no duplicates, and synthesize aligned scenario items.

#### Mode B: Autonomous Search & Redesign (Zero-Bank)
1. **Search & Blueprint Discovery:**
   - Use `search_web` to find the official curriculum guide, exam breakdown, topic percentages, duration, and question formats.
   - Fetch official details via `read_url_content`.
2. **Construct Competency & Weight Matrix:**
   - Apportion the requested question count according to official domain percentages (e.g., Domain A: 30%, Domain B: 40%, Domain C: 30%).
   - Establish unique `concept_id` tags for each distinct knowledge point to prevent superficial clones.
3. **Redesign & Original Question Synthesis:**
   - Author original, syllabus-calibrated questions adhering to Bloom's cognitive taxonomy.
   - Provide realistic numerical parameters, plausible distractors, and complete bilingual explanations (`explanation_en/zh` and `why_wrong_en/zh`).
   - Avoid direct verbatim copies of copyrighted live past papers; author original homomorphic/scenario-based problems.
4. **Build Profile & Validate Bank:**
   - Save metadata to `examples/exam_profile.json` (or `<exam_slug>/exam_profile.json`).
   - Save items to `questions.json`.
   - Run `python scripts/validate_bank.py questions.json --profile exam_profile.json`.
5. **Compile & Deliver:**
   - Run `python scripts/build_site.py questions.json --profile exam_profile.json --out practice.html`.
   - Deliver the standalone HTML and audit report (topic distribution, verified concepts, passing benchmark).

---

## Quality Gates
- **Anti-Hallucination & Provenance:** Never claim a full past exam was read if it was not. Differentiate official materials from original synthetic items. Never invent past-exam provenance.
- **Official Rules Honesty:** Never label unverified estimates as official rules. Mark unverified time limits and passing thresholds clearly as practice defaults or unverified benchmarks. Never silently assume written-event rubrics equal multiple-choice online exam blueprints.
- **Concept Authenticity:** Never generate 100 questions from only 5 repetitive templates. Report distinct `concept_id` count vs variations.
- **Distractor Rigor:** Every option must have a clear rationale explaining why it fails or why it is correct.
- **True Offline Portability:** No external fonts, scripts, CDNs, or server dependencies. Progress stored in `localStorage` with JSON export/import.
- **Bilingual Parity:** Ensure equal depth and accuracy between English and Chinese explanations.

---

## Useful Prompts
- **Autonomous Search & Redesign:** “Create a 60-question bilingual practice site for AP Microeconomics. I have no reference question bank—search the official College Board CED, map unit weights, and author original questions with distractor analysis.”
- **Target Count Redesign:** “Here is an exam syllabus URL. Redesign and generate 100 distinct questions covering all major competencies with passing score 75%.”
- **Audit & Expansion:** “Audit the existing questions.json and expand it with 50 new high-difficulty items on Unit 4.”

---
name: exam-practice-builder
description: Turn user-provided exam resources into a bilingual adaptive practice website with traceable questions, progressive mastery stages, realistic timed mocks, and multi-theme UI.
---
# Exam Practice Builder

## Purpose
Build a **subject-agnostic English/Chinese progressive practice system** from a user's list of source resources (PDFs, URLs, text, sample exams, syllabi). Produce a standalone, zero-dependency offline HTML site and editable source files. Suitable for DECA EIP, AMC, AP (CSA, Calc, Physics), Biology Olympiad, professional certifications, etc.

## Trigger
Use when asked to create, rebuild, expand, or curate exam-practice websites, mock testing portals, or question banks from study resources. Do not trigger for simply answering one practice question.

## Core Pillars & Features
1. **Exam Profile & Target Metrics:** Explicitly track exam identity, official syllabus URL, duration, official mock item count, passing score benchmark (e.g. 75%), and target concept bank size.
2. **5-Stage Progressive Learning Framework:** Avoid passive, repetitive rote drilling. Guide learners along a structured mastery ladder:
   - **Stage 1 (Diagnostic Baseline):** Stratified sample to expose blind spots and establish baseline competency.
   - **Stage 2 (Topic Competency Drilling):** Focused domain practice with bilingual distractor analysis (`why_wrong_en/zh`).
   - **Stage 3 (Mistake Elimination):** Bayesian-smoothed mistake killer targeting high-frequency pitfalls until 100% resolved.
   - **Stage 4 (Real-world Timed Mock):** Official duration countdown with pass/fail threshold verdict against the benchmark.
   - **Stage 5 (Adaptive Sprint to Certification):** 5–10 personalized test sets balancing 60% weak domains, 25% unattempted, and 15% retention review.
3. **Multi-theme UI & Dynamic Exam Crest:**
   - 4 built-in themes: Cyber Dark, Academic Light, Midnight Navy, Forest Green.
   - Dynamic SVG Exam Crest logo generated from the exam monogram/initials (e.g. `DECA`, `AMC`, `AP`, `MATH`).
4. **Math, Code, & Multi-Question Types Support:**
   - Render inline and block formulas (`$...$` and `$$...$$`) via native lightweight Math formatting.
   - Render programming code blocks (`` `code` `` and ```` ```python ... ``` ````).
   - Support Single Choice, Multiple Choice (`type: "multiple"`), and True/False (`type: "boolean"`).
5. **Anti-Memorization Option Shuffling:** Toggleable option permutation that maintains strict 1:1 mapping with answer keys and distractor reasoning.

---

## Required Workflow
1. **Intake & Profile Setup:**
   - Inquire or detect: `exam_name`, `official_url`, `passing_score_pct`, `exam_duration_mins`, `mock_questions_count`, and `target_bank_size`.
   - Store or configure via `exam_profile.json` (see `examples/exam_profile.json`).
2. **Retrieve & Verify Resources:**
   - Differentiate official syllabi, past exams, unofficial drill sheets, and user notes.
   - Respect copyright and licensing. Do not suggest official coverage beyond verified materials.
3. **Map Competencies & Curate Concepts:**
   - Tag each item with `topic`, `concept_id`, `difficulty` (1–3), and `source_type`.
   - Author original, syllabus-aligned questions with 4 plausible options, bilingual text, and detailed distractor analysis (`why_wrong_en` / `why_wrong_zh`).
   - Avoid superficial duplicates: report distinct `concept_id` count vs `variant_of` count.
4. **Validate Question Bank & Profile:**
   - Run `python scripts/validate_bank.py questions.json --profile exam_profile.json`.
   - Verify zero broken references, translations, duplicate stems, or index out-of-bounds errors.
5. **Generate Standalone Site:**
   - Run `python scripts/build_site.py questions.json --profile exam_profile.json --out practice.html`.
   - Verify resulting HTML operates 100% offline with zero CDN dependencies.
6. **Deliver:**
   - Provide the standalone `practice.html` for immediate student use.
   - Deliver project files (`questions.json`, `exam_profile.json`, scripts) for future expansion.
   - Provide an evidence audit: distinct concept count, total questions, syllabus coverage %, and verified exam rules.

---

## Quality Gates
- **Anti-Hallucination:** Never claim a full past exam was read if it was not. Never invent past-exam provenance.
- **Concept Authenticity:** Never generate 1,000 near-duplicate items merely to hit an arbitrary count.
- **Distractor Rigor:** Every option must have a clear rationale explaining why it fails or why it is correct.
- **True Offline Portability:** No external fonts, scripts, CDNs, or server dependencies. Progress stored in `localStorage` with JSON export/import.
- **Bilingual Parity:** Ensure equal depth between English and Chinese explanations.

---

## File Specifications
- **Exam Profile (`exam_profile.json`):** Contains `exam_name`, `exam_code`, `official_url`, `passing_score_pct`, `exam_duration_mins`, `mock_questions_count`, `target_bank_size`, `logo_monogram`, `theme_default`.
- **Question Bank (`questions.json`):** Array of objects with `id`, `topic`, `difficulty`, `en`, `zh`, `choices_en`, `choices_zh`, `answer`, `explanation_en`, `explanation_zh`, `why_wrong_en`, `why_wrong_zh`, `concept_id`, `type`.
- **Full Guide:** Refer to [`GUIDE.md`](file:///Users/willdu/Documents/github/exam_forge/GUIDE.md) for complete detailed instructions.
